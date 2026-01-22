"""
Constantes de roles del sistema
"""

class UserRole:
    """Roles de usuario disponibles en el sistema"""
    ADMIN = 'ADMIN'
    CLIENT = 'CLIENT'
    
    @classmethod
    def all_roles(cls):
        """Retorna todos los roles disponibles"""
        return [cls.ADMIN, cls.CLIENT]
    
    @classmethod
    def is_valid_role(cls, role):
        """Verifica si un rol es válido"""
        return role in cls.all_roles()


# Permisos por rol (para RBAC)
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        # Productos
        'products:create',
        'products:read',
        'products:update',
        'products:delete',
        'products:export',
        
        # Inventario
        'inventory:read',
        'inventory:update',
        'inventory:audit',
        
        # Usuarios
        'users:create',
        'users:read',
        'users:update',
        'users:delete',
        
        # Reservas
        'reservations:read_all',
        'reservations:approve',
        'reservations:reject',
        'reservations:cancel',
        
        # Categorías
        'categories:create',
        'categories:read',
        'categories:update',
        'categories:delete',
        
        # Auditoría
        'audit:read',
        
        # Reportes
        'reports:generate',
    ],
    
    UserRole.CLIENT: [
        # Productos (solo lectura)
        'products:read',
        
        # Perfil propio
        'profile:read',
        'profile:update',
        
        # Wishlist
        'wishlist:create',
        'wishlist:read',
        'wishlist:update',
        'wishlist:delete',
        
        # Reservas (solo propias)
        'reservations:create',
        'reservations:read_own',
        'reservations:cancel_own',
    ]
}


def has_permission(role, permission):
    """
    Verifica si un rol tiene un permiso específico
    
    Args:
        role: El rol a verificar
        permission: El permiso a verificar (ej: 'products:create')
    
    Returns:
        bool: True si el rol tiene el permiso, False en caso contrario
    """
    return permission in ROLE_PERMISSIONS.get(role, [])


def get_permissions(role):
    """
    Obtiene todos los permisos de un rol
    
    Args:
        role: El rol del cual obtener permisos
    
    Returns:
        list: Lista de permisos del rol
    """
    return ROLE_PERMISSIONS.get(role, [])