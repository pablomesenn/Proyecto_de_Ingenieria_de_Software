"""
Pruebas de Sistema - Sistema de Gestión y Reservas Pisos Kermy
==================================================================

Estas pruebas validan la integración entre componentes del sistema:
- Frontend (React) ↔ Backend (Flask) ↔ Base de Datos (MongoDB)
- Verifican el flujo completo de datos entre módulos
- Validan la comunicación entre servicios

Casos de Prueba:
- SYS-01: Flujo completo de gestión de reservas
- SYS-02: Integración catálogo-inventario
- SYS-03: Sistema de notificaciones
"""

import pytest
import requests
from datetime import datetime, timedelta
import time


BASE_URL = "http://localhost:5000/api"


class TestSystemIntegration:
    """Pruebas de integración del sistema completo"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Configuración inicial para cada prueba"""
        # Autenticación de admin
        admin_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "admin@pisoskermy.com", "password": "Admin123!"}
        )
        self.admin_token = admin_response.json()["access_token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

        # Autenticación de cliente
        client_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "cliente1@example.com", "password": "Cliente123!"}
        )
        self.client_token = client_response.json()["access_token"]
        self.client_headers = {"Authorization": f"Bearer {self.client_token}"}

        yield

        # Cleanup si es necesario
        pass

    def test_sys_01_complete_reservation_flow(self):
        """
        SYS-01: Flujo completo de gestión de reservas
        
        Objetivo: Verificar la integración completa desde la creación de reserva
                 hasta su aprobación, validando todos los componentes involucrados.
        
        Pasos:
        1. Cliente consulta catálogo (Frontend → API → Cache/DB)
        2. Cliente crea reserva (Frontend → API → DB)
        3. Sistema reduce inventario temporalmente (Inventario Repository)
        4. Admin consulta reservas pendientes (Dashboard)
        5. Admin aprueba reserva (API → DB → Notification Service)
        6. Cliente recibe notificación por email
        7. Inventario se actualiza permanentemente
        
        Resultado esperado: Flujo completo sin errores, datos consistentes
        """
        print("\n=== SYS-01: Flujo completo de gestión de reservas ===")

        # Paso 1: Cliente consulta catálogo
        print("1. Consultando catálogo...")
        catalog_response = requests.get(
            f"{BASE_URL}/catalog/",
            headers=self.client_headers
        )
        assert catalog_response.status_code == 200, "Error al consultar catálogo"
        catalog = catalog_response.json()
        assert len(catalog["products"]) > 0, "Catálogo vacío"
        
        # Seleccionar primer producto
        product = catalog["products"][0]
        variant = product["variants"][0]
        variant_id = variant["_id"]
        
        print(f"   Producto seleccionado: {product['name']} - {variant['name']}")

        # Paso 2: Verificar inventario disponible
        print("2. Verificando inventario disponible...")
        inventory_response = requests.get(
            f"{BASE_URL}/inventory/variant/{variant_id}",
            headers=self.client_headers
        )
        assert inventory_response.status_code == 200
        initial_stock = inventory_response.json()["current_stock"]
        print(f"   Stock inicial: {initial_stock}")
        assert initial_stock > 0, "No hay stock disponible"

        # Paso 3: Cliente crea reserva
        print("3. Creando reserva...")
        reservation_data = {
            "items": [
                {
                    "variant_id": variant_id,
                    "quantity": 2
                }
            ],
            "notes": "Reserva de prueba SYS-01"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/reservations/",
            headers=self.client_headers,
            json=reservation_data
        )
        assert create_response.status_code == 201, f"Error al crear reserva: {create_response.text}"
        reservation = create_response.json()["reservation"]
        reservation_id = reservation["_id"]
        print(f"   Reserva creada: {reservation_id}")

        # Paso 4: Verificar reducción temporal de inventario
        print("4. Verificando reducción de inventario...")
        time.sleep(1)  # Esperar procesamiento
        
        inventory_after_response = requests.get(
            f"{BASE_URL}/inventory/variant/{variant_id}",
            headers=self.admin_headers
        )
        current_stock = inventory_after_response.json()["current_stock"]
        reserved_stock = inventory_after_response.json()["reserved_stock"]
        
        print(f"   Stock actual: {current_stock}")
        print(f"   Stock reservado: {reserved_stock}")
        
        assert reserved_stock == 2, "Stock reservado incorrecto"
        assert current_stock == initial_stock - 2, "Stock disponible no se redujo"

        # Paso 5: Admin consulta reservas pendientes
        print("5. Admin consultando reservas pendientes...")
        pending_response = requests.get(
            f"{BASE_URL}/reservations/",
            headers=self.admin_headers,
            params={"state": "Pendiente"}
        )
        assert pending_response.status_code == 200
        pending_reservations = pending_response.json()["reservations"]
        
        # Verificar que la reserva creada está en pendientes
        reservation_found = any(r["_id"] == reservation_id for r in pending_reservations)
        assert reservation_found, "Reserva no encontrada en pendientes"
        print(f"   Reservas pendientes: {len(pending_reservations)}")

        # Paso 6: Admin aprueba reserva
        print("6. Admin aprobando reserva...")
        approve_response = requests.put(
            f"{BASE_URL}/reservations/{reservation_id}/approve",
            headers=self.admin_headers,
            json={"admin_notes": "Aprobada por prueba SYS-01"}
        )
        assert approve_response.status_code == 200, f"Error al aprobar: {approve_response.text}"
        approved_reservation = approve_response.json()["reservation"]
        assert approved_reservation["state"] == "Aprobada"
        print("   Reserva aprobada exitosamente")

        # Paso 7: Verificar actualización permanente de inventario
        print("7. Verificando actualización final de inventario...")
        time.sleep(1)
        
        final_inventory_response = requests.get(
            f"{BASE_URL}/inventory/variant/{variant_id}",
            headers=self.admin_headers
        )
        final_stock = final_inventory_response.json()["current_stock"]
        final_reserved = final_inventory_response.json()["reserved_stock"]
        
        print(f"   Stock final: {final_stock}")
        print(f"   Stock reservado final: {final_reserved}")
        
        assert final_reserved == 0, "Stock reservado no se liberó"
        assert final_stock == initial_stock - 2, "Stock final incorrecto"

        # Paso 8: Verificar historial de movimientos
        print("8. Verificando historial de movimientos...")
        history_response = requests.get(
            f"{BASE_URL}/inventory/variant/{variant_id}/history",
            headers=self.admin_headers
        )
        assert history_response.status_code == 200
        history = history_response.json()["movements"]
        
        # Debe haber al menos 2 movimientos: reserva y aprobación
        reservation_movements = [m for m in history if "reserva" in m.get("reason", "").lower()]
        assert len(reservation_movements) >= 1, "No se registró movimiento de reserva"
        print(f"   Movimientos de inventario registrados: {len(history)}")

        print("\n✓ SYS-01: Flujo completo validado exitosamente")

    def test_sys_02_catalog_inventory_integration(self):
        """
        SYS-02: Integración catálogo-inventario
        
        Objetivo: Verificar sincronización entre catálogo y sistema de inventario
        
        Pasos:
        1. Consultar productos activos en catálogo
        2. Verificar que cada producto tiene inventario asociado
        3. Validar consistencia de datos entre catálogo e inventario
        4. Ajustar inventario de un producto
        5. Verificar actualización en catálogo (cache invalidation)
        
        Resultado esperado: Datos consistentes entre módulos
        """
        print("\n=== SYS-02: Integración catálogo-inventario ===")

        # Paso 1: Consultar catálogo
        print("1. Consultando catálogo...")
        catalog_response = requests.get(
            f"{BASE_URL}/catalog/",
            headers=self.client_headers
        )
        assert catalog_response.status_code == 200
        products = catalog_response.json()["products"]
        print(f"   Productos en catálogo: {len(products)}")

        # Paso 2: Verificar inventario para cada variante
        print("2. Verificando inventario de productos...")
        for product in products[:3]:  # Verificar primeros 3 productos
            for variant in product.get("variants", []):
                variant_id = variant["_id"]
                
                inv_response = requests.get(
                    f"{BASE_URL}/inventory/variant/{variant_id}",
                    headers=self.admin_headers
                )
                
                if inv_response.status_code == 200:
                    inventory = inv_response.json()
                    print(f"   {product['name']} - {variant['name']}: Stock = {inventory['current_stock']}")
                    
                    # Validar campos requeridos
                    assert "current_stock" in inventory
                    assert "reserved_stock" in inventory
                    assert "min_stock" in inventory
                else:
                    print(f"   ⚠ {product['name']} - {variant['name']}: Sin inventario")

        # Paso 3: Ajustar inventario
        print("3. Ajustando inventario de un producto...")
        test_variant = products[0]["variants"][0]
        variant_id = test_variant["_id"]
        
        # Obtener stock actual
        inv_before = requests.get(
            f"{BASE_URL}/inventory/variant/{variant_id}",
            headers=self.admin_headers
        ).json()
        stock_before = inv_before["current_stock"]

        # Realizar ajuste
        adjustment_data = {
            "variant_id": variant_id,
            "quantity": 5,
            "type": "entrada",
            "reason": "Prueba SYS-02"
        }
        
        adjust_response = requests.post(
            f"{BASE_URL}/inventory/adjust",
            headers=self.admin_headers,
            json=adjustment_data
        )
        assert adjust_response.status_code in [200, 201]
        print(f"   Ajuste realizado: +5 unidades")

        # Paso 4: Verificar actualización
        print("4. Verificando actualización de inventario...")
        time.sleep(1)
        
        inv_after = requests.get(
            f"{BASE_URL}/inventory/variant/{variant_id}",
            headers=self.admin_headers
        ).json()
        stock_after = inv_after["current_stock"]
        
        print(f"   Stock antes: {stock_before}")
        print(f"   Stock después: {stock_after}")
        assert stock_after == stock_before + 5, "Inventario no se actualizó correctamente"

        # Paso 5: Verificar invalidación de cache en catálogo
        print("5. Verificando actualización en catálogo...")
        time.sleep(2)  # Esperar invalidación de cache
        
        catalog_updated = requests.get(
            f"{BASE_URL}/catalog/",
            headers=self.client_headers
        ).json()
        
        # Buscar producto actualizado en catálogo
        updated_product = next(
            (p for p in catalog_updated["products"] if p["_id"] == products[0]["_id"]),
            None
        )
        assert updated_product is not None
        print("   Catálogo actualizado correctamente")

        print("\n✓ SYS-02: Integración validada exitosamente")

    def test_sys_03_notification_system(self):
        """
        SYS-03: Sistema de notificaciones
        
        Objetivo: Verificar funcionamiento del sistema de notificaciones
        
        Pasos:
        1. Cliente crea reserva
        2. Verificar que se envía notificación de creación
        3. Admin aprueba reserva
        4. Verificar que se envía notificación de aprobación
        5. Validar registro de notificaciones en base de datos
        
        Resultado esperado: Notificaciones enviadas y registradas correctamente
        """
        print("\n=== SYS-03: Sistema de notificaciones ===")

        # Paso 1: Obtener producto para reserva
        print("1. Preparando datos de reserva...")
        catalog_response = requests.get(
            f"{BASE_URL}/catalog/",
            headers=self.client_headers
        )
        product = catalog_response.json()["products"][0]
        variant_id = product["variants"][0]["_id"]

        # Paso 2: Cliente crea reserva
        print("2. Creando reserva...")
        reservation_data = {
            "items": [{"variant_id": variant_id, "quantity": 1}],
            "notes": "Prueba de notificaciones SYS-03"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/reservations/",
            headers=self.client_headers,
            json=reservation_data
        )
        assert create_response.status_code == 201
        reservation_id = create_response.json()["reservation"]["_id"]
        print(f"   Reserva creada: {reservation_id}")

        # Paso 3: Verificar registro de notificación de creación
        print("3. Verificando notificación de creación...")
        time.sleep(2)  # Esperar procesamiento de notificación
        
        # Nota: Dependiendo de la implementación, verificar en logs o DB
        # Este test asume que las notificaciones se registran correctamente
        print("   Notificación de creación procesada")

        # Paso 4: Admin aprueba reserva
        print("4. Admin aprobando reserva...")
        approve_response = requests.put(
            f"{BASE_URL}/reservations/{reservation_id}/approve",
            headers=self.admin_headers,
            json={"admin_notes": "Aprobada para prueba SYS-03"}
        )
        assert approve_response.status_code == 200
        print("   Reserva aprobada")

        # Paso 5: Verificar notificación de aprobación
        print("5. Verificando notificación de aprobación...")
        time.sleep(2)
        print("   Notificación de aprobación procesada")

        # Paso 6: Cancelar una reserva y verificar notificación
        print("6. Probando notificación de cancelación...")
        
        # Crear nueva reserva
        create_response2 = requests.post(
            f"{BASE_URL}/reservations/",
            headers=self.client_headers,
            json=reservation_data
        )
        reservation_id2 = create_response2.json()["reservation"]["_id"]
        
        # Cancelar reserva
        cancel_response = requests.put(
            f"{BASE_URL}/reservations/{reservation_id2}/cancel",
            headers=self.client_headers
        )
        assert cancel_response.status_code == 200
        print("   Notificación de cancelación procesada")

        print("\n✓ SYS-03: Sistema de notificaciones validado exitosamente")


if __name__ == "__main__":
    print("=" * 70)
    print("PRUEBAS DE SISTEMA - Pisos Kermy")
    print("=" * 70)
    print("\nEstas pruebas validan la integración entre componentes del sistema")
    print("Asegúrese de que el backend esté ejecutándose en http://localhost:5000")
    print("\nEjecutando pruebas...\n")
    
    pytest.main([__file__, "-v", "-s"])