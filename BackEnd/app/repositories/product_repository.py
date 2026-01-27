"""
Product Repository with proper lazy database loading
This prevents creating new connections on every instantiation
"""
from bson import ObjectId
from app.config.database import get_db, RedisHelper
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ProductRepository:
    def __init__(self):
        self._db = None
        self.redis_helper = RedisHelper()

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
    def products_collection(self):
        """Get products collection (lazy loaded)"""
        return self.db.products

    @property
    def variants_collection(self):
        """Get variants collection (lazy loaded)"""
        return self.db.variants

    # ============================================================================
    # REPOSITORY METHODS - Now use properties instead of direct access
    # ============================================================================

    def find_by_id(self, product_id):
        cache_key = f"product:{product_id}"
        cached = self.redis_helper.get(cache_key)

        if cached:
            logger.info(f"Product {product_id} obtenido de caché")
            return json.loads(cached)

        # Use property - this will lazy-load DB connection if needed
        product = self.products_collection.find_one({'_id': ObjectId(product_id)})

        if product:
            product['_id'] = str(product['_id'])
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
        """Busca y filtra productos"""
        query = {}

        if disponibilidad:
            query['estado'] = 'activo'

        if search_text:
            query['nombre'] = {'$regex': search_text, '$options': 'i'}

        if categoria:
            query['categoria'] = categoria

        if tags:
            if isinstance(tags, list):
                query['tags'] = {'$in': tags}
            else:
                query['tags'] = tags

        cache_key = f"products_search:{json.dumps(query, sort_keys=True)}:{skip}:{limit}"
        cached = self.redis_helper.get(cache_key)

        if cached:
            logger.info("Resultados de búsqueda obtenidos de caché")
            return json.loads(cached)

        cursor = self.products_collection.find(query).sort('nombre', 1).skip(skip).limit(limit)
        products = []
        for product in cursor:
            product['_id'] = str(product['_id'])
            products.append(product)

        self.redis_helper.set_with_expiry(cache_key, json.dumps(products, default=str), 300)

        return products

    def create(self, product_data):
        result = self.products_collection.insert_one(product_data)
        product_data['_id'] = str(result.inserted_id)

        self._invalidate_products_cache()

        return product_data

    def update(self, product_id, update_data):
        update_data['updated_at'] = datetime.utcnow()

        result = self.products_collection.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': update_data}
        )

        if result.modified_count > 0:
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
                    "t": {"$ifNull": ["$tags", "$etiquetas"]}
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
        self._db = None

    @property
    def db(self):
        """Lazy load database connection"""
        if self._db is None:
            self._db = get_db()
        return self._db

    @property
    def variants_collection(self):
        return self.db.variants

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
