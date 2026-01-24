"""
Rutas de Catálogo
Endpoints para búsqueda y filtrado de productos
Implementa CU-005: Buscar y filtrar catálogo
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.services.catalog_service import CatalogService
from app.middleware.error_handler import success_response, error_response
from app.config.config import Config

# Crear blueprint
catalog_bp = Blueprint('catalog', __name__, url_prefix='/api/catalog')

# Rate limiter (se configurará en __init__.py de la app)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=Config.RATELIMIT_STORAGE_URL
)


@catalog_bp.route('/products', methods=['GET'])
@limiter.limit(Config.RATE_LIMITS['search'])  # 120 búsquedas por minuto
def get_products():
    """
    GET /api/catalog/products

    Obtiene listado de productos con filtros opcionales
    Implementa RF-07: Búsqueda avanzada y filtros

    Query params:
    - texto: Búsqueda de texto (opcional)
    - categoria: Filtrar por categoría (opcional)
    - tags: Filtrar por tags, separados por coma (opcional)
    - disponible: true/false - solo productos disponibles (opcional)
    - page: Número de página (default: 1)
    - per_page: Elementos por página (default: 20, max: 100)

    Returns:
        200: Lista de productos con paginación
        400: Parámetros inválidos
    """
    try:
        # Parsear parámetros
        texto = request.args.get('texto', '').strip()
        categoria = request.args.get('categoria', '').strip()
        tags_str = request.args.get('tags', '').strip()
        disponible = request.args.get('disponible', '').lower() == 'true'

        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)

        # Construir filtros
        filters = {}

        if texto:
            filters['texto'] = texto

        if categoria:
            filters['categoria'] = categoria

        if tags_str:
            filters['tags'] = [t.strip() for t in tags_str.split(',') if t.strip()]

        if disponible:
            filters['disponible'] = True

        # Obtener productos
        result = CatalogService.get_products(
            filters=filters,
            page=page,
            per_page=per_page,
            include_availability=True
        )

        return success_response(result)

    except ValueError as e:
        return error_response(f"Parámetros inválidos: {str(e)}", 400)
    except Exception as e:
        return error_response(f"Error al obtener productos: {str(e)}", 500)


@catalog_bp.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """
    GET /api/catalog/products/<product_id>

    Obtiene detalle de un producto con disponibilidad

    Returns:
        200: Producto con variantes y disponibilidad
        404: Producto no encontrado
    """
    try:
        product = CatalogService.get_product_by_id(
            product_id,
            include_availability=True
        )

        return success_response(product)

    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response(f"Error al obtener producto: {str(e)}", 500)


@catalog_bp.route('/search', methods=['GET'])
@limiter.limit(Config.RATE_LIMITS['search'])
def search_products():
    """
    GET /api/catalog/search

    Búsqueda de productos con texto
    Wrapper más intuitivo sobre /products con filtro de texto

    Query params:
    - q: Texto de búsqueda (requerido)
    - categoria: Filtrar por categoría (opcional)
    - tags: Filtrar por tags (opcional)
    - disponible: Solo disponibles (opcional)
    - page: Página (default: 1)
    - per_page: Elementos por página (default: 20)

    Returns:
        200: Resultados de búsqueda
        400: Query vacío
    """
    try:
        query = request.args.get('q', '').strip()

        if not query:
            return error_response("Parámetro 'q' requerido", 400)

        categoria = request.args.get('categoria', '').strip()
        tags_str = request.args.get('tags', '').strip()
        disponible = request.args.get('disponible', '').lower() == 'true'

        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)

        # Construir filtros
        filters = {}

        if categoria:
            filters['categoria'] = categoria

        if tags_str:
            filters['tags'] = [t.strip() for t in tags_str.split(',') if t.strip()]

        if disponible:
            filters['disponible'] = True

        # Realizar búsqueda
        result = CatalogService.search_products(
            search_text=query,
            filters=filters,
            page=page,
            per_page=per_page
        )

        return success_response(result)

    except ValueError as e:
        return error_response(f"Parámetros inválidos: {str(e)}", 400)
    except Exception as e:
        return error_response(f"Error en búsqueda: {str(e)}", 500)


@catalog_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    GET /api/catalog/categories

    Obtiene todas las categorías disponibles
    Útil para filtros en el frontend

    Returns:
        200: Lista de categorías
    """
    try:
        categories = CatalogService.get_categories()
        return success_response({'categories': categories})
    except Exception as e:
        return error_response(f"Error al obtener categorías: {str(e)}", 500)


@catalog_bp.route('/tags', methods=['GET'])
def get_tags():
    """
    GET /api/catalog/tags

    Obtiene todos los tags disponibles
    Útil para filtros en el frontend

    Returns:
        200: Lista de tags
    """
    try:
        tags = CatalogService.get_tags()
        return success_response({'tags': tags})
    except Exception as e:
        return error_response(f"Error al obtener tags: {str(e)}", 500)
