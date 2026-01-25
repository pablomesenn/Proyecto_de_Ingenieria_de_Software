from app.repositories.product_repository import ProductRepository, VariantRepository
from app.repositories.inventory_repository import InventoryRepository
from app.constants.states import ProductState
import logging

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.variant_repo = VariantRepository()
        self.inventory_repo = InventoryRepository()

    def search_and_filter_catalog(self, search_text=None, categoria=None, tags=None, disponibilidad=True, skip=0, limit=20):
        """
        Busca y filtra productos en el catálogo (CU-005)
        Calcula disponibilidad en tiempo real considerando reservas activas
        """
        # Obtener productos según filtros
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
            raise ValueError("La categoría es requerida")

        # Establecer estado por defecto
        if 'estado' not in product_data:
            product_data['estado'] = ProductState.ACTIVE

        # Crear producto
        product = self.product_repo.create(product_data)

        # Registrar auditoría
        self._log_audit(admin_id, 'create_product', product['_id'])

        return product

    def update_product(self, product_id, update_data, admin_id):
        # Verificar que el producto existe
        product = self.product_repo.find_by_id(product_id)
        if not product:
            raise ValueError("Producto no encontrado")

        # Actualizar producto
        success = self.product_repo.update(product_id, update_data)

        if success:
            self._log_audit(admin_id, 'update_product', product_id)

        return self.product_repo.find_by_id(product_id)

    def update_product_state(self, product_id, new_state, admin_id):
        """
        Actualiza el estado de un producto (CU-018, RF-24)
        Estados: activo, inactivo, agotado
        """
        if not ProductState.is_valid_state(new_state):
            raise ValueError(f"Estado inválido: {new_state}")

        success = self.product_repo.update_state(product_id, new_state)

        if success:
            self._log_audit(admin_id, 'update_product_state', product_id, {'new_state': new_state})

        return success

    def delete_product(self, product_id, admin_id):
        # En lugar de eliminar, cambiar estado a inactivo
        return self.update_product_state(product_id, ProductState.INACTIVE, admin_id)

    def get_categories(self):
        """Obtiene todas las categorías disponibles"""
        return self.product_repo.get_categories()

    def get_tags(self):
        """Obtiene todos los tags disponibles"""
        return self.product_repo.get_tags()

    def _log_audit(self, actor_id, action, entity_id, details=None):
        """Registra una acción en auditoría"""
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
