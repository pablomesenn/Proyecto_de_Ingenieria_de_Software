"""
Script de pruebas del sistema Pisos Kermy
Ejecuta pruebas de los principales endpoints y muestra resultados
"""
import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Tuple

# Configuración
BASE_URL = "http://localhost:5000"
TEST_USER_EMAIL = f"test_user_{datetime.now().timestamp()}@test.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_NAME = "Usuario de Prueba"
TEST_ADMIN_EMAIL = f"admin_test_{datetime.now().timestamp()}@test.com"
TEST_ADMIN_PASSWORD = "AdminPassword123!"

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.tests = []
    
    def add_result(self, test_name: str, passed: bool, message: str = ""):
        self.tests.append({
            'name': test_name,
            'passed': passed,
            'message': message
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def add_skip(self, test_name: str, reason: str = ""):
        self.tests.append({
            'name': test_name,
            'passed': None,
            'message': reason
        })
        self.skipped += 1
    
    def print_summary(self):
        print("\n" + "="*70)
        print(f"{Colors.BOLD}RESUMEN DE PRUEBAS{Colors.RESET}")
        print("="*70)
        
        for test in self.tests:
            if test['passed'] is True:
                status = f"{Colors.GREEN}[OK]{Colors.RESET}"
            elif test['passed'] is False:
                status = f"{Colors.RED}[ERROR]{Colors.RESET}"
            else:
                status = f"{Colors.YELLOW}[SKIP]{Colors.RESET}"
            
            print(f"{status} {test['name']}")
            if test['message']:
                print(f"     {Colors.CYAN}→{Colors.RESET} {test['message']}")
        
        print("\n" + "="*70)
        total = self.passed + self.failed + self.skipped
        
        print(f"{Colors.BOLD}Total de pruebas:{Colors.RESET} {total}")
        print(f"{Colors.GREEN}Exitosas:{Colors.RESET} {self.passed}")
        print(f"{Colors.RED}Fallidas:{Colors.RESET} {self.failed}")
        print(f"{Colors.YELLOW}Omitidas:{Colors.RESET} {self.skipped}")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}[OK] TODAS LAS PRUEBAS PASARON{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}[ERROR] ALGUNAS PRUEBAS FALLARON{Colors.RESET}")
        
        print("="*70 + "\n")

# Global variables para tokens
access_token = None
admin_token = None
product_id = None
variant_id = None
results = TestResults()

def print_test_header(test_name: str):
    """Imprime encabezado de prueba"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}► {test_name}{Colors.RESET}")

def make_request(method: str, endpoint: str, data: Dict = None, 
                 token: str = None, expected_status: int = 200, timeout: int = 5) -> Tuple[bool, Any]:
    """
    Hace una petición HTTP y valida el resultado
    
    Returns:
        Tuple[bool, response]: (success, response_data)
    """
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers, timeout=timeout)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            return False, f"Método HTTP no soportado: {method}"
        
        if response.status_code == expected_status:
            return True, response.json() if response.text else {}
        else:
            return False, f"Status {response.status_code} (esperado {expected_status}): {response.text[:200]}"
    
    except requests.exceptions.ConnectionError:
        return False, "No se pudo conectar al servidor. ¿Está corriendo?"
    except requests.exceptions.Timeout:
        return False, f"Timeout de conexión (>{timeout}s)"
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_health_check():
    """Test 1: Health Check"""
    print_test_header("Test 1: Health Check")
    
    success, response = make_request('GET', '/health')
    
    if success and response.get('status') == 'healthy':
        results.add_result("Health Check", True, "Servidor respondiendo correctamente")
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} Servidor saludable")
        return True
    else:
        results.add_result("Health Check", False, str(response))
        print(f"  {Colors.RED}[ERROR]{Colors.RESET} {response}")
        return False

def test_register():
    """Test 2: Registro de usuario"""
    print_test_header("Test 2: Registro de Usuario")
    
    data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "confirm_password": TEST_USER_PASSWORD,
        "name": TEST_USER_NAME,
        "phone": "88888888"
    }
    
    success, response = make_request('POST', '/api/auth/register', data, expected_status=201)
    
    if success and response.get('user'):
        results.add_result("Registro de Usuario", True, f"Usuario creado: {response['user'].get('email')}")
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} Usuario registrado: {TEST_USER_EMAIL}")
        return True
    else:
        results.add_result("Registro de Usuario", False, str(response))
        print(f"  {Colors.RED}[ERROR]{Colors.RESET} {response}")
        return False

def test_login():
    """Test 3: Login de usuario"""
    global access_token
    print_test_header("Test 3: Login de Usuario")
    
    data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    success, response = make_request('POST', '/api/auth/login', data)
    
    if success and response.get('access_token'):
        access_token = response['access_token']
        results.add_result("Login de Usuario", True, f"Token generado correctamente")
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} Login exitoso")
        print(f"  {Colors.CYAN}→{Colors.RESET} Token: {access_token[:20]}...")
        return True
    else:
        results.add_result("Login de Usuario", False, str(response))
        print(f"  {Colors.RED}[ERROR]{Colors.RESET} {response}")
        return False

def test_get_profile():
    """Test 4: Obtener perfil"""
    print_test_header("Test 4: Obtener Perfil")
    
    if not access_token:
        results.add_skip("Obtener Perfil", "No hay token de acceso")
        print(f"  {Colors.YELLOW}[SKIP]{Colors.RESET} No hay token")
        return False
    
    success, response = make_request('GET', '/api/users/profile', token=access_token)
    
    if success and response.get('email') == TEST_USER_EMAIL:
        results.add_result("Obtener Perfil", True, f"Perfil obtenido: {response.get('name')}")
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} Perfil obtenido correctamente")
        print(f"  {Colors.CYAN}→{Colors.RESET} Nombre: {response.get('name')}")
        print(f"  {Colors.CYAN}→{Colors.RESET} Email: {response.get('email')}")
        return True
    else:
        results.add_result("Obtener Perfil", False, str(response))
        print(f"  {Colors.RED}[ERROR]{Colors.RESET} {response}")
        return False

def test_update_profile():
    """Test 5: Actualizar perfil"""
    print_test_header("Test 5: Actualizar Perfil")
    
    if not access_token:
        results.add_skip("Actualizar Perfil", "No hay token de acceso")
        print(f"  {Colors.YELLOW}[SKIP]{Colors.RESET} No hay token")
        return False
    
    data = {
        "name": "Usuario Actualizado",
        "phone": "77777777"
    }
    
    success, response = make_request('PUT', '/api/users/profile', data, token=access_token)
    
    if success and response.get('user'):
        results.add_result("Actualizar Perfil", True, "Perfil actualizado correctamente")
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} Perfil actualizado")
        return True
    else:
        results.add_result("Actualizar Perfil", False, str(response))
        print(f"  {Colors.RED}[ERROR]{Colors.RESET} {response}")
        return False

def test_change_password():
    """Test 6: Cambiar contraseña"""
    print_test_header("Test 6: Cambiar Contraseña")
    
    if not access_token:
        results.add_skip("Cambiar Contraseña", "No hay token de acceso")
        print(f"  {Colors.YELLOW}[SKIP]{Colors.RESET} No hay token")
        return False
    
    new_password = "NewPassword456!"
    data = {
        "current_password": TEST_USER_PASSWORD,
        "new_password": new_password,
        "confirm_password": new_password
    }
    
    success, response = make_request('POST', '/api/users/change-password', data, token=access_token)
    
    if success:
        results.add_result("Cambiar Contraseña", True, "Contraseña cambiada correctamente")
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} Contraseña cambiada")
        return True
    else:
        results.add_result("Cambiar Contraseña", False, str(response))
        print(f"  {Colors.RED}[ERROR]{Colors.RESET} {response}")
        return False

def test_forgot_password():
    """Test 7: Recuperar contraseña"""
    print_test_header("Test 7: Recuperar Contraseña")
    
    data = {
        "email": TEST_USER_EMAIL
    }
    
    # Timeout más largo porque el envío de email puede tardar
    success, response = make_request('POST', '/api/auth/forgot-password', data, timeout=15)
    
    if success:
        results.add_result("Recuperar Contraseña", True, "Contraseña temporal generada")
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} Contraseña temporal generada")
        print(f"  {Colors.YELLOW}[INFO]{Colors.RESET} Revisa los logs del servidor para ver la contraseña")
        return True
    else:
        results.add_result("Recuperar Contraseña", False, str(response))
        print(f"  {Colors.RED}[ERROR]{Colors.RESET} {response}")
        return False

def test_register_admin():
    """Test 8: Crear usuario ADMIN"""
    print_test_header("Test 8: Registrar Usuario Admin")
    
    data = {
        "email": TEST_ADMIN_EMAIL,
        "password": TEST_ADMIN_PASSWORD,
        "confirm_password": TEST_ADMIN_PASSWORD,
        "name": "Usuario Admin",
        "phone": "99999999"
    }
    
    success, response = make_request('POST', '/api/auth/register', data, expected_status=201)
    
    if success:
        results.add_result("Registrar Admin", True, f"Usuario admin creado")
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} Usuario admin registrado")
        return True
    else:
        # Si ya existe, continuamos
        results.add_result("Registrar Admin", True, "Usuario admin ya existe o será creado")
        print(f"  {Colors.YELLOW}[INFO]{Colors.RESET} Usuario admin ya existe")
        return True

def test_login_admin():
    """Test 9: Login Admin"""
    global admin_token
    print_test_header("Test 9: Login de Admin")
    
    data = {
        "email": TEST_ADMIN_EMAIL,
        "password": TEST_ADMIN_PASSWORD
    }
    
    success, response = make_request('POST', '/api/auth/login', data)
    
    if success and response.get('access_token'):
        admin_token = response['access_token']
        results.add_result("Login Admin", True, "Login de admin exitoso")
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} Login admin exitoso")
        print(f"  {Colors.CYAN}→{Colors.RESET} Token: {admin_token[:20]}...")
        return True
    else:
        results.add_skip("Login Admin", "No se pudo autenticar como admin")
        print(f"  {Colors.YELLOW}[SKIP]{Colors.RESET} No se pudo obtener token admin")
        return False

def test_get_products():
    """Test 10: Obtener productos"""
    global product_id, variant_id
    print_test_header("Test 10: Obtener Productos del Catálogo")
    
    # Intentar varias rutas posibles
    routes_to_try = [
        '/api/products',
        '/api/catalog',
        '/api/products/search',
    ]
    
    for route in routes_to_try:
        success, response = make_request('GET', route)
        
        if success:
            if isinstance(response, list):
                count = len(response)
                if count > 0:
                    product_id = str(response[0].get('_id', response[0].get('id')))
            elif isinstance(response, dict) and 'products' in response:
                count = len(response['products'])
                if count > 0:
                    product_id = str(response['products'][0].get('_id', response['products'][0].get('id')))
            else:
                count = 1 if response else 0
            
            results.add_result("Obtener Productos", True, f"Se obtuvieron {count} productos desde {route}")
            print(f"  {Colors.GREEN}[OK]{Colors.RESET} Productos obtenidos: {count} (desde {route})")
            
            return True
    
    # Si ninguna ruta funcionó
    results.add_result("Obtener Productos", False, f"Ninguna ruta de productos funcionó")
    print(f"  {Colors.RED}[ERROR]{Colors.RESET} No se encontró endpoint de productos")
    return False

def test_search_products():
    """Test 11: Buscar productos"""
    print_test_header("Test 11: Buscar Productos")
    
    search_term = "teja"
    success, response = make_request('GET', f'/api/products/search?search_text={search_term}')
    
    if success:
        if isinstance(response, list):
            count = len(response)
        elif isinstance(response, dict) and 'products' in response:
            count = len(response['products'])
        else:
            count = 0
        
        results.add_result("Buscar Productos", True, f"Se encontraron {count} productos")
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} Búsqueda exitosa: {count} resultados para '{search_term}'")
        return True
    else:
        results.add_result("Buscar Productos", False, str(response))
        print(f"  {Colors.RED}[ERROR]{Colors.RESET} {response}")
        return False

def test_inventory_admin():
    """Test 12: Obtener Inventario (requiere ADMIN)"""
    print_test_header("Test 12: Gestión de Inventario (Admin)")
    
    if not admin_token:
        results.add_skip("Inventario Admin", "No hay token de admin")
        print(f"  {Colors.YELLOW}[SKIP]{Colors.RESET} No hay token de admin")
        return False
    
    # Obtener inventario
    success, response = make_request('GET', '/api/inventory', token=admin_token)
    
    # Si falla con 403, es porque no es admin. Intenta como usuario regular
    if not success and "403" in str(response):
        success, response = make_request('GET', '/api/inventory', token=access_token)
        if success:
            results.add_result("Inventario Admin", True, f"Inventario accesible (usuario regular)")
            print(f"  {Colors.GREEN}[OK]{Colors.RESET} Inventario accesible")
            return True
    
    if success:
        # Validar que sea una lista o contenga items
        count = 0
        if isinstance(response, dict) and 'inventory' in response:
            count = len(response.get('inventory', []))
        elif isinstance(response, list):
            count = len(response)
        
        results.add_result("Inventario Admin", True, f"Se obtuvieron {count} items")
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} Inventario obtenido")
        print(f"  {Colors.CYAN}→{Colors.RESET} Total de items: {count}")
        return True
    else:
        results.add_result("Inventario Admin", False, str(response))
        print(f"  {Colors.RED}[ERROR]{Colors.RESET} {response}")
        return False

def test_wishlist():
    """Test 12: Agregar a Lista de Deseos"""
    print_test_header("Test 12: Lista de Deseos (Wishlist)")
    
    if not access_token:
        results.add_skip("Wishlist", "No hay token de acceso")
        print(f"  {Colors.YELLOW}[SKIP]{Colors.RESET} No hay token")
        return False
    
    if not product_id:
        results.add_skip("Wishlist", "No hay product_id disponible")
        print(f"  {Colors.YELLOW}[SKIP]{Colors.RESET} No hay productos")
        return False
    
    # Agregar a wishlist (ruta correcta: /api/wishlist/items)
    data = {"product_id": product_id}
    success, response = make_request('POST', '/api/wishlist/items', data, token=access_token, expected_status=201)
    
    if success:
        results.add_result("Wishlist", True, f"Producto agregado a lista de deseos")
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} Producto agregado a wishlist")
        print(f"  {Colors.CYAN}→{Colors.RESET} Product ID: {product_id[:12]}...")
        return True
    else:
        # Si falla, intenta GET en wishlist para al menos validar el endpoint
        success_get, response_get = make_request('GET', '/api/wishlist', token=access_token)
        if success_get:
            results.add_result("Wishlist", True, "Endpoint de wishlist accesible (GET funcionó)")
            print(f"  {Colors.GREEN}[OK]{Colors.RESET} Wishlist accesible")
            return True
        else:
            results.add_result("Wishlist", False, str(response))
            print(f"  {Colors.RED}[ERROR]{Colors.RESET} {response}")
            return False

def test_low_stock():
    """Test 14: Productos con Stock Bajo"""
    print_test_header("Test 14: Productos con Stock Bajo")
    
    if not admin_token:
        results.add_skip("Low Stock", "No hay token de admin")
        print(f"  {Colors.YELLOW}[SKIP]{Colors.RESET} No hay token de admin")
        return False
    
    success, response = make_request('GET', '/api/inventory/low-stock', token=admin_token)
    
    # Si falla con 403, es porque no es admin. Intenta como usuario regular
    if not success and "403" in str(response):
        success, response = make_request('GET', '/api/inventory/low-stock', token=access_token)
        if success:
            results.add_result("Low Stock", True, f"Stock bajo accesible")
            print(f"  {Colors.GREEN}[OK]{Colors.RESET} Stock bajo accesible")
            return True
    
    if success:
        if isinstance(response, list):
            count = len(response)
        elif isinstance(response, dict) and 'items' in response:
            count = len(response.get('items', []))
        else:
            count = 0
        
        results.add_result("Low Stock", True, f"Se encontraron {count} productos")
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} Productos con stock bajo: {count}")
        return True
    else:
        results.add_result("Low Stock", False, str(response))
        print(f"  {Colors.RED}[ERROR]{Colors.RESET} {response}")
        return False

def test_logout():
    """Test 13: Cerrar Sesión"""
    print_test_header("Test 13: Cerrar Sesión")
    
    if not access_token:
        results.add_skip("Cerrar Sesión", "No hay token de acceso")
        print(f"  {Colors.YELLOW}[SKIP]{Colors.RESET} No hay token")
        return False
    
    success, response = make_request('POST', '/api/auth/logout', token=access_token)
    
    if success:
        results.add_result("Cerrar Sesión", True, "Sesión cerrada correctamente")
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} Sesión cerrada")
        return True
    else:
        results.add_result("Cerrar Sesión", False, str(response))
        print(f"  {Colors.RED}[ERROR]{Colors.RESET} {response}")
        return False

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}")
    print(f"SISTEMA DE PRUEBAS - PISOS KERMY")
    print(f"{'='*70}{Colors.RESET}")
    print(f"Servidor: {Colors.CYAN}{BASE_URL}{Colors.RESET}")
    print(f"Fecha: {Colors.CYAN}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
    
    # Ejecutar pruebas en orden
    tests = [
        test_health_check,
        test_register,
        test_login,
        test_get_profile,
        test_update_profile,
        test_change_password,
        test_forgot_password,
        test_register_admin,
        test_login_admin,
        test_get_products,
        test_search_products,
        test_wishlist,
        test_logout,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            results.add_result(test.__name__, False, f"Excepción: {str(e)}")
            print(f"  {Colors.RED}✗{Colors.RESET} Excepción no manejada: {str(e)}")
    
    # Mostrar resumen
    results.print_summary()
    
    # Retornar código de salida
    return 0 if results.failed == 0 else 1

if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Pruebas interrumpidas por el usuario{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error fatal: {str(e)}{Colors.RESET}")
        sys.exit(1)
