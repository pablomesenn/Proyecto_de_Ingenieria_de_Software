from datetime import datetime
from bson import ObjectId
from app.config.database import get_db
from app.models.reservation import Reservation
from app.constants.states import ReservationState


class ReservationRepository:
    """Repositorio para operaciones de base de datos de Reservas"""
    
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.reservations
        
    def create(self, reservation):
        """Crea una nueva reserva"""
        result = self.collection.insert_one(reservation.to_dict())
        reservation._id = result.inserted_id
        return reservation
    
    def find_by_id(self, reservation_id):
        """Busca una reserva por ID"""
        data = self.collection.find_one({'_id': ObjectId(reservation_id)})
        return Reservation.from_dict(data) if data else None
    
    def find_by_user_id(self, user_id, state=None, skip=0, limit=20):
        """Busca reservas de un usuario especifico"""
        query = {'user_id': ObjectId(user_id)}
        if state:
            query['state'] = state
        
        cursor = self.collection.find(query).sort('created_at', -1).skip(skip).limit(limit)
        return [Reservation.from_dict(data) for data in cursor]
    
    def find_all(self, filters=None, skip=0, limit=20):
        """Busca todas las reservas con filtros opcionales"""
        query = filters or {}
        
        cursor = self.collection.find(query).sort('created_at', -1).skip(skip).limit(limit)
        return [Reservation.from_dict(data) for data in cursor]
    
    def find_expired(self):
        """Busca reservas vencidas que aun no han sido procesadas"""
        now = datetime.utcnow()
        query = {
            'state': {'$in': [ReservationState.PENDING, ReservationState.APPROVED]},
            'expires_at': {'$lte': now}
        }
        cursor = self.collection.find(query)
        return [Reservation.from_dict(data) for data in cursor]
    
    def find_expiring_today(self):
        """Busca reservas que vencen el mismo dia"""
        now = datetime.utcnow()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        query = {
            'state': {'$in': [ReservationState.PENDING, ReservationState.APPROVED]},
            'expires_at': {
                '$gte': now,
                '$lte': end_of_day
            }
        }
        cursor = self.collection.find(query)
        return [Reservation.from_dict(data) for data in cursor]
    
    def update(self, reservation_id, update_data):
        """Actualiza una reserva"""
        result = self.collection.update_one(
            {'_id': ObjectId(reservation_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def update_state(self, reservation_id, new_state, timestamp_field=None):
        """Actualiza el estado de una reserva"""
        update_data = {
            'state': new_state
        }
        
        if timestamp_field:
            update_data[timestamp_field] = datetime.utcnow()
            
        return self.update(reservation_id, update_data)
    
    def delete(self, reservation_id):
        """Elimina una reserva (no recomendado, mejor usar estados)"""
        result = self.collection.delete_one({'_id': ObjectId(reservation_id)})
        return result.deleted_count > 0
    
    def count(self, filters=None):
        """Cuenta reservas con filtros opcionales"""
        query = filters or {}
        return self.collection.count_documents(query)
    
    def get_user_active_reservations_count(self, user_id):
        """Cuenta reservas activas de un usuario"""
        query = {
            'user_id': ObjectId(user_id),
            'state': {'$in': [ReservationState.PENDING, ReservationState.APPROVED]}
        }
        return self.collection.count_documents(query)