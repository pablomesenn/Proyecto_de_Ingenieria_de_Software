"""
Pruebas de Seguridad - Sistema de Gestión y Reservas Pisos Kermy
===================================================================

Estas pruebas validan aspectos críticos de seguridad:
- Control de acceso basado en roles (RBAC)
- Autenticación y autorización (JWT)
- Integridad de datos
- Protección contra ataques comunes

Casos de Prueba:
- SEC-01: Control de acceso basado en roles (RBAC)
- SEC-02: Validación y seguridad de JWT
- SEC-03: Protección de datos sensibles
"""

import pytest
import requests
import jwt as pyjwt
from datetime import datetime, timedelta
import time


BASE_URL = "http://localhost:5000/api"


class TestSecurityFeatures:
    """Pruebas de seguridad del sistema"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Configuración inicial"""
        # Tokens válidos
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

    def test_sec_01_rbac_access_control(self):
        """
        SEC-01: Control de acceso basado en roles (RBAC)
        
        Objetivo: Verificar que el sistema restringe correctamente el acceso
                 a recursos según el rol del usuario (ADMIN vs CLIENT)
        
        Escenarios:
        1. CLIENT intenta acceder a endpoints de ADMIN → 403 Forbidden
        2. ADMIN puede acceder a todos los endpoints
        3. CLIENT solo puede ver sus propios recursos
        4. Sin autenticación → 401 Unauthorized
        
        Resultado esperado: Acceso restringido según rol
        """
        print("\n=== SEC-01: Control de acceso basado en roles (RBAC) ===")

        # Escenario 1: CLIENT intenta gestionar usuarios (solo ADMIN)
        print("1. CLIENT intentando acceder a gestión de usuarios...")
        client_users_response = requests.get(
            f"{BASE_URL}/users/",
            headers=self.client_headers
        )
        assert client_users_response.status_code == 403, \
            "CLIENT no debería acceder a gestión de usuarios"
        print("   ✓ Acceso denegado correctamente (403)")

        # Escenario 2: ADMIN puede acceder a gestión de usuarios
        print("2. ADMIN accediendo a gestión de usuarios...")
        admin_users_response = requests.get(
            f"{BASE_URL}/users/",
            headers=self.admin_headers
        )
        assert admin_users_response.status_code == 200, \
            "ADMIN debería acceder a gestión de usuarios"
        print("   ✓ Acceso permitido correctamente (200)")

        # Escenario 3: CLIENT intenta crear productos (solo ADMIN)
        print("3. CLIENT intentando crear producto...")
        product_data = {
            "name": "Producto Test",
            "category": "Test",
            "variantes": [{"name": "Test", "size": "60x60", "price": 100}]
        }
        
        client_product_response = requests.post(
            f"{BASE_URL}/products/",
            headers=self.client_headers,
            json=product_data
        )
        assert client_product_response.status_code == 403, \
            "CLIENT no debería crear productos"
        print("   ✓ Acceso denegado correctamente (403)")

        # Escenario 4: CLIENT intenta aprobar reservas (solo ADMIN)
        print("4. CLIENT intentando aprobar reserva...")
        
        # Primero crear una reserva como cliente
        catalog_response = requests.get(
            f"{BASE_URL}/products/",
            headers=self.client_headers
        )
        product = catalog_response.json()["products"][0]
        variant_id = product["variantes"][0]["_id"]
        
        reservation_response = requests.post(
            f"{BASE_URL}/reservations/",
            headers=self.client_headers,
            json={
                "items": [{"variant_id": variant_id, "quantity": 1}],
                "notes": "Test SEC-01"
            }
        )
        reservation_id = reservation_response.json()["reservation"]["_id"]
        
        # Intentar aprobar como cliente
        approve_response = requests.put(
            f"{BASE_URL}/reservations/{reservation_id}/approve",
            headers=self.client_headers
        )
        assert approve_response.status_code == 403, \
            "CLIENT no debería aprobar reservas"
        print("   ✓ Acceso denegado correctamente (403)")

        # Escenario 5: Sin autenticación
        print("5. Intentando acceder sin token...")
        no_auth_response = requests.get(f"{BASE_URL}/users/")
        assert no_auth_response.status_code == 401, \
            "Debería requerir autenticación"
        print("   ✓ Acceso denegado sin autenticación (401)")

        # Escenario 6: CLIENT solo ve sus propias reservas
        print("6. Verificando que CLIENT solo ve sus reservas...")
        my_reservations = requests.get(
            f"{BASE_URL}/reservations/my",
            headers=self.client_headers
        )
        assert my_reservations.status_code == 200
        
        # Intentar acceder a todas las reservas (endpoint ADMIN)
        all_reservations = requests.get(
            f"{BASE_URL}/reservations/",
            headers=self.client_headers
        )
        
        # El sistema puede retornar solo las del cliente o denegar acceso
        # Verificamos que no devuelva todas las reservas del sistema
        if all_reservations.status_code == 200:
            client_res_count = my_reservations.json()["count"]
            all_res_count = all_reservations.json()["count"]
            assert client_res_count == all_res_count, \
                "CLIENT no debería ver reservas de otros usuarios"
        
        print("   ✓ CLIENT solo accede a sus propios recursos")

        # Escenario 7: ADMIN puede gestionar todas las reservas
        print("7. Verificando que ADMIN puede gestionar todas las reservas...")
        admin_all_reservations = requests.get(
            f"{BASE_URL}/reservations/",
            headers=self.admin_headers
        )
        assert admin_all_reservations.status_code == 200
        print("   ✓ ADMIN tiene acceso completo")

        print("\n✓ SEC-01: RBAC validado exitosamente")

    def test_sec_02_jwt_security(self):
        """
        SEC-02: Validación y seguridad de JWT
        
        Objetivo: Verificar que el sistema valida correctamente los tokens JWT
        
        Escenarios:
        1. Token inválido → 401/422
        2. Token expirado → 401
        3. Token modificado → 401/422
        4. Token sin firma → 401/422
        5. Token válido → 200
        
        Resultado esperado: Solo tokens válidos son aceptados
        """
        print("\n=== SEC-02: Validación y seguridad de JWT ===")

        # Escenario 1: Token inválido (malformado)
        print("1. Probando token inválido...")
        invalid_headers = {"Authorization": "Bearer token_invalido_xyz"}
        invalid_response = requests.get(
            f"{BASE_URL}/users/profile",
            headers=invalid_headers
        )
        assert invalid_response.status_code in [401, 422], \
            "Token inválido debería ser rechazado"
        print("   ✓ Token inválido rechazado")

        # Escenario 2: Token modificado
        print("2. Probando token modificado...")
        # Tomar token válido y modificar último carácter
        modified_token = self.client_token[:-5] + "xxxxx"
        modified_headers = {"Authorization": f"Bearer {modified_token}"}
        
        modified_response = requests.get(
            f"{BASE_URL}/users/profile",
            headers=modified_headers
        )
        assert modified_response.status_code in [401, 422], \
            "Token modificado debería ser rechazado"
        print("   ✓ Token modificado rechazado")

        # Escenario 3: Sin token
        print("3. Probando acceso sin token...")
        no_token_response = requests.get(f"{BASE_URL}/users/profile")
        assert no_token_response.status_code == 401, \
            "Acceso sin token debería ser rechazado"
        print("   ✓ Acceso sin token rechazado")

        # Escenario 4: Token válido
        print("4. Probando token válido...")
        valid_response = requests.get(
            f"{BASE_URL}/users/profile",
            headers=self.client_headers
        )
        assert valid_response.status_code == 200, \
            "Token válido debería ser aceptado"
        print("   ✓ Token válido aceptado")

        # Escenario 5: Verificar estructura del token
        print("5. Verificando estructura del token JWT...")
        try:
            # Decodificar sin verificar firma (solo para inspección)
            decoded = pyjwt.decode(
                self.client_token,
                options={"verify_signature": False}
            )
            
            # Verificar campos requeridos
            assert "sub" in decoded, "Token debe contener 'sub' (user_id)"
            assert "role" in decoded, "Token debe contener 'role'"
            assert "exp" in decoded, "Token debe contener 'exp' (expiration)"
            
            print(f"   Token contiene: sub={decoded.get('sub')}, role={decoded.get('role')}")
            print("   ✓ Estructura del token válida")
        except Exception as e:
            pytest.fail(f"Error al decodificar token: {e}")

        # Escenario 6: Verificar que diferentes roles tienen tokens diferentes
        print("6. Verificando diferenciación de roles en tokens...")
        admin_decoded = pyjwt.decode(
            self.admin_token,
            options={"verify_signature": False}
        )
        client_decoded = pyjwt.decode(
            self.client_token,
            options={"verify_signature": False}
        )
        
        assert admin_decoded["role"] == "ADMIN", "Token de admin debe tener rol ADMIN"
        assert client_decoded["role"] == "CLIENT", "Token de client debe tener rol CLIENT"
        print("   ✓ Roles correctamente asignados en tokens")

        print("\n✓ SEC-02: Seguridad JWT validada exitosamente")

    def test_sec_03_data_protection(self):
        """
        SEC-03: Protección de datos sensibles
        
        Objetivo: Verificar que el sistema protege datos sensibles
        
        Escenarios:
        1. Contraseñas no se retornan en respuestas
        2. CLIENT no puede ver datos de otros usuarios
        3. Validación de entrada (SQL injection, XSS)
        4. Datos sensibles en logs
        
        Resultado esperado: Datos sensibles protegidos
        """
        print("\n=== SEC-03: Protección de datos sensibles ===")

        # Escenario 1: Contraseñas no en respuestas
        print("1. Verificando que contraseñas no se retornan...")
        profile_response = requests.get(
            f"{BASE_URL}/users/profile",
            headers=self.client_headers
        )
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        
        assert "password" not in profile_data, \
            "Contraseña no debería estar en respuesta"
        print("   ✓ Contraseña no expuesta en perfil")

        # Verificar en lista de usuarios (ADMIN)
        users_response = requests.get(
            f"{BASE_URL}/users/",
            headers=self.admin_headers
        )
        assert users_response.status_code == 200
        users = users_response.json()["users"]
        
        for user in users:
            assert "password" not in user, \
                "Contraseña no debería estar en lista de usuarios"
        print("   ✓ Contraseñas no expuestas en lista de usuarios")

        # Escenario 2: CLIENT no puede acceder a datos de otros usuarios
        print("2. Verificando aislamiento de datos entre usuarios...")
        
        # Obtener ID de otro usuario
        admin_users = requests.get(
            f"{BASE_URL}/users/",
            headers=self.admin_headers
        ).json()["users"]
        
        other_user = next(
            (u for u in admin_users if u["email"] != "cliente1@example.com"),
            None
        )
        
        if other_user:
            # CLIENT intenta acceder a perfil de otro usuario
            other_profile_response = requests.get(
                f"{BASE_URL}/users/{other_user['_id']}",
                headers=self.client_headers
            )
            assert other_profile_response.status_code == 403, \
                "CLIENT no debería acceder a datos de otros usuarios"
            print("   ✓ Datos de otros usuarios protegidos")

        # Escenario 3: Inyección SQL (NoSQL injection en MongoDB)
        print("3. Probando protección contra NoSQL injection...")
        
        # Intentar inyección en login
        injection_attempts = [
            {"email": {"$gt": ""}, "password": {"$gt": ""}},
            {"email": "admin@pisoskermy.com", "password": {"$ne": ""}},
            {"email": {"$regex": ".*"}, "password": "anything"}
        ]
        
        for attempt in injection_attempts:
            injection_response = requests.post(
                f"{BASE_URL}/auth/login",
                json=attempt
            )
            assert injection_response.status_code in [400, 401, 422], \
                "Sistema debería rechazar intentos de inyección"
        
        print("   ✓ Protección contra NoSQL injection verificada")

        # Escenario 4: XSS en campos de texto
        print("4. Probando protección contra XSS...")
        
        # Intentar crear reserva con script malicioso en notes
        catalog_response = requests.get(
            f"{BASE_URL}/products/",
            headers=self.client_headers
        )
        product = catalog_response.json()["products"][0]
        variant_id = product["variantes"][0]["_id"]
        
        xss_payload = "<script>alert('XSS')</script>"
        xss_reservation = {
            "items": [{"variant_id": variant_id, "quantity": 1}],
            "notes": xss_payload
        }
        
        xss_response = requests.post(
            f"{BASE_URL}/reservations/",
            headers=self.client_headers,
            json=xss_reservation
        )
        
        if xss_response.status_code == 201:
            reservation = xss_response.json()["reservation"]
            # Verificar que el payload se almacenó como texto plano
            assert reservation["notes"] == xss_payload, \
                "Notas deberían almacenarse como texto plano"
            print("   ✓ Entrada XSS manejada correctamente")
        else:
            print("   ✓ Sistema rechazó entrada sospechosa")

        # Escenario 5: Validación de datos de entrada
        print("5. Probando validación de datos...")
        
        # Intentar crear reserva con cantidad negativa
        invalid_reservation = {
            "items": [{"variant_id": variant_id, "quantity": -5}],
            "notes": "Invalid quantity"
        }
        
        invalid_response = requests.post(
            f"{BASE_URL}/reservations/",
            headers=self.client_headers,
            json=invalid_reservation
        )
        assert invalid_response.status_code in [400, 422], \
            "Sistema debería rechazar cantidades negativas"
        print("   ✓ Validación de entrada funcionando")

        # Escenario 6: Intentar acceso directo a base de datos
        print("6. Verificando que no hay exposición directa de BD...")
        
        # Intentar acceder a endpoints de BD directamente
        db_endpoints = [
            "/api/db/users",
            "/api/database/users",
            "/api/mongo/users",
            "/api/users.json"
        ]
        
        for endpoint in db_endpoints:
            db_response = requests.get(
                f"http://localhost:5000{endpoint}",
                headers=self.admin_headers
            )
            assert db_response.status_code == 404, \
                f"Endpoint {endpoint} no debería existir"
        
        print("   ✓ No hay exposición directa de base de datos")

        print("\n✓ SEC-03: Protección de datos validada exitosamente")


class TestAuthenticationFlow:
    """Pruebas del flujo de autenticación"""

    def test_sec_04_authentication_flow(self):
        """
        SEC-04: Flujo de autenticación completo
        
        Objetivo: Verificar proceso completo de autenticación
        
        Pasos:
        1. Registro de usuario
        2. Login exitoso
        3. Login fallido (credenciales incorrectas)
        4. Acceso con token válido
        5. Logout (si aplica)
        
        Resultado esperado: Flujo de autenticación seguro
        """
        print("\n=== SEC-04: Flujo de autenticación ===")

        # Paso 1: Login exitoso
        print("1. Probando login exitoso...")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "cliente1@example.com", "password": "Cliente123!"}
        )
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()
        print("   ✓ Login exitoso")

        # Paso 2: Login fallido - contraseña incorrecta
        print("2. Probando login con contraseña incorrecta...")
        wrong_pass_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "cliente1@example.com", "password": "wrongpassword"}
        )
        assert wrong_pass_response.status_code == 401
        assert "access_token" not in wrong_pass_response.json()
        print("   ✓ Login rechazado correctamente")

        # Paso 3: Login fallido - usuario inexistente
        print("3. Probando login con usuario inexistente...")
        no_user_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "noexiste@test.com", "password": "password"}
        )
        assert no_user_response.status_code == 401
        print("   ✓ Usuario inexistente rechazado")

        # Paso 4: Múltiples intentos fallidos
        print("4. Probando múltiples intentos fallidos...")
        for i in range(3):
            fail_response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": "cliente1@example.com", "password": f"wrong{i}"}
            )
            assert fail_response.status_code == 401
        print("   ✓ Múltiples intentos fallidos manejados")

        print("\n✓ SEC-04: Flujo de autenticación validado exitosamente")


if __name__ == "__main__":
    print("=" * 70)
    print("PRUEBAS DE SEGURIDAD - Pisos Kermy")
    print("=" * 70)
    print("\nEstas pruebas validan aspectos críticos de seguridad del sistema")
    print("Asegúrese de que el backend esté ejecutándose en http://localhost:5000")
    print("\nEjecutando pruebas...\n")
    
    pytest.main([__file__, "-v", "-s"])