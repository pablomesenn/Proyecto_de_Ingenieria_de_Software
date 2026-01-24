"""
Servicio de Catálogo
Implementa la lógica de negocio para búsqueda y filtrado de productos
Caso de Uso CU-005: Buscar y filtrar catálogo
"""

from app.models.product import Product
from app.models.inventory import Inventory
from app.constants.states import ProductState
from app.config.database import RedisHelper
from flask import current_app
import json


class CatalogService:
    """
    Servicio para gestión del catálogo de productos
    Implementa RF-07: Búsqueda avanzada y filtros
    """

    CACHE_KEY_PREFIX = 'catalog:'
    CACHE_TIMEOUT = 600  # 10 minutos

    @staticmethod
    def get_products(filters=None, page=1, per_page=20, include_availability=True):
        """
        Obtiene productos con filtros y paginación

        Args:
            filters: Diccionario con filtros opcionales:
                - texto: búsqueda de texto en nombre/descripción
                - categoria: filtrar por categoría
                - tags: filtrar por tags (lista)
                - disponible: solo productos con disponibilidad > 0
                - estado: filtrar por estado (default: solo activos para clientes)
            page: Página actual
            per_page: Elementos por página
            include_availability: Si incluir cálculo de disponibilidad

        Returns:
            dict: {
                'products': [...],
                'total': int,
                'page': int,
                'per_page': int,
                'total_pages': int
            }
        """
        filters = filters or {}

        # Construir query de MongoDB
        query = {}

        # Por defecto, solo mostrar productos activos (reglas de visibilidad RF-24)
        estado_filter = filters.get('estado')
        if estado_filter:
            query['estado'] = estado_filter
        else:
            query['estado__in'] = ProductState.visible_states()

        # Filtro por categoría
        if filters.get('categoria'):
            query['categoria'] = filters['categoria']

        # Filtro por tags
        if filters.get('tags'):
            tags = filters['tags'] if isinstance(filters['tags'], list) else [filters['tags']]
            query['tags__in'] = tags

        # Búsqueda de texto (RF-07)
        texto = filters.get('texto')
        if texto:
            query['$or'] = [
                {'nombre__icontains': texto},
                {'descripcion_embalaje__icontains': texto}
            ]

        # Ejecutar query con paginación
        total = Product.objects(**query).count()
        skip = (page - 1) * per_page

        products = Product.objects(**query).skip(skip).limit(per_page).order_by('-creado_en')

        # Convertir a diccionarios
        products_data = []
        for product in products:
            product_dict = product.to_dict()

            # Agregar disponibilidad por variante si se solicita (RF-12)
            if include_availability:
                product_dict['variantes_disponibilidad'] = (
                    CatalogService._get_product_availability(product)
                )

            products_data.append(product_dict)

        # Si se filtró por disponibilidad, filtrar productos sin stock
        if filters.get('disponible') and include_availability:
            products_data = [
                p for p in products_data
                if any(v['disponibilidad'] > 0 for v in p.get('variantes_disponibilidad', []))
            ]
            total = len(products_data)

        total_pages = (total + per_page - 1) // per_page

        return {
            'products': products_data,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }

    @staticmethod
    def get_product_by_id(product_id, include_availability=True):
        """
        Obtiene un producto por ID con disponibilidad

        Args:
            product_id: ID del producto
            include_availability: Si incluir disponibilidad

        Returns:
            dict: Producto con disponibilidad por variante
        """
        product = Product.objects.get(id=product_id)

        # Verificar visibilidad
        if not product.is_visible():
            raise ValueError("Producto no disponible")

        product_dict = product.to_dict()

        if include_availability:
            product_dict['variantes_disponibilidad'] = (
                CatalogService._get_product_availability(product)
            )

        return product_dict

    @staticmethod
    def _get_product_availability(product):
        """
        Calcula disponibilidad para todas las variantes de un producto
        Implementa cálculo: disponible = stock_total - stock_retenido

        Args:
            product: Instancia de Product

        Returns:
            list: Lista de disponibilidad por variante
        """
        availability = []

        for i, variante in enumerate(product.variantes):
            try:
                # Buscar inventario para esta variante
                inventory = Inventory.objects.get(
                    producto_id=product.id,
                    variante_index=i
                )

                availability.append({
                    'variante_index': i,
                    'tamano_pieza': variante.tamano_pieza,
                    'unidad': variante.unidad,
                    'stock_total': inventory.stock_total,
                    'stock_retenido': inventory.stock_retenido,
                    'disponibilidad': inventory.get_disponibilidad()
                })
            except Inventory.DoesNotExist:
                # Si no hay registro de inventario, asumimos 0
                availability.append({
                    'variante_index': i,
                    'tamano_pieza': variante.tamano_pieza,
                    'unidad': variante.unidad,
                    'stock_total': 0,
                    'stock_retenido': 0,
                    'disponibilidad': 0
                })

        return availability

    @staticmethod
    def search_products(search_text, filters=None, page=1, per_page=20):
        """
        Búsqueda de productos con texto
        Wrapper sobre get_products para búsqueda específica

        Args:
            search_text: Texto a buscar
            filters: Filtros adicionales
            page: Página
            per_page: Elementos por página

        Returns:
            dict: Resultados de búsqueda
        """
        filters = filters or {}
        filters['texto'] = search_text

        return CatalogService.get_products(
            filters=filters,
            page=page,
            per_page=per_page,
            include_availability=True
        )

    @staticmethod
    def get_categories():
        """
        Obtiene todas las categorías únicas del catálogo

        Returns:
            list: Lista de categorías
        """
        categories = Product.objects(
            estado__in=ProductState.visible_states()
        ).distinct('categoria')
        return sorted(categories)

    @staticmethod
    def get_tags():
        """
        Obtiene todos los tags únicos del catálogo

        Returns:
            list: Lista de tags
        """
        # MongoDB no tiene distinct para arrays, hay que hacerlo manualmente
        all_tags = set()
        products = Product.objects(
            estado__in=ProductState.visible_states()
        ).only('tags')

        for product in products:
            all_tags.update(product.tags)

        return sorted(list(all_tags))

    @staticmethod
    def invalidate_cache():
        """
        Invalida el caché del catálogo
        Se debe llamar cuando se modifica productos o inventario
        """
        RedisHelper.delete_pattern(f'{CatalogService.CACHE_KEY_PREFIX}*')
        current_app.logger.info("Caché de catálogo invalidado")
