"""
Script para limpiar y crear reservas de ejemplo realistas
Usa usuarios y productos reales de la base de datos
"""
import os
import sys
from datetime import datetime, timedelta
import random

# Agregar el path del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.config.database import get_db
from bson import ObjectId

def main():
    """Función principal"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("LIMPIEZA Y CREACIÓN DE RESERVAS DE EJEMPLO")
        print("="*70 + "\n")
        
        # Obtener conexión a BD
        db = get_db()
        
        # Paso 1: Limpiar reservas existentes
        print("🗑️  Eliminando reservas antiguas...")
        deleted_result = db.reservations.delete_many({})
        print(f"   ✓ {deleted_result.deleted_count} reservas eliminadas\n")
        
        # Paso 2: Obtener usuarios clientes
        print("👥 Obteniendo usuarios...")
        clients = list(db.users.find({'role': 'CLIENT'}))
        
        if len(clients) == 0:
            print("   ❌ No hay clientes en la BD. Ejecuta seed_database.py primero.")
            return
        
        print(f"   ✓ {len(clients)} clientes encontrados\n")
        
        # Paso 3: Obtener productos y variantes
        print("📦 Obteniendo productos...")
        products = list(db.products.find({'state': 'activo'}))
        
        if len(products) == 0:
            print("   ❌ No hay productos en la BD. Ejecuta seed_database.py primero.")
            return
        
        # Recopilar todas las variantes disponibles
        all_variants = []
        for product in products:
            for variant in product.get('variantes', []):
                if variant.get('stock_actual', 0) > 0:  # Solo variantes con stock
                    all_variants.append({
                        'variant_id': str(variant['_id']),
                        'product_name': product['nombre'],
                        'variant_name': variant['nombre'],
                        'available_stock': variant['stock_actual']
                    })
        
        if len(all_variants) == 0:
            print("   ❌ No hay variantes con stock disponible.")
            return
        
        print(f"   ✓ {len(all_variants)} variantes con stock disponibles\n")
        
        # Paso 4: Crear reservas de ejemplo
        print("🎯 Creando reservas de ejemplo...\n")
        
        reservations_to_create = [
            {
                'client': random.choice(clients),
                'num_items': random.randint(1, 3),
                'state': 'Pendiente',
                'days_ago': 0,  # Hoy
                'notes': "Reserva reciente - Necesito estos productos para un proyecto urgente"
            },
            {
                'client': random.choice(clients),
                'num_items': random.randint(2, 4),
                'state': 'Pendiente',
                'days_ago': 1,  # Ayer
                'notes': "Por favor confirmar disponibilidad antes del viernes"
            },
            {
                'client': random.choice(clients),
                'num_items': random.randint(1, 2),
                'state': 'Aprobada',
                'days_ago': 3,
                'notes': "Cliente frecuente - envío prioritario",
                'admin_notes': "Aprobado - Cliente verificado"
            },
            {
                'client': random.choice(clients),
                'num_items': random.randint(2, 3),
                'state': 'Rechazada',
                'days_ago': 5,
                'notes': "Solicitud para remodelación de casa",
                'admin_notes': "Stock insuficiente al momento de la revisión"
            },
            {
                'client': random.choice(clients),
                'num_items': random.randint(1, 3),
                'state': 'Cancelada',
                'days_ago': 7,
                'notes': "El cliente cambió de parecer sobre el proyecto"
            },
        ]
        
        created_count = 0
        for idx, reservation_data in enumerate(reservations_to_create, 1):
            try:
                client = reservation_data['client']
                num_items = reservation_data['num_items']
                
                # Seleccionar variantes aleatorias
                selected_variants = random.sample(all_variants, min(num_items, len(all_variants)))
                
                # Crear items con cantidades realistas
                items = []
                for variant in selected_variants:
                    quantity = random.randint(1, min(5, variant['available_stock']))
                    items.append({
                        'variant_id': variant['variant_id'],
                        'product_name': variant['product_name'],
                        'variant_name': variant['variant_name'],
                        'quantity': quantity
                    })
                
                # Calcular fechas
                created_at = datetime.utcnow() - timedelta(days=reservation_data['days_ago'])
                expires_at = created_at + timedelta(hours=24)
                
                # Crear documento de reserva
                reservation_doc = {
                    'user_id': client['_id'],
                    'items': items,
                    'state': reservation_data['state'],
                    'notes': reservation_data.get('notes'),
                    'admin_notes': reservation_data.get('admin_notes'),
                    'created_at': created_at,
                    'expires_at': expires_at if reservation_data['state'] in ['Pendiente', 'Aprobada'] else None,
                    'approved_at': None,
                    'cancelled_at': None,
                    'rejected_at': None,
                    'expired_at': None
                }
                
                # Insertar en BD
                result = db.reservations.insert_one(reservation_doc)
                
                print(f"   ✓ Reserva {idx}: {reservation_data['state']}")
                print(f"      Usuario: {client['email']}")
                print(f"      Items: {len(items)} productos, {sum(item['quantity'] for item in items)} unidades")
                print(f"      Fecha: {created_at.strftime('%Y-%m-%d %H:%M')}")
                if expires_at and reservation_data['state'] in ['Pendiente', 'Aprobada']:
                    print(f"      Expira: {expires_at.strftime('%Y-%m-%d %H:%M')}")
                print()
                
                created_count += 1
                
            except Exception as e:
                print(f"   ❌ Error al crear reserva {idx}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Resumen
        print("\n" + "="*70)
        print(f"✅ COMPLETADO: {created_count} reservas creadas exitosamente")
        print("="*70 + "\n")
        
        print("Reservas creadas:")
        print(f"  • Pendientes: {sum(1 for r in reservations_to_create if r['state'] == 'Pendiente')}")
        print(f"  • Aprobadas: {sum(1 for r in reservations_to_create if r['state'] == 'Aprobada')}")
        print(f"  • Rechazadas: {sum(1 for r in reservations_to_create if r['state'] == 'Rechazada')}")
        print(f"  • Canceladas: {sum(1 for r in reservations_to_create if r['state'] == 'Cancelada')}")
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()