"""
Punto de entrada de la aplicación
"""
import os
from app import create_app
from app.models.user import create_user, find_user_by_email
from app.constants.roles import UserRole

# Crear la aplicación
app = create_app()

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
    
    """)
    
    # Ejecutar la aplicación
    app.run(
        host=host,
        port=port,
        debug=debug
    )