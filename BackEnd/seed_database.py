#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos de prueba
Crea usuarios, productos, variantes e inventario inicial
"""

import sys
import os
from datetime import datetime
from werkzeug.security import generate_password_hash
from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio raiz al path
sys.path.insert(0, os.path.abspath('.'))

from app.constants.roles import UserRole
from app.constants.states import ProductState


def get_db():
    """Obtiene conexion a MongoDB usando PyMongo"""
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/pisos_kermy_db')
    client = MongoClient(mongodb_uri)
    db_name = mongodb_uri.split('/')[-1]
    return client[db_name]


def clear_collections(db):
    """Limpia las colecciones de prueba"""
    print("Limpiando colecciones existentes...")
    collections = [
        'users', 'products', 'variants', 'inventory',
        'reservations', 'email_notifications', 'revoked_tokens',
        'audit_logs', 'inventory_movements'
    ]
    
    for collection in collections:
        db[collection].delete_many({})
    
    print("✓ Colecciones limpiadas")


def create_users(db):
    """Crea usuarios de prueba"""
    print("\nCreando usuarios de prueba...")
    
    users = [
        {
            'email': 'admin@pisoskermy.com',
            'password': generate_password_hash('Admin123!'),
            'name': 'Administrador Pisos Kermy',
            'phone': '88888888',
            'role': UserRole.ADMIN,
            'state': 'activo',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'email': 'cliente1@example.com',
            'password': generate_password_hash('Cliente123!'),
            'name': 'Juan Perez',
            'phone': '87654321',
            'role': UserRole.CLIENT,
            'state': 'activo',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'email': 'cliente2@example.com',
            'password': generate_password_hash('Cliente123!'),
            'name': 'Maria Rodriguez',
            'phone': '87654322',
            'role': UserRole.CLIENT,
            'state': 'activo',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    ]
    
    result = db.users.insert_many(users)
    print(f"✓ {len(result.inserted_ids)} usuarios creados")
    
    return {
        'admin_id': result.inserted_ids[0],
        'client1_id': result.inserted_ids[1],
        'client2_id': result.inserted_ids[2]
    }


def create_products_and_inventory(db):
    """Crea productos, variantes e inventario"""
    print("\nCreando productos y variantes...")
    
    # Producto 1: Piso Laminado
    product1 = {
        'name': 'Piso Laminado Premium',
        'description': 'Piso laminado de alta calidad, resistente al agua',
        'category': 'Laminados',
        'state': ProductState.ACTIVE,
        'image_url': 'https://example.com/laminado.jpg',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    product1_id = db.products.insert_one(product1).inserted_id
    
    # Variantes del producto 1
    variants1 = [
        {
            'product_id': product1_id,
            'size': '1x1m',
            'sku': 'LAM-PREM-1X1',
            'price': 15000.00,
            'created_at': datetime.utcnow()
        },
        {
            'product_id': product1_id,
            'size': '2x2m',
            'sku': 'LAM-PREM-2X2',
            'price': 55000.00,
            'created_at': datetime.utcnow()
        }
    ]
    
    variant1_ids = db.variants.insert_many(variants1).inserted_ids
    
    # Inventario para variantes del producto 1
    inventory1 = [
        {
            'variant_id': variant1_ids[0],
            'stock_total': 100,
            'stock_retenido': 0,
            'updated_at': datetime.utcnow()
        },
        {
            'variant_id': variant1_ids[1],
            'stock_total': 50,
            'stock_retenido': 0,
            'updated_at': datetime.utcnow()
        }
    ]
    
    db.inventory.insert_many(inventory1)
    
    # Producto 2: Piso de Porcelanato
    product2 = {
        'name': 'Porcelanato Italiano',
        'description': 'Porcelanato importado de Italia, acabado brillante',
        'category': 'Porcelanato',
        'state': ProductState.ACTIVE,
        'image_url': 'https://example.com/porcelanato.jpg',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    product2_id = db.products.insert_one(product2).inserted_id
    
    # Variantes del producto 2
    variants2 = [
        {
            'product_id': product2_id,
            'size': '60x60cm',
            'sku': 'PORC-ITA-60',
            'price': 25000.00,
            'created_at': datetime.utcnow()
        },
        {
            'product_id': product2_id,
            'size': '80x80cm',
            'sku': 'PORC-ITA-80',
            'price': 40000.00,
            'created_at': datetime.utcnow()
        }
    ]
    
    variant2_ids = db.variants.insert_many(variants2).inserted_ids
    
    # Inventario para variantes del producto 2
    inventory2 = [
        {
            'variant_id': variant2_ids[0],
            'stock_total': 75,
            'stock_retenido': 0,
            'updated_at': datetime.utcnow()
        },
        {
            'variant_id': variant2_ids[1],
            'stock_total': 30,
            'stock_retenido': 0,
            'updated_at': datetime.utcnow()
        }
    ]
    
    db.inventory.insert_many(inventory2)
    
    print(f"✓ 2 productos creados")
    print(f"✓ 4 variantes creadas")
    print(f"✓ 4 registros de inventario creados")
    
    return {
        'product1_id': product1_id,
        'product2_id': product2_id,
        'variant_ids': variant1_ids + variant2_ids
    }


def main():
    print("=" * 60)
    print("POBLANDO BASE DE DATOS CON DATOS DE PRUEBA")
    print("=" * 60)
    
    try:
        db = get_db()
        
        # Limpiar colecciones
        clear_collections(db)
        
        # Crear usuarios
        user_ids = create_users(db)
        
        # Crear productos e inventario
        product_data = create_products_and_inventory(db)
        
        print("\n" + "=" * 60)
        print("DATOS DE PRUEBA CREADOS EXITOSAMENTE")
        print("=" * 60)
        print("\nCredenciales de prueba:")
        print("-" * 60)
        print("ADMIN:")
        print("  Email: admin@pisoskermy.com")
        print("  Password: Admin123!")
        print()
        print("CLIENTE 1:")
        print("  Email: cliente1@example.com")
        print("  Password: Cliente123!")
        print()
        print("CLIENTE 2:")
        print("  Email: cliente2@example.com")
        print("  Password: Cliente123!")
        print()
        print("IDs generados:")
        print(f"  Admin ID: {user_ids['admin_id']}")
        print(f"  Cliente 1 ID: {user_ids['client1_id']}")
        print(f"  Cliente 2 ID: {user_ids['client2_id']}")
        print(f"  Producto 1 ID: {product_data['product1_id']}")
        print(f"  Producto 2 ID: {product_data['product2_id']}")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())