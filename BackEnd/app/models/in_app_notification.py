from datetime import datetime
from bson import ObjectId


class InAppNotification:
    """
    Modelo de Notificacion In-App para el sistema
    Notificaciones que el usuario ve en la interfaz
    """
    
    # Tipos de notificaciones
    TYPE_NEW_RESERVATION = 'new_reservation'
    TYPE_RESERVATION_APPROVED = 'reservation_approved'
    TYPE_RESERVATION_REJECTED = 'reservation_rejected'
    TYPE_RESERVATION_CANCELLED = 'reservation_cancelled'
    TYPE_RESERVATION_EXPIRED = 'reservation_expired'
    TYPE_RESERVATION_EXPIRING = 'reservation_expiring'
    TYPE_LOW_STOCK = 'low_stock'
    TYPE_OUT_OF_STOCK = 'out_of_stock'
    TYPE_INVENTORY_ADJUSTED = 'inventory_adjusted'
    
    # Prioridades
    PRIORITY_LOW = 'low'
    PRIORITY_NORMAL = 'normal'
    PRIORITY_HIGH = 'high'
    PRIORITY_URGENT = 'urgent'
    
    def __init__(
        self,
        user_id,
        title,
        message,
        notification_type,
        priority=PRIORITY_NORMAL,
        related_entity_id=None,
        related_entity_type=None,  # 'reservation', 'product', 'inventory'
        action_url=None,
        read=False,
        read_at=None,
        created_at=None,
        _id=None
    ):
        self._id = _id or ObjectId()
        self.user_id = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
        self.title = title
        self.message = message
        self.notification_type = notification_type
        self.priority = priority
        self.related_entity_id = ObjectId(related_entity_id) if related_entity_id and not isinstance(related_entity_id, ObjectId) else related_entity_id
        self.related_entity_type = related_entity_type
        self.action_url = action_url
        self.read = read
        self.read_at = read_at
        self.created_at = created_at or datetime.utcnow()
        
    def to_dict(self):
        """Convierte el modelo a diccionario para MongoDB"""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'priority': self.priority,
            'related_entity_id': self.related_entity_id,
            'related_entity_type': self.related_entity_type,
            'action_url': self.action_url,
            'read': self.read,
            'read_at': self.read_at,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        """Crea una instancia desde un diccionario"""
        if not data:
            return None
        return InAppNotification(
            user_id=data.get('user_id'),
            title=data.get('title'),
            message=data.get('message'),
            notification_type=data.get('notification_type'),
            priority=data.get('priority', InAppNotification.PRIORITY_NORMAL),
            related_entity_id=data.get('related_entity_id'),
            related_entity_type=data.get('related_entity_type'),
            action_url=data.get('action_url'),
            read=data.get('read', False),
            read_at=data.get('read_at'),
            created_at=data.get('created_at'),
            _id=data.get('_id')
        )