from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.reservation_service import ReservationService
from app.services.notification_service import NotificationService
from app.services.user_service import UserService
from app.schemas.reservation_schema import (
    CreateReservationSchema,
    UpdateReservationStateSchema,
    ReservationFilterSchema
)
from marshmallow import ValidationError
from app.constants.roles import UserRole
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

reservations_bp = Blueprint('reservations', __name__)
reservation_service = ReservationService()
notification_service = NotificationService()
user_service = UserService()


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


@reservations_bp.route('/', methods=['POST'])
@jwt_required()
def create_reservation():
    """
    Crea una nueva reserva (CU-007 - Cliente)
    Solo clientes pueden crear reservas
    """
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        user_role = jwt_data.get('role')

        # Solo clientes pueden crear reservas
        if user_role != UserRole.CLIENT:
            return jsonify({'error': 'Solo clientes pueden crear reservas'}), 403

        # Validar datos
        schema = CreateReservationSchema()
        data = schema.load(request.get_json())

        # Crear reserva
        reservation = reservation_service.create_reservation(
            user_id=user_id,
            items=data['items'],
            notes=data.get('notes')
        )

        # Obtener usuario para notificacion
        user = user_service.get_user_by_id(user_id)

        # Enviar notificacion de nueva reserva
        notification_service.send_reservation_created(user, reservation)

        res_dict = reservation.to_dict()
        res_dict['_id'] = str(res_dict['_id'])
        res_dict['user_id'] = str(res_dict['user_id'])

        return jsonify({
            'message': 'Reserva creada exitosamente',
            'reservation': res_dict
        }), 201

    except ValidationError as e:
        return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando reserva: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@reservations_bp.route('/', methods=['GET'])
@jwt_required()
def get_reservations():
    """
    Obtiene reservas
    - CLIENT: solo sus propias reservas
    - ADMIN: todas las reservas con filtros
    """
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        user_role = jwt_data.get('role')

        # Validar parametros de query
        schema = ReservationFilterSchema()
        filters = schema.load(request.args)

        if user_role == UserRole.CLIENT:
            # Cliente solo ve sus propias reservas
            reservations = reservation_service.get_reservations_by_user(
                user_id=user_id,
                state=filters.get('state'),
                skip=filters.get('skip', 0),
                limit=filters.get('limit', 20)
            )
        else:
            # Admin ve todas las reservas
            query_filters = {}
            if filters.get('state'):
                query_filters['state'] = filters['state']
            if filters.get('user_id'):
                query_filters['user_id'] = ObjectId(filters['user_id'])

            reservations = reservation_service.get_all_reservations(
                filters=query_filters,
                skip=filters.get('skip', 0),
                limit=filters.get('limit', 20)
            )

        # Convertir a dict
        result = []
        for res in reservations:
            res_dict = res.to_dict()
            res_dict['_id'] = str(res_dict['_id'])
            res_dict['user_id'] = str(res_dict['user_id'])
            result.append(res_dict)

        return jsonify({
            'reservations': result,
            'count': len(result)
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
    except Exception as e:
        logger.error(f"Error obteniendo reservas: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@reservations_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_reservations():
    """
    Obtiene las reservas del usuario autenticado
    Endpoint dedicado para clientes - DEBE IR ANTES de /<reservation_id>
    """
    try:
        user_id = get_jwt_identity()

        # Validar parametros de query
        schema = ReservationFilterSchema()
        filters = schema.load(request.args)

        # Obtener reservas del usuario
        reservations = reservation_service.get_reservations_by_user(
            user_id=user_id,
            state=filters.get('state'),
            skip=filters.get('skip', 0),
            limit=filters.get('limit', 20)
        )

        # Convertir a dict
        result = []
        for res in reservations:
            res_dict = res.to_dict()
            res_dict['_id'] = str(res_dict['_id'])
            res_dict['user_id'] = str(res_dict['user_id'])
            result.append(res_dict)

        return jsonify({
            'reservations': result,
            'count': len(result)
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
    except Exception as e:
        logger.error(f"Error obteniendo reservas del usuario: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@reservations_bp.route('/<reservation_id>', methods=['GET'])
@jwt_required()
def get_reservation(reservation_id):
    """Obtiene una reserva por ID"""
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        user_role = jwt_data.get('role')

        reservation = reservation_service.get_reservation_by_id(reservation_id)

        if not reservation:
            return jsonify({'error': 'Reserva no encontrada'}), 404

        # Verificar permisos
        if user_role == UserRole.CLIENT and str(reservation.user_id) != user_id:
            return jsonify({'error': 'No tienes permiso para ver esta reserva'}), 403

        res_dict = reservation.to_dict()
        res_dict['_id'] = str(res_dict['_id'])
        res_dict['user_id'] = str(res_dict['user_id'])

        return jsonify(res_dict), 200

    except Exception as e:
        logger.error(f"Error obteniendo reserva: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@reservations_bp.route('/<reservation_id>/approve', methods=['PUT'])
@jwt_required()
@require_role(UserRole.ADMIN)
def approve_reservation(reservation_id):
    """Aprueba una reserva (CU-010 - ADMIN)"""
    try:
        admin_id = get_jwt_identity()

        # Validar datos
        schema = UpdateReservationStateSchema()
        data = schema.load(request.get_json() or {})

        # Aprobar reserva
        reservation = reservation_service.approve_reservation(
            reservation_id=reservation_id,
            admin_id=admin_id,
            admin_notes=data.get('admin_notes')
        )

        # Obtener usuario para notificacion
        user = user_service.get_user_by_id(str(reservation.user_id))

        # Enviar notificacion
        notification_service.send_reservation_approved(user, reservation)

        res_dict = reservation.to_dict()
        res_dict['_id'] = str(res_dict['_id'])
        res_dict['user_id'] = str(res_dict['user_id'])

        return jsonify({
            'message': 'Reserva aprobada exitosamente',
            'reservation': res_dict
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error aprobando reserva: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@reservations_bp.route('/<reservation_id>/reject', methods=['PUT'])
@jwt_required()
@require_role(UserRole.ADMIN)
def reject_reservation(reservation_id):
    """Rechaza una reserva (CU-010 - ADMIN)"""
    try:
        admin_id = get_jwt_identity()

        # Validar datos
        schema = UpdateReservationStateSchema()
        data = schema.load(request.get_json() or {})

        # Rechazar reserva
        reservation = reservation_service.reject_reservation(
            reservation_id=reservation_id,
            admin_id=admin_id,
            admin_notes=data.get('admin_notes')
        )

        # Obtener usuario para notificacion
        user = user_service.get_user_by_id(str(reservation.user_id))

        # Enviar notificacion
        notification_service.send_reservation_rejected(user, reservation)

        res_dict = reservation.to_dict()
        res_dict['_id'] = str(res_dict['_id'])
        res_dict['user_id'] = str(res_dict['user_id'])

        return jsonify({
            'message': 'Reserva rechazada exitosamente',
            'reservation': res_dict
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error rechazando reserva: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@reservations_bp.route('/<reservation_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_reservation(reservation_id):
    """
    Cancela una reserva (CU-009 para CLIENT, CU-010 para ADMIN)
    CLIENT: solo puede cancelar sus propias reservas
    ADMIN: puede cancelar cualquier reserva (cancelacion forzada)
    """
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        user_role = jwt_data.get('role')

        is_forced = user_role == UserRole.ADMIN

        # Cancelar reserva
        if is_forced:
            reservation = reservation_service.cancel_reservation(
                reservation_id=reservation_id,
                admin_id=user_id,
                is_forced=True
            )
        else:
            reservation = reservation_service.cancel_reservation(
                reservation_id=reservation_id,
                user_id=user_id,
                is_forced=False
            )

        # Obtener usuario para notificacion
        user = user_service.get_user_by_id(str(reservation.user_id))

        # Enviar notificacion
        notification_service.send_reservation_cancelled(user, reservation)

        res_dict = reservation.to_dict()
        res_dict['_id'] = str(res_dict['_id'])
        res_dict['user_id'] = str(res_dict['user_id'])

        return jsonify({
            'message': 'Reserva cancelada exitosamente',
            'reservation': res_dict
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error cancelando reserva: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
