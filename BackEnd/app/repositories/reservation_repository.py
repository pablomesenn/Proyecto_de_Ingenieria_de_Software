"""
Reservation Repository with proper lazy database loading
This prevents creating new connections on every instantiation
"""
from datetime import datetime, time
from bson import ObjectId
from app.config.database import get_db
from app.models.reservation import Reservation
from app.constants.states import ReservationState
import logging

logger = logging.getLogger(__name__)


class ReservationRepository:
    """Repositorio para operaciones de base de datos de Reservas"""

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
        """Get reservations collection (lazy loaded)"""
        return self.db.reservations

    # ============================================================================
    # REPOSITORY METHODS - Now use properties instead of direct access
    # ============================================================================
    def create(self, reservation):
        """Crea una nueva reserva"""
        result = self.collection.insert_one(reservation.to_dict())
        reservation._id = result.inserted_id
        return reservation

    def count_by_user_id(self, user_id, state=None):
        """Cuenta reservas por usuario (soporta user_id string u ObjectId en BD)"""

        user_id_str = str(user_id)

        query = {
            "$or": [
                {"user_id": user_id_str},
            ]
        }

        if ObjectId.is_valid(user_id_str):
            query["$or"].append({"user_id": ObjectId(user_id_str)})

        if state:
            query["state"] = state

        return self.collection.count_documents(query)

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

    def find_for_export(self, state=None, date_from=None, date_to=None):
        """
        Retorna reservas para exportar (sin paginación).
        date_from/date_to: strings "YYYY-MM-DD" (opcionales)
        """
        query = {}

        if state:
            query["state"] = state

        if date_from or date_to:
            created_filter = {}
            if date_from:
                # 00:00:00
                dfrom = datetime.strptime(date_from, "%Y-%m-%d")
                created_filter["$gte"] = datetime.combine(dfrom.date(), time.min)
            if date_to:
                # 23:59:59.999999
                dto = datetime.strptime(date_to, "%Y-%m-%d")
                created_filter["$lte"] = datetime.combine(dto.date(), time.max)

            query["created_at"] = created_filter

        cursor = self.collection.find(query).sort("created_at", -1)
        return list(cursor)
    
    def get_export_rows(self, filters=None):
        """
        Retorna filas planas para export (una fila por item de reserva)
        filters:
          - state: str | None
          - date_from: datetime | None
          - date_to: datetime | None
        """
        filters = filters or {}
        match = {}

        state = filters.get("state")
        date_from = filters.get("date_from")  # datetime | None
        date_to = filters.get("date_to")      # datetime | None

        if state:
            match["state"] = state

        if date_from or date_to:
            created_filter = {}
            if date_from:
                created_filter["$gte"] = date_from
            if date_to:
                created_filter["$lte"] = date_to
            match["created_at"] = created_filter

        pipeline = [
            {"$match": match},

            # Un item por fila
            {"$unwind": {"path": "$items", "preserveNullAndEmptyArrays": False}},

            # Normalizar user_id a string para lookup robusto (user_id puede ser ObjectId o string)
            {"$addFields": {
                "user_id_str": {"$toString": "$user_id"},
                "variant_id_str": {"$toString": "$items.variant_id"},
                "reservation_id_str": {"$toString": "$_id"},
            }},

            # Lookup user por comparación string($_id) == user_id_str
            {"$lookup": {
                "from": "users",
                "let": {"uid": "$user_id_str"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": [{"$toString": "$_id"}, "$$uid"]}}}
                ],
                "as": "user"
            }},
            {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},

            # Lookup variant por comparación string($_id) == variant_id_str
            {"$lookup": {
                "from": "variants",
                "let": {"vid": "$variant_id_str"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": [{"$toString": "$_id"}, "$$vid"]}}}
                ],
                "as": "variant"
            }},
            {"$unwind": {"path": "$variant", "preserveNullAndEmptyArrays": True}},

            # Lookup product desde variant.product_id (puede ser ObjectId normalmente)
            {"$lookup": {
                "from": "products",
                "localField": "variant.product_id",
                "foreignField": "_id",
                "as": "product"
            }},
            {"$unwind": {"path": "$product", "preserveNullAndEmptyArrays": True}},

            # Proyección final (campos export)
            {"$project": {
                "_id": 0,
                "reservation_id": "$reservation_id_str",
                "state": 1,
                "created_at": 1,

                "user_name": {"$ifNull": ["$user.nombre", {"$ifNull": ["$user.name", ""]}]},
                "user_email": {"$ifNull": ["$user.email", ""]},

                "product_name": {"$ifNull": ["$product.nombre", ""]},

                # Variante: intenta varios campos típicos
                "variant_name": {
                    "$ifNull": [
                        "$variant.tamano_pieza",
                        {"$ifNull": ["$variant.nombre", {"$ifNull": ["$variant.name", ""]}]}
                    ]
                },

                "quantity": {"$ifNull": ["$items.quantity", 0]},
            }},

            {"$sort": {"created_at": -1}},
        ]

        return list(self.collection.aggregate(pipeline))
