"""
Configuración de conexiones a bases de datos
Maneja MongoDB y Redis
"""
from flask import current_app
from mongoengine import connect, disconnect
import redis
from functools import wraps


# Instancia global de Redis (se inicializa en init_db)
redis_client = None


def init_mongodb(app):
    """
    Inicializa la conexión a MongoDB usando MongoEngine
    """
    try:
        connect(
            **app.config['MONGODB_SETTINGS'],
            alias='default'
        )
        app.logger.info("✓ Conexión a MongoDB establecida correctamente")
    except Exception as e:
        app.logger.error(f"✗ Error al conectar a MongoDB: {str(e)}")
        raise


def close_mongodb():
    """
    Cierra la conexión a MongoDB
    """
    try:
        disconnect(alias='default')
    except Exception as e:
        print(f"Error al desconectar MongoDB: {str(e)}")


def init_redis(app):
    """
    Inicializa la conexión a Redis
    """
    global redis_client
    
    try:
        redis_client = redis.Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            db=app.config['REDIS_DB'],
            password=app.config['REDIS_PASSWORD'],
            decode_responses=True,  # Para obtener strings en lugar de bytes
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        
        # Verificar conexión
        redis_client.ping()
        app.logger.info("✓ Conexión a Redis establecida correctamente")
        
    except redis.ConnectionError as e:
        app.logger.error(f"✗ Error al conectar a Redis: {str(e)}")
        redis_client = None
        # No lanzamos excepción para permitir que la app funcione sin caché


def get_redis():
    """
    Obtiene la instancia de Redis
    Retorna None si Redis no está disponible
    """
    return redis_client


def init_db(app):
    """
    Inicializa todas las conexiones de bases de datos
    """
    init_mongodb(app)
    init_redis(app)


def close_db():
    """
    Cierra todas las conexiones de bases de datos
    """
    close_mongodb()
    
    global redis_client
    if redis_client:
        try:
            redis_client.close()
        except Exception as e:
            print(f"Error al cerrar Redis: {str(e)}")


# Decorador para verificar disponibilidad de Redis
def require_redis(f):
    """
    Decorador que verifica que Redis esté disponible
    Si no lo está, ejecuta la función sin caché
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if redis_client is None:
            current_app.logger.warning(
                f"Redis no disponible para {f.__name__}, ejecutando sin caché"
            )
        return f(*args, **kwargs)
    return decorated_function


# Funciones helper para operaciones comunes con Redis
class RedisHelper:
    """
    Clase helper con métodos útiles para operaciones con Redis
    """
    
    @staticmethod
    def set_with_expiry(key, value, expiry=None):
        """
        Guarda un valor en Redis con tiempo de expiración
        """
        if not redis_client:
            return False
        
        try:
            if expiry:
                redis_client.setex(key, expiry, value)
            else:
                redis_client.set(key, value)
            return True
        except Exception as e:
            current_app.logger.error(f"Error al guardar en Redis: {str(e)}")
            return False
    
    @staticmethod
    def get(key):
        """
        Obtiene un valor de Redis
        """
        if not redis_client:
            return None
        
        try:
            return redis_client.get(key)
        except Exception as e:
            current_app.logger.error(f"Error al leer de Redis: {str(e)}")
            return None
    
    @staticmethod
    def delete(key):
        """
        Elimina una o varias claves de Redis
        """
        if not redis_client:
            return False
        
        try:
            redis_client.delete(key)
            return True
        except Exception as e:
            current_app.logger.error(f"Error al eliminar de Redis: {str(e)}")
            return False
    
    @staticmethod
    def delete_pattern(pattern):
        """
        Elimina todas las claves que coincidan con un patrón
        Útil para invalidar caché de categorías completas
        """
        if not redis_client:
            return False
        
        try:
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
            return True
        except Exception as e:
            current_app.logger.error(f"Error al eliminar patrón de Redis: {str(e)}")
            return False
    
    @staticmethod
    def exists(key):
        """
        Verifica si una clave existe en Redis
        """
        if not redis_client:
            return False
        
        try:
            return redis_client.exists(key) > 0
        except Exception as e:
            current_app.logger.error(f"Error al verificar existencia en Redis: {str(e)}")
            return False


def get_db():
    """
    Obtiene una conexión directa a MongoDB usando PyMongo
    Útil para scripts y operaciones que no usan MongoEngine
    """
    from pymongo import MongoClient
    from flask import current_app
    
    try:
        mongodb_settings = current_app.config['MONGODB_SETTINGS']
        client = MongoClient(mongodb_settings['host'])
        db_name = mongodb_settings.get('db', 'pisos_kermy_db')
        return client[db_name]
    except:
        # Fallback si no hay app context
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/pisos_kermy_db')
        client = MongoClient(mongodb_uri)
        
        # Obtener nombre de DB del .env
        db_name = os.getenv('MONGODB_DB', 'pisos_kermy_db')
        
        return client[db_name]