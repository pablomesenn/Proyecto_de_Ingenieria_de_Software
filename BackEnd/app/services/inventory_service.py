from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import VariantRepository
from app.models.inventory import Inventory
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class InventoryService:
    def __init__(self):
        self.inventory_repo = InventoryRepository()
        self.variant_repo = VariantRepository()

    def get_inventory_by_variant(self, variant_id):
        """
        Obtiene el inventario de una variante específica
        Incluye cálculo de disponibilidad
        """
        inventory = self.inventory_repo.find_by_variant_id(variant_id)

        if not inventory:
            # Si no existe inventario, retornar estructura vacía
            return {
                'variant_id': variant_id,
                'stock_total': 0,
                'stock_retenido': 0,
                'disponibilidad': 0,
                'exists': False
            }

        disponibilidad = inventory.get('stock_total', 0) - inventory.get('stock_retenido', 0)

        return {
            '_id': str(inventory['_id']),
            'variant_id': str(inventory['variant_id']),
            'stock_total': inventory['stock_total'],
            'stock_retenido': inventory['stock_retenido'],
            'disponibilidad': max(0, disponibilidad),
            'actualizado_en': inventory.get('actualizado_en'),
            'creado_en': inventory.get('creado_en'),
            'exists': True
        }

    def get_all_inventory(self, skip=0, limit=20):
        """
        Obtiene todo el inventario con información de variantes
        """
        inventories = self.inventory_repo.get_all_with_details(skip=skip, limit=limit)

        result = []
        for inv in inventories:
            disponibilidad = inv.get('stock_total', 0) - inv.get('stock_retenido', 0)

            result.append({
                '_id': str(inv['_id']),
                'variant_id': str(inv['variant_id']),
                'stock_total': inv['stock_total'],
                'stock_retenido': inv['stock_retenido'],
                'disponibilidad': max(0, disponibilidad),
                'product_name': inv.get('product_name'),
                'variant_size': inv.get('variant_size'),
                'variant_price': inv.get('variant_price'),
                'actualizado_en': inv.get('actualizado_en'),
                'creado_en': inv.get('creado_en')
            })

        return result

    def create_inventory(self, variant_id, stock_total, stock_retenido=0, admin_id=None):
        """
        Crea un nuevo registro de inventario para una variante (ADMIN)
        """
        # Validar que la variante existe
        variant = self.variant_repo.find_by_id(variant_id)
        if not variant:
            raise ValueError("Variante no encontrada")

        # Verificar que no exista ya un inventario para esta variante
        existing = self.inventory_repo.find_by_variant_id(variant_id)
        if existing:
            raise ValueError(f"Ya existe inventario para la variante {variant_id}")

        # Validar que stock_retenido no sea mayor que stock_total
        if stock_retenido > stock_total:
            raise ValueError("Stock retenido no puede ser mayor que stock total")

        # Crear inventario
        inventory = Inventory(
            variant_id=variant_id,
            stock_total=stock_total,
            stock_retenido=stock_retenido
        )

        created = self.inventory_repo.create(inventory)

        # Registrar auditoría
        self._log_audit(
            admin_id,
            'create_inventory',
            created['_id'],
            {'variant_id': variant_id, 'stock_total': stock_total}
        )

        return self.get_inventory_by_variant(variant_id)

    def update_stock_total(self, variant_id, new_stock_total, admin_id=None):
        """
        Actualiza el stock total de una variante (ADMIN)
        Valida que el nuevo stock no sea menor al stock retenido
        """
        inventory = self.inventory_repo.find_by_variant_id(variant_id)

        if not inventory:
            raise ValueError("Inventario no encontrado para esta variante")

        stock_retenido = inventory.get('stock_retenido', 0)

        # Validar que el nuevo stock total no sea menor al stock retenido
        if new_stock_total < stock_retenido:
            raise ValueError(
                f"El stock total ({new_stock_total}) no puede ser menor "
                f"al stock retenido ({stock_retenido})"
            )

        # Actualizar stock total
        success = self.inventory_repo.update_stock_total(variant_id, new_stock_total)

        if not success:
            raise ValueError("No se pudo actualizar el inventario")

        # Registrar auditoría
        self._log_audit(
            admin_id,
            'update_stock_total',
            inventory['_id'],
            {'old_stock': inventory['stock_total'], 'new_stock': new_stock_total}
        )

        return self.get_inventory_by_variant(variant_id)

    def adjust_inventory(self, variant_id, delta, reason, admin_id=None):
        """
        Ajusta el inventario (incrementa o decrementa) (ADMIN)
        delta positivo = incremento, delta negativo = decremento
        """
        inventory = self.inventory_repo.find_by_variant_id(variant_id)

        if not inventory:
            raise ValueError("Inventario no encontrado para esta variante")

        current_stock = inventory.get('stock_total', 0)
        stock_retenido = inventory.get('stock_retenido', 0)
        new_stock = current_stock + delta

        # Validar que el nuevo stock no sea negativo
        if new_stock < 0:
            raise ValueError(
                f"El ajuste resultaría en stock negativo "
                f"(actual: {current_stock}, delta: {delta})"
            )

        # Validar que el nuevo stock no sea menor al stock retenido
        if new_stock < stock_retenido:
            raise ValueError(
                f"El nuevo stock ({new_stock}) no puede ser menor "
                f"al stock retenido ({stock_retenido})"
            )

        # Realizar ajuste
        success = self.inventory_repo.adjust_stock(
            variant_id=variant_id,
            delta=delta,
            reason=reason,
            actor_id=admin_id
        )

        if not success:
            raise ValueError("No se pudo ajustar el inventario")

        # Registrar auditoría
        self._log_audit(
            admin_id,
            'adjust_inventory',
            inventory['_id'],
            {'delta': delta, 'reason': reason, 'old_stock': current_stock, 'new_stock': new_stock}
        )

        return self.get_inventory_by_variant(variant_id)

    def retain_stock(self, variant_id, quantity, reason=None, actor_id=None):
        """
        Retiene stock (usado internamente por el sistema de reservas)
        """
        # Validar disponibilidad
        if not self.inventory_repo.validate_availability(variant_id, quantity):
            available = self.inventory_repo.get_available_stock(variant_id)
            raise ValueError(
                f"Stock insuficiente. Disponible: {available}, Solicitado: {quantity}"
            )

        # Retener stock
        success = self.inventory_repo.increase_retained_stock(
            variant_id=variant_id,
            quantity=quantity,
            reason=reason or 'manual_retention',
            actor_id=actor_id
        )

        if not success:
            raise ValueError("No se pudo retener el stock")

        return self.get_inventory_by_variant(variant_id)

    def release_stock(self, variant_id, quantity, reason=None, actor_id=None):
        """
        Libera stock retenido (usado internamente por el sistema de reservas)
        """
        inventory = self.inventory_repo.find_by_variant_id(variant_id)

        if not inventory:
            raise ValueError("Inventario no encontrado")

        stock_retenido = inventory.get('stock_retenido', 0)

        # Validar que hay suficiente stock retenido para liberar
        if quantity > stock_retenido:
            raise ValueError(
                f"No hay suficiente stock retenido para liberar. "
                f"Retenido: {stock_retenido}, Solicitado: {quantity}"
            )

        # Liberar stock
        success = self.inventory_repo.decrease_retained_stock(
            variant_id=variant_id,
            quantity=quantity,
            reason=reason or 'manual_release',
            actor_id=actor_id
        )

        if not success:
            raise ValueError("No se pudo liberar el stock")

        return self.get_inventory_by_variant(variant_id)

    def get_inventory_movements(self, variant_id=None, movement_type=None, skip=0, limit=50):
        """
        Obtiene el historial de movimientos de inventario
        """
        movements = self.inventory_repo.get_movements(
            variant_id=variant_id,
            movement_type=movement_type,
            skip=skip,
            limit=limit
        )

        result = []
        for movement in movements:
            result.append({
                '_id': str(movement['_id']),
                'variant_id': str(movement['variant_id']),
                'quantity': movement['quantity'],
                'movement_type': movement['movement_type'],
                'reason': movement.get('reason'),
                'actor_id': str(movement['actor_id']) if movement.get('actor_id') else None,
                'creado_en': movement['creado_en']
            })

        return result

    def get_low_stock_alerts(self, threshold=10):
        """
        Obtiene variantes con stock disponible bajo (menor al umbral)
        Útil para alertas administrativas
        """
        all_inventory = self.get_all_inventory(skip=0, limit=1000)

        low_stock = [
            inv for inv in all_inventory
            if inv['disponibilidad'] < threshold
        ]

        return sorted(low_stock, key=lambda x: x['disponibilidad'])

    def _log_audit(self, actor_id, action, entity_id, details=None):
        """Registra una acción en auditoría"""
        from app.config.database import get_db
        from datetime import datetime

        db = get_db()

        audit_log = {
            'actor_id': ObjectId(actor_id) if actor_id else None,
            'action': action,
            'entity_type': 'inventory',
            'entity_id': ObjectId(entity_id) if entity_id else None,
            'details': details,
            'timestamp': datetime.utcnow()
        }

        db.audit_logs.insert_one(audit_log)
    
    def get_inventory_movements_detailed(self, skip=0, limit=50, filters=None):
        return self.inventory_repo.get_movements_detailed(skip=skip, limit=limit, filters=filters)
 

