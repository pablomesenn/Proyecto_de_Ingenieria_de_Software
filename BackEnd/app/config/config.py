"""
Configuración central del sistema
Maneja todas las variables de entorno y configuraciones necesarias
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración base"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # MongoDB
    MONGODB_SETTINGS = {
        'host': os.getenv('MONGODB_URI', 'mongodb://localhost:27017/pisos_kermy_db'),
        'db': os.getenv('MONGODB_DB', 'pisos_kermy_db'),
        'connect': False,  # Para evitar problemas con threading
    }
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)) #3600 para una hora
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
    )
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:8080,http://localhost:3000,http://localhost:5173',).split(',')
    CORS_SUPPORTS_CREDENTIALS = True
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv('RATE_LIMIT_STORAGE_URL', 'redis://localhost:6379/1')
    RATELIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_STRATEGY = 'fixed-window'
    
    # Rate Limits específicos (según RNF del ERS)
    RATE_LIMITS = {
        'login': '5 per 15 minutes',  # 5 intentos por 15 min
        'create_reservation': '10 per hour',  # 10 reservas por hora
        'wishlist_actions': '60 per minute',  # 60 acciones por minuto
        'search': '120 per minute',  # 120 búsquedas por minuto por IP
    }
    
    # Email (SMTP Gmail)
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'True').lower() == 'true'
    SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', '')
    SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'Pisos Kermy Jacó')
    
    # Cache
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    CACHE_PRODUCT_TIMEOUT = int(os.getenv('CACHE_PRODUCT_TIMEOUT', 600))
    
    # Reservations
    RESERVATION_HOLD_HOURS = int(os.getenv('RESERVATION_HOLD_HOURS', 24))
    RESERVATION_EXPIRY_CHECK_INTERVAL = int(
        os.getenv('RESERVATION_EXPIRY_CHECK_INTERVAL', 300)
    )
    
    # Notifications
    NOTIFICATION_SAME_DAY_EXPIRY_HOUR = int(
        os.getenv('NOTIFICATION_SAME_DAY_EXPIRY_HOUR', 9)
    )
    
    # File Upload
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = set(
        os.getenv('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif').split(',')
    )
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # Pagination
    DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', 20))
    MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', 100))
    
    # Security
    PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', 10))
    PASSWORD_REQUIRE_SPECIAL_CHAR = (
        os.getenv('PASSWORD_REQUIRE_SPECIAL_CHAR', 'True').lower() == 'true'
    )


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    DEBUG = True
    
    # Usar bases de datos de prueba
    MONGODB_SETTINGS = {
        'host': 'mongodb://localhost:27017/pisos_kermy_test_db',
        'db': 'pisos_kermy_test_db',
    }
    REDIS_DB = 1  # Usar diferente DB de Redis para testing


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    
    # En producción, todas las variables deben venir del entorno
    # No usar valores por defecto
    

# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Obtiene la configuración según el entorno"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])