from flask_jwt_extended import get_jwt
from functools import wraps
from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def get_auth_service():
    """Obtiene instancia de AuthService de manera lazy"""
    from app.services.auth_service import AuthService
    return AuthService()


def token_required_and_not_revoked(fn):
    """
    Decorador adicional para verificar que el token no este revocado
    Se usa junto con @jwt_required()
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        jti = get_jwt()['jti']
        auth_service = get_auth_service()
        
        if auth_service.is_token_revoked(jti):
            return jsonify({'error': 'Token revocado'}), 401
        
        return fn(*args, **kwargs)
    
    return wrapper


def setup_jwt_callbacks(jwt):
    """
    Configura callbacks para JWT
    Se debe llamar despues de inicializar JWTManager
    """
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """Verifica si un token esta en la lista de revocados"""
        try:
            logger.info(f"Verificando token - JTI: {jwt_payload.get('jti')}")
            jti = jwt_payload['jti']
            auth_service = get_auth_service()
            result = auth_service.is_token_revoked(jti)
            logger.info(f"Token revocado? {result}")
            return result
        except Exception as e:
            logger.error(f"ERROR al verificar token: {str(e)}")
            logger.exception(e)
            return False
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Callback cuando el token expira"""
        return jsonify({
            'error': 'Token expirado',
            'message': 'El token ha expirado. Por favor, refresca tu sesion.'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Callback cuando el token es invalido"""
        logger.error(f"Token invalido: {error}")
        return jsonify({
            'error': 'Token invalido',
            'message': 'El token proporcionado es invalido.'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Callback cuando no se proporciona token"""
        logger.error(f"Token faltante: {error}")
        return jsonify({
            'error': 'Token requerido',
            'message': 'Se requiere autenticacion para acceder a este recurso.'
        }), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """Callback cuando el token esta revocado"""
        return jsonify({
            'error': 'Token revocado',
            'message': 'El token ha sido revocado. Por favor, inicia sesion nuevamente.'
        }), 401
    
    logger.info("JWT callbacks configurados")