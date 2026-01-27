"""
Punto de entrada de la aplicación
"""
import os
from app import create_app
from flask_jwt_extended import JWTManager
from app.utils.jwt_utils import setup_jwt_callbacks
from app.jobs import init_scheduler
from app.models.user import create_user, find_user_by_email
from app.constants.roles import UserRole
from app.routes.products import products_bp
from app.routes.wishlist import wishlist_bp
from app.routes.inventory import inventory_bp

# Crear la aplicación
app = create_app()

# Configurar JWT
jwt = JWTManager(app)
setup_jwt_callbacks(jwt)

# Registrar nuevos blueprints
from app.routes.auth import auth_bp
from app.routes.users import users_bp
from app.routes.reservations import reservations_bp
from app.routes.catalog_routes import catalog_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(reservations_bp, url_prefix='/api/reservations')
app.register_blueprint(products_bp, url_prefix='/api/products')
app.register_blueprint(wishlist_bp, url_prefix='/api/wishlist')
app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
app.register_blueprint(catalog_bp, url_prefix="/api/catalog")

# Inicializar jobs programados
scheduler = init_scheduler()

# Seed DB en desarrollo: crea un usuario semilla si no existe
try:
    if app.config.get('DEBUG'):
        with app.app_context():
            seed_email = os.getenv('SEED_USER_EMAIL', 'seed@example.com')
            seed_password = os.getenv('SEED_USER_PASSWORD', 'password123')
            seed_name = os.getenv('SEED_USER_NAME', 'Seed User')
            seed_admin = os.getenv('SEED_USER_ADMIN', 'False').lower() == 'true'

            existing = find_user_by_email(seed_email)
            if existing is None:
                role = UserRole.ADMIN if seed_admin else UserRole.CLIENT
                user = create_user(email=seed_email, password=seed_password, nombre=seed_name, rol=role)
                app.logger.info(f"✓ Usuario semilla creado: {user.email}")
            else:
                app.logger.info(f"ℹ️ Usuario semilla ya existe: {existing.email}")
except Exception as e:
    # No detener el arranque por un error al insertar usuario semilla
    try:
        app.logger.error(f"✗ Error al crear usuario semilla: {str(e)}")
    except Exception:
        print(f"Error al crear usuario semilla: {str(e)}")

if __name__ == '__main__':
    # Obtener configuración del entorno
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', False)

    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        Pisos Kermy Jacó - Sistema de Gestión y Reservas      ║
    ║                          Backend API                         ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝

    🚀 Servidor iniciando en http://{host}:{port}
    🔧 Modo: {'Desarrollo' if debug else 'Producción'}
    📝 Documentación: http://{host}:{port}/
    💚 Health Check: http://{host}:{port}/health

    ✓ JWT configurado
    ✓ Blueprints registrados: auth, users, reservations
    ✓ Jobs programados iniciados (expiración cada 5 min, notificaciones diarias)
    ✓ Sistema de usuarios semilla activo
    """)

    # Ejecutar la aplicación
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=False  # Importante con APScheduler
    )
