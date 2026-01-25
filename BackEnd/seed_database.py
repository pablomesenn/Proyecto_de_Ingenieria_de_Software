#!/usr/bin/env python3
"""
Script mejorado para poblar la base de datos con datos de prueba
MEJORAS:
- Crea inventario correctamente para cada variante
- Asegura que haya stock disponible > 0
- Mejor estructura y logging
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

    # Obtener nombre de DB del .env o extraer de la URI
    db_name = os.getenv('MONGODB_DB', 'pisos_kermy_db')

    return client[db_name]


def clear_collections(db):
    """Limpia las colecciones de prueba"""
    print("\n" + "="*70)
    print("LIMPIANDO COLECCIONES EXISTENTES")
    print("="*70)

    collections = [
        'users', 'products', 'variants', 'inventory', 'wishlists',
        'reservations', 'email_notifications', 'revoked_tokens',
        'audit_logs', 'inventory_movements'
    ]

    for collection in collections:
        count = db[collection].count_documents({})
        db[collection].delete_many({})
        print(f"✓ {collection}: {count} documentos eliminados")

    print("="*70)


def create_users(db):
    """Crea usuarios de prueba"""
    print("\n" + "="*70)
    print("CREANDO USUARIOS DE PRUEBA")
    print("="*70)

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

    print(f"✓ {len(result.inserted_ids)} usuarios creados:")
    for i, user in enumerate(users):
        print(f"  - {user['email']} ({user['role']}) - ID: {result.inserted_ids[i]}")

    print("="*70)

    return {
        'admin_id': result.inserted_ids[0],
        'client1_id': result.inserted_ids[1],
        'client2_id': result.inserted_ids[2]
    }


def create_products_and_inventory(db):
    """Crea productos, variantes e inventario CON STOCK"""
    print("\n" + "="*70)
    print("CREANDO PRODUCTOS, VARIANTES E INVENTARIO")
    print("="*70)

    products_data = []
    variants_data = []
    inventory_data = []

    # ========== PRODUCTO 1: Piso Laminado ==========
    product1 = {
        'nombre': 'Piso Laminado Premium',
        'imagen_url': 'https://example.com/laminado-premium.jpg',
        'categoria': 'Laminados',
        'tags': ['premium', 'resistente', 'facil-instalacion'],
        'estado': ProductState.ACTIVE,
        'descripcion_embalaje': 'Caja de 10 piezas - 2.5m² por caja',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    product1_id = db.products.insert_one(product1).inserted_id
    products_data.append((product1_id, product1['nombre']))

    # Variantes del producto 1
    variant1_1 = {
        'product_id': product1_id,
        'tamano_pieza': '1.2m x 0.2m',
        'unidad': 'm²',
        'precio': 15000.00,
        'created_at': datetime.utcnow()
    }
    variant1_2 = {
        'product_id': product1_id,
        'tamano_pieza': '2.0m x 0.25m',
        'unidad': 'm²',
        'precio': 22000.00,
        'created_at': datetime.utcnow()
    }

    variant1_1_id = db.variants.insert_one(variant1_1).inserted_id
    variant1_2_id = db.variants.insert_one(variant1_2).inserted_id
    variants_data.extend([
        (variant1_1_id, variant1_1['tamano_pieza'], variant1_1['precio']),
        (variant1_2_id, variant1_2['tamano_pieza'], variant1_2['precio'])
    ])

    # ========== PRODUCTO 2: Porcelanato ==========
    product2 = {
        'nombre': 'Porcelanato Italiano Carrara',
        'imagen_url': 'https://example.com/porcelanato-carrara.jpg',
        'categoria': 'Porcelanato',
        'tags': ['italiano', 'marmol', 'elegante'],
        'estado': ProductState.ACTIVE,
        'descripcion_embalaje': 'Caja de 6 piezas - 2.16m² por caja',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    product2_id = db.products.insert_one(product2).inserted_id
    products_data.append((product2_id, product2['nombre']))

    # Variantes del producto 2
    variant2_1 = {
        'product_id': product2_id,
        'tamano_pieza': '60cm x 60cm',
        'unidad': 'm²',
        'precio': 28000.00,
        'created_at': datetime.utcnow()
    }
    variant2_2 = {
        'product_id': product2_id,
        'tamano_pieza': '80cm x 80cm',
        'unidad': 'm²',
        'precio': 42000.00,
        'created_at': datetime.utcnow()
    }

    variant2_1_id = db.variants.insert_one(variant2_1).inserted_id
    variant2_2_id = db.variants.insert_one(variant2_2).inserted_id
    variants_data.extend([
        (variant2_1_id, variant2_1['tamano_pieza'], variant2_1['precio']),
        (variant2_2_id, variant2_2['tamano_pieza'], variant2_2['precio'])
    ])

    # ========== PRODUCTO 3: Ceramica ==========
    product3 = {
        'nombre': 'Cerámica Antideslizante Exterior',
        'imagen_url': 'https://example.com/ceramica-antideslizante.jpg',
        'categoria': 'Ceramica',
        'tags': ['exterior', 'antideslizante', 'durable'],
        'estado': ProductState.ACTIVE,
        'descripcion_embalaje': 'Caja de 12 piezas - 1.44m² por caja',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    product3_id = db.products.insert_one(product3).inserted_id
    products_data.append((product3_id, product3['nombre']))

    # Variantes del producto 3
    variant3_1 = {
        'product_id': product3_id,
        'tamano_pieza': '30cm x 30cm',
        'unidad': 'm²',
        'precio': 12000.00,
        'created_at': datetime.utcnow()
    }
    variant3_2 = {
        'product_id': product3_id,
        'tamano_pieza': '45cm x 45cm',
        'unidad': 'm²',
        'precio': 18000.00,
        'created_at': datetime.utcnow()
    }

    variant3_1_id = db.variants.insert_one(variant3_1).inserted_id
    variant3_2_id = db.variants.insert_one(variant3_2).inserted_id
    variants_data.extend([
        (variant3_1_id, variant3_1['tamano_pieza'], variant3_1['precio']),
        (variant3_2_id, variant3_2['tamano_pieza'], variant3_2['precio'])
    ])

    # ========== CREAR INVENTARIO CON STOCK ==========
    print("\nCreando registros de inventario:")

    # Inventario para todas las variantes con STOCK ABUNDANTE
    inventory_records = [
        # Producto 1 - Laminado
        {'variant_id': variant1_1_id, 'stock_total': 150, 'stock_retenido': 0},
        {'variant_id': variant1_2_id, 'stock_total': 100, 'stock_retenido': 0},
        # Producto 2 - Porcelanato
        {'variant_id': variant2_1_id, 'stock_total': 200, 'stock_retenido': 0},
        {'variant_id': variant2_2_id, 'stock_total': 80, 'stock_retenido': 0},
        # Producto 3 - Cerámica
        {'variant_id': variant3_1_id, 'stock_total': 300, 'stock_retenido': 0},
        {'variant_id': variant3_2_id, 'stock_total': 120, 'stock_retenido': 0},
    ]

    for inv in inventory_records:
        inv['updated_at'] = datetime.utcnow()
        inv['created_at'] = datetime.utcnow()

    db.inventory.insert_many(inventory_records)

    # Imprimir resumen
    print(f"\n✓ {len(products_data)} productos creados:")
    for prod_id, name in products_data:
        print(f"  - {name} (ID: {prod_id})")

    print(f"\n✓ {len(variants_data)} variantes creadas:")
    for var_id, size, price in variants_data:
        print(f"  - {size} - ₡{price:,.2f} (ID: {var_id})")

    print(f"\n✓ {len(inventory_records)} registros de inventario creados:")
    for inv in inventory_records:
        print(f"  - Variante {inv['variant_id']}: {inv['stock_total']} unidades disponibles")

    print("="*70)

    return {
        'product_ids': [p[0] for p in products_data],
        'variant_ids': [v[0] for v in variants_data],
        'total_stock': sum(inv['stock_total'] for inv in inventory_records)
    }


def verify_data(db):
    """Verifica que los datos se hayan creado correctamente"""
    print("\n" + "="*70)
    print("VERIFICANDO DATOS CREADOS")
    print("="*70)

    counts = {
        'users': db.users.count_documents({}),
        'products': db.products.count_documents({}),
        'variants': db.variants.count_documents({}),
        'inventory': db.inventory.count_documents({})
    }

    print(f"✓ Usuarios: {counts['users']}")
    print(f"✓ Productos: {counts['products']}")
    print(f"✓ Variantes: {counts['variants']}")
    print(f"✓ Inventario: {counts['inventory']}")

    # Verificar stock disponible
    total_stock = 0
    for inv in db.inventory.find():
        disponible = inv['stock_total'] - inv.get('stock_retenido', 0)
        total_stock += disponible

    print(f"✓ Stock total disponible: {total_stock} unidades")

    # Verificar que al menos una variante tenga stock
    variants_with_stock = db.inventory.count_documents({
        '$expr': {'$gt': [{'$subtract': ['$stock_total', '$stock_retenido']}, 0]}
    })

    print(f"✓ Variantes con stock disponible: {variants_with_stock}")

    if variants_with_stock == 0:
        print("\n⚠️  ADVERTENCIA: No hay variantes con stock disponible!")
        return False

    print("="*70)
    return True


def print_credentials(user_ids):
    """Imprime las credenciales de acceso"""
    print("\n" + "="*70)
    print("CREDENCIALES DE ACCESO")
    print("="*70)

    credentials = [
        {
            'tipo': 'ADMINISTRADOR',
            'email': 'admin@pisoskermy.com',
            'password': 'Admin123!',
            'id': user_ids['admin_id']
        },
        {
            'tipo': 'CLIENTE 1',
            'email': 'cliente1@example.com',
            'password': 'Cliente123!',
            'id': user_ids['client1_id']
        },
        {
            'tipo': 'CLIENTE 2',
            'email': 'cliente2@example.com',
            'password': 'Cliente123!',
            'id': user_ids['client2_id']
        }
    ]

    for cred in credentials:
        print(f"\n{cred['tipo']}:")
        print(f"  Email:    {cred['email']}")
        print(f"  Password: {cred['password']}")
        print(f"  ID:       {cred['id']}")

    print("\n" + "="*70)


def main():
    print("\n" + "="*70)
    print("SEED DATABASE - PISOS KERMY")
    print("Poblando base de datos con datos de prueba completos")
    print("="*70)

    try:
        db = get_db()

        # Limpiar colecciones
        clear_collections(db)

        # Crear usuarios
        user_ids = create_users(db)

        # Crear productos e inventario
        product_data = create_products_and_inventory(db)

        # Verificar datos
        success = verify_data(db)

        if success:
            print("\n" + "="*70)
            print("✅ BASE DE DATOS POBLADA EXITOSAMENTE")
            print("="*70)

            print(f"\nResumen:")
            print(f"  - 3 usuarios creados")
            print(f"  - 3 productos creados")
            print(f"  - 6 variantes creadas")
            print(f"  - Stock total: {product_data['total_stock']} unidades")

            # Imprimir credenciales
            print_credentials(user_ids)

            print("\n🚀 Puedes ejecutar ahora:")
            print("   python test_all_endpoints_fixed.py")
            print("\n" + "="*70)

            return 0
        else:
            print("\n❌ ERROR: La verificación de datos falló")
            return 1

    except Exception as e:
        print(f"\n❌ ERROR FATAL: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
