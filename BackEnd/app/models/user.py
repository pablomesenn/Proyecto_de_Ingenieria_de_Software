"""
Modelo de Usuario
Define la estructura de datos para usuarios en MongoDB
"""
from mongoengine import (
    Document, StringField, EmailField, 
    DateTimeField, BooleanField
)
from datetime import datetime
from app.constants.roles import UserRole
from app.constants.states import UserState
import bcrypt


class User(Document):
    """
    Modelo de Usuario según Tabla 20 del ERS
    
    Campos:
    - id (automático por MongoDB)
    - email
    - password_hash
    - rol (ADMIN/CLIENT)
    - nombre
    - telefono
    - estado (activo/inactivo)
    - creado_en
    - actualizado_en
    """
    
    # Metadatos de la colección
    meta = {
        'collection': 'users',
        'indexes': [
            'email',  # Índice único en email
            'rol',
            'estado',
            '-creado_en'  # Índice descendente por fecha de creación
        ]
    }
    
    # Campos del documento
    email = EmailField(required=True, unique=True, max_length=255)
    password_hash = StringField(required=True, max_length=255)
    rol = StringField(
        required=True, 
        choices=UserRole.all_roles(),
        default=UserRole.CLIENT
    )
    nombre = StringField(required=True, max_length=255)
    telefono = StringField(max_length=20)
    estado = StringField(
        required=True,
        choices=UserState.all_states(),
        default=UserState.ACTIVE
    )
    
    # Timestamps
    creado_en = DateTimeField(default=datetime.utcnow)
    actualizado_en = DateTimeField(default=datetime.utcnow)
    
    def set_password(self, password):
        """
        Hashea y guarda la contraseña del usuario
        
        Args:
            password: Contraseña en texto plano
        """
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            salt
        ).decode('utf-8')
    
    def check_password(self, password):
        """
        Verifica si una contraseña coincide con el hash almacenado
        
        Args:
            password: Contraseña en texto plano a verificar
        
        Returns:
            bool: True si la contraseña es correcta, False en caso contrario
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    def is_active(self):
        """Verifica si el usuario está activo"""
        return self.estado == UserState.ACTIVE
    
    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.rol == UserRole.ADMIN
    
    def is_client(self):
        """Verifica si el usuario es cliente"""
        return self.rol == UserRole.CLIENT
    
    def save(self, *args, **kwargs):
        """
        Override del método save para actualizar timestamp
        """
        self.actualizado_en = datetime.utcnow()
        return super(User, self).save(*args, **kwargs)
    
    def to_dict(self, include_sensitive=False):
        """
        Convierte el usuario a diccionario
        
        Args:
            include_sensitive: Si incluir datos sensibles (para admin)
        
        Returns:
            dict: Representación del usuario
        """
        data = {
            'id': str(self.id),
            'email': self.email,
            'rol': self.rol,
            'nombre': self.nombre,
            'telefono': self.telefono,
            'estado': self.estado,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
            'actualizado_en': self.actualizado_en.isoformat() if self.actualizado_en else None,
        }
        
        # Solo incluir datos sensibles si se solicita explícitamente
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data
    
    def to_json_safe(self):
        """
        Convierte a diccionario sin datos sensibles (para respuestas API)
        """
        return self.to_dict(include_sensitive=False)
    
    def __repr__(self):
        """Representación en string del usuario"""
        return f'<User {self.email} ({self.rol})>'
    
    def __str__(self):
        """String del usuario"""
        return self.nombre or self.email


# Funciones helper para el modelo User

def create_user(email, password, nombre, rol=UserRole.CLIENT, telefono=None):
    """
    Crea un nuevo usuario
    
    Args:
        email: Email del usuario
        password: Contraseña en texto plano
        nombre: Nombre del usuario
        rol: Rol del usuario (default: CLIENT)
        telefono: Teléfono opcional
    
    Returns:
        User: Usuario creado
    """
    user = User(
        email=email.lower().strip(),
        nombre=nombre.strip(),
        rol=rol,
        telefono=telefono,
        estado=UserState.ACTIVE
    )
    user.set_password(password)
    user.save()
    return user


def find_user_by_email(email):
    """
    Busca un usuario por email
    
    Args:
        email: Email a buscar
    
    Returns:
        User o None: Usuario encontrado o None
    """
    try:
        return User.objects.get(email=email.lower().strip())
    except User.DoesNotExist:
        return None


def find_user_by_id(user_id):
    """
    Busca un usuario por ID
    
    Args:
        user_id: ID del usuario
    
    Returns:
        User o None: Usuario encontrado o None
    """
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


def get_all_users(include_inactive=False, role=None):
    """
    Obtiene todos los usuarios con filtros opcionales
    
    Args:
        include_inactive: Si incluir usuarios inactivos
        role: Filtrar por rol específico
    
    Returns:
        QuerySet: Lista de usuarios
    """
    query = {}
    
    if not include_inactive:
        query['estado'] = UserState.ACTIVE
    
    if role:
        query['rol'] = role
    
    return User.objects(**query).order_by('-creado_en')