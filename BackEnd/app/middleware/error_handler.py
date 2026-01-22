"""
Manejador centralizado de errores
Proporciona respuestas consistentes para todos los errores
"""
from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException
from mongoengine.errors import ValidationError, DoesNotExist, NotUniqueError
from jwt.exceptions import InvalidTokenError


class APIError(Exception):
    """Excepción base para errores de la API"""
    
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        """Convierte el error a diccionario para JSON"""
        rv = dict(self.payload or ())
        rv['error'] = True
        rv['message'] = self.message
        return rv


class ValidationError(APIError):
    """Error de validación de datos"""
    def __init__(self, message, errors=None):
        super().__init__(message, status_code=400)
        self.errors = errors
    
    def to_dict(self):
        rv = super().to_dict()
        if self.errors:
            rv['errors'] = self.errors
        return rv


class NotFoundError(APIError):
    """Error cuando un recurso no se encuentra"""
    def __init__(self, message="Recurso no encontrado"):
        super().__init__(message, status_code=404)


class UnauthorizedError(APIError):
    """Error de autenticación"""
    def __init__(self, message="No autorizado"):
        super().__init__(message, status_code=401)


class ForbiddenError(APIError):
    """Error de permisos"""
    def __init__(self, message="Acceso denegado"):
        super().__init__(message, status_code=403)


class ConflictError(APIError):
    """Error de conflicto (ej: sobre-reserva)"""
    def __init__(self, message="Conflicto en la operación"):
        super().__init__(message, status_code=409)


def register_error_handlers(app):
    """
    Registra los manejadores de errores en la aplicación
    """
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Maneja errores personalizados de la API"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        current_app.logger.error(f"API Error: {error.message}")
        return response
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Maneja excepciones HTTP de Werkzeug"""
        response = jsonify({
            'error': True,
            'message': error.description,
            'status_code': error.code
        })
        response.status_code = error.code
        return response
    
    @app.errorhandler(DoesNotExist)
    def handle_does_not_exist(error):
        """Maneja errores de MongoDB cuando no se encuentra un documento"""
        response = jsonify({
            'error': True,
            'message': 'Recurso no encontrado'
        })
        response.status_code = 404
        current_app.logger.warning(f"DoesNotExist: {str(error)}")
        return response
    
    @app.errorhandler(NotUniqueError)
    def handle_not_unique(error):
        """Maneja errores de duplicados en MongoDB"""
        response = jsonify({
            'error': True,
            'message': 'Ya existe un registro con estos datos',
            'details': str(error)
        })
        response.status_code = 409
        current_app.logger.warning(f"NotUniqueError: {str(error)}")
        return response
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Maneja errores de validación de MongoEngine"""
        response = jsonify({
            'error': True,
            'message': 'Error de validación',
            'details': str(error)
        })
        response.status_code = 400
        current_app.logger.warning(f"ValidationError: {str(error)}")
        return response
    
    @app.errorhandler(InvalidTokenError)
    def handle_invalid_token(error):
        """Maneja errores de tokens JWT inválidos"""
        response = jsonify({
            'error': True,
            'message': 'Token inválido o expirado'
        })
        response.status_code = 401
        current_app.logger.warning(f"InvalidTokenError: {str(error)}")
        return response
    
    @app.errorhandler(429)
    def handle_rate_limit(error):
        """Maneja errores de rate limiting"""
        response = jsonify({
            'error': True,
            'message': 'Demasiadas solicitudes. Por favor, intente más tarde.',
            'retry_after': error.description
        })
        response.status_code = 429
        return response
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Maneja errores internos del servidor"""
        current_app.logger.error(f"Internal Server Error: {str(error)}")
        response = jsonify({
            'error': True,
            'message': 'Error interno del servidor'
        })
        response.status_code = 500
        return response
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Maneja errores inesperados"""
        current_app.logger.critical(f"Unexpected Error: {str(error)}", exc_info=True)
        response = jsonify({
            'error': True,
            'message': 'Ha ocurrido un error inesperado'
        })
        response.status_code = 500
        return response


def success_response(data=None, message=None, status_code=200):
    """
    Función helper para crear respuestas exitosas consistentes
    
    Args:
        data: Datos a retornar
        message: Mensaje opcional
        status_code: Código de estado HTTP
    
    Returns:
        tuple: (response, status_code)
    """
    response = {
        'success': True
    }
    
    if message:
        response['message'] = message
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code


def error_response(message, status_code=400, errors=None):
    """
    Función helper para crear respuestas de error consistentes
    
    Args:
        message: Mensaje de error
        status_code: Código de estado HTTP
        errors: Detalles adicionales del error
    
    Returns:
        tuple: (response, status_code)
    """
    response = {
        'error': True,
        'message': message
    }
    
    if errors:
        response['errors'] = errors
    
    return jsonify(response), status_code