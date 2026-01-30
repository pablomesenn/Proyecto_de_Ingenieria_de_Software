from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.user_service import UserService
from app.schemas.user_schema import (
    UpdateProfileSchema,
    CreateUserSchema,
    UpdateUserSchema,
    UserListQuerySchema,
    ChangePasswordSchema
)
from marshmallow import ValidationError
from app.constants.roles import UserRole
import logging

logger = logging.getLogger(__name__)

users_bp = Blueprint('users', __name__)
user_service = UserService()


def require_role(required_role):
    """Decorador para verificar rol de usuario"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            jwt_data = get_jwt()
            user_role = jwt_data.get('role')
            
            if user_role != required_role:
                return jsonify({'error': 'Permisos insuficientes'}), 403
            
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Obtiene el perfil del usuario actual
    Disponible para CLIENT y ADMIN
    """
    try:
        user_id = get_jwt_identity()
        
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify(user), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo perfil: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Actualiza el perfil del usuario actual (CU-015)
    Solo puede editar su propio perfil
    """
    try:
        user_id = get_jwt_identity()
        
        # Validar datos
        schema = UpdateProfileSchema()
        data = schema.load(request.get_json())
        
        # Actualizar perfil
        updated_user = user_service.update_profile(user_id, data)
        
        return jsonify({
            'message': 'Perfil actualizado exitosamente',
            'user': updated_user
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error actualizando perfil: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@users_bp.route('/change-password', methods=['POST', 'OPTIONS'])
@jwt_required(optional=True)
def change_password():
    """
    Cambia la contraseña del usuario actual
    Requiere: contraseña actual, nueva contraseña y confirmación
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    # Verificar autenticación para POST
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({'error': 'Token requerido'}), 401
    
    try:
        # Validar datos
        schema = ChangePasswordSchema()
        data = schema.load(request.get_json())
        
        # Validar que las contraseñas coincidan
        if data['new_password'] != data['confirm_password']:
            return jsonify({'error': 'Las contraseñas no coinciden'}), 400
        
        # Cambiar contraseña
        user_service.change_password(
            user_id=user_id,
            current_password=data['current_password'],
            new_password=data['new_password']
        )
        
        return jsonify({
            'message': 'Contraseña actualizada exitosamente'
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error cambiando contraseña: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@users_bp.route('/', methods=['GET'])
@jwt_required()
@require_role(UserRole.ADMIN)
def get_users():
    """
    Lista todos los usuarios (ADMIN)
    """
    try:
        # Validar parametros
        schema = UserListQuerySchema()
        params = schema.load(request.args)
        
        users = user_service.get_all_users(
            skip=params.get('skip', 0),
            limit=params.get('limit', 100)
        )
        
        return jsonify({
            'users': users,
            'count': len(users)
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Parametros invalidos', 'details': e.messages}), 400
    except Exception as e:
        logger.error(f"Error obteniendo usuarios: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Obtiene un usuario por ID
    ADMIN: puede ver cualquier usuario
    CLIENT: solo puede ver su propio perfil
    """
    try:
        current_user_id = get_jwt_identity()
        jwt_data = get_jwt()
        user_role = jwt_data.get('role')
        
        # Verificar permisos
        if user_role != UserRole.ADMIN and user_id != current_user_id:
            return jsonify({'error': 'No tienes permiso para ver este usuario'}), 403
        
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify(user), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo usuario: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@users_bp.route('/', methods=['POST'])
@jwt_required()
@require_role(UserRole.ADMIN)
def create_user():
    """
    Crea un nuevo usuario (ADMIN)
    """
    try:
        # Validar datos
        schema = CreateUserSchema()
        data = schema.load(request.get_json())
        
        # Crear usuario
        new_user = user_service.create_user(data)
        
        return jsonify({
            'message': 'Usuario creado exitosamente',
            'user': new_user
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando usuario: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@users_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
@require_role(UserRole.ADMIN)
def update_user(user_id):
    """
    Actualiza un usuario (ADMIN)
    """
    try:
        admin_id = get_jwt_identity()
        
        # Validar datos
        schema = UpdateUserSchema()
        data = schema.load(request.get_json())
        
        # Actualizar usuario
        updated_user = user_service.update_user(user_id, data, admin_id)
        
        return jsonify({
            'message': 'Usuario actualizado exitosamente',
            'user': updated_user
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error actualizando usuario: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@users_bp.route('/<user_id>', methods=['DELETE'])
@jwt_required()
@require_role(UserRole.ADMIN)
def delete_user(user_id):
    """
    Desactiva un usuario (ADMIN)
    No elimina realmente, solo cambia el estado a inactivo
    """
    try:
        admin_id = get_jwt_identity()
        
        # Desactivar usuario
        user_service.delete_user(user_id, admin_id)
        
        return jsonify({
            'message': 'Usuario desactivado exitosamente'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error desactivando usuario: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500