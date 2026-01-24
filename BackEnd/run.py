"""
Punto de entrada de la aplicación
"""
import os
from app import create_app

# Crear la aplicación
app = create_app()

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