"""
Rutas de Wishlist
Endpoints para gestión de wishlist y conversión a reserva
Implementa CU-006: Gestionar wishlist
Implementa CU-007: Mover de wishlist a reserva
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.services.wishlist_service import WishlistService
from app.services.reservation_service import ReservationService
from app.middleware.error_handler import success_response, error_response
from app.config.config import Config

# Crear blueprint
wishlist_bp = Blueprint('wishlist', __name__, url_prefix='/api/wishlist')

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=Config.RATELIMIT_STORAGE_URL
)


@wishlist_bp.route('/', methods=['GET'])
@jwt_required()
def get_wishlist():
    """
    GET /api/wishlist

    Obtiene la wishlist del usuario actual con disponibilidad
    Implementa RF-12: Wishlist con disponibilidad en tiempo real

    Returns:
        200: Wishlist con ítems y disponibilidad
    """
    try:
        user_id = get_jwt_identity()

        wishlist = WishlistService.get_wishlist(
            user_id,
            include_availability=True
        )

        return success_response(wishlist)

    except Exception as e:
        return error_response(f"Error al obtener wishlist: {str(e)}", 500)


@wishlist_bp.route('/items', methods=['POST'])
@jwt_required()
@limiter.limit(Config.RATE_LIMITS['wishlist_actions'])  # 60 acciones por minuto
def add_item():
    """
    POST /api/wishlist/items

    Agrega un ítem a la wishlist
    Implementa RF-10: Gestión de wishlist
    Implementa RF-11: Consolidación automática de duplicados

    Body:
    {
        "producto_id": "string",
        "variante_index": int,
        "cantidad": int (opcional, default: 1)
    }

    Returns:
        200: Ítem agregado/consolidado
        400: Datos inválidos
        404: Producto no encontrado
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Validar datos requeridos
        if not data or 'producto_id' not in data or 'variante_index' not in data:
            return error_response(
                "Se requieren producto_id y variante_index",
                400
            )

        producto_id = data['producto_id']
        variante_index = int(data['variante_index'])
        cantidad = int(data.get('cantidad', 1))

        result = WishlistService.add_item(
            user_id,
            producto_id,
            variante_index,
            cantidad
        )

        return success_response(result, result['message'])

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Error al agregar ítem: {str(e)}", 500)


@wishlist_bp.route('/items', methods=['PUT'])
@jwt_required()
@limiter.limit(Config.RATE_LIMITS['wishlist_actions'])
def update_item():
    """
    PUT /api/wishlist/items

    Actualiza la cantidad de un ítem en la wishlist
    Si la cantidad es 0, elimina el ítem

    Body:
    {
        "producto_id": "string",
        "variante_index": int,
        "cantidad": int
    }

    Returns:
        200: Cantidad actualizada
        400: Datos inválidos
        404: Ítem no encontrado
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or 'producto_id' not in data or 'variante_index' not in data:
            return error_response(
                "Se requieren producto_id y variante_index",
                400
            )

        producto_id = data['producto_id']
        variante_index = int(data['variante_index'])
        cantidad = int(data.get('cantidad', 0))

        result = WishlistService.update_item(
            user_id,
            producto_id,
            variante_index,
            cantidad
        )

        return success_response(result, result['message'])

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Error al actualizar ítem: {str(e)}", 500)


@wishlist_bp.route('/items', methods=['DELETE'])
@jwt_required()
@limiter.limit(Config.RATE_LIMITS['wishlist_actions'])
def remove_item():
    """
    DELETE /api/wishlist/items

    Elimina un ítem de la wishlist

    Query params o Body:
    - producto_id: ID del producto
    - variante_index: Índice de la variante

    Returns:
        200: Ítem eliminado
        400: Datos inválidos
        404: Ítem no encontrado
    """
    try:
        user_id = get_jwt_identity()

        # Aceptar datos por query params o body
        if request.is_json:
            data = request.get_json()
        else:
            data = {
                'producto_id': request.args.get('producto_id'),
                'variante_index': request.args.get('variante_index')
            }

        if not data or 'producto_id' not in data or 'variante_index' not in data:
            return error_response(
                "Se requieren producto_id y variante_index",
                400
            )

        producto_id = data['producto_id']
        variante_index = int(data['variante_index'])

        result = WishlistService.remove_item(
            user_id,
            producto_id,
            variante_index
        )

        return success_response(result, result['message'])

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Error al eliminar ítem: {str(e)}", 500)


@wishlist_bp.route('/clear', methods=['POST'])
@jwt_required()
def clear_wishlist():
    """
    POST /api/wishlist/clear

    Vacía completamente la wishlist

    Returns:
        200: Wishlist vaciada
    """
    try:
        user_id = get_jwt_identity()

        result = WishlistService.clear_wishlist(user_id)

        return success_response(result, result['message'])

    except Exception as e:
        return error_response(f"Error al vaciar wishlist: {str(e)}", 500)


@wishlist_bp.route('/validate', methods=['GET'])
@jwt_required()
def validate_wishlist():
    """
    GET /api/wishlist/validate

    Valida que la wishlist pueda convertirse a reserva
    Útil para mostrar al usuario qué ítems tienen problemas antes de reservar
    Implementa RF-13: Validación previa a reserva

    Returns:
        200: Resultado de validación
    """
    try:
        user_id = get_jwt_identity()

        validation = WishlistService.validate_for_reservation(user_id)

        return success_response(validation)

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Error al validar wishlist: {str(e)}", 500)


@wishlist_bp.route('/convert-to-reservation', methods=['POST'])
@jwt_required()
def convert_to_reservation():
    """
    POST /api/wishlist/convert-to-reservation

    Convierte la wishlist a una reserva
    Implementa CU-007: Mover de wishlist a reserva
    Implementa RF-13: Conversión con validación de cantidades

    Body (opcional):
    {
        "item_quantities": {
            "producto_id": {
                variante_index: cantidad
            }
        }
    }

    Si no se especifican cantidades, usa las de la wishlist

    Returns:
        200: Reserva creada
        400: Validación fallida
        409: Conflicto de disponibilidad
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}

        item_quantities = data.get('item_quantities')

        reservation = ReservationService.create_from_wishlist(
            user_id,
            item_quantities
        )

        return success_response(
            reservation,
            "Reserva creada exitosamente. Válida por 24 horas.",
            201
        )

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        if 'disponibilidad' in str(e).lower() or 'conflicto' in str(e).lower():
            return error_response(str(e), 409)
        return error_response(f"Error al crear reserva: {str(e)}", 500)
