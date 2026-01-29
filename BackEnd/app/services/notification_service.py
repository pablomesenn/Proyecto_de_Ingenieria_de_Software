from app.repositories.notification_repository import NotificationRepository
from app.models.in_app_notification import InAppNotification
from app.services.email_service import EmailService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Servicio para gestionar notificaciones"""
    
    def __init__(self):
        self.repository = NotificationRepository()
        self.email_service = EmailService()
    
    def get_user_notifications(self, user_id, unread_only=False, limit=50, skip=0):
        """Obtiene notificaciones de un usuario"""
        result = self.repository.get_user_notifications(user_id, unread_only, limit, skip)
        
        # Convertir notificaciones a formato JSON serializable
        notifications_dict = []
        for notification in result['notifications']:
            notif_dict = {
                'id': str(notification._id),
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'priority': notification.priority,
                'read': notification.read,
                'read_at': notification.read_at.isoformat() if notification.read_at else None,
                'created_at': notification.created_at.isoformat() if notification.created_at else None,
                'action_url': notification.action_url,
                'related_entity_id': str(notification.related_entity_id) if notification.related_entity_id else None,
                'related_entity_type': notification.related_entity_type
            }
            notifications_dict.append(notif_dict)
        
        return {
            'notifications': notifications_dict,
            'unread_count': result['unread_count'],
            'total': result['total']
        }
    
    def mark_as_read(self, notification_id, user_id):
        """Marca una notificacion como leida"""
        return self.repository.mark_as_read(notification_id, user_id)
    
    def mark_all_as_read(self, user_id):
        """Marca todas las notificaciones como leidas"""
        count = self.repository.mark_all_as_read(user_id)
        return {'marked_count': count}
    
    def delete_notification(self, notification_id, user_id):
        """Elimina una notificacion"""
        return self.repository.delete_notification(notification_id, user_id)
    
    def get_unread_count(self, user_id):
        """Obtiene el conteo de notificaciones no leidas"""
        count = self.repository.get_unread_count(user_id)
        return {'unread_count': count}
    
    # Metodos para crear notificaciones basadas en eventos
    
    def notify_new_reservation(self, reservation_id, customer_name, customer_email):
        """Notifica a admins sobre nueva reserva"""
        notification_data = {
            'title': 'Nueva reserva pendiente',
            'message': f'{customer_name} ({customer_email}) ha creado una nueva reserva',
            'notification_type': InAppNotification.TYPE_NEW_RESERVATION,
            'priority': InAppNotification.PRIORITY_NORMAL,
            'related_entity_id': reservation_id,
            'related_entity_type': 'reservation',
            'action_url': f'/admin/reservations/{reservation_id}'
        }
        return self.repository.create_notification_for_admins(notification_data)
    
    def notify_reservation_approved(self, user_id, reservation_id):
        """Notifica al cliente que su reserva fue aprobada"""
        notification = InAppNotification(
            user_id=user_id,
            title='Reserva aprobada',
            message='Tu reserva ha sido aprobada por el administrador',
            notification_type=InAppNotification.TYPE_RESERVATION_APPROVED,
            priority=InAppNotification.PRIORITY_NORMAL,
            related_entity_id=reservation_id,
            related_entity_type='reservation',
            action_url=f'/reservations/{reservation_id}'
        )
        return self.repository.create_notification(notification)
    
    def notify_reservation_rejected(self, user_id, reservation_id, reason=None):
        """Notifica al cliente que su reserva fue rechazada"""
        message = 'Tu reserva ha sido rechazada por el administrador'
        if reason:
            message += f'. Motivo: {reason}'
        
        notification = InAppNotification(
            user_id=user_id,
            title='Reserva rechazada',
            message=message,
            notification_type=InAppNotification.TYPE_RESERVATION_REJECTED,
            priority=InAppNotification.PRIORITY_HIGH,
            related_entity_id=reservation_id,
            related_entity_type='reservation',
            action_url=f'/reservations/{reservation_id}'
        )
        return self.repository.create_notification(notification)
    
    def notify_reservation_expiring(self, user_id, reservation_id, hours_remaining):
        """Notifica al cliente que su reserva esta por expirar"""
        notification = InAppNotification(
            user_id=user_id,
            title='Reserva por expirar',
            message=f'Tu reserva expirara en {hours_remaining} horas. Completa el proceso pronto.',
            notification_type=InAppNotification.TYPE_RESERVATION_EXPIRING,
            priority=InAppNotification.PRIORITY_HIGH,
            related_entity_id=reservation_id,
            related_entity_type='reservation',
            action_url=f'/reservations/{reservation_id}'
        )
        return self.repository.create_notification(notification)
    
    def notify_reservation_expired(self, user_id, reservation_id):
        """Notifica al cliente que su reserva expiro"""
        notification = InAppNotification(
            user_id=user_id,
            title='Reserva expirada',
            message='Tu reserva ha expirado por falta de confirmacion',
            notification_type=InAppNotification.TYPE_RESERVATION_EXPIRED,
            priority=InAppNotification.PRIORITY_NORMAL,
            related_entity_id=reservation_id,
            related_entity_type='reservation',
            action_url='/reservations'
        )
        return self.repository.create_notification(notification)
    
    def notify_low_stock(self, product_name, variant_name, current_stock):
        """Notifica a admins sobre stock bajo"""
        notification_data = {
            'title': 'Stock bajo',
            'message': f'{product_name} - {variant_name} tiene solo {current_stock} unidades disponibles',
            'notification_type': InAppNotification.TYPE_LOW_STOCK,
            'priority': InAppNotification.PRIORITY_HIGH,
            'related_entity_type': 'inventory',
            'action_url': '/admin/inventory'
        }
        return self.repository.create_notification_for_admins(notification_data)
    
    def notify_out_of_stock(self, product_name, variant_name):
        """Notifica a admins sobre producto agotado"""
        notification_data = {
            'title': 'Producto agotado',
            'message': f'{product_name} - {variant_name} se ha agotado',
            'notification_type': InAppNotification.TYPE_OUT_OF_STOCK,
            'priority': InAppNotification.PRIORITY_URGENT,
            'related_entity_type': 'inventory',
            'action_url': '/admin/inventory'
        }
        return self.repository.create_notification_for_admins(notification_data)
    
    # Metodos send_ para compatibilidad con llamadas desde routes
    
    def send_reservation_created(self, user, reservation):
        """Envia notificacion y correo cuando se crea una reserva"""
        try:
            # Crear notificacion in-app para admins
            self.notify_new_reservation(
                reservation_id=str(reservation._id),
                customer_name=user.nombre,
                customer_email=user.email
            )
            
            # Enviar correo al cliente
            self._send_reservation_email(
                user_email=user.email,
                user_name=user.nombre,
                reservation=reservation,
                email_type='created'
            )
            
            logger.info(f"Notificacion de reserva creada enviada para reserva {reservation._id}")
        except Exception as e:
            logger.error(f"Error enviando notificacion de reserva creada: {str(e)}")
    
    def send_reservation_approved(self, user, reservation):
        """Envia notificacion y correo cuando se aprueba una reserva"""
        try:
            # Crear notificacion in-app
            self.notify_reservation_approved(
                user_id=str(user._id),
                reservation_id=str(reservation._id)
            )
            
            # Enviar correo
            self._send_reservation_email(
                user_email=user.email,
                user_name=user.nombre,
                reservation=reservation,
                email_type='approved'
            )
            
            logger.info(f"Notificacion de reserva aprobada enviada para reserva {reservation._id}")
        except Exception as e:
            logger.error(f"Error enviando notificacion de reserva aprobada: {str(e)}")
    
    def send_reservation_rejected(self, user, reservation):
        """Envia notificacion y correo cuando se rechaza una reserva"""
        try:
            # Crear notificacion in-app
            reason = reservation.admin_notes if hasattr(reservation, 'admin_notes') else None
            self.notify_reservation_rejected(
                user_id=str(user._id),
                reservation_id=str(reservation._id),
                reason=reason
            )
            
            # Enviar correo
            self._send_reservation_email(
                user_email=user.email,
                user_name=user.nombre,
                reservation=reservation,
                email_type='rejected'
            )
            
            logger.info(f"Notificacion de reserva rechazada enviada para reserva {reservation._id}")
        except Exception as e:
            logger.error(f"Error enviando notificacion de reserva rechazada: {str(e)}")
    
    def send_reservation_cancelled(self, user, reservation):
        """Envia notificacion y correo cuando se cancela una reserva"""
        try:
            # Enviar correo
            self._send_reservation_email(
                user_email=user.email,
                user_name=user.nombre,
                reservation=reservation,
                email_type='cancelled'
            )
            
            logger.info(f"Notificacion de reserva cancelada enviada para reserva {reservation._id}")
        except Exception as e:
            logger.error(f"Error enviando notificacion de reserva cancelada: {str(e)}")
    
    def send_reservation_expired(self, user, reservation):
        """Envia notificacion y correo cuando expira una reserva"""
        try:
            # Crear notificacion in-app
            self.notify_reservation_expired(
                user_id=str(user._id),
                reservation_id=str(reservation._id)
            )
            
            # Enviar correo
            self._send_reservation_email(
                user_email=user.email,
                user_name=user.nombre,
                reservation=reservation,
                email_type='expired'
            )
            
            logger.info(f"Notificacion de reserva expirada enviada para reserva {reservation._id}")
        except Exception as e:
            logger.error(f"Error enviando notificacion de reserva expirada: {str(e)}")
    
    def send_reservation_expiring_soon(self, user, reservation):
        """Envia notificacion y correo cuando una reserva esta por vencer (CU-012)"""
        try:
            # Calcular horas restantes
            if hasattr(reservation, 'expires_at') and reservation.expires_at:
                hours_remaining = int((reservation.expires_at - datetime.utcnow()).total_seconds() / 3600)
                if hours_remaining < 0:
                    hours_remaining = 0
            else:
                hours_remaining = 0
            
            # Crear notificacion in-app
            self.notify_reservation_expiring(
                user_id=str(user._id),
                reservation_id=str(reservation._id),
                hours_remaining=hours_remaining
            )
            
            # Enviar correo
            self._send_reservation_email(
                user_email=user.email,
                user_name=user.nombre,
                reservation=reservation,
                email_type='expiring_soon'
            )
            
            logger.info(f"Notificacion de reserva por vencer enviada para reserva {reservation._id}")
        except Exception as e:
            logger.error(f"Error enviando notificacion de reserva por vencer: {str(e)}")
    
    def _send_reservation_email(self, user_email, user_name, reservation, email_type):
        """Metodo auxiliar para enviar correos de reservas"""
        try:
            import yagmail
            import os
            
            sender_email = os.getenv('SMTP_USERNAME', 'kermypisos@gmail.com')
            sender_password = os.getenv('SMTP_PASSWORD', '')
            
            if not sender_email or not sender_password:
                logger.warning("Credenciales SMTP no configuradas, no se puede enviar correo")
                return
            
            yag = yagmail.SMTP(sender_email, sender_password)
            
            # Construir contenido segun tipo
            if email_type == 'created':
                subject = 'Reserva Creada - Pisos Kermy'
                message = self._build_created_email(user_name, reservation)
            elif email_type == 'approved':
                subject = 'Reserva Aprobada - Pisos Kermy'
                message = self._build_approved_email(user_name, reservation)
            elif email_type == 'rejected':
                subject = 'Reserva Rechazada - Pisos Kermy'
                message = self._build_rejected_email(user_name, reservation)
            elif email_type == 'cancelled':
                subject = 'Reserva Cancelada - Pisos Kermy'
                message = self._build_cancelled_email(user_name, reservation)
            elif email_type == 'expired':
                subject = 'Reserva Expirada - Pisos Kermy'
                message = self._build_expired_email(user_name, reservation)
            elif email_type == 'expiring_soon':
                subject = 'Tu Reserva Vence Hoy - Pisos Kermy'
                message = self._build_expiring_soon_email(user_name, reservation)
            else:
                return
            
            yag.send(to=user_email, subject=subject, contents=message)
            logger.info(f"Correo de tipo {email_type} enviado a {user_email}")
            
        except Exception as e:
            logger.error(f"Error enviando correo de reserva: {str(e)}")
    
    def _build_created_email(self, user_name, reservation):
        """Construye el HTML del correo de reserva creada"""
        items_html = ""
        for item in reservation.items:
            items_html += f"<li>{item.get('product_name', 'Producto')} - {item.get('variant_size', '')} x{item.get('quantity', 1)}</li>"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0;">Pisos Kermy</h1>
                    <p style="margin: 10px 0 0 0;">Jaco S.A.</p>
                </div>
                <div style="background-color: white; padding: 30px;">
                    <h2>Hola {user_name}!</h2>
                    <p>Tu reserva ha sido creada exitosamente.</p>
                    <div style="background-color: #f0f0f0; padding: 15px; margin: 20px 0;">
                        <h3>Detalles de tu reserva:</h3>
                        <ul>{items_html}</ul>
                    </div>
                    <p><strong>Estado:</strong> Pendiente de aprobacion</p>
                    <p>Tu reserva esta pendiente de aprobacion por nuestro equipo. Te notificaremos cuando sea procesada.</p>
                    <p style="color: #e74c3c;"><strong>Importante:</strong> Esta reserva expira en 24 horas si no es aprobada.</p>
                </div>
                <div style="text-align: center; padding: 20px; font-size: 12px; color: #666;">
                    <p>2024-2026 Pisos Kermy Jaco S.A.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _build_approved_email(self, user_name, reservation):
        """Construye el HTML del correo de reserva aprobada"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>Hola {user_name}!</h2>
                <p>Tu reserva ha sido <strong style="color: #28a745;">APROBADA</strong>.</p>
                <p>Por favor contactanos para coordinar la entrega de tus productos.</p>
                <p>Email: kermypisos@gmail.com</p>
            </div>
        </body>
        </html>
        """
    
    def _build_rejected_email(self, user_name, reservation):
        """Construye el HTML del correo de reserva rechazada"""
        reason = reservation.admin_notes if hasattr(reservation, 'admin_notes') and reservation.admin_notes else "No se especifico un motivo"
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>Hola {user_name}</h2>
                <p>Lamentablemente tu reserva ha sido <strong style="color: #dc3545;">RECHAZADA</strong>.</p>
                <p><strong>Motivo:</strong> {reason}</p>
                <p>Si tienes dudas, contactanos.</p>
            </div>
        </body>
        </html>
        """
    
    def _build_cancelled_email(self, user_name, reservation):
        """Construye el HTML del correo de reserva cancelada"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>Hola {user_name}</h2>
                <p>Tu reserva ha sido <strong>CANCELADA</strong>.</p>
                <p>El stock ha sido liberado y esta disponible nuevamente.</p>
            </div>
        </body>
        </html>
        """
    
    def _build_expired_email(self, user_name, reservation):
        """Construye el HTML del correo de reserva expirada"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>Hola {user_name}</h2>
                <p>Tu reserva ha <strong style="color: #dc3545;">EXPIRADO</strong> por falta de confirmacion.</p>
                <p>El stock retenido ha sido liberado.</p>
                <p>Si aun estas interesado, puedes crear una nueva reserva.</p>
            </div>
        </body>
        </html>
        """
    
    def _build_expiring_soon_email(self, user_name, reservation):
        """Construye el HTML del correo de reserva por vencer (CU-012)"""
        items_html = ""
        for item in reservation.items:
            items_html += f"<li>{item.get('product_name', 'Producto')} - {item.get('variant_size', '')} x{item.get('quantity', 1)}</li>"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
                <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0;">Tu Reserva Vence Hoy</h1>
                    <p style="margin: 10px 0 0 0;">Pisos Kermy - Jaco S.A.</p>
                </div>
                <div style="background-color: white; padding: 30px;">
                    <h2>Hola {user_name}!</h2>
                    <p style="font-size: 16px;"><strong>Tu reserva expira hoy.</strong></p>
                    <p>Por favor, contactanos lo antes posible para coordinar la entrega de tus productos.</p>
                    <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
                        <h3>Productos reservados:</h3>
                        <ul>{items_html}</ul>
                    </div>
                    <p style="color: #e74c3c; font-weight: bold;">Si no coordinamos la entrega hoy, la reserva expirara automaticamente.</p>
                    <p>Contactanos:</p>
                    <p>Email: kermypisos@gmail.com</p>
                </div>
                <div style="text-align: center; padding: 20px; font-size: 12px; color: #666;">
                    <p>2024-2026 Pisos Kermy Jaco S.A.</p>
                </div>
            </div>
        </body>
        </html>
        """