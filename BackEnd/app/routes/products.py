from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.product_service import ProductService
from app.schemas.product_schema import (
    ProductSearchSchema,
    CreateProductSchema,
    UpdateProductSchema,
    UpdateProductStateSchema
)
from marshmallow import ValidationError
from app.constants.roles import UserRole
import logging

logger = logging.getLogger(__name__)

products_bp = Blueprint('products', __name__)
product_service = ProductService()


def require_role(required_role):
    """Decorador para verificar rol de usuario"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            jwt_data = get_jwt()
            user_role = jwt_data.get('role')

            if user_role != required_role and user_role != UserRole.ADMIN:
                return jsonify({'error': 'Permisos insuficientes'}), 403

            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


@products_bp.route('/search', methods=['GET'])
def search_catalog():
    """
    Búsqueda y filtrado de catálogo (CU-005)
    Disponible para todos (no requiere autenticación)
    """
    try:
        # Validar parámetros
        schema = ProductSearchSchema()
        params = schema.load(request.args)

        # Buscar productos
        products = product_service.search_and_filter_catalog(
            search_text=params.get('search_text'),
            categoria=params.get('categoria'),
            tags=params.get('tags'),
            disponibilidad=params.get('disponibilidad', True),
            skip=params.get('skip', 0),
            limit=params.get('limit', 20)
        )

        return jsonify({
            'products': products,
            'count': len(products)
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Parámetros inválidos', 'details': e.messages}), 400
    except Exception as e:
        logger.error(f"Error buscando productos: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@products_bp.route('/', methods=['GET'])
def get_products():
    """
    Lista todos los productos
    Disponible para todos (no requiere autenticación)
    """
    try:
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 20))

        products = product_service.search_and_filter_catalog(
            disponibilidad=None,
            skip=skip,
            limit=limit
        )

        return jsonify({
            'products': products,
            'count': len(products)
        }), 200

    except Exception as e:
        logger.error(f"Error obteniendo productos: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """
    Obtiene detalle de un producto con variantes y disponibilidad
    Disponible para todos (no requiere autenticación)
    """
    try:
        product = product_service.get_product_detail(product_id)
        return jsonify(product), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error obteniendo producto: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@products_bp.route('/', methods=['POST'])
@jwt_required()
@require_role(UserRole.ADMIN)
def create_product():
    """
    Crea un nuevo producto (ADMIN)
    """
    try:
        admin_id = get_jwt_identity()

        # Validar datos
        schema = CreateProductSchema()
        data = schema.load(request.get_json())

        # Crear producto
        product = product_service.create_product(data, admin_id)

        return jsonify({
            'message': 'Producto creado exitosamente',
            'product': product
        }), 201

    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando producto: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@products_bp.route('/<product_id>', methods=['PUT'])
@jwt_required()
@require_role(UserRole.ADMIN)
def update_product(product_id):
    """
    Actualiza un producto (ADMIN)
    """
    try:
        admin_id = get_jwt_identity()

        # Validar datos
        schema = UpdateProductSchema()
        data = schema.load(request.get_json())

        # Actualizar producto
        product = product_service.update_product(product_id, data, admin_id)

        return jsonify({
            'message': 'Producto actualizado exitosamente',
            'product': product
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error actualizando producto: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@products_bp.route('/<product_id>/state', methods=['PUT'])
@jwt_required()
@require_role(UserRole.ADMIN)
def update_product_state(product_id):
    """
    Actualiza el estado de un producto (ADMIN) (CU-018)
    """
    try:
        admin_id = get_jwt_identity()

        # Validar datos
        schema = UpdateProductStateSchema()
        data = schema.load(request.get_json())

        # Actualizar estado
        success = product_service.update_product_state(
            product_id,
            data['estado'],
            admin_id
        )

        if success:
            return jsonify({
                'message': 'Estado actualizado exitosamente'
            }), 200
        else:
            return jsonify({'error': 'No se pudo actualizar el estado'}), 400

    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error actualizando estado: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@products_bp.route('/<product_id>', methods=['DELETE'])
@jwt_required()
@require_role(UserRole.ADMIN)
def delete_product(product_id):
    """
    Elimina (desactiva) un producto (ADMIN)
    """
    try:
        admin_id = get_jwt_identity()

        # Desactivar producto
        success = product_service.delete_product(product_id, admin_id)

        if success:
            return jsonify({
                'message': 'Producto desactivado exitosamente'
            }), 200
        else:
            return jsonify({'error': 'No se pudo desactivar el producto'}), 400

    except Exception as e:
        logger.error(f"Error desactivando producto: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    Obtiene todas las categorías disponibles
    Disponible para todos
    """
    try:
        categories = product_service.get_categories()
        return jsonify({'categories': categories}), 200

    except Exception as e:
        logger.error(f"Error obteniendo categorías: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@products_bp.route('/tags', methods=['GET'])
def get_tags():
    """
    Obtiene todos los tags disponibles
    Disponible para todos
    """
    try:
        tags = product_service.get_tags()
        return jsonify({'tags': tags}), 200

    except Exception as e:
        logger.error(f"Error obteniendo tags: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
