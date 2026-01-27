"""
Notification Repository with proper lazy database loading
This prevents creating new connections on every instantiation
"""
from datetime import datetime
from bson import ObjectId
from app.config.database import get_db
from app.models.notification import EmailNotification
import logging

logger = logging.getLogger(__name__)


class NotificationRepository:
    """Repositorio para operaciones de notificaciones"""

    def __init__(self):
        self._db = None

    # ============================================================================
    # LAZY LOADING PROPERTIES - Database is only accessed when needed
    # ============================================================================
    @property
    def db(self):
        """Lazy load database connection - reuses existing connection pool"""
        if self._db is None:
            self._db = get_db()  # This now returns the SHARED database instance
        return self._db

    @property
    def collection(self):
        """Get email notifications collection (lazy loaded)"""
        return self.db.email_notifications

    # ============================================================================
    # REPOSITORY METHODS - Now use properties instead of direct access
    # ============================================================================
    def create(self, notification):
        """Crea una nueva notificacion"""
        result = self.collection.insert_one(notification.to_dict())
        notification._id = result.inserted_id
        return notification

    def find_by_id(self, notification_id):
        """Busca una notificacion por ID"""
        data = self.collection.find_one({'_id': ObjectId(notification_id)})
        return EmailNotification.from_dict(data) if data else None

    def find_pending(self, limit=100):
        """Busca notificaciones pendientes de envio"""
        query = {'status': EmailNotification.STATUS_PENDING}
        cursor = self.collection.find(query).limit(limit)
        return [EmailNotification.from_dict(data) for data in cursor]

    def find_by_related_entity(self, entity_id, notification_type=None):
        """Busca notificaciones por entidad relacionada"""
        query = {'related_entity_id': ObjectId(entity_id)}
        if notification_type:
            query['notification_type'] = notification_type

        cursor = self.collection.find(query).sort('created_at', -1)
        return [EmailNotification.from_dict(data) for data in cursor]

    def update_status(self, notification_id, status, error_message=None):
        """Actualiza el estado de una notificacion"""
        update_data = {
            'status': status,
            'sent_at': datetime.utcnow() if status == EmailNotification.STATUS_SENT else None
        }

        if error_message:
            update_data['error_message'] = error_message

        result = self.collection.update_one(
            {'_id': ObjectId(notification_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0

    def increment_retry_count(self, notification_id):
        """Incrementa el contador de reintentos"""
        result = self.collection.update_one(
            {'_id': ObjectId(notification_id)},
            {'$inc': {'retry_count': 1}}
        )
        return result.modified_count > 0

    def mark_as_sent(self, notification_id):
        """Marca una notificacion como enviada"""
        return self.update_status(notification_id, EmailNotification.STATUS_SENT)

    def mark_as_failed(self, notification_id, error_message):
        """Marca una notificacion como fallida"""
        return self.update_status(notification_id, EmailNotification.STATUS_FAILED, error_message)

    def check_if_already_notified(self, entity_id, notification_type):
        """Verifica si ya se envio una notificacion para evitar duplicados"""
        count = self.collection.count_documents({
            'related_entity_id': ObjectId(entity_id),
            'notification_type': notification_type,
            'status': EmailNotification.STATUS_SENT
        })
        return count > 0
