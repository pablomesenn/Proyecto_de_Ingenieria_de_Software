"""
Constantes de estados del sistema
Según definiciones del ERS
"""

class ProductState:
    """Estados posibles de un producto"""
    ACTIVE = 'activo'
    INACTIVE = 'inactivo'
    OUT_OF_STOCK = 'agotado'
    
    @classmethod
    def all_states(cls):
        """Retorna todos los estados disponibles"""
        return [cls.ACTIVE, cls.INACTIVE, cls.OUT_OF_STOCK]
    
    @classmethod
    def is_valid_state(cls, state):
        """Verifica si un estado es válido"""
        return state in cls.all_states()
    
    @classmethod
    def visible_states(cls):
        """Estados que hacen visible el producto al cliente"""
        return [cls.ACTIVE]


class ReservationState:
    """Estados posibles de una reserva (según ERS)"""
    PENDING = 'Pendiente'
    APPROVED = 'Aprobada'
    REJECTED = 'Rechazada'
    CANCELLED = 'Cancelada'
    EXPIRED = 'Expirada'
    
    @classmethod
    def all_states(cls):
        """Retorna todos los estados disponibles"""
        return [cls.PENDING, cls.APPROVED, cls.REJECTED, cls.CANCELLED, cls.EXPIRED]
    
    @classmethod
    def is_valid_state(cls, state):
        """Verifica si un estado es válido"""
        return state in cls.all_states()
    
    @classmethod
    def active_states(cls):
        """Estados que retienen inventario"""
        return [cls.PENDING, cls.APPROVED]
    
    @classmethod
    def final_states(cls):
        """Estados finales (no pueden cambiar)"""
        return [cls.REJECTED, cls.CANCELLED, cls.EXPIRED]
    
    @classmethod
    def can_transition(cls, from_state, to_state):
        """
        Verifica si una transición de estado es válida
        
        Transiciones permitidas según ERS:
        - Pendiente -> Aprobada
        - Pendiente -> Rechazada
        - Aprobada -> Cancelada (forzada por admin)
        - Pendiente/Aprobada -> Expirada (automático)
        - Pendiente/Aprobada -> Cancelada (por cliente)
        """
        valid_transitions = {
            cls.PENDING: [cls.APPROVED, cls.REJECTED, cls.CANCELLED, cls.EXPIRED],
            cls.APPROVED: [cls.CANCELLED, cls.EXPIRED],
            cls.REJECTED: [],
            cls.CANCELLED: [],
            cls.EXPIRED: [],
        }
        
        return to_state in valid_transitions.get(from_state, [])


class UserState:
    """Estados de usuario"""
    ACTIVE = 'activo'
    INACTIVE = 'inactivo'
    
    @classmethod
    def all_states(cls):
        """Retorna todos los estados disponibles"""
        return [cls.ACTIVE, cls.INACTIVE]
    
    @classmethod
    def is_valid_state(cls, state):
        """Verifica si un estado es válido"""
        return state in cls.all_states()


class InventoryAdjustmentReason:
    """
    Motivos de ajuste de inventario según ERS
    """
    PURCHASE = 'compra'
    COUNT = 'conteo'
    RETURN = 'devolucion'
    NEW_STOCK = 'llegada_nuevos_productos'
    STOCK_INCREASE = 'aumento_stock'
    SHRINKAGE = 'merma_dano'
    LOSS_THEFT = 'perdida_robo'
    ADMIN_ADJUSTMENT = 'ajuste_administrativo'
    
    @classmethod
    def all_reasons(cls):
        """Retorna todos los motivos disponibles"""
        return [
            cls.PURCHASE,
            cls.COUNT,
            cls.RETURN,
            cls.NEW_STOCK,
            cls.STOCK_INCREASE,
            cls.SHRINKAGE,
            cls.LOSS_THEFT,
            cls.ADMIN_ADJUSTMENT,
        ]
    
    @classmethod
    def is_valid_reason(cls, reason):
        """Verifica si un motivo es válido"""
        return reason in cls.all_reasons()


class NotificationStatus:
    """Estados de notificaciones por email"""
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'
    
    @classmethod
    def all_statuses(cls):
        """Retorna todos los estados disponibles"""
        return [cls.PENDING, cls.SENT, cls.FAILED]


class NotificationType:
    """Tipos de notificaciones según RF-19 del ERS"""
    RESERVATION_CREATED = 'reservation_created'
    RESERVATION_EXPIRING = 'reservation_expiring'  # Mismo día de vencimiento
    RESERVATION_EXPIRED = 'reservation_expired'
    RESERVATION_CANCELLED = 'reservation_cancelled'
    RESERVATION_APPROVED = 'reservation_approved'
    RESERVATION_REJECTED = 'reservation_rejected'
    
    @classmethod
    def all_types(cls):
        """Retorna todos los tipos disponibles"""
        return [
            cls.RESERVATION_CREATED,
            cls.RESERVATION_EXPIRING,
            cls.RESERVATION_EXPIRED,
            cls.RESERVATION_CANCELLED,
            cls.RESERVATION_APPROVED,
            cls.RESERVATION_REJECTED,
        ]