from unittest import result
from bson import ObjectId
from app.config.database import get_db
from app.models.inventory import Inventory
from datetime import datetime


class InventoryRepository:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.inventory
        self.movements_collection = self.db.inventory_movements

    def find_by_variant_id(self, variant_id):
        return self.collection.find_one({'variant_id': ObjectId(variant_id)})

    def find_by_id(self, inventory_id):
        return self.collection.find_one({'_id': ObjectId(inventory_id)})

    def get_all(self, skip=0, limit=20):
        cursor = self.collection.find({}).sort('actualizado_en', -1).skip(skip).limit(limit)
        return list(cursor)

    def get_movements_detailed(self, skip=0, limit=50, filters=None):
        filters = filters or {}
        match = {}

        if filters.get("variant_id"):
            match["variant_id"] = ObjectId(filters["variant_id"])

        if filters.get("movement_type"):
            match["movement_type"] = filters["movement_type"]

        pipeline = [
            {"$match": match},
            {"$sort": {"creado_en": -1}},
            {"$skip": int(skip)},
            {"$limit": int(limit)},

            # Variant
            {"$lookup": {
                "from": "variants",
                "localField": "variant_id",
                "foreignField": "_id",
                "as": "variant"
            }},
            {"$unwind": {"path": "$variant", "preserveNullAndEmptyArrays": True}},

            # Product
            {"$lookup": {
                "from": "products",
                "localField": "variant.product_id",
                "foreignField": "_id",
                "as": "product"
            }},
            {"$unwind": {"path": "$product", "preserveNullAndEmptyArrays": True}},

            # Actor (ajusta "users" si tu colección se llama distinto)
            {"$lookup": {
                "from": "users",
                "localField": "actor_id",
                "foreignField": "_id",
                "as": "actor"
            }},
            {"$unwind": {"path": "$actor", "preserveNullAndEmptyArrays": True}},

            {"$project": {
                "_id": 1,
                "variant_id": 1,
                "movement_type": 1,
                "quantity": 1,
                "reason": 1,
                "actor_id": 1,
                "creado_en": 1,

                "stock_before": 1,
                "stock_after": 1,

                # Nombres
                "product_name": "$product.nombre",
                "variant_name": {"$ifNull": ["$variant.tamano_pieza", "$variant.nombre"]},

                # Actor: intenta varios campos típicos
                "actor_name": {
                    "$ifNull": [
                        "$actor.nombre",
                        {"$ifNull": ["$actor.name", "$actor.email"]}
                    ]
                },
            }},
        ]

        return list(self.movements_collection.aggregate(pipeline))


    def get_all_with_details(self, skip=0, limit=20):
        pipeline = [
            {
                '$lookup': {
                    'from': 'variants',
                    'localField': 'variant_id',
                    'foreignField': '_id',
                    'as': 'variant_details'
                }
            },
            {'$unwind': '$variant_details'},
            {
                '$lookup': {
                    'from': 'products',
                    'localField': 'variant_details.product_id',
                    'foreignField': '_id',
                    'as': 'product_details'
                }
            },
            {'$unwind': '$product_details'},
            {
                '$project': {
                    '_id': 1,
                    'variant_id': 1,
                    'stock_total': 1,
                    'stock_retenido': 1,
                    'actualizado_en': 1,
                    'creado_en': 1,
                    'product_name': '$product_details.nombre',
                    'variant_size': '$variant_details.tamano_pieza',
                    'variant_price': '$variant_details.precio'
                }
            },
            {'$sort': {'actualizado_en': -1}},
            {'$skip': skip},
            {'$limit': limit}
        ]

        return list(self.collection.aggregate(pipeline))

    def create(self, inventory):
        before = {"total": 0, "retained": 0, "available": 0}
        result = self.collection.insert_one(inventory.to_dict())
        after = self._snapshot(str(inventory.variant_id))

        self._log_movement(
            variant_id=inventory.variant_id,
            quantity=inventory.stock_total,
            movement_type='initial',
            reason='initial_stock',
            before=before,
            after=after
        )

        return self.collection.find_one({'_id': result.inserted_id})

    def update_stock_total(self, variant_id, new_stock_total):
        result = self.collection.update_one(
            {'variant_id': ObjectId(variant_id)},
            {
                '$set': {
                    'stock_total': new_stock_total,
                    'actualizado_en': datetime.utcnow()
                }
            }
        )

        return result.modified_count > 0

    def get_available_stock(self, variant_id):
        """Calcula stock disponible (total - retenido)"""
        inventory = self.find_by_variant_id(variant_id)
        if not inventory:
            return 0

        total_stock = inventory.get('stock_total', 0)
        retained_stock = inventory.get('stock_retenido', 0)
        return max(0, total_stock - retained_stock)

    def increase_retained_stock(self, variant_id, quantity, reason='reservation_created'):
        before = self._snapshot(variant_id)

        result = self.collection.update_one(
            {'variant_id': ObjectId(variant_id)},
            {
                '$inc': {'stock_retenido': quantity},
                '$set': {'actualizado_en': datetime.utcnow()}
            }
        )

        if result.modified_count > 0:
            after = self._snapshot(variant_id)
            self._log_movement(
                variant_id=variant_id,
                quantity=quantity,
                movement_type='retain',
                reason=reason,
                before=before,
                after=after
            )

        return result.modified_count > 0



    def decrease_retained_stock(self, variant_id, quantity, reason='reservation_released'):
        before = self._snapshot(variant_id)

        inventory = self.find_by_variant_id(variant_id)
        if not inventory:
            return False

        current_retained = inventory.get('stock_retenido', 0)
        new_retained = max(0, current_retained - quantity)

        result = self.collection.update_one(
            {'variant_id': ObjectId(variant_id)},
            {
                '$set': {
                    'stock_retenido': new_retained,
                    'actualizado_en': datetime.utcnow()
                }
            }
        )

        if result.modified_count > 0:
            after = self._snapshot(variant_id)
            self._log_movement(
                variant_id=variant_id,
                quantity=-quantity,
                movement_type='release',
                reason=reason,
                before=before,
                after=after
            )

        return result.modified_count > 0



    def adjust_stock(self, variant_id, delta, reason, actor_id=None):
        before = self._snapshot(variant_id)

        inventory = self.find_by_variant_id(variant_id)
        if not inventory:
            return False

        current_stock = inventory.get('stock_total', 0)
        new_stock = current_stock + delta
        if new_stock < 0:
            return False

        result = self.collection.update_one(
            {'variant_id': ObjectId(variant_id)},
            {'$set': {'stock_total': new_stock, 'actualizado_en': datetime.utcnow()}}
        )

        if result.modified_count > 0:
            after = self._snapshot(variant_id)
            self._log_movement(
                variant_id=variant_id,
                quantity=delta,
                movement_type='adjustment',
                reason=reason,
                actor_id=actor_id,
                before=before,
                after=after
            )

        return result.modified_count > 0


    def _snapshot(self, variant_id):
        inv = self.collection.find_one({'variant_id': ObjectId(variant_id)})
        if not inv:
            return {
                "total": 0,
                "retained": 0,
                "available": 0,
            }
        total = inv.get("stock_total", 0)
        retained = inv.get("stock_retenido", 0)
        return {
            "total": total,
            "retained": retained,
            "available": max(0, total - retained),
        }

    def _log_movement(self, variant_id, quantity, movement_type, reason, actor_id=None,
                      before=None, after=None):
        before = before or {"total": None, "retained": None, "available": None}
        after = after or {"total": None, "retained": None, "available": None}

        movement = {
            'variant_id': ObjectId(variant_id),
            'quantity': quantity,
            'movement_type': movement_type,
            'reason': reason,
            'actor_id': ObjectId(actor_id) if actor_id else None,
            'creado_en': datetime.utcnow(),

            # Para tu tabla:
            'stock_before': before.get("available"),
            'stock_after': after.get("available"),

            # (extra útil por si luego lo ocupas)
            'total_before': before.get("total"),
            'total_after': after.get("total"),
            'retained_before': before.get("retained"),
            'retained_after': after.get("retained"),
        }

        self.movements_collection.insert_one(movement)

    def get_movements(self, variant_id=None, movement_type=None, skip=0, limit=50):
        """Obtiene el historial de movimientos"""
        query = {}
        if variant_id:
            query['variant_id'] = ObjectId(variant_id)
        if movement_type:
            query['movement_type'] = movement_type

        cursor = self.movements_collection.find(query).sort('creado_en', -1).skip(skip).limit(limit)
        return list(cursor)

    def validate_availability(self, variant_id, quantity):
        """Valida si hay suficiente stock disponible"""
        available = self.get_available_stock(variant_id)
        return available >= quantity

    def count(self):
        """Cuenta el total de registros de inventario"""
        return self.collection.count_documents({})
    
    