from bson import ObjectId
from app.config.database import get_db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WishlistRepository:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.wishlists

    def find_by_user_id(self, user_id):
        wishlist = self.collection.find_one({'user_id': ObjectId(user_id)})
        return wishlist

    def create(self, user_id):
        wishlist = {
            'user_id': ObjectId(user_id),
            'items': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        result = self.collection.insert_one(wishlist)
        wishlist['_id'] = result.inserted_id

        return wishlist

    def get_or_create(self, user_id):
        """Obtiene la wishlist de un usuario o la crea si no existe"""
        wishlist = self.find_by_user_id(user_id)

        if not wishlist:
            wishlist = self.create(user_id)

        return wishlist

    def add_item(self, user_id, variant_id, quantity=1):
        """
        Agrega un item a la wishlist
        Si el item ya existe, incrementa la cantidad
        """
        wishlist = self.get_or_create(user_id)

        # Buscar si el item ya existe
        item_exists = False
        for item in wishlist['items']:
            if str(item['variant_id']) == str(variant_id):
                # Consolidar: incrementar cantidad
                item['quantity'] += quantity
                item['updated_at'] = datetime.utcnow()
                item_exists = True
                break

        # Si no existe, agregar nuevo item
        if not item_exists:
            new_item = {
                'item_id': ObjectId(),
                'variant_id': ObjectId(variant_id),
                'quantity': quantity,
                'added_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            wishlist['items'].append(new_item)

        # Actualizar wishlist en DB
        self.collection.update_one(
            {'user_id': ObjectId(user_id)},
            {
                '$set': {
                    'items': wishlist['items'],
                    'updated_at': datetime.utcnow()
                }
            }
        )

        return self.find_by_user_id(user_id)

    def remove_item(self, user_id, item_id):
        result = self.collection.update_one(
            {'user_id': ObjectId(user_id)},
            {
                '$pull': {'items': {'item_id': ObjectId(item_id)}},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )

        return result.modified_count > 0

    def update_item_quantity(self, user_id, item_id, quantity):
        if quantity <= 0:
            # Si la cantidad es 0 o negativa, eliminar el item
            return self.remove_item(user_id, item_id)

        result = self.collection.update_one(
            {
                'user_id': ObjectId(user_id),
                'items.item_id': ObjectId(item_id)
            },
            {
                '$set': {
                    'items.$.quantity': quantity,
                    'items.$.updated_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            }
        )

        return result.modified_count > 0

    def clear(self, user_id):
        """Limpia todos los items de la wishlist"""
        result = self.collection.update_one(
            {'user_id': ObjectId(user_id)},
            {
                '$set': {
                    'items': [],
                    'updated_at': datetime.utcnow()
                }
            }
        )

        return result.modified_count > 0

    def get_items_with_details(self, user_id):
        wishlist = self.find_by_user_id(user_id)

        if not wishlist or not wishlist.get('items'):
            return []

        # Pipeline de agregación para obtener detalles
        pipeline = [
            {'$match': {'user_id': ObjectId(user_id)}},
            {'$unwind': '$items'},
            {'$lookup': {
                'from': 'variants',
                'localField': 'items.variant_id',
                'foreignField': '_id',
                'as': 'variant_details'
            }},
            {'$unwind': '$variant_details'},
            {'$lookup': {
                'from': 'products',
                'localField': 'variant_details.product_id',
                'foreignField': '_id',
                'as': 'product_details'
            }},
            {'$unwind': '$product_details'},
            {'$lookup': {
                'from': 'inventory',
                'localField': 'items.variant_id',
                'foreignField': 'variant_id',
                'as': 'inventory_details'
            }},
            {'$unwind': {
                'path': '$inventory_details',
                'preserveNullAndEmptyArrays': True
            }},
            {'$project': {
                'item_id': '$items.item_id',
                'variant_id': '$items.variant_id',
                'quantity': '$items.quantity',
                'added_at': '$items.added_at',
                'product_name': '$product_details.nombre',
                'product_image': '$product_details.imagen_url',
                'product_estado': '$product_details.estado',
                'variant_size': '$variant_details.tamano_pieza',
                'variant_unit': '$variant_details.unidad',
                'variant_price': '$variant_details.precio',
                'stock_total': {'$ifNull': ['$inventory_details.stock_total', 0]},
                'stock_retenido': {'$ifNull': ['$inventory_details.stock_retenido', 0]},
                'disponibilidad': {
                    '$subtract': [
                        {'$ifNull': ['$inventory_details.stock_total', 0]},
                        {'$ifNull': ['$inventory_details.stock_retenido', 0]}
                    ]
                }
            }}
        ]

        result = list(self.collection.aggregate(pipeline))

        # Convertir ObjectIds a strings
        for item in result:
            item['_id'] = str(item['_id'])
            item['item_id'] = str(item['item_id'])
            item['variant_id'] = str(item['variant_id'])

        return result
