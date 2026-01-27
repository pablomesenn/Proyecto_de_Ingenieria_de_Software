"""
Inicialización de la aplicación Flask
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from logging.handlers import RotatingFileHandler
import os

from app.config.config import get_config
from app.config.database import init_db, close_db
from app.middleware.error_handler import register_error_handlers


# Instancias globales
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=None,  # Se configura en create_app
)


def create_app(config_name=None):
    """
    Application Factory
    Crea y configura la aplicación Flask
    """
    app = Flask(__name__)

    # Cargar configuración
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    config_class = get_config()
    app.config.from_object(config_class)

    # Configurar logging
    setup_logging(app)

    # Inicializar extensiones
    init_extensions(app)

    # Inicializar bases de datos
    init_db(app)

    # Registrar blueprints (rutas)
    register_blueprints(app)

    # Registrar manejadores de errores
    register_error_handlers(app)

    # Registrar eventos de cierre
    register_teardown(app)

    # Ruta de health check
    @app.route('/health', methods=['GET'])
    def health_check():
        """Endpoint para verificar que el servidor está funcionando"""
        return jsonify({
            'status': 'healthy',
            'service': 'Pisos Kermy API',
            'version': '1.0.0'
        }), 200

    # Ruta raíz
    @app.route('/', methods=['GET'])
    def index():
        """Endpoint raíz con información de la API"""
        return jsonify({
            'message': 'Pisos Kermy - Sistema de Gestión y Reservas API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'auth': '/api/auth',
                'users': '/api/users',
                'products': '/api/products',
                'inventory': '/api/inventory',
                'wishlist': '/api/wishlist',
                'reservations': '/api/reservations',
                'admin': '/api/admin'
            }
        }), 200

    app.logger.info("✓ Aplicación Flask inicializada correctamente")

    return app


def init_extensions(app):
    """
    Inicializa las extensiones de Flask
    """
    # CORS
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=app.config["CORS_SUPPORTS_CREDENTIALS"],
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    @app.before_request
    def _cors_preflight():
        if request.method == "OPTIONS":
            return ("", 204)
    # JWT
    jwt.init_app(app)

    # Configurar callbacks de JWT
    setup_jwt_callbacks(app)

    # Rate Limiter
    limiter.init_app(app)
    limiter.storage_uri = app.config['RATELIMIT_STORAGE_URL']

    app.logger.info("✓ Extensiones inicializadas")


def setup_jwt_callbacks(app):
    """
    Configura los callbacks personalizados de JWT
    """
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'token_expired',
            'message': 'El token ha expirado'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'invalid_token',
            'message': 'Token inválido'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'missing_token',
            'message': 'Token de autorización no proporcionado'
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'token_revoked',
            'message': 'El token ha sido revocado'
        }), 401


def register_blueprints(app):
    """
    Registra todos los blueprints (rutas) de la aplicación

    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    from app.routes.product_routes import product_bp
    from app.routes.inventory_routes import inventory_bp
    from app.routes.wishlist_routes import wishlist_bp
    from app.routes.reservation_routes import reservation_bp
    from app.routes.admin_routes import admin_bp

    # Registrar con prefijo /api
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(wishlist_bp, url_prefix='/api/wishlist')
    app.register_blueprint(reservation_bp, url_prefix='/api/reservations')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    """
    app.logger.info("✓ Blueprints registrados")


def register_teardown(app):
    """
    Registra funciones para ejecutar al cerrar la aplicación
    """
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Cierra las conexiones al terminar el contexto"""
        if exception:
            app.logger.error(f"Error en contexto de aplicación: {str(exception)}")


def setup_logging(app):
    """
    Configura el sistema de logging
    """
    if not app.debug and not app.testing:
        # Crear directorio de logs si no existe
        if not os.path.exists('logs'):
            os.mkdir('logs')

        # Configurar handler de archivo
        file_handler = RotatingFileHandler(
            f"logs/{app.config['LOG_FILE']}",
            maxBytes=10240000,  # 10MB
            backupCount=10
        )

        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))

        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.addHandler(file_handler)

    app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    app.logger.info('✓ Sistema de logging configurado')
