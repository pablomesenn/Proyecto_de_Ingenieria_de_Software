from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.wishlist_service import WishlistService
from app.services.notification_service import NotificationService
from app.services.user_service import UserService
from app.schemas.wishlist_schema import (
    AddWishlistItemSchema,
    UpdateWishlistItemSchema,
    ConvertWishlistToReservationSchema
)
from marshmallow import ValidationError
from app.constants.roles import UserRole
import logging

logger = logging.getLogger(__name__)

wishlist_bp = Blueprint('wishlist', __name__)
wishlist_service = WishlistService()
notification_service = NotificationService()
user_service = UserService()


@wishlist_bp.route('/', methods=['GET'])
@jwt_required()
def get_wishlist():
    """
    Obtiene la wishlist del usuario actual (CU-006)
    Solo clientes pueden tener wishlist
    """
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        user_role = jwt_data.get('role')

        # Solo clientes tienen wishlist
        if user_role != UserRole.CLIENT:
            return jsonify({'error': 'Solo clientes pueden tener wishlist'}), 403

        wishlist = wishlist_service.get_wishlist(user_id)

        return jsonify(wishlist), 200

    except Exception as e:
        logger.error(f"Error obteniendo wishlist: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@wishlist_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_wishlist_summary():
    """
    Obtiene un resumen de la wishlist con totales
    """
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        user_role = jwt_data.get('role')

        if user_role != UserRole.CLIENT:
            return jsonify({'error': 'Solo clientes pueden tener wishlist'}), 403

        summary = wishlist_service.get_wishlist_summary(user_id)

        return jsonify(summary), 200

    except Exception as e:
        logger.error(f"Error obteniendo resumen: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@wishlist_bp.route('/items', methods=['POST'])
@jwt_required()
def add_item():
    """
    Agrega un item a la wishlist (CU-006)
    Consolida automáticamente si ya existe
    """
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        user_role = jwt_data.get('role')

        if user_role != UserRole.CLIENT:
            return jsonify({'error': 'Solo clientes pueden tener wishlist'}), 403

        # Validar datos
        schema = AddWishlistItemSchema()
        data = schema.load(request.get_json())

        # Agregar item
        wishlist = wishlist_service.add_item(
            user_id=user_id,
            variant_id=data['variant_id'],
            quantity=data.get('quantity', 1)
        )

        return jsonify({
            'message': 'Item agregado a la wishlist',
            'wishlist': wishlist
        }), 201

    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error agregando item: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@wishlist_bp.route('/items/<item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    """
    Actualiza la cantidad de un item en la wishlist (CU-006)
    """
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        user_role = jwt_data.get('role')

        if user_role != UserRole.CLIENT:
            return jsonify({'error': 'Solo clientes pueden tener wishlist'}), 403

        # Validar datos
        schema = UpdateWishlistItemSchema()
        data = schema.load(request.get_json())

        # Actualizar item
        wishlist = wishlist_service.update_item(
            user_id=user_id,
            item_id=item_id,
            quantity=data['quantity']
        )

        return jsonify({
            'message': 'Item actualizado',
            'wishlist': wishlist
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error actualizando item: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@wishlist_bp.route('/items/<item_id>', methods=['DELETE'])
@jwt_required()
def remove_item(item_id):
    """
    Elimina un item de la wishlist (CU-006)
    """
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        user_role = jwt_data.get('role')

        if user_role != UserRole.CLIENT:
            return jsonify({'error': 'Solo clientes pueden tener wishlist'}), 403

        # Eliminar item
        wishlist = wishlist_service.remove_item(user_id, item_id)

        return jsonify({
            'message': 'Item eliminado de la wishlist',
            'wishlist': wishlist
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error eliminando item: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@wishlist_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_wishlist():
    """
    Limpia toda la wishlist (CU-006)
    """
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        user_role = jwt_data.get('role')

        if user_role != UserRole.CLIENT:
            return jsonify({'error': 'Solo clientes pueden tener wishlist'}), 403

        # Limpiar wishlist
        result = wishlist_service.clear_wishlist(user_id)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error limpiando wishlist: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@wishlist_bp.route('/convert-to-reservation', methods=['POST'])
@jwt_required()
def convert_to_reservation():
    """
    Convierte items de la wishlist a reserva (CU-007)
    Valida disponibilidad y crea la reserva
    """
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        user_role = jwt_data.get('role')

        if user_role != UserRole.CLIENT:
            return jsonify({'error': 'Solo clientes pueden crear reservas'}), 403

        # Validar datos
        schema = ConvertWishlistToReservationSchema()
        data = schema.load(request.get_json())

        # Convertir a reserva
        reservation = wishlist_service.convert_to_reservation(
            user_id=user_id,
            items_to_reserve=data['items']
        )

        # Obtener usuario para notificación
        user = user_service.get_user_by_id(user_id)

        # Enviar notificación de nueva reserva
        notification_service.send_reservation_created(user, reservation)

        # Convertir a dict
        res_dict = reservation.to_dict()
        res_dict['_id'] = str(res_dict['_id'])
        res_dict['user_id'] = str(res_dict['user_id'])

        return jsonify({
            'message': 'Reserva creada exitosamente desde wishlist',
            'reservation': res_dict
        }), 201

    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error convirtiendo wishlist a reserva: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
