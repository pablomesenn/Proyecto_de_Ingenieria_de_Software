from bson import ObjectId
from app.config.database import get_db, RedisHelper
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ProductRepository:
    def __init__(self):
        self.db = get_db()
        self.products_collection = self.db.products
        self.variants_collection = self.db.variants
        self.redis_helper = RedisHelper()

    def find_by_id(self, product_id):
        # Intentar obtener de caché
        cache_key = f"product:{product_id}"
        cached = self.redis_helper.get(cache_key)

        if cached:
            logger.info(f"Product {product_id} obtenido de caché")
            return json.loads(cached)

        # Si no está en caché, buscar en DB
        product = self.products_collection.find_one({'_id': ObjectId(product_id)})

        if product:
            product['_id'] = str(product['_id'])
            # Guardar en caché por 10 minutos
            self.redis_helper.set_with_expiry(cache_key, json.dumps(product, default=str), 600)

        return product

    def find_all(self, filters=None, skip=0, limit=20):
        """Busca todos los productos con filtros opcionales"""
        query = filters or {}

        cursor = self.products_collection.find(query).sort('created_at', -1).skip(skip).limit(limit)
        products = []
        for product in cursor:
            product['_id'] = str(product['_id'])
            products.append(product)

        return products

    def search_and_filter(self, search_text=None, categoria=None, tags=None, disponibilidad=True, skip=0, limit=20):
        """
        Busca y filtra productos
        """
        query = {}

        # Filtro de visibilidad por estado
        if disponibilidad:
            query['estado'] = 'activo'

        # Búsqueda por texto en nombre
        if search_text:
            query['nombre'] = {'$regex': search_text, '$options': 'i'}

        # Filtro por categoría
        if categoria:
            query['categoria'] = categoria

        # Filtro por tags
        if tags:
            if isinstance(tags, list):
                query['tags'] = {'$in': tags}
            else:
                query['tags'] = tags

        # Intentar obtener de caché
        cache_key = f"products_search:{json.dumps(query, sort_keys=True)}:{skip}:{limit}"
        cached = self.redis_helper.get(cache_key)

        if cached:
            logger.info("Resultados de búsqueda obtenidos de caché")
            return json.loads(cached)

        # Buscar en DB
        cursor = self.products_collection.find(query).sort('nombre', 1).skip(skip).limit(limit)
        products = []
        for product in cursor:
            product['_id'] = str(product['_id'])
            products.append(product)

        # Guardar en caché por 5 minutos
        self.redis_helper.set_with_expiry(cache_key, json.dumps(products, default=str), 300)

        return products

    def create(self, product_data):
        result = self.products_collection.insert_one(product_data)
        product_data['_id'] = str(result.inserted_id)

        # Invalidar caché de productos
        self._invalidate_products_cache()

        return product_data

    def update(self, product_id, update_data):
        update_data['updated_at'] = datetime.utcnow()

        result = self.products_collection.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': update_data}
        )

        if result.modified_count > 0:
            # Invalidar caché del producto y de búsquedas
            self._invalidate_product_cache(product_id)
            self._invalidate_products_cache()

        return result.modified_count > 0

    def delete(self, product_id):
        result = self.products_collection.delete_one({'_id': ObjectId(product_id)})

        if result.deleted_count > 0:
            self._invalidate_product_cache(product_id)
            self._invalidate_products_cache()

        return result.deleted_count > 0

    def update_state(self, product_id, new_state):
        return self.update(product_id, {'estado': new_state})

    def count(self, filters=None):
        """Cuenta productos con filtros opcionales"""
        query = filters or {}
        return self.products_collection.count_documents(query)

    def get_categories(self):
        pipeline = [
            {
                "$project": {
                    "cat": {
                        "$ifNull": ["$categoria", {"$ifNull": ["$category", "$categoryName"]}]
                    }
                }
            },
            {"$match": {"cat": {"$ne": None, "$ne": ""}}},
            {"$group": {"_id": "$cat"}},
            {"$sort": {"_id": 1}},
        ]
        return [d["_id"] for d in self.products_collection.aggregate(pipeline)]


    def get_tags(self):
        pipeline = [
            {
                "$project": {
                    "t": {"$ifNull": ["$tags", "$etiquetas"]}  # si no existe 'etiquetas', no estorba
                }
            },
            {"$unwind": {"path": "$t", "preserveNullAndEmptyArrays": False}},
            {"$match": {"t": {"$ne": None, "$ne": ""}}},
            {"$group": {"_id": "$t"}},
            {"$sort": {"_id": 1}},
        ]
        return [d["_id"] for d in self.products_collection.aggregate(pipeline)]


    def count_by_category_value(self, slug: str = None, name: str = None, only_active: bool = False) -> int:
        values = [v for v in [slug, name] if v]
        if not values:
            return 0

        query = {
            "$or": [
                {"categoria": {"$in": values}},
                {"category": {"$in": values}},
                {"categoryName": {"$in": values}},
            ]
        }
        if only_active:
            query["estado"] = "activo"

        return self.products_collection.count_documents(query)


    def count_by_tag_value(self, slug: str = None, name: str = None, only_active: bool = False) -> int:
        values = [v for v in [slug, name] if v]
        if not values:
            return 0

        query = {
            "$or": [
                {"tags": {"$in": values}},
                {"etiquetas": {"$in": values}},
            ]
        }
        if only_active:
            query["estado"] = "activo"

        return self.products_collection.count_documents(query)

    def _invalidate_product_cache(self, product_id):
        """Invalida el caché de un producto específico"""
        cache_key = f"product:{product_id}"
        self.redis_helper.delete(cache_key)

    def _invalidate_products_cache(self):
        """Invalida todo el caché de productos y búsquedas"""
        self.redis_helper.delete_pattern("products_search:*")
        self.redis_helper.delete_pattern("product:*")


class VariantRepository:
    def __init__(self):
        self.db = get_db()
        self.variants_collection = self.db.variants

    def find_by_id(self, variant_id):
        variant = self.variants_collection.find_one({'_id': ObjectId(variant_id)})
        if variant:
            variant['_id'] = str(variant['_id'])
            variant['product_id'] = str(variant['product_id'])
        return variant

    def find_by_product_id(self, product_id):
        cursor = self.variants_collection.find({'product_id': ObjectId(product_id)})
        variants = []
        for variant in cursor:
            variant['_id'] = str(variant['_id'])
            variant['product_id'] = str(variant['product_id'])
            variants.append(variant)
        return variants

    def create(self, variant_data):
        result = self.variants_collection.insert_one(variant_data)
        variant_data['_id'] = str(result.inserted_id)
        return variant_data

    def update(self, variant_id, update_data):
        result = self.variants_collection.update_one(
            {'_id': ObjectId(variant_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0

    def delete(self, variant_id):
        result = self.variants_collection.delete_one({'_id': ObjectId(variant_id)})
        return result.deleted_count > 0
