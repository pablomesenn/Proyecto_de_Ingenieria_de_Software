"""
Configuración de conexiones a bases de datos
Maneja MongoDB y Redis con connection pooling apropiado
"""
from flask import current_app
from mongoengine import connect, disconnect
import redis
from functools import wraps
from pymongo import MongoClient


# ============================================================================
# INSTANCIAS GLOBALES - SE INICIALIZAN UNA SOLA VEZ
# ============================================================================
redis_client = None
mongo_client = None  # Cliente PyMongo compartido
mongo_db = None      # Database compartida


def init_mongodb(app):
    """
    Inicializa la conexión a MongoDB usando MongoEngine
    """
    try:
        connect(
            **app.config['MONGODB_SETTINGS'],
            alias='default'
        )
        app.logger.info("✓ Conexión a MongoDB (MongoEngine) establecida correctamente")
    except Exception as e:
        app.logger.error(f"✗ Error al conectar a MongoDB: {str(e)}")
        raise


def close_mongodb():
    """
    Cierra la conexión a MongoDB
    """
    global mongo_client

    try:
        disconnect(alias='default')

        # Cerrar cliente PyMongo si existe
        if mongo_client:
            mongo_client.close()
            mongo_client = None

    except Exception as e:
        print(f"Error al desconectar MongoDB: {str(e)}")


def init_pymongo(app):
    """
    Inicializa el cliente PyMongo compartido (para repositorios)
    IMPORTANTE: Este cliente se reutiliza en todas las peticiones
    """
    global mongo_client, mongo_db

    try:
        mongodb_settings = app.config['MONGODB_SETTINGS']

        # Crear cliente con pool de conexiones
        mongo_client = MongoClient(
            mongodb_settings['host'],
            maxPoolSize=50,        # Máximo de conexiones en el pool
            minPoolSize=10,        # Mínimo de conexiones mantenidas
            maxIdleTimeMS=45000,   # Tiempo antes de cerrar conexión inactiva
            waitQueueTimeoutMS=5000,  # Timeout para obtener conexión del pool
        )

        # Obtener database
        db_name = mongodb_settings.get('db', 'pisos_kermy_db')
        mongo_db = mongo_client[db_name]

        # Verificar conexión
        mongo_client.admin.command('ping')

        app.logger.info("✓ Cliente PyMongo inicializado correctamente con connection pooling")

    except Exception as e:
        app.logger.error(f"✗ Error al inicializar PyMongo: {str(e)}")
        raise


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
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            max_connections=50,  # Pool de conexiones
        )

        # Verificar conexión
        redis_client.ping()
        app.logger.info("✓ Conexión a Redis establecida correctamente")

    except redis.ConnectionError as e:
        app.logger.error(f"✗ Error al conectar a Redis: {str(e)}")
        redis_client = None


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
    init_pymongo(app)  # Nuevo: inicializar PyMongo con pooling
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


# ============================================================================
# FUNCIÓN PRINCIPAL: GET_DB - AHORA REUTILIZA LA CONEXIÓN EXISTENTE
# ============================================================================
def get_db():
    """
    Obtiene la database compartida de MongoDB

    IMPORTANTE: Esta función NO crea una nueva conexión.
    Reutiliza la conexión global inicializada en init_db().

    Returns:
        Database: Instancia de la database MongoDB
    """
    global mongo_db

    if mongo_db is None:
        # Fallback: si no hay conexión global, intentar inicializar
        # Esto solo debería ocurrir en contextos especiales (scripts, tests)
        import os
        from dotenv import load_dotenv
        load_dotenv()

        global mongo_client
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/pisos_kermy_db')
        db_name = os.getenv('MONGODB_DB', 'pisos_kermy_db')

        if mongo_client is None:
            mongo_client = MongoClient(
                mongodb_uri,
                maxPoolSize=50,
                minPoolSize=10,
            )

        mongo_db = mongo_client[db_name]

    return mongo_db


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
