from app.repositories.notification_repository import NotificationRepository
from app.models.in_app_notification import InAppNotification
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Servicio para gestionar notificaciones"""
    
    def __init__(self):
        self.repository = NotificationRepository()
    
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
        """Marca una notificación como leída"""
        return self.repository.mark_as_read(notification_id, user_id)
    
    def mark_all_as_read(self, user_id):
        """Marca todas las notificaciones como leídas"""
        count = self.repository.mark_all_as_read(user_id)
        return {'marked_count': count}
    
    def delete_notification(self, notification_id, user_id):
        """Elimina una notificación"""
        return self.repository.delete_notification(notification_id, user_id)
    
    def get_unread_count(self, user_id):
        """Obtiene el conteo de notificaciones no leídas"""
        count = self.repository.get_unread_count(user_id)
        return {'unread_count': count}
    
    # Métodos para crear notificaciones basadas en eventos
    
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
        """Notifica al cliente que su reserva está por expirar"""
        notification = InAppNotification(
            user_id=user_id,
            title='Reserva por expirar',
            message=f'Tu reserva expirará en {hours_remaining} horas. Completa el proceso pronto.',
            notification_type=InAppNotification.TYPE_RESERVATION_EXPIRING,
            priority=InAppNotification.PRIORITY_HIGH,
            related_entity_id=reservation_id,
            related_entity_type='reservation',
            action_url=f'/reservations/{reservation_id}'
        )
        return self.repository.create_notification(notification)
    
    def notify_reservation_expired(self, user_id, reservation_id):
        """Notifica al cliente que su reserva expiró"""
        notification = InAppNotification(
            user_id=user_id,
            title='Reserva expirada',
            message='Tu reserva ha expirado por falta de confirmación',
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