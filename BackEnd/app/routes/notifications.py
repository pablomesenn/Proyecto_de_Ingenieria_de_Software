from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)

notifications_bp = Blueprint('notifications', __name__)
notification_service = NotificationService()


@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    """
    Obtiene las notificaciones del usuario actual
    Query params:
        - unread_only: boolean (opcional, default=false)
        - limit: int (opcional, default=50)
        - skip: int (opcional, default=0)
    """
    try:
        user_id = get_jwt_identity()
        
        # Obtener parámetros de query
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        # Validar límites
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 50
        if skip < 0:
            skip = 0
        
        result = notification_service.get_user_notifications(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit,
            skip=skip
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        logger.error(f"Error en parámetros de query: {str(e)}")
        return jsonify({'error': 'Parámetros inválidos'}), 400
    except Exception as e:
        logger.error(f"Error obteniendo notificaciones: {str(e)}")
        return jsonify({'error': 'Error obteniendo notificaciones'}), 500


@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """
    Obtiene el conteo de notificaciones no leídas del usuario actual
    """
    try:
        user_id = get_jwt_identity()
        result = notification_service.get_unread_count(user_id)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error obteniendo conteo de no leídas: {str(e)}")
        return jsonify({'error': 'Error obteniendo conteo'}), 500


@notifications_bp.route('/<notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_as_read(notification_id):
    """
    Marca una notificación como leída
    """
    try:
        user_id = get_jwt_identity()
        
        success = notification_service.mark_as_read(notification_id, user_id)
        
        if success:
            return jsonify({'message': 'Notificación marcada como leída'}), 200
        else:
            return jsonify({'error': 'Notificación no encontrada o ya estaba leída'}), 404
            
    except Exception as e:
        logger.error(f"Error marcando notificación como leída: {str(e)}")
        return jsonify({'error': 'Error al marcar notificación'}), 500


@notifications_bp.route('/mark-all-read', methods=['PUT'])
@jwt_required()
def mark_all_as_read():
    """
    Marca todas las notificaciones del usuario como leídas
    """
    try:
        user_id = get_jwt_identity()
        result = notification_service.mark_all_as_read(user_id)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error marcando todas como leídas: {str(e)}")
        return jsonify({'error': 'Error al marcar notificaciones'}), 500


@notifications_bp.route('/<notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """
    Elimina una notificación
    """
    try:
        user_id = get_jwt_identity()
        
        success = notification_service.delete_notification(notification_id, user_id)
        
        if success:
            return jsonify({'message': 'Notificación eliminada'}), 200
        else:
            return jsonify({'error': 'Notificación no encontrada'}), 404
            
    except Exception as e:
        logger.error(f"Error eliminando notificación: {str(e)}")
        return jsonify({'error': 'Error al eliminar notificación'}), 500