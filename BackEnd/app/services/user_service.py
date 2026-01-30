from datetime import datetime
from bson import ObjectId
from app.repositories.reservation_repository import ReservationRepository
from app.config.database import get_db
import logging
import re

logger = logging.getLogger(__name__)


class UserService:
    """Servicio para gestion de usuarios"""
    
    def __init__(self):
        self.db = get_db()
        self.users_collection = self.db.users
        
    def get_user_by_id(self, user_id):
        """Obtiene un usuario por ID"""
        user = self.users_collection.find_one({'_id': ObjectId(user_id)})
        if user:
            user['_id'] = str(user['_id'])
            user.pop('password', None)  # No exponer contraseña
        return user
    
    def get_user_by_email(self, email):
        """Obtiene un usuario por email"""
        user = self.users_collection.find_one({'email': email})
        if user:
            user['_id'] = str(user['_id'])
        return user
    
    def update_profile(self, user_id, update_data):
        """Actualiza el perfil de un usuario (CU-015)"""
        
        # Validar que el usuario existe
        user = self.users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Campos permitidos para actualizar
        allowed_fields = ['name', 'phone', 'address', 'preferences']
        
        # Filtrar solo campos permitidos
        filtered_data = {
            key: value for key, value in update_data.items() 
            if key in allowed_fields
        }
        
        # Validaciones
        if 'phone' in filtered_data:
            if not self._validate_phone(filtered_data['phone']):
                raise ValueError("Formato de telefono invalido")
        
        if 'email' in update_data:
            # Si intenta cambiar email, validar formato
            if not self._validate_email(update_data['email']):
                raise ValueError("Formato de email invalido")
            
            # Verificar que no exista otro usuario con ese email
            existing_user = self.users_collection.find_one({
                'email': update_data['email'],
                '_id': {'$ne': ObjectId(user_id)}
            })
            
            if existing_user:
                raise ValueError("Email ya esta en uso")
            
            filtered_data['email'] = update_data['email']
        
        # Agregar timestamp de actualizacion
        filtered_data['updated_at'] = datetime.utcnow()
        
        # Actualizar usuario
        result = self.users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': filtered_data}
        )
        
        if result.modified_count == 0:
            logger.warning(f"No se modifico el perfil del usuario {user_id}")
        
        # Registrar auditoria
        self._log_audit(user_id, 'update_profile', user_id)
        
        # Retornar usuario actualizado
        return self.get_user_by_id(user_id)
    
    def change_password(self, user_id, current_password, new_password):
        """Cambia la contraseña de un usuario"""
        from werkzeug.security import check_password_hash, generate_password_hash
        
        # Validar que el usuario existe
        user = self.users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Verificar contraseña actual
        if not check_password_hash(user['password'], current_password):
            raise ValueError("Contraseña actual incorrecta")
        
        # Validar nueva contraseña
        if not self._validate_password(new_password):
            raise ValueError("La nueva contraseña debe tener al menos 10 caracteres y 1 caracter especial")
        
        # Verificar que la nueva contraseña sea diferente
        if check_password_hash(user['password'], new_password):
            raise ValueError("La nueva contraseña debe ser diferente a la actual")
        
        # Actualizar contraseña
        hashed_password = generate_password_hash(new_password)
        result = self.users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'password': hashed_password,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise ValueError("No se pudo actualizar la contraseña")
        
        # Registrar auditoría
        self._log_audit(user_id, 'change_password', user_id)
        
        logger.info(f"Contraseña cambiada exitosamente para usuario {user_id}")
        return True
    
    def create_user(self, user_data):
        """Crea un nuevo usuario (ADMIN)"""
        from werkzeug.security import generate_password_hash
        
        # Validar email
        if not self._validate_email(user_data.get('email')):
            raise ValueError("Formato de email invalido")
        
        # Verificar que el email no exista
        if self.users_collection.find_one({'email': user_data['email']}):
            raise ValueError("Email ya esta en uso")
        
        # Validar contraseña
        if not self._validate_password(user_data.get('password')):
            raise ValueError("Contraseña debe tener al menos 10 caracteres y 1 caracter especial")
        
        # Crear usuario
        user = {
            'email': user_data['email'],
            'password': generate_password_hash(user_data['password']),
            'name': user_data.get('name'),
            'phone': user_data.get('phone'),
            'role': user_data.get('role', 'CLIENT'),
            'state': 'activo',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.users_collection.insert_one(user)
        user['_id'] = str(result.inserted_id)
        user.pop('password', None)
        
        return user
    
    def update_user(self, user_id, update_data, admin_id):
        """Actualiza un usuario (ADMIN)"""
        from werkzeug.security import generate_password_hash
        
        # Validar que el usuario existe
        user = self.users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Preparar datos de actualizacion
        filtered_data = {}
        
        if 'email' in update_data:
            if not self._validate_email(update_data['email']):
                raise ValueError("Formato de email invalido")
            
            # Verificar que no exista otro usuario con ese email
            existing_user = self.users_collection.find_one({
                'email': update_data['email'],
                '_id': {'$ne': ObjectId(user_id)}
            })
            
            if existing_user:
                raise ValueError("Email ya esta en uso")
            
            filtered_data['email'] = update_data['email']
        
        if 'password' in update_data:
            if not self._validate_password(update_data['password']):
                raise ValueError("Contraseña debe tener al menos 10 caracteres y 1 caracter especial")
            filtered_data['password'] = generate_password_hash(update_data['password'])
        
        if 'name' in update_data:
            filtered_data['name'] = update_data['name']
        
        if 'phone' in update_data:
            if not self._validate_phone(update_data['phone']):
                raise ValueError("Formato de telefono invalido")
            filtered_data['phone'] = update_data['phone']
        
        if 'role' in update_data:
            if update_data['role'] not in ['ADMIN', 'CLIENT']:
                raise ValueError("Rol invalido")
            filtered_data['role'] = update_data['role']
        
        if 'state' in update_data:
            if update_data['state'] not in ['activo', 'inactivo']:
                raise ValueError("Estado invalido")
            filtered_data['state'] = update_data['state']
        
        filtered_data['updated_at'] = datetime.utcnow()
        
        # Actualizar usuario
        self.users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': filtered_data}
        )
        
        # Registrar auditoria
        self._log_audit(admin_id, 'update_user', user_id)
        
        return self.get_user_by_id(user_id)
    
    def delete_user(self, user_id, admin_id):
        """Desactiva un usuario (ADMIN)"""
        # No eliminamos, solo desactivamos
        result = self.users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'state': 'inactivo', 'updated_at': datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise ValueError("Usuario no encontrado")
        
        # Registrar auditoria
        self._log_audit(admin_id, 'delete_user', user_id)
        
        return True

    def get_all_users(self, skip=0, limit=100):
        """Obtiene todos los usuarios (ADMIN) + reservationsCount"""

        cursor = self.users_collection.find({}).skip(skip).limit(limit) 
        users = [] 
        reservation_repo = ReservationRepository()

        for user in cursor: 
            user['_id'] = str(user['_id']) 
            user.pop('password', None)

            # Añadir reservationsCount
            user['reservationsCount'] = reservation_repo.count_by_user_id(user['_id'])

            users.append(user) 
        
        return users
    
    def _validate_email(self, email):
        """Valida formato de email"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_password(self, password):
        """Valida contraseña segun politica del ERS"""
        if not password or len(password) < 10:
            return False
        
        # Al menos un caracter especial
        special_chars = r'[!@#$%^&*(),.?":{}|<>]'
        return re.search(special_chars, password) is not None
    
    def _validate_phone(self, phone):
        """Valida formato de telefono"""
        if not phone:
            return True  # Telefono es opcional
        
        # Permitir numeros, espacios, guiones y parentesis
        pattern = r'^[\d\s\-\(\)]+$'
        return re.match(pattern, phone) is not None and len(phone) >= 8
    
    def _log_audit(self, actor_id, action, entity_id):
        """Registra una accion en auditoria"""
        audit_log = {
            'actor_id': ObjectId(actor_id) if actor_id else None,
            'action': action,
            'entity_type': 'user',
            'entity_id': ObjectId(entity_id),
            'timestamp': datetime.utcnow()
        }
        
        self.db.audit_logs.insert_one(audit_log)