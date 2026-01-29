from app.repositories.product_repository import ProductRepository, VariantRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.catalog_repository import CatalogRepository
from app.constants.states import ProductState
import logging

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.variant_repo = VariantRepository()
        self.inventory_repo = InventoryRepository()
        self.catalog_repo = CatalogRepository()

    def search_and_filter_catalog(self, search_text=None, categoria=None, tags=None, disponibilidad=True, skip=0, limit=20):
        """
        Busca y filtra productos en el catalogo (CU-005)
        Calcula disponibilidad en tiempo real considerando reservas activas
        """
        # Obtener productos segun filtros
        products = self.product_repo.search_and_filter(
            search_text=search_text,
            categoria=categoria,
            tags=tags,
            disponibilidad=disponibilidad,
            skip=skip,
            limit=limit
        )

        # Enriquecer con variantes y disponibilidad
        enriched_products = []
        for product in products:
            # Obtener variantes del producto
            variants = self.variant_repo.find_by_product_id(product['_id'])

            # Calcular disponibilidad para cada variante
            for variant in variants:
                available = self.inventory_repo.get_available_stock(variant['_id'])
                variant['disponibilidad'] = available

            product['variantes'] = variants
            enriched_products.append(product)

        return enriched_products

    def get_product_detail(self, product_id):
        """
        Obtiene el detalle completo de un producto con variantes y disponibilidad
        """
        product = self.product_repo.find_by_id(product_id)

        if not product:
            raise ValueError("Producto no encontrado")

        # Obtener variantes
        variants = self.variant_repo.find_by_product_id(product_id)

        # Calcular disponibilidad para cada variante
        for variant in variants:
            available = self.inventory_repo.get_available_stock(variant['_id'])
            variant['disponibilidad'] = available

        product['variantes'] = variants

        return product

    def create_product(self, product_data, admin_id):
        # Validaciones
        if not product_data.get('nombre'):
            raise ValueError("El nombre del producto es requerido")

        if not product_data.get('categoria'):
            raise ValueError("La categoria es requerida")
        
        if not product_data.get('imagen_url'):
            raise ValueError("La imagen es requerida")

        # Extraer variantes si existen
        variantes_data = product_data.pop('variantes', [])
        
        # Validar que haya al menos una variante
        if not variantes_data or len(variantes_data) == 0:
            raise ValueError("Debe agregar al menos una variante (tamano)")

        # Establecer estado por defecto
        if 'estado' not in product_data:
            product_data['estado'] = ProductState.ACTIVE

        # Crear producto
        from datetime import datetime
        product_data['created_at'] = datetime.utcnow()
        product_data['updated_at'] = datetime.utcnow()
        
        product = self.product_repo.create(product_data)
        product_id = product['_id']

        # Crear variantes
        from bson import ObjectId
        for variante in variantes_data:
            variante['product_id'] = ObjectId(product_id)
            variante['created_at'] = datetime.utcnow()
            created_variant = self.variant_repo.create(variante)
            
            # Siempre crear registro de inventario inicial (incluso con stock 0)
            stock_inicial = variante.get('stock_inicial', 0)
            self.inventory_repo.create_initial_stock(
                created_variant['_id'],
                stock_inicial,
                admin_id,
                'Inventario inicial'
            )

        # Registrar auditoria
        self._log_audit(admin_id, 'create_product', product_id)

        # Invalidar cache
        self.product_repo._invalidate_products_cache()

        return product

    def update_product(self, product_id, update_data, admin_id):
        # Verificar que el producto existe
        product = self.product_repo.find_by_id(product_id)
        if not product:
            raise ValueError("Producto no encontrado")

        # Extraer variantes si existen
        variantes_data = update_data.pop('variantes', None)

        # Actualizar producto
        from datetime import datetime
        update_data['updated_at'] = datetime.utcnow()
        
        success = self.product_repo.update(product_id, update_data)

        # Si se proporcionaron variantes, actualizarlas
        if variantes_data is not None:
            from bson import ObjectId
            
            # Obtener variantes existentes
            existing_variants = self.variant_repo.find_by_product_id(product_id)
            existing_ids = {v['_id'] for v in existing_variants}
            
            # Procesar variantes nuevas/actualizadas
            updated_ids = set()
            for variante in variantes_data:
                variant_id = variante.get('_id')
                
                if variant_id and variant_id in existing_ids:
                    # Actualizar variante existente
                    # Eliminar _id del diccionario antes de actualizar (MongoDB no permite modificar _id)
                    variant_update_data = {k: v for k, v in variante.items() if k != '_id'}
                    self.variant_repo.update(variant_id, variant_update_data)
                    updated_ids.add(variant_id)
                else:
                    # Crear nueva variante
                    # Eliminar _id si existe (para variantes nuevas que vienen con _id null o undefined)
                    variante_clean = {k: v for k, v in variante.items() if k != '_id'}
                    variante_clean['product_id'] = ObjectId(product_id)
                    variante_clean['created_at'] = datetime.utcnow()
                    created = self.variant_repo.create(variante_clean)
                    updated_ids.add(created['_id'])
                    
                    # Siempre crear inventario inicial (incluso con stock 0)
                    stock_inicial = variante.get('stock_inicial', 0)
                    self.inventory_repo.create_initial_stock(
                        created['_id'],
                        stock_inicial,
                        admin_id,
                        'Inventario inicial'
                    )
            
            # Eliminar variantes que no estan en la lista actualizada
            for variant_id in existing_ids - updated_ids:
                self.variant_repo.delete(variant_id)

        if success:
            self._log_audit(admin_id, 'update_product', product_id)
            # Invalidar cache
            self.product_repo._invalidate_products_cache()

        return self.product_repo.find_by_id(product_id)

    def update_product_state(self, product_id, new_state, admin_id):
        """
        Actualiza el estado de un producto (CU-018, RF-24)
        Estados: activo, inactivo, agotado
        """
        if not ProductState.is_valid_state(new_state):
            raise ValueError(f"Estado invalido: {new_state}")

        success = self.product_repo.update_state(product_id, new_state)

        if success:
            self._log_audit(admin_id, 'update_product_state', product_id, {'new_state': new_state})

        return success

    def delete_product(self, product_id, admin_id):
        # En lugar de eliminar, cambiar estado a inactivo
        return self.update_product_state(product_id, ProductState.INACTIVE, admin_id)

    def get_categories(self):
        """
        Obtiene todas las categorias desde la coleccion categories (no desde productos)
        Esto permite mostrar categorias disponibles incluso si no hay productos que las usen
        """
        categories_docs = self.catalog_repo.list_categories()
        # Extraer solo los nombres de las categorias
        categories = [cat['name'] for cat in categories_docs]
        logger.info(f"Categorias enviadas para nuevo producto desde coleccion categories: {categories}")
        return categories

    def get_tags(self):
        """
        Obtiene todos los tags desde la coleccion tags (no desde productos)
        Esto permite mostrar tags disponibles incluso si no hay productos que las usen
        """
        tags_docs = self.catalog_repo.list_tags()
        # Extraer solo los nombres de los tags
        tags = [tag['name'] for tag in tags_docs]
        logger.info(f"Tags enviados para nuevo producto desde coleccion tags: {tags}")
        return tags

    def _log_audit(self, actor_id, action, entity_id, details=None):
        """Registra una accion en auditoria"""
        from app.config.database import get_db
        from bson import ObjectId
        from datetime import datetime

        db = get_db()

        audit_log = {
            'actor_id': ObjectId(actor_id) if actor_id else None,
            'action': action,
            'entity_type': 'product',
            'entity_id': ObjectId(entity_id) if entity_id else None,
            'details': details,
            'timestamp': datetime.utcnow()
        }

        db.audit_logs.insert_one(audit_log)