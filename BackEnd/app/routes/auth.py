from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required, 
    get_jwt_identity, 
    get_jwt,
    create_access_token,
    create_refresh_token
)
from app.services.auth_service import AuthService
from app.schemas.auth_schema import LoginSchema
from marshmallow import ValidationError
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Inicio de sesion (CU-001)
    Genera access token y refresh token
    """
    try:
        # Validar datos
        schema = LoginSchema()
        data = schema.load(request.get_json())
        
        # Autenticar
        result = auth_service.login(
            email=data['email'],
            password=data['password']
        )
        
        return jsonify(result), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresca el access token (CU-014)
    Requiere un refresh token valido
    """
    try:
        current_user = get_jwt_identity()
        
        # Refrescar token
        result = auth_service.refresh_token(current_user)
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        logger.error(f"Error en refresh: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Cierra sesion (CU-013)
    Revoca el access token actual
    """
    try:
        jti = get_jwt()['jti']
        token_type = get_jwt()['type']
        
        # Revocar token
        auth_service.logout(jti, token_type)
        
        return jsonify({'message': 'Sesion cerrada exitosamente'}), 200
        
    except Exception as e:
        logger.error(f"Error en logout: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@auth_bp.route('/logout-all', methods=['POST'])
@jwt_required()
def logout_all():
    """
    Cierra todas las sesiones
    Revoca tanto access token como refresh token si estan disponibles
    """
    try:
        # Revocar access token
        access_jti = get_jwt()['jti']
        auth_service.logout(access_jti, 'access')
        
        # Si se proporciono refresh token, tambien revocarlo
        refresh_token_header = request.headers.get('X-Refresh-Token')
        if refresh_token_header:
            from flask_jwt_extended import decode_token
            try:
                decoded = decode_token(refresh_token_header)
                refresh_jti = decoded['jti']
                auth_service.logout(refresh_jti, 'refresh')
            except Exception as e:
                logger.warning(f"No se pudo revocar refresh token: {str(e)}")
        
        return jsonify({'message': 'Todas las sesiones cerradas exitosamente'}), 200
        
    except Exception as e:
        logger.error(f"Error en logout-all: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@auth_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    """
    Verifica que el token actual sea valido
    Util para el frontend para verificar estado de sesion
    """
    try:
        current_user = get_jwt_identity()
        jti = get_jwt()['jti']
        
        # Verificar si el token esta revocado
        if auth_service.is_token_revoked(jti):
            return jsonify({'valid': False, 'reason': 'Token revocado'}), 401
        
        return jsonify({
            'valid': True,
            'user': current_user
        }), 200
        
    except Exception as e:
        logger.error(f"Error verificando token: {str(e)}")
        return jsonify({'valid': False, 'reason': 'Error verificando token'}), 500