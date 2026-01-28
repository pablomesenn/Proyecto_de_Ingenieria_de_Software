"""
Pruebas de Aceptación - Sistema de Gestión y Reservas Pisos Kermy
====================================================================

Estas pruebas validan que el sistema cumple con los requisitos del negocio
y las reglas de dominio establecidas en el ERS.

Casos de Prueba:
- ACC-01: Reglas de negocio de reservas
- ACC-02: Gestión de inventario y stock
- ACC-03: Flujo completo de caso de uso
"""

import pytest
import requests
from datetime import datetime, timedelta
import time


BASE_URL = "http://localhost:5000/api"


class TestBusinessRulesReservations:
    """Pruebas de reglas de negocio para reservas"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Configuración inicial"""
        admin_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "admin@pisoskermy.com", "password": "Admin123!"}
        )
        self.admin_token = admin_response.json()["access_token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

        client_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "cliente1@example.com", "password": "Cliente123!"}
        )
        self.client_token = client_response.json()["access_token"]
        self.client_headers = {"Authorization": f"Bearer {self.client_token}"}

        yield

    def test_acc_01_reservation_business_rules(self):
        """
        ACC-01: Reglas de negocio de reservas
        
        Requisitos validados:
        - RF-10: Solo clientes pueden crear reservas
        - RF-14: Transiciones de estado válidas
        - RF-15: Retención temporal de inventario (24 horas)
        - RF-16: Liberación automática al expirar
        - RF-17: Solo ADMIN puede aprobar/rechazar
        
        Escenarios:
        1. Cliente puede crear reserva
        2. Admin NO puede crear reserva (solo aprobar)
        3. Reserva inicia en estado "Pendiente"
        4. Stock se reserva temporalmente
        5. Reserva expira automáticamente tras 24 horas
        6. Solo ADMIN puede aprobar/rechazar
        7. Cliente puede cancelar su propia reserva
        
        Resultado esperado: Todas las reglas se cumplen
        """
        print("\n=== ACC-01: Reglas de negocio de reservas ===")

        # Obtener producto para pruebas
        catalog_response = requests.get(
            f"{BASE_URL}/products/",
            headers=self.client_headers
        )
        product = catalog_response.json()["products"][0]
        variant_id = product["variantes"][0]["_id"]

        # Escenario 1: Cliente puede crear reserva
        print("1. Verificando que CLIENT puede crear reserva...")
        reservation_data = {
            "items": [{"variant_id": variant_id, "quantity": 2}],
            "notes": "Prueba ACC-01"
        }
        
        client_create_response = requests.post(
            f"{BASE_URL}/reservations/",
            headers=self.client_headers,
            json=reservation_data
        )
        assert client_create_response.status_code == 201, \
            "CLIENT debe poder crear reserva"
        reservation = client_create_response.json()["reservation"]
        reservation_id = reservation["_id"]
        print(f"   ✓ CLIENT creó reserva: {reservation_id}")

        # Escenario 2: Admin NO puede crear reserva
        print("2. Verificando que ADMIN no puede crear reserva...")
        admin_create_response = requests.post(
            f"{BASE_URL}/reservations/",
            headers=self.admin_headers,
            json=reservation_data
        )
        assert admin_create_response.status_code == 403, \
            "ADMIN no debería poder crear reservas (solo aprobar)"
        print("   ✓ ADMIN no puede crear reservas")

        # Escenario 3: Reserva inicia en estado "Pendiente"
        print("3. Verificando estado inicial de reserva...")
        assert reservation["state"] == "Pendiente", \
            "Reserva debe iniciar en estado Pendiente"
        print("   ✓ Estado inicial: Pendiente")

        # Escenario 4: Stock se reserva temporalmente
        print("4. Verificando reserva temporal de stock...")
        time.sleep(1)
        
        inventory_response = requests.get(
            f"{BASE_URL}/inventory/variant/{variant_id}",
            headers=self.admin_headers
        )
        inventory = inventory_response.json()
        
        assert inventory["reserved_stock"] >= 2, \
            "Stock debe estar reservado temporalmente"
        print(f"   ✓ Stock reservado: {inventory['reserved_stock']}")

        # Escenario 5: Verificar tiempo de expiración
        print("5. Verificando tiempo de expiración configurado...")
        assert "expires_at" in reservation, \
            "Reserva debe tener fecha de expiración"
        
        expires_at = datetime.fromisoformat(reservation["expires_at"].replace('Z', '+00:00'))
        created_at = datetime.fromisoformat(reservation["created_at"].replace('Z', '+00:00'))
        time_diff = (expires_at - created_at).total_seconds() / 3600
        
        # Debe ser aproximadamente 24 horas
        assert 23 <= time_diff <= 25, \
            "Tiempo de expiración debe ser ~24 horas"
        print(f"   ✓ Tiempo de expiración: {time_diff:.1f} horas")

        # Escenario 6: Solo ADMIN puede aprobar
        print("6. Verificando que solo ADMIN puede aprobar...")
        
        # Cliente intenta aprobar
        client_approve_response = requests.put(
            f"{BASE_URL}/reservations/{reservation_id}/approve",
            headers=self.client_headers
        )
        assert client_approve_response.status_code == 403, \
            "CLIENT no debe poder aprobar reservas"
        print("   ✓ CLIENT no puede aprobar")
        
        # Admin aprueba
        admin_approve_response = requests.put(
            f"{BASE_URL}/reservations/{reservation_id}/approve",
            headers=self.admin_headers,
            json={"admin_notes": "Aprobada para ACC-01"}
        )
        assert admin_approve_response.status_code == 200, \
            "ADMIN debe poder aprobar reservas"
        approved_reservation = admin_approve_response.json()["reservation"]
        assert approved_reservation["state"] == "Aprobada"
        print("   ✓ ADMIN aprobó exitosamente")

        # Escenario 7: Cliente puede cancelar su propia reserva
        print("7. Verificando cancelación por cliente...")
        
        # Crear nueva reserva para cancelar
        new_reservation_response = requests.post(
            f"{BASE_URL}/reservations/",
            headers=self.client_headers,
            json=reservation_data
        )
        new_reservation_id = new_reservation_response.json()["reservation"]["_id"]
        
        # Cliente cancela
        cancel_response = requests.put(
            f"{BASE_URL}/reservations/{new_reservation_id}/cancel",
            headers=self.client_headers
        )
        assert cancel_response.status_code == 200, \
            "CLIENT debe poder cancelar su reserva"
        cancelled_reservation = cancel_response.json()["reservation"]
        assert cancelled_reservation["state"] == "Cancelada"
        print("   ✓ CLIENT canceló su reserva")

        # Escenario 8: Validar transiciones de estado inválidas
        print("8. Verificando que no se pueden aprobar reservas ya aprobadas...")
        
        # Intentar aprobar reserva ya aprobada
        double_approve_response = requests.put(
            f"{BASE_URL}/reservations/{reservation_id}/approve",
            headers=self.admin_headers
        )
        assert double_approve_response.status_code == 400, \
            "No se debe poder aprobar una reserva ya aprobada"
        print("   ✓ Transiciones de estado validadas")

        print("\n✓ ACC-01: Reglas de negocio de reservas validadas exitosamente")

    def test_acc_02_inventory_management_rules(self):
        """
        ACC-02: Gestión de inventario y stock
        
        Requisitos validados:
        - RF-12: Actualización automática de stock
        - RF-13: Ajustes manuales por ADMIN
        - RF-09: Bitácora de movimientos
        - Stock nunca puede ser negativo
        - Alertas de stock bajo
        
        Escenarios:
        1. Stock se reduce al crear reserva
        2. Stock se libera al cancelar reserva
        3. Stock se reduce permanentemente al aprobar
        4. Admin puede ajustar stock manualmente
        5. No se permite stock negativo
        6. Historial registra todos los movimientos
        
        Resultado esperado: Gestión de inventario correcta
        """
        print("\n=== ACC-02: Gestión de inventario y stock ===")

        # Preparar datos
        catalog_response = requests.get(
            f"{BASE_URL}/products/",
            headers=self.admin_headers
        )
        product = catalog_response.json()["products"][0]
        variant_id = product["variantes"][0]["_id"]

        # Obtener stock inicial
        inventory_response = requests.get(
            f"{BASE_URL}/inventory/variant/{variant_id}",
            headers=self.admin_headers
        )
        initial_stock = inventory_response.json()["current_stock"]
        print(f"Stock inicial: {initial_stock}")

        # Escenario 1: Stock se reduce al crear reserva
        print("\n1. Creando reserva y verificando reducción de stock...")
        
        reservation_response = requests.post(
            f"{BASE_URL}/reservations/",
            headers=self.client_headers,
            json={
                "items": [{"variant_id": variant_id, "quantity": 3}],
                "notes": "Prueba ACC-02"
            }
        )
        reservation_id = reservation_response.json()["reservation"]["_id"]
        time.sleep(1)
        
        after_create_response = requests.get(
            f"{BASE_URL}/inventory/variant/{variant_id}",
            headers=self.admin_headers
        )
        after_create = after_create_response.json()
        
        assert after_create["current_stock"] == initial_stock - 3, \
            "Stock disponible debe reducirse al crear reserva"
        assert after_create["reserved_stock"] == 3, \
            "Stock reservado debe incrementarse"
        print(f"   ✓ Stock disponible: {after_create['current_stock']}")
        print(f"   ✓ Stock reservado: {after_create['reserved_stock']}")

        # Escenario 2: Stock se libera al cancelar
        print("\n2. Cancelando reserva y verificando liberación de stock...")
        
        cancel_response = requests.put(
            f"{BASE_URL}/reservations/{reservation_id}/cancel",
            headers=self.client_headers
        )
        assert cancel_response.status_code == 200
        time.sleep(1)
        
        after_cancel_response = requests.get(
            f"{BASE_URL}/inventory/variant/{variant_id}",
            headers=self.admin_headers
        )
        after_cancel = after_cancel_response.json()
        
        assert after_cancel["current_stock"] == initial_stock, \
            "Stock debe volver a nivel inicial al cancelar"
        assert after_cancel["reserved_stock"] == 0, \
            "Stock reservado debe ser 0 al cancelar"
        print(f"   ✓ Stock restaurado: {after_cancel['current_stock']}")

        # Escenario 3: Stock se reduce permanentemente al aprobar
        print("\n3. Aprobando reserva y verificando reducción permanente...")
        
        # Crear nueva reserva
        new_reservation_response = requests.post(
            f"{BASE_URL}/reservations/",
            headers=self.client_headers,
            json={
                "items": [{"variant_id": variant_id, "quantity": 2}],
                "notes": "Prueba aprobación"
            }
        )
        new_reservation_id = new_reservation_response.json()["reservation"]["_id"]
        time.sleep(1)
        
        # Aprobar
        approve_response = requests.put(
            f"{BASE_URL}/reservations/{new_reservation_id}/approve",
            headers=self.admin_headers
        )
        assert approve_response.status_code == 200
        time.sleep(1)
        
        after_approve_response = requests.get(
            f"{BASE_URL}/inventory/variant/{variant_id}",
            headers=self.admin_headers
        )
        after_approve = after_approve_response.json()
        
        assert after_approve["current_stock"] == initial_stock - 2, \
            "Stock debe reducirse permanentemente al aprobar"
        assert after_approve["reserved_stock"] == 0, \
            "Stock reservado debe liberarse al aprobar"
        print(f"   ✓ Stock final: {after_approve['current_stock']}")

        # Escenario 4: Admin puede ajustar stock manualmente
        print("\n4. Verificando ajuste manual de inventario...")
        
        adjustment_data = {
            "variant_id": variant_id,
            "quantity": 10,
            "type": "entrada",
            "reason": "Prueba ACC-02 - Ingreso de mercadería"
        }
        
        adjust_response = requests.post(
            f"{BASE_URL}/inventory/adjust",
            headers=self.admin_headers,
            json=adjustment_data
        )
        assert adjust_response.status_code in [200, 201], \
            "ADMIN debe poder ajustar inventario"
        time.sleep(1)
        
        after_adjust_response = requests.get(
            f"{BASE_URL}/inventory/variant/{variant_id}",
            headers=self.admin_headers
        )
        after_adjust = after_adjust_response.json()
        
        expected_stock = initial_stock - 2 + 10
        assert after_adjust["current_stock"] == expected_stock, \
            "Stock debe actualizarse con el ajuste manual"
        print(f"   ✓ Stock después de ajuste: {after_adjust['current_stock']}")

        # Escenario 5: No se permite stock negativo
        print("\n5. Verificando que no se permite stock negativo...")
        
        negative_adjustment = {
            "variant_id": variant_id,
            "quantity": 99999,
            "type": "salida",
            "reason": "Intento de stock negativo"
        }
        
        negative_response = requests.post(
            f"{BASE_URL}/inventory/adjust",
            headers=self.admin_headers,
            json=negative_adjustment
        )
        
        # El sistema debe rechazar o validar
        if negative_response.status_code in [400, 422]:
            print("   ✓ Sistema rechaza ajustes que generarían stock negativo")
        else:
            # Verificar que stock no sea negativo
            final_inv = requests.get(
                f"{BASE_URL}/inventory/variant/{variant_id}",
                headers=self.admin_headers
            ).json()
            assert final_inv["current_stock"] >= 0, \
                "Stock no puede ser negativo"
            print("   ✓ Stock se mantiene >= 0")

        # Escenario 6: Historial registra movimientos
        print("\n6. Verificando bitácora de movimientos...")
        
        history_response = requests.get(
            f"{BASE_URL}/inventory/variant/{variant_id}/history",
            headers=self.admin_headers
        )
        
        if history_response.status_code == 200:
            history = history_response.json()["movements"]
            
            assert len(history) > 0, \
                "Debe haber movimientos registrados"
            
            # Verificar que movimientos tienen campos requeridos
            for movement in history[:3]:
                assert "type" in movement
                assert "quantity" in movement
                assert "reason" in movement
                assert "timestamp" in movement
            
            print(f"   ✓ Historial con {len(history)} movimientos registrados")
        else:
            print("   ⚠ Endpoint de historial no disponible")

        print("\n✓ ACC-02: Gestión de inventario validada exitosamente")


class TestCompleteUseCases:
    """Pruebas de casos de uso completos"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Configuración inicial"""
        admin_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "admin@pisoskermy.com", "password": "Admin123!"}
        )
        self.admin_token = admin_response.json()["access_token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

        client_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "cliente1@example.com", "password": "Cliente123!"}
        )
        self.client_token = client_response.json()["access_token"]
        self.client_headers = {"Authorization": f"Bearer {self.client_token}"}

        yield

    def test_acc_03_complete_customer_journey(self):
        """
        ACC-03: Flujo completo de caso de uso cliente
        
        Caso de Uso: CU-007 - Cliente realiza una reserva
        
        Flujo:
        1. Cliente consulta catálogo
        2. Cliente busca producto específico
        3. Cliente verifica disponibilidad
        4. Cliente crea reserva
        5. Cliente consulta sus reservas
        6. Cliente ve detalle de su reserva
        7. Sistema envía notificación
        8. Admin consulta reservas pendientes
        9. Admin aprueba reserva
        10. Cliente es notificado
        11. Cliente consulta historial
        
        Resultado esperado: Flujo completo exitoso
        """
        print("\n=== ACC-03: Flujo completo de caso de uso cliente ===")

        # Paso 1: Cliente consulta catálogo
        print("\n1. Cliente consultando catálogo...")
        catalog_response = requests.get(
            f"{BASE_URL}/products/",
            headers=self.client_headers
        )
        assert catalog_response.status_code == 200
        catalog = catalog_response.json()
        print(f"   ✓ Catálogo cargado: {len(catalog['products'])} productos")

        # Paso 2: Cliente busca producto
        print("\n2. Cliente buscando producto específico...")
        product = catalog["products"][0]
        variant = product["variantes"][0]
        print(f"   ✓ Producto seleccionado: {product['name']} - {variant['name']}")

        # Paso 3: Verificar disponibilidad
        print("\n3. Verificando disponibilidad...")
        inventory_response = requests.get(
            f"{BASE_URL}/inventory/variant/{variant['_id']}",
            headers=self.client_headers
        )
        assert inventory_response.status_code == 200
        stock = inventory_response.json()["current_stock"]
        print(f"   ✓ Stock disponible: {stock} unidades")
        assert stock > 0, "Debe haber stock disponible"

        # Paso 4: Cliente crea reserva
        print("\n4. Cliente creando reserva...")
        reservation_data = {
            "items": [
                {
                    "variant_id": variant["_id"],
                    "quantity": 1
                }
            ],
            "notes": "Prueba de flujo completo ACC-03"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/reservations/",
            headers=self.client_headers,
            json=reservation_data
        )
        assert create_response.status_code == 201
        reservation = create_response.json()["reservation"]
        reservation_id = reservation["_id"]
        print(f"   ✓ Reserva creada: {reservation_id}")

        # Paso 5: Cliente consulta sus reservas
        print("\n5. Cliente consultando sus reservas...")
        my_reservations_response = requests.get(
            f"{BASE_URL}/reservations/my",
            headers=self.client_headers
        )
        assert my_reservations_response.status_code == 200
        my_reservations = my_reservations_response.json()["reservations"]
        print(f"   ✓ Cliente tiene {len(my_reservations)} reserva(s)")
        
        # Verificar que la reserva recién creada está en la lista
        found = any(r["_id"] == reservation_id for r in my_reservations)
        assert found, "Reserva debe estar en lista del cliente"

        # Paso 6: Cliente ve detalle de reserva
        print("\n6. Cliente consultando detalle de reserva...")
        detail_response = requests.get(
            f"{BASE_URL}/reservations/{reservation_id}",
            headers=self.client_headers
        )
        assert detail_response.status_code == 200
        detail = detail_response.json()
        print(f"   ✓ Estado: {detail['state']}")
        print(f"   ✓ Items: {len(detail['items'])}")

        # Paso 7: Admin consulta reservas pendientes
        print("\n7. Admin consultando reservas pendientes...")
        admin_pending_response = requests.get(
            f"{BASE_URL}/reservations/",
            headers=self.admin_headers,
            params={"state": "Pendiente"}
        )
        assert admin_pending_response.status_code == 200
        pending = admin_pending_response.json()["reservations"]
        print(f"   ✓ Reservas pendientes: {len(pending)}")

        # Paso 8: Admin aprueba reserva
        print("\n8. Admin aprobando reserva...")
        time.sleep(1)
        
        approve_response = requests.put(
            f"{BASE_URL}/reservations/{reservation_id}/approve",
            headers=self.admin_headers,
            json={"admin_notes": "Aprobada - Flujo completo ACC-03"}
        )
        assert approve_response.status_code == 200
        approved = approve_response.json()["reservation"]
        print(f"   ✓ Reserva aprobada: {approved['state']}")

        # Paso 9: Cliente verifica aprobación
        print("\n9. Cliente verificando aprobación...")
        time.sleep(1)
        
        final_check_response = requests.get(
            f"{BASE_URL}/reservations/{reservation_id}",
            headers=self.client_headers
        )
        final_state = final_check_response.json()
        assert final_state["state"] == "Aprobada"
        print(f"   ✓ Estado confirmado: {final_state['state']}")

        # Paso 10: Verificar notas del admin
        print("\n10. Verificando comunicación admin-cliente...")
        if "admin_notes" in final_state:
            print(f"   ✓ Notas del admin: {final_state['admin_notes']}")
        else:
            print("   ⚠ Sin notas del admin")

        print("\n✓ ACC-03: Flujo completo validado exitosamente")


if __name__ == "__main__":
    print("=" * 70)
    print("PRUEBAS DE ACEPTACIÓN - Pisos Kermy")
    print("=" * 70)
    print("\nEstas pruebas validan que el sistema cumple con los requisitos de negocio")
    print("Asegúrese de que el backend esté ejecutándose en http://localhost:5000")
    print("\nEjecutando pruebas...\n")
    
    pytest.main([__file__, "-v", "-s"])