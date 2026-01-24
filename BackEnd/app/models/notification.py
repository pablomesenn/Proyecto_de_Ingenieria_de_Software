from datetime import datetime
from bson import ObjectId


class EmailNotification:
    """
    Modelo de Notificacion por Email segun ERS
    Registra eventos de correo para seguimiento
    """
    
    TYPE_RESERVATION_CREATED = 'reservation_created'
    TYPE_RESERVATION_APPROVED = 'reservation_approved'
    TYPE_RESERVATION_REJECTED = 'reservation_rejected'
    TYPE_RESERVATION_CANCELLED = 'reservation_cancelled'
    TYPE_RESERVATION_EXPIRED = 'reservation_expired'
    TYPE_RESERVATION_EXPIRING_SOON = 'reservation_expiring_soon'
    
    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    
    def __init__(
        self,
        user_id,
        email_to,
        notification_type,
        subject,
        body,
        related_entity_id=None,
        status=STATUS_PENDING,
        sent_at=None,
        error_message=None,
        retry_count=0,
        created_at=None,
        _id=None
    ):
        self._id = _id or ObjectId()
        self.user_id = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
        self.email_to = email_to
        self.notification_type = notification_type
        self.subject = subject
        self.body = body
        self.related_entity_id = ObjectId(related_entity_id) if related_entity_id and not isinstance(related_entity_id, ObjectId) else related_entity_id
        self.status = status
        self.sent_at = sent_at
        self.error_message = error_message
        self.retry_count = retry_count
        self.created_at = created_at or datetime.utcnow()
        
    def to_dict(self):
        """Convierte el modelo a diccionario para MongoDB"""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'email_to': self.email_to,
            'notification_type': self.notification_type,
            'subject': self.subject,
            'body': self.body,
            'related_entity_id': self.related_entity_id,
            'status': self.status,
            'sent_at': self.sent_at,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        """Crea una instancia desde un diccionario"""
        if not data:
            return None
        return EmailNotification(
            user_id=data.get('user_id'),
            email_to=data.get('email_to'),
            notification_type=data.get('notification_type'),
            subject=data.get('subject'),
            body=data.get('body'),
            related_entity_id=data.get('related_entity_id'),
            status=data.get('status'),
            sent_at=data.get('sent_at'),
            error_message=data.get('error_message'),
            retry_count=data.get('retry_count', 0),
            created_at=data.get('created_at'),
            _id=data.get('_id')
        )