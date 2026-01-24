#!/usr/bin/env python3
"""
Script de verificacion de instalacion
Verifica que todos los modulos y dependencias esten correctamente instalados
"""

import sys
import importlib

def check_module(module_name):
    """Verifica si un modulo esta instalado"""
    try:
        importlib.import_module(module_name)
        print(f"✓ {module_name} instalado")
        return True
    except ImportError:
        print(f"✗ {module_name} NO instalado")
        return False

def check_file_exists(filepath):
    """Verifica si un archivo existe"""
    import os
    if os.path.exists(filepath):
        print(f"✓ {filepath} existe")
        return True
    else:
        print(f"✗ {filepath} NO existe")
        return False

def main():
    print("=" * 60)
    print("VERIFICACION DE INSTALACION - Backend Pisos Kermy")
    print("=" * 60)
    print()
    
    # Verificar dependencias principales
    print("1. Verificando dependencias de Python...")
    print("-" * 60)
    modules = [
        'flask',
        'flask_jwt_extended',
        'pymongo',
        'redis',
        'marshmallow',
        'apscheduler',
        'werkzeug',
        'bson'
    ]
    
    modules_ok = all(check_module(m) for m in modules)
    print()
    
    # Verificar estructura de archivos
    print("2. Verificando estructura de archivos...")
    print("-" * 60)
    files = [
        'app/models/reservation.py',
        'app/models/notification.py',
        'app/repositories/reservation_repository.py',
        'app/repositories/inventory_repository.py',
        'app/repositories/notification_repository.py',
        'app/services/reservation_service.py',
        'app/services/auth_service.py',
        'app/services/user_service.py',
        'app/services/notification_service.py',
        'app/routes/reservations.py',
        'app/routes/auth.py',
        'app/routes/users.py',
        'app/jobs/reservation_expiration_job.py',
        'app/jobs/notification_job.py',
        'app/jobs/__init__.py',
        'app/schemas/reservation_schema.py',
        'app/schemas/auth_schema.py',
        'app/schemas/user_schema.py',
        'app/utils/jwt_utils.py'
    ]
    
    files_ok = all(check_file_exists(f) for f in files)
    print()
    
    # Verificar archivos de configuracion
    print("3. Verificando archivos de configuracion...")
    print("-" * 60)
    config_files = [
        'app/config/config.py',
        'app/config/database.py',
        'app/constants/roles.py',
        'app/constants/states.py',
        '.env'
    ]
    
    config_ok = all(check_file_exists(f) for f in config_files)
    print()
    
    # Verificar variables de entorno
    print("4. Verificando variables de entorno...")
    print("-" * 60)
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    env_vars = {
        'MONGODB_URI': os.getenv('MONGODB_URI'),
        'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY'),
        'SMTP_USERNAME': os.getenv('SMTP_USERNAME'),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD')
    }
    
    env_ok = True
    for var, value in env_vars.items():
        if value:
            print(f"✓ {var} configurado")
        else:
            print(f"✗ {var} NO configurado")
            env_ok = False
    print()
    
    # Resultado final
    print("=" * 60)
    print("RESULTADO DE LA VERIFICACION")
    print("=" * 60)
    
    if modules_ok and files_ok and config_ok and env_ok:
        print("✓ TODO CORRECTO - El proyecto esta listo para ejecutarse")
        return 0
    else:
        print("✗ HAY PROBLEMAS - Revisa los errores anteriores")
        if not modules_ok:
            print("  - Instala las dependencias: pip install -r requirements.txt")
        if not files_ok:
            print("  - Verifica que todos los archivos esten en su lugar")
        if not config_ok:
            print("  - Verifica los archivos de configuracion")
        if not env_ok:
            print("  - Configura las variables de entorno en .env")
        return 1

if __name__ == '__main__':
    sys.exit(main())
