#!/usr/bin/env python3
"""
Script mejorado para poblar la base de datos con datos de prueba
MEJORAS:
- Crea inventario correctamente para cada variante
- Asegura que haya stock disponible > 0
- Mejor estructura y logging
- Datos más realistas y variados
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
    inventory_records = []

    # ========== PRODUCTO 1: Piso Laminado Premium ==========
    product1 = {
        'nombre': 'Piso Laminado Premium Roble Europeo',
        'imagen_url': 'https://images.unsplash.com/photo-1615971677499-5467cbab01c0?w=600&h=600&fit=crop',
        'categoria': 'Laminados',
        'tags': ['Premium', 'Interior', 'Moderno'],
        'estado': ProductState.ACTIVE,
        'descripcion_embalaje': 'Resistente al agua y rayones. Fácil instalación con sistema click. Caja de 10 piezas - 2.5m² por caja',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    product1_id = db.products.insert_one(product1).inserted_id
    products_data.append((product1_id, product1['nombre']))

    # Variantes del producto 1
    p1_variants = [
        {'tamano_pieza': '1.2m x 0.2m', 'precio': 15000.00, 'stock': 150},
        {'tamano_pieza': '2.0m x 0.25m', 'precio': 22000.00, 'stock': 100},
    ]

    for var_data in p1_variants:
        variant = {
            'product_id': product1_id,
            'tamano_pieza': var_data['tamano_pieza'],
            'unidad': 'm²',
            'precio': var_data['precio'],
            'created_at': datetime.utcnow()
        }
        variant_id = db.variants.insert_one(variant).inserted_id
        variants_data.append((variant_id, var_data['tamano_pieza'], var_data['precio']))

        # Crear inventario para esta variante
        inventory_records.append({
            'variant_id': variant_id,
            'stock_total': var_data['stock'],
            'stock_retenido': 0
        })

    # ========== PRODUCTO 2: Porcelanato Carrara ==========
    product2 = {
        'nombre': 'Porcelanato Italiano Carrara Blanco',
        'imagen_url': 'https://images.unsplash.com/photo-1615876234886-fd9a39fda97f?w=600&h=600&fit=crop',
        'categoria': 'Porcelanato',
        'tags': ['Premium', 'Elegante', 'Interior'],
        'estado': ProductState.ACTIVE,
        'descripcion_embalaje': 'Acabado marmolado elegante. Alta resistencia al tráfico. Caja de 6 piezas - 2.16m² por caja',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    product2_id = db.products.insert_one(product2).inserted_id
    products_data.append((product2_id, product2['nombre']))

    # Variantes del producto 2
    p2_variants = [
        {'tamano_pieza': '60cm x 60cm', 'precio': 28000.00, 'stock': 200},
        {'tamano_pieza': '80cm x 80cm', 'precio': 42000.00, 'stock': 80},
    ]

    for var_data in p2_variants:
        variant = {
            'product_id': product2_id,
            'tamano_pieza': var_data['tamano_pieza'],
            'unidad': 'm²',
            'precio': var_data['precio'],
            'created_at': datetime.utcnow()
        }
        variant_id = db.variants.insert_one(variant).inserted_id
        variants_data.append((variant_id, var_data['tamano_pieza'], var_data['precio']))

        inventory_records.append({
            'variant_id': variant_id,
            'stock_total': var_data['stock'],
            'stock_retenido': 0
        })

    # ========== PRODUCTO 3: Cerámica Antideslizante ==========
    product3 = {
        'nombre': 'Cerámica Antideslizante Exterior Gris',
        'imagen_url': 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=600&h=600&fit=crop',
        'categoria': 'Ceramica',
        'tags': ['Exterior', 'Antideslizante', 'Durable'],
        'estado': ProductState.ACTIVE,
        'descripcion_embalaje': 'Superficie antideslizante certificada. Ideal para exteriores. Caja de 12 piezas - 1.44m² por caja',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    product3_id = db.products.insert_one(product3).inserted_id
    products_data.append((product3_id, product3['nombre']))

    # Variantes del producto 3
    p3_variants = [
        {'tamano_pieza': '30cm x 30cm', 'precio': 12000.00, 'stock': 300},
        {'tamano_pieza': '45cm x 45cm', 'precio': 18000.00, 'stock': 120},
    ]

    for var_data in p3_variants:
        variant = {
            'product_id': product3_id,
            'tamano_pieza': var_data['tamano_pieza'],
            'unidad': 'm²',
            'precio': var_data['precio'],
            'created_at': datetime.utcnow()
        }
        variant_id = db.variants.insert_one(variant).inserted_id
        variants_data.append((variant_id, var_data['tamano_pieza'], var_data['precio']))

        inventory_records.append({
            'variant_id': variant_id,
            'stock_total': var_data['stock'],
            'stock_retenido': 0
        })

    # ========== PRODUCTO 4: Porcelanato Madera ==========
    product4 = {
        'nombre': 'Porcelanato Símil Madera Natural',
        'imagen_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&h=600&fit=crop',
        'categoria': 'Porcelanato',
        'tags': ['Moderno', 'Interior', 'Rústico'],
        'estado': ProductState.ACTIVE,
        'descripcion_embalaje': 'Efecto madera realista. Fácil limpieza. Caja de 8 piezas - 2.4m² por caja',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    product4_id = db.products.insert_one(product4).inserted_id
    products_data.append((product4_id, product4['nombre']))

    # Variantes del producto 4
    p4_variants = [
        {'tamano_pieza': '20cm x 120cm', 'precio': 32000.00, 'stock': 90},
        {'tamano_pieza': '25cm x 150cm', 'precio': 45000.00, 'stock': 60},
    ]

    for var_data in p4_variants:
        variant = {
            'product_id': product4_id,
            'tamano_pieza': var_data['tamano_pieza'],
            'unidad': 'm²',
            'precio': var_data['precio'],
            'created_at': datetime.utcnow()
        }
        variant_id = db.variants.insert_one(variant).inserted_id
        variants_data.append((variant_id, var_data['tamano_pieza'], var_data['precio']))

        inventory_records.append({
            'variant_id': variant_id,
            'stock_total': var_data['stock'],
            'stock_retenido': 0
        })

    # ========== PRODUCTO 5: Granito Negro ==========
    product5 = {
        'nombre': 'Granito Negro Absoluto Premium',
        'imagen_url': 'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=600&h=600&fit=crop',
        'categoria': 'Granito',
        'tags': ['Premium', 'Elegante', 'Interior'],
        'estado': ProductState.ACTIVE,
        'descripcion_embalaje': 'Granito natural de alta calidad. Pulido brillante. Caja de 4 piezas - 1.44m² por caja',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    product5_id = db.products.insert_one(product5).inserted_id
    products_data.append((product5_id, product5['nombre']))

    # Variantes del producto 5
    p5_variants = [
        {'tamano_pieza': '60cm x 60cm', 'precio': 55000.00, 'stock': 50},
        {'tamano_pieza': '80cm x 80cm', 'precio': 78000.00, 'stock': 30},
    ]

    for var_data in p5_variants:
        variant = {
            'product_id': product5_id,
            'tamano_pieza': var_data['tamano_pieza'],
            'unidad': 'm²',
            'precio': var_data['precio'],
            'created_at': datetime.utcnow()
        }
        variant_id = db.variants.insert_one(variant).inserted_id
        variants_data.append((variant_id, var_data['tamano_pieza'], var_data['precio']))

        inventory_records.append({
            'variant_id': variant_id,
            'stock_total': var_data['stock'],
            'stock_retenido': 0
        })

    # ========== PRODUCTO 6: Mármol Blanco (Stock bajo para testing) ==========
    product6 = {
        'nombre': 'Mármol Blanco Calacatta',
        'imagen_url': 'https://images.unsplash.com/photo-1615875474908-f403b2a3f247?w=600&h=600&fit=crop',
        'categoria': 'Mármol',
        'tags': ['Premium', 'Elegante', 'Exclusivo'],
        'estado': ProductState.ACTIVE,
        'descripcion_embalaje': 'Mármol natural italiano. Vetas doradas únicas. Caja de 3 piezas - 1.08m² por caja',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    product6_id = db.products.insert_one(product6).inserted_id
    products_data.append((product6_id, product6['nombre']))

    # Variantes del producto 6 - CON STOCK BAJO para testing de alertas
    p6_variants = [
        {'tamano_pieza': '60cm x 60cm', 'precio': 95000.00, 'stock': 8},  # Stock bajo
        {'tamano_pieza': '80cm x 80cm', 'precio': 135000.00, 'stock': 3},  # Stock muy bajo
    ]

    for var_data in p6_variants:
        variant = {
            'product_id': product6_id,
            'tamano_pieza': var_data['tamano_pieza'],
            'unidad': 'm²',
            'precio': var_data['precio'],
            'created_at': datetime.utcnow()
        }
        variant_id = db.variants.insert_one(variant).inserted_id
        variants_data.append((variant_id, var_data['tamano_pieza'], var_data['precio']))

        inventory_records.append({
            'variant_id': variant_id,
            'stock_total': var_data['stock'],
            'stock_retenido': 0
        })

    # ========== INSERTAR INVENTARIO ==========
    print(f"\nCreando {len(inventory_records)} registros de inventario:")

    for inv in inventory_records:
        inv['actualizado_en'] = datetime.utcnow()
        inv['creado_en'] = datetime.utcnow()

    db.inventory.insert_many(inventory_records)

    # Crear movimientos iniciales de inventario
    for inv in inventory_records:
        movement = {
            'variant_id': inv['variant_id'],
            'quantity': inv['stock_total'],
            'movement_type': 'initial',
            'reason': 'initial_stock',
            'actor_id': None,
            'creado_en': datetime.utcnow()
        }
        db.inventory_movements.insert_one(movement)

    # Imprimir resumen con tabla
    print(f"\n✓ {len(products_data)} productos creados")
    print(f"✓ {len(variants_data)} variantes creadas")
    print(f"✓ {len(inventory_records)} registros de inventario creados")

    print("\n" + "="*70)
    print("RESUMEN DE INVENTARIO POR PRODUCTO")
    print("="*70)

    for prod_id, prod_name in products_data:
        print(f"\n📦 {prod_name}")
        # Get variants for this product
        product_variants = [(v_id, size, price) for v_id, size, price in variants_data
                           if any(inv['variant_id'] == v_id for inv in inventory_records)]

        for var_id, size, price in product_variants:
            # Find inventory for this variant
            inv = next((i for i in inventory_records if i['variant_id'] == var_id), None)
            if inv:
                disponible = inv['stock_total'] - inv['stock_retenido']
                status = "✅" if disponible > 10 else ("⚠️" if disponible > 0 else "❌")
                print(f"   {status} {size:20s} - ₡{price:>10,.2f} - Stock: {disponible:>3} unidades")

    print("\n" + "="*70)

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
        'inventory': db.inventory.count_documents({}),
        'inventory_movements': db.inventory_movements.count_documents({})
    }

    print(f"✓ Usuarios: {counts['users']}")
    print(f"✓ Productos: {counts['products']}")
    print(f"✓ Variantes: {counts['variants']}")
    print(f"✓ Registros de Inventario: {counts['inventory']}")
    print(f"✓ Movimientos de Inventario: {counts['inventory_movements']}")

    # Verificar stock disponible
    total_stock = 0
    total_retenido = 0
    for inv in db.inventory.find():
        disponible = inv['stock_total'] - inv.get('stock_retenido', 0)
        total_stock += inv['stock_total']
        total_retenido += inv.get('stock_retenido', 0)

    total_disponible = total_stock - total_retenido

    print(f"\n📊 Estadísticas de Stock:")
    print(f"   Stock Total: {total_stock} unidades")
    print(f"   Stock Retenido: {total_retenido} unidades")
    print(f"   Stock Disponible: {total_disponible} unidades")

    # Verificar que al menos una variante tenga stock
    variants_with_stock = 0
    variants_low_stock = 0
    variants_no_stock = 0

    for inv in db.inventory.find():
        disponible = inv['stock_total'] - inv.get('stock_retenido', 0)
        if disponible > 10:
            variants_with_stock += 1
        elif disponible > 0:
            variants_low_stock += 1
        else:
            variants_no_stock += 1

    print(f"\n📈 Análisis de Disponibilidad:")
    print(f"   ✅ Stock Alto (>10): {variants_with_stock} variantes")
    print(f"   ⚠️  Stock Bajo (1-10): {variants_low_stock} variantes")
    print(f"   ❌ Sin Stock: {variants_no_stock} variantes")

    if variants_with_stock == 0 and variants_low_stock == 0:
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
            print(f"  - 6 productos creados con descripciones detalladas")
            print(f"  - 12 variantes creadas con diferentes tamaños")
            print(f"  - Stock total: {product_data['total_stock']} unidades")
            print(f"  - Incluye productos con stock alto y bajo para testing")

            # Imprimir credenciales
            print_credentials(user_ids)

            print("\n🚀 Sistema listo para usar:")
            print("   1. Backend: python run.py")
            print("   2. Frontend: npm run dev")
            print("   3. Prueba el endpoint: curl http://localhost:5000/api/inventory/variant/<variant_id>")
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
