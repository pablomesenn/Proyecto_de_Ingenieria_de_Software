from datetime import datetime, timedelta
from bson import ObjectId


class Reservation:
    """
    Modelo de Reserva segun ERS
    Representa una retencion temporal (hold) de inventario con prioridad
    """
    
    def __init__(
        self,
        user_id,
        items,
        state='Pendiente',
        created_at=None,
        expires_at=None,
        approved_at=None,
        cancelled_at=None,
        rejected_at=None,
        expired_at=None,
        notes=None,
        admin_notes=None,
        _id=None
    ):
        self._id = _id or ObjectId()
        self.user_id = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
        self.items = items
        self.state = state
        self.created_at = created_at or datetime.utcnow()
        self.expires_at = expires_at or (self.created_at + timedelta(hours=24))
        self.approved_at = approved_at
        self.cancelled_at = cancelled_at
        self.rejected_at = rejected_at
        self.expired_at = expired_at
        self.notes = notes
        self.admin_notes = admin_notes
        
    def to_dict(self):
        """Convierte el modelo a diccionario para MongoDB"""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'items': self.items,
            'state': self.state,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'approved_at': self.approved_at,
            'cancelled_at': self.cancelled_at,
            'rejected_at': self.rejected_at,
            'expired_at': self.expired_at,
            'notes': self.notes,
            'admin_notes': self.admin_notes
        }
    
    @staticmethod
    def from_dict(data):
        """Crea una instancia desde un diccionario"""
        if not data:
            return None
        return Reservation(
            user_id=data.get('user_id'),
            items=data.get('items'),
            state=data.get('state'),
            created_at=data.get('created_at'),
            expires_at=data.get('expires_at'),
            approved_at=data.get('approved_at'),
            cancelled_at=data.get('cancelled_at'),
            rejected_at=data.get('rejected_at'),
            expired_at=data.get('expired_at'),
            notes=data.get('notes'),
            admin_notes=data.get('admin_notes'),
            _id=data.get('_id')
        )
    
    def is_expired(self):
        """Verifica si la reserva esta vencida"""
        if self.state not in ['Pendiente', 'Aprobada']:
            return False
        return datetime.utcnow() >= self.expires_at
    
    def expires_today(self):
        """Verifica si la reserva vence el mismo dia"""
        if self.state not in ['Pendiente', 'Aprobada']:
            return False
        now = datetime.utcnow()
        return (self.expires_at.date() == now.date() and 
                self.expires_at > now)