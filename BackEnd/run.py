"""
Punto de entrada de la aplicación
"""
import os
from app import create_app
from flask_jwt_extended import JWTManager
from app.utils.jwt_utils import setup_jwt_callbacks
from app.jobs import init_scheduler

# Crear la aplicación
app = create_app()

# Configurar JWT
jwt = JWTManager(app)
setup_jwt_callbacks(jwt)

# Registrar nuevos blueprints
from app.routes.auth import auth_bp
from app.routes.users import users_bp
from app.routes.reservations import reservations_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(reservations_bp, url_prefix='/api/reservations')

# Inicializar jobs programados
scheduler = init_scheduler()

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
    
    """)
    
    # Ejecutar la aplicación
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=False 
    )