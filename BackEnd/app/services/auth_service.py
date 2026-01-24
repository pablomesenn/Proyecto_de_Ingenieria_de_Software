from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from app.config.database import get_db
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Servicio para autenticacion y manejo de tokens JWT"""
    
    def __init__(self):
        self._db = None
        
    @property
    def db(self):
        """Obtiene la conexion a DB de manera lazy"""
        if self._db is None:
            self._db = get_db()
        return self._db
    
    @property
    def users_collection(self):
        return self.db.users
    
    @property
    def revoked_tokens_collection(self):
        return self.db.revoked_tokens
        
    def login(self, email, password):
        """Autentica usuario y genera tokens (CU-001)"""
        from werkzeug.security import check_password_hash
        
        # Buscar usuario
        user = self.users_collection.find_one({'email': email})
        
        if not user:
            raise ValueError("Credenciales invalidas")
        
        # Verificar estado de cuenta
        if user.get('state') != 'activo':
            raise ValueError("Cuenta inactiva")
        
        # Verificar contraseña
        if not check_password_hash(user['password'], password):
            raise ValueError("Credenciales invalidas")
        
        # Generar tokens
        user_id = str(user['_id'])

        # Datos adicionales en el token
        additional_claims = {
            'email': user['email'],
            'role': user['role']
        }

        access_token = create_access_token(
            identity=user_id,
            fresh=True,
            additional_claims=additional_claims
        )

        refresh_token = create_refresh_token(
            identity=user_id,
            additional_claims=additional_claims
        )
        
        # Actualizar ultimo acceso
        self.users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {'last_login': datetime.utcnow()}}
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user.get('name'),
                'role': user['role']
            }
        }
    
    def refresh_token(self, current_user):
        """Refresca el access token usando el refresh token (CU-014)"""
        
        # current_user ahora es solo el user_id (string)
        user = self.users_collection.find_one({'_id': ObjectId(current_user)})
        
        if not user:
            raise ValueError("Usuario no encontrado")
        
        if user.get('state') != 'activo':
            raise ValueError("Cuenta inactiva")
        
        # Verificar que el refresh token no este revocado
        jti = get_jwt().get('jti')
        if self.is_token_revoked(jti):
            raise ValueError("Token revocado")
        
        # Generar nuevo access token
        user_id = str(user['_id'])
        additional_claims = {
            'email': user['email'],
            'role': user['role']
        }
        
        new_access_token = create_access_token(
            identity=user_id,
            fresh=False,
            additional_claims=additional_claims
        )
        
        new_refresh_token = create_refresh_token(
            identity=user_id,
            additional_claims=additional_claims
        )
        
        return {
            'access_token': new_access_token,
            'refresh_token': new_refresh_token
        }
    
    def logout(self, jti, token_type='access'):
        """Cierra sesion revocando el token (CU-013)"""
        
        # Calcular tiempo de expiracion del token
        if token_type == 'access':
            # Access token expira en 1 hora
            expires_at = datetime.utcnow() + timedelta(hours=1)
        else:
            # Refresh token expira en 30 dias
            expires_at = datetime.utcnow() + timedelta(days=30)
        
        # Guardar token revocado
        revoked_token = {
            'jti': jti,
            'token_type': token_type,
            'revoked_at': datetime.utcnow(),
            'expires_at': expires_at
        }
        
        self.revoked_tokens_collection.insert_one(revoked_token)
        
        logger.info(f"Token {jti} revocado exitosamente")
        
        return True
    
    def is_token_revoked(self, jti):
        """Verifica si un token ha sido revocado"""
        token = self.revoked_tokens_collection.find_one({'jti': jti})
        return token is not None
    
    def cleanup_expired_tokens(self):
        """Limpia tokens revocados que ya expiraron"""
        result = self.revoked_tokens_collection.delete_many({
            'expires_at': {'$lt': datetime.utcnow()}
        })
        
        logger.info(f"Limpieza de tokens: {result.deleted_count} tokens eliminados")
        
        return result.deleted_count
    
    def verify_token(self, token):
        """Verifica la validez de un token"""
        from flask_jwt_extended import decode_token
        
        try:
            decoded = decode_token(token)
            jti = decoded.get('jti')
            
            if self.is_token_revoked(jti):
                return {'valid': False, 'reason': 'Token revocado'}
            
            return {'valid': True, 'data': decoded}
            
        except Exception as e:
            return {'valid': False, 'reason': str(e)}