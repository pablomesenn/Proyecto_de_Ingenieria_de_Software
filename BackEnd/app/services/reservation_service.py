from app.repositories.reservation_repository import ReservationRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.notification_repository import NotificationRepository
from app.services.notification_service import NotificationService
from app.constants.states import ReservationState
from app.models.reservation import Reservation
from app.config.database import get_db
from bson import ObjectId
from datetime import datetime, timedelta
from io import BytesIO
import csv
from openpyxl import Workbook
import logging

logger = logging.getLogger(__name__)


class ReservationService:
    """Servicio para logica de negocio de reservas"""

    def __init__(self):
        self.reservation_repo = ReservationRepository()
        self.inventory_repo = InventoryRepository()
        self.notification_service = NotificationService()

    def create_reservation(self, user_id, items, notes=None):
        """Crea una nueva reserva y retiene inventario"""

        # Validar disponibilidad para todos los items
        for item in items:
            variant_id = item['variant_id']
            quantity = item['quantity']

            if not self.inventory_repo.validate_availability(variant_id, quantity):
                raise ValueError(f"Stock insuficiente para variante {variant_id}")

        # Crear reserva
        reservation = Reservation(
            user_id=user_id,
            items=items,
            state=ReservationState.PENDING,
            notes=notes
        )

        reservation = self.reservation_repo.create(reservation)

        # Retener inventario
        for item in items:
            self.inventory_repo.increase_retained_stock(
                variant_id=item['variant_id'],
                quantity=item['quantity'],
                reason=f'reservation_{str(reservation._id)}_created'
            )

        return reservation

    def approve_reservation(self, reservation_id, admin_id, admin_notes=None):
        """Aprueba una reserva (CU-010)"""
        reservation = self.reservation_repo.find_by_id(reservation_id)

        if not reservation:
            raise ValueError("Reserva no encontrada")

        if reservation.state != ReservationState.PENDING:
            raise ValueError(f"No se puede aprobar una reserva en estado {reservation.state}")

        if not ReservationState.can_transition(reservation.state, ReservationState.APPROVED):
            raise ValueError("Transicion de estado invalida")

        # Actualizar estado
        update_data = {
            'state': ReservationState.APPROVED,
            'approved_at': datetime.utcnow(),
            'admin_notes': admin_notes
        }

        self.reservation_repo.update(reservation_id, update_data)

        # Registrar auditoria
        self._log_audit(admin_id, 'approve_reservation', reservation_id)

        return self.reservation_repo.find_by_id(reservation_id)

    def reject_reservation(self, reservation_id, admin_id, admin_notes=None):
        """Rechaza una reserva y libera inventario (CU-010)"""
        reservation = self.reservation_repo.find_by_id(reservation_id)

        if not reservation:
            raise ValueError("Reserva no encontrada")

        if reservation.state != ReservationState.PENDING:
            raise ValueError(f"No se puede rechazar una reserva en estado {reservation.state}")

        if not ReservationState.can_transition(reservation.state, ReservationState.REJECTED):
            raise ValueError("Transicion de estado invalida")

        # Liberar inventario
        for item in reservation.items:
            self.inventory_repo.decrease_retained_stock(
                variant_id=item['variant_id'],
                quantity=item['quantity'],
                reason=f'reservation_{str(reservation_id)}_rejected'
            )

        # Actualizar estado
        update_data = {
            'state': ReservationState.REJECTED,
            'rejected_at': datetime.utcnow(),
            'admin_notes': admin_notes
        }

        self.reservation_repo.update(reservation_id, update_data)

        # Registrar auditoria
        self._log_audit(admin_id, 'reject_reservation', reservation_id)

        return self.reservation_repo.find_by_id(reservation_id)

    def cancel_reservation(self, reservation_id, user_id=None, admin_id=None, is_forced=False):
        """Cancela una reserva y libera inventario (CU-009 y CU-010)"""
        reservation = self.reservation_repo.find_by_id(reservation_id)

        if not reservation:
            raise ValueError("Reserva no encontrada")

        # Validar permisos
        if user_id and str(reservation.user_id) != str(user_id):
            raise ValueError("No tienes permiso para cancelar esta reserva")

        # Validar estado
        if reservation.state not in [ReservationState.PENDING, ReservationState.APPROVED]:
            raise ValueError(f"No se puede cancelar una reserva en estado {reservation.state}")

        if not ReservationState.can_transition(reservation.state, ReservationState.CANCELLED):
            raise ValueError("Transicion de estado invalida")

        # Liberar inventario
        for item in reservation.items:
            self.inventory_repo.decrease_retained_stock(
                variant_id=item['variant_id'],
                quantity=item['quantity'],
                reason=f'reservation_{str(reservation_id)}_cancelled'
            )

        # Actualizar estado
        update_data = {
            'state': ReservationState.CANCELLED,
            'cancelled_at': datetime.utcnow()
        }

        self.reservation_repo.update(reservation_id, update_data)

        # Registrar auditoria
        actor_id = admin_id if admin_id else user_id
        action = 'force_cancel_reservation' if is_forced else 'cancel_reservation'
        self._log_audit(actor_id, action, reservation_id)

        return self.reservation_repo.find_by_id(reservation_id)

    def expire_reservations(self):
        """Expira reservas vencidas automaticamente (CU-011)"""
        expired_reservations = self.reservation_repo.find_expired()

        results = {
            'processed': 0,
            'errors': 0
        }

        for reservation in expired_reservations:
            try:
                # Liberar inventario
                for item in reservation.items:
                    self.inventory_repo.decrease_retained_stock(
                        variant_id=item['variant_id'],
                        quantity=item['quantity'],
                        reason=f'reservation_{str(reservation._id)}_expired'
                    )

                # Actualizar estado
                update_data = {
                    'state': ReservationState.EXPIRED,
                    'expired_at': datetime.utcnow()
                }

                self.reservation_repo.update(reservation._id, update_data)

                results['processed'] += 1

                logger.info(f"Reserva {reservation._id} expirada exitosamente")

            except Exception as e:
                logger.error(f"Error expirando reserva {reservation._id}: {str(e)}")
                results['errors'] += 1

        return results

    def notify_expiring_soon(self):
        """Envia notificaciones de reservas que vencen hoy (CU-012)"""
        expiring_reservations = self.reservation_repo.find_expiring_today()

        results = {
            'processed': 0,
            'errors': 0
        }

        for reservation in expiring_reservations:
            try:
                # Verificar si ya se notifico
                notification_repo = NotificationRepository()
                if notification_repo.check_if_already_notified(
                    reservation._id,
                    'reservation_expiring_soon'
                ):
                    logger.info(f"Reserva {reservation._id} ya fue notificada")
                    continue

                results['processed'] += 1

                logger.info(f"Notificacion de vencimiento programada para reserva {reservation._id}")

            except Exception as e:
                logger.error(f"Error notificando reserva {reservation._id}: {str(e)}")
                results['errors'] += 1

        return results

    def get_reservations_by_user(self, user_id, state=None, skip=0, limit=20):
        """Obtiene reservas de un usuario"""
        return self.reservation_repo.find_by_user_id(user_id, state, skip, limit)

    def get_all_reservations(self, filters=None, skip=0, limit=20):
        """Obtiene todas las reservas (ADMIN)"""
        return self.reservation_repo.find_all(filters, skip, limit)

    def get_reservation_by_id(self, reservation_id):
        """Obtiene una reserva por ID"""
        return self.reservation_repo.find_by_id(reservation_id)

    def _log_audit(self, actor_id, action, entity_id):
        """Registra una accion en auditoria"""
        from app.config.database import get_db
        db = get_db()

        audit_log = {
            'actor_id': ObjectId(actor_id) if actor_id else None,
            'action': action,
            'entity_type': 'reservation',
            'entity_id': ObjectId(entity_id),
            'timestamp': datetime.utcnow()
        }

        db.audit_logs.insert_one(audit_log)
    
    def export_reservations(self, fmt="csv", state=None, date_from=None, date_to=None):

        filters = {
            "state": state,
            "date_from": self._parse_date_start(date_from),
            "date_to": self._parse_date_end(date_to),
        }

        rows = self.reservation_repo.get_export_rows(filters=filters)

        if fmt not in ("csv", "xlsx"):
            fmt = "csv"

        if fmt == "csv":
            content = self._build_csv(rows)
            filename = f"reservas-{datetime.utcnow().date().isoformat()}.csv"
            return content, "text/csv; charset=utf-8", filename

        content = self._build_xlsx(rows)
        filename = f"reservas-{datetime.utcnow().date().isoformat()}.xlsx"
        return content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename

    def _parse_date_start(self, s):
        if not s:
            return None
        # YYYY-MM-DD -> 00:00:00
        d = datetime.fromisoformat(s)
        return datetime(d.year, d.month, d.day)

    def _parse_date_end(self, s):
        if not s:
            return None
        # YYYY-MM-DD -> 23:59:59
        d = datetime.fromisoformat(s)
        return datetime(d.year, d.month, d.day) + timedelta(days=1) - timedelta(seconds=1)

    def _build_csv(self, rows):
        out = BytesIO()
        # csv necesita texto: usamos write en str y luego encode
        from io import StringIO
        sio = StringIO()
        w = csv.writer(sio)

        w.writerow([
            "reservation_id", "state", "created_at",
            "user_name", "user_email",
            "product_name", "variant_name", "quantity"
        ])

        for r in rows:
            w.writerow([
                r.get("reservation_id", ""),
                r.get("state", ""),
                r.get("created_at", ""),
                r.get("user_name", ""),
                r.get("user_email", ""),
                r.get("product_name", ""),
                r.get("variant_name", ""),
                r.get("quantity", ""),
            ])

        out.write(sio.getvalue().encode("utf-8"))
        return out.getvalue()

    def _build_xlsx(self, rows):
        wb = Workbook()

        # Sheet 1: Reservas (resumen)
        ws1 = wb.active
        ws1.title = "Reservas"
        ws1.append(["reservation_id", "state", "created_at", "user_name", "user_email", "items_count", "total_qty"])

        summary = {}
        for r in rows:
            rid = r.get("reservation_id")
            if not rid:
                continue
            if rid not in summary:
                summary[rid] = {
                    "state": r.get("state", ""),
                    "created_at": r.get("created_at", ""),
                    "user_name": r.get("user_name", ""),
                    "user_email": r.get("user_email", ""),
                    "items_count": 0,
                    "total_qty": 0,
                }
            summary[rid]["items_count"] += 1
            try:
                summary[rid]["total_qty"] += int(r.get("quantity") or 0)
            except Exception:
                pass

        for rid, s in summary.items():
            ws1.append([rid, s["state"], s["created_at"], s["user_name"], s["user_email"], s["items_count"], s["total_qty"]])

        # Sheet 2: Items (detalle)
        ws2 = wb.create_sheet("Items")
        ws2.append(["reservation_id", "product_name", "variant_name", "quantity"])
        for r in rows:
            ws2.append([
                r.get("reservation_id", ""),
                r.get("product_name", ""),
                r.get("variant_name", ""),
                r.get("quantity", ""),
            ])

        bio = BytesIO()
        wb.save(bio)
        return bio.getvalue()
