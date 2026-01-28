"""
Notification Repository with proper lazy database loading
This prevents creating new connections on every instantiation
"""
from app.config.database import get_db
from app.models.in_app_notification import InAppNotification
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NotificationRepository:
    """Repositorio para gestionar notificaciones in-app"""
    
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
        """Lazy load collection"""
        return self.db.in_app_notifications
        
    def create_notification(self, notification: InAppNotification):
        """Crea una nueva notificación"""
        try:
            result = self.collection.insert_one(notification.to_dict())
            notification._id = result.inserted_id
            logger.info(f"Notificación creada: {notification._id}")
            return notification
        except Exception as e:
            logger.error(f"Error creando notificación: {str(e)}")
            raise
    
    def get_by_id(self, notification_id):
        """Obtiene una notificación por ID"""
        try:
            data = self.collection.find_one({'_id': ObjectId(notification_id)})
            return InAppNotification.from_dict(data) if data else None
        except Exception as e:
            logger.error(f"Error obteniendo notificación {notification_id}: {str(e)}")
            return None
    
    def get_user_notifications(self, user_id, unread_only=False, limit=50, skip=0):
        """
        Obtiene notificaciones de un usuario
        Args:
            user_id: ID del usuario
            unread_only: Si True, solo notificaciones no leídas
            limit: Límite de resultados
            skip: Número de resultados a saltar
        """
        try:
            query = {'user_id': ObjectId(user_id)}
            if unread_only:
                query['read'] = False
            
            cursor = self.collection.find(query).sort('created_at', -1).skip(skip).limit(limit)
            notifications = [InAppNotification.from_dict(data) for data in cursor]
            
            # Obtener total de no leídas
            unread_count = self.collection.count_documents({
                'user_id': ObjectId(user_id),
                'read': False
            })
            
            return {
                'notifications': notifications,
                'unread_count': unread_count,
                'total': self.collection.count_documents(query)
            }
        except Exception as e:
            logger.error(f"Error obteniendo notificaciones del usuario {user_id}: {str(e)}")
            return {'notifications': [], 'unread_count': 0, 'total': 0}
    
    def mark_as_read(self, notification_id, user_id):
        """Marca una notificación como leída"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(notification_id), 'user_id': ObjectId(user_id)},
                {
                    '$set': {
                        'read': True,
                        'read_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error marcando notificación {notification_id} como leída: {str(e)}")
            return False
    
    def mark_all_as_read(self, user_id):
        """Marca todas las notificaciones de un usuario como leídas"""
        try:
            result = self.collection.update_many(
                {'user_id': ObjectId(user_id), 'read': False},
                {
                    '$set': {
                        'read': True,
                        'read_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count
        except Exception as e:
            logger.error(f"Error marcando todas las notificaciones como leídas para usuario {user_id}: {str(e)}")
            return 0
    
    def delete_notification(self, notification_id, user_id):
        """Elimina una notificación"""
        try:
            result = self.collection.delete_one({
                '_id': ObjectId(notification_id),
                'user_id': ObjectId(user_id)
            })
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error eliminando notificación {notification_id}: {str(e)}")
            return False
    
    def get_unread_count(self, user_id):
        """Obtiene el conteo de notificaciones no leídas"""
        try:
            return self.collection.count_documents({
                'user_id': ObjectId(user_id),
                'read': False
            })
        except Exception as e:
            logger.error(f"Error obteniendo conteo de no leídas para usuario {user_id}: {str(e)}")
            return 0
    
    def create_notification_for_admins(self, notification_data):
        """Crea notificaciones para todos los administradores"""
        try:
            from app.constants.roles import UserRole
            
            # Obtener todos los admins directamente
            users_collection = self.db.users
            admins = list(users_collection.find({'role': UserRole.ADMIN}))
            
            created_count = 0
            for admin in admins:
                notification = InAppNotification(
                    user_id=admin['_id'],
                    title=notification_data['title'],
                    message=notification_data['message'],
                    notification_type=notification_data['notification_type'],
                    priority=notification_data.get('priority', InAppNotification.PRIORITY_NORMAL),
                    related_entity_id=notification_data.get('related_entity_id'),
                    related_entity_type=notification_data.get('related_entity_type'),
                    action_url=notification_data.get('action_url')
                )
                self.create_notification(notification)
                created_count += 1
            
            logger.info(f"Notificación enviada a {created_count} administradores")
            return created_count
        except Exception as e:
            logger.error(f"Error creando notificaciones para admins: {str(e)}")
            return 0