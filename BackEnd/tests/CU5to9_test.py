#!/usr/bin/env python3
"""
Script de pruebas para CU-005 a CU-009
Tests enfocados en Productos, Wishlist y Reservas

CU-005: Buscar y filtrar catálogo
CU-006: Gestionar wishlist (CRUD completo)
CU-007: Mover de wishlist a reserva
CU-008: Crear reserva directa
CU-009: Cancelar reserva

Ejecutar después de seed_database.py para tener datos de prueba
"""

import requests
import json
from datetime import datetime
from colorama import Fore, Style, init

# Inicializar colorama
init(autoreset=True)

BASE_URL = "http://localhost:5000"

# Variables globales
client_token = None
admin_token = None
test_product_id = None
test_variant_ids = []
test_wishlist_item_ids = []
test_reservation_id = None
test_results = []


def log_test(test_name, success, message="", response_data=None):
    """Registra el resultado de una prueba"""
    status = f"{Fore.GREEN}✓ PASS{Style.RESET_ALL}" if success else f"{Fore.RED}✗ FAIL{Style.RESET_ALL}"
    print(f"\n{status} {test_name}")
    if message:
        print(f"  {message}")
    if response_data and not success:
        print(f"  Response: {json.dumps(response_data, indent=2)}")

    test_results.append({
        'test': test_name,
        'success': success,
        'message': message,
        'timestamp': datetime.now().isoformat()
    })


def print_section(title):
    """Imprime un encabezado de sección"""
    print(f"\n{'='*80}")
    print(f"{Fore.CYAN}{title}{Style.RESET_ALL}")
    print('='*80)


def setup_authentication():
    """Autentica usuarios para las pruebas"""
    global client_token, admin_token

    print_section("SETUP: Autenticación")

    # Login cliente
    try:
        payload = {"email": "cliente1@example.com", "password": "Cliente123!"}
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)

        if response.status_code == 200:
            client_token = response.json().get('access_token')
            print(f"{Fore.GREEN}✓ Cliente autenticado{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Error autenticando cliente{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")
        return False

    # Login admin
    try:
        payload = {"email": "admin@pisoskermy.com", "password": "Admin123!"}
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)

        if response.status_code == 200:
            admin_token = response.json().get('access_token')
            print(f"{Fore.GREEN}✓ Admin autenticado{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Error autenticando admin{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")
        return False

    return True


# ============================================================================
# CU-005: BUSCAR Y FILTRAR CATÁLOGO
# ============================================================================

def test_search_catalog_all_products():
    """CU-005: Buscar catálogo - Todos los productos"""
    print_section("CU-005: Buscar Catálogo - Todos los Productos")

    try:
        response = requests.get(f"{BASE_URL}/api/products/search")

        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            log_test(
                "Buscar todos los productos",
                len(products) > 0,
                f"Encontrados: {len(products)} productos"
            )

            # Guardar IDs para pruebas posteriores
            if products:
                global test_product_id
                test_product_id = products[0].get('_id')
        else:
            log_test("Buscar todos los productos", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Buscar todos los productos", False, str(e))


def test_search_by_text():
    """CU-005: Buscar por texto"""
    print_section("CU-005: Buscar por Texto")

    try:
        params = {"search_text": "laminado"}
        response = requests.get(f"{BASE_URL}/api/products/search", params=params)

        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])

            # Verificar que los productos encontrados contienen el texto
            contains_text = all(
                'laminado' in p.get('nombre', '').lower()
                for p in products
            ) if products else True

            log_test(
                "Buscar por texto 'laminado'",
                contains_text,
                f"Encontrados: {len(products)} productos"
            )
        else:
            log_test("Buscar por texto", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Buscar por texto", False, str(e))


def test_search_by_category():
    """CU-005: Filtrar por categoría"""
    print_section("CU-005: Filtrar por Categoría")

    try:
        params = {"categoria": "Laminados"}
        response = requests.get(f"{BASE_URL}/api/products/search", params=params)

        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])

            # Verificar que todos son de la categoría correcta
            correct_category = all(
                p.get('categoria') == 'Laminados'
                for p in products
            ) if products else True

            log_test(
                "Filtrar por categoría 'Laminados'",
                correct_category,
                f"Encontrados: {len(products)} productos"
            )
        else:
            log_test("Filtrar por categoría", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Filtrar por categoría", False, str(e))


def test_search_with_availability():
    """CU-005: Verificar cálculo de disponibilidad en tiempo real"""
    print_section("CU-005: Disponibilidad en Tiempo Real")

    try:
        params = {"disponibilidad": "true"}
        response = requests.get(f"{BASE_URL}/api/products/search", params=params)

        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])

            # Verificar que solo productos activos
            all_active = all(
                p.get('estado') == 'activo'
                for p in products
            ) if products else True

            # Verificar que variantes tienen disponibilidad calculada
            has_availability = False
            for product in products:
                variantes = product.get('variantes', [])
                if variantes:
                    has_availability = any(
                        'disponibilidad' in v
                        for v in variantes
                    )
                    if has_availability:
                        break

            log_test(
                "Disponibilidad calculada en tiempo real",
                all_active and (has_availability or not products),
                f"Productos activos con disponibilidad: {len(products)}"
            )
        else:
            log_test("Disponibilidad en tiempo real", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Disponibilidad en tiempo real", False, str(e))


def test_get_product_detail():
    """CU-005: Obtener detalle de producto con variantes"""
    print_section("CU-005: Detalle de Producto")

    if not test_product_id:
        log_test("Detalle de producto", False, "No hay product_id de prueba")
        return

    try:
        response = requests.get(f"{BASE_URL}/api/products/{test_product_id}")

        if response.status_code == 200:
            data = response.json()
            has_variants = len(data.get('variantes', [])) > 0

            # Guardar variant IDs para pruebas posteriores
            global test_variant_ids
            test_variant_ids = [v['_id'] for v in data.get('variantes', [])]

            log_test(
                "Obtener detalle de producto",
                has_variants,
                f"Producto con {len(data.get('variantes', []))} variantes"
            )
        else:
            log_test("Detalle de producto", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Detalle de producto", False, str(e))


def test_get_categories():
    """CU-005: Obtener categorías disponibles"""
    print_section("CU-005: Obtener Categorías")

    try:
        response = requests.get(f"{BASE_URL}/api/products/categories")

        if response.status_code == 200:
            data = response.json()
            categories = data.get('categories', [])
            log_test(
                "Obtener categorías",
                len(categories) > 0,
                f"Categorías: {', '.join(categories)}"
            )
        else:
            log_test("Obtener categorías", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Obtener categorías", False, str(e))


def test_pagination():
    """CU-005: Paginación de resultados"""
    print_section("CU-005: Paginación")

    try:
        # Primera página
        params1 = {"skip": 0, "limit": 1}
        response1 = requests.get(f"{BASE_URL}/api/products/search", params=params1)

        # Segunda página
        params2 = {"skip": 1, "limit": 1}
        response2 = requests.get(f"{BASE_URL}/api/products/search", params=params2)

        if response1.status_code == 200 and response2.status_code == 200:
            products1 = response1.json().get('products', [])
            products2 = response2.json().get('products', [])

            # Verificar que son diferentes productos
            different = True
            if products1 and products2:
                different = products1[0].get('_id') != products2[0].get('_id')

            log_test(
                "Paginación funcional",
                different,
                f"Página 1: {len(products1)} productos, Página 2: {len(products2)} productos"
            )
        else:
            log_test("Paginación funcional", False, "Error en requests")
    except Exception as e:
        log_test("Paginación funcional", False, str(e))


# ============================================================================
# CU-006: GESTIONAR WISHLIST (CRUD COMPLETO)
# ============================================================================

def test_get_empty_wishlist():
    """CU-006: Obtener wishlist vacía"""
    print_section("CU-006: Obtener Wishlist Vacía")

    if not client_token:
        log_test("Obtener wishlist vacía", False, "No hay token de cliente")
        return

    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/wishlist/", headers=headers)

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            log_test(
                "Obtener wishlist vacía",
                True,
                f"Wishlist con {len(items)} items"
            )
        else:
            log_test("Obtener wishlist vacía", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Obtener wishlist vacía", False, str(e))


def test_add_item_to_wishlist():
    """CU-006: Agregar item a wishlist"""
    print_section("CU-006: Agregar Item a Wishlist")

    if not client_token or not test_variant_ids:
        log_test("Agregar item a wishlist", False, "Faltan datos de prueba")
        return

    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        payload = {
            "variant_id": test_variant_ids[0],
            "quantity": 5
        }
        response = requests.post(f"{BASE_URL}/api/wishlist/items", headers=headers, json=payload)

        if response.status_code == 201:
            data = response.json()
            wishlist = data.get('wishlist', {})
            items = wishlist.get('items', [])

            # Guardar item_id para pruebas posteriores
            global test_wishlist_item_ids
            if items:
                test_wishlist_item_ids.append(items[0].get('item_id'))

            log_test(
                "Agregar item a wishlist",
                len(items) > 0,
                f"Item agregado, total: {len(items)} items"
            )
        else:
            log_test("Agregar item a wishlist", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Agregar item a wishlist", False, str(e))


def test_add_duplicate_item_consolidation():
    """CU-006: Consolidación automática de duplicados (RF-11)"""
    print_section("CU-006: Consolidación Automática de Duplicados")

    if not client_token or not test_variant_ids:
        log_test("Consolidación de duplicados", False, "Faltan datos de prueba")
        return

    try:
        headers = {"Authorization": f"Bearer {client_token}"}

        # Agregar mismo item otra vez
        payload = {
            "variant_id": test_variant_ids[0],
            "quantity": 3
        }
        response = requests.post(f"{BASE_URL}/api/wishlist/items", headers=headers, json=payload)

        if response.status_code == 201:
            data = response.json()
            wishlist = data.get('wishlist', {})
            items = wishlist.get('items', [])

            # Debe seguir habiendo 1 solo item pero con cantidad incrementada
            consolidated = len(items) == 1
            if items:
                # La cantidad debe ser 5 + 3 = 8
                total_quantity = items[0].get('quantity', 0)
                consolidated = consolidated and total_quantity == 8

            log_test(
                "Consolidación automática de duplicados",
                consolidated,
                f"Items consolidados correctamente, cantidad total: {total_quantity if items else 0}"
            )
        else:
            log_test("Consolidación de duplicados", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Consolidación de duplicados", False, str(e))


def test_add_second_item():
    """CU-006: Agregar segundo item diferente"""
    print_section("CU-006: Agregar Segundo Item")

    if not client_token or len(test_variant_ids) < 2:
        log_test("Agregar segundo item", False, "Faltan datos de prueba")
        return

    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        payload = {
            "variant_id": test_variant_ids[1],
            "quantity": 2
        }
        response = requests.post(f"{BASE_URL}/api/wishlist/items", headers=headers, json=payload)

        if response.status_code == 201:
            data = response.json()
            wishlist = data.get('wishlist', {})
            items = wishlist.get('items', [])

            # Guardar segundo item_id
            if len(items) >= 2:
                test_wishlist_item_ids.append(items[1].get('item_id'))

            log_test(
                "Agregar segundo item",
                len(items) == 2,
                f"Total items en wishlist: {len(items)}"
            )
        else:
            log_test("Agregar segundo item", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Agregar segundo item", False, str(e))


def test_get_wishlist_with_items():
    """CU-006: Obtener wishlist con items y disponibilidad"""
    print_section("CU-006: Obtener Wishlist con Items")

    if not client_token:
        log_test("Obtener wishlist con items", False, "No hay token de cliente")
        return

    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/wishlist/", headers=headers)

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])

            # Verificar que items tienen disponibilidad calculada
            has_availability = all(
                'disponibilidad' in item
                for item in items
            ) if items else False

            log_test(
                "Obtener wishlist con disponibilidad",
                has_availability and len(items) > 0,
                f"Wishlist con {len(items)} items, disponibilidad calculada"
            )
        else:
            log_test("Obtener wishlist con items", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Obtener wishlist con items", False, str(e))


def test_get_wishlist_summary():
    """CU-006: Obtener resumen de wishlist"""
    print_section("CU-006: Resumen de Wishlist")

    if not client_token:
        log_test("Resumen de wishlist", False, "No hay token de cliente")
        return

    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{BASE_URL}/api/wishlist/summary", headers=headers)

        if response.status_code == 200:
            data = response.json()
            has_summary = all(k in data for k in ['total_items', 'total_quantity', 'total_value'])

            log_test(
                "Resumen de wishlist",
                has_summary,
                f"Total items: {data.get('total_items')}, Total cantidad: {data.get('total_quantity')}"
            )
        else:
            log_test("Resumen de wishlist", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Resumen de wishlist", False, str(e))


def test_update_wishlist_item():
    """CU-006: Actualizar cantidad de item"""
    print_section("CU-006: Actualizar Cantidad de Item")

    if not client_token or not test_wishlist_item_ids:
        log_test("Actualizar item", False, "Faltan datos de prueba")
        return

    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        item_id = test_wishlist_item_ids[0]
        payload = {"quantity": 10}

        response = requests.put(
            f"{BASE_URL}/api/wishlist/items/{item_id}",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            data = response.json()
            wishlist = data.get('wishlist', {})
            items = wishlist.get('items', [])

            # Verificar que la cantidad se actualizó
            updated_item = next((i for i in items if i.get('item_id') == item_id), None)
            quantity_updated = updated_item and updated_item.get('quantity') == 10

            log_test(
                "Actualizar cantidad de item",
                quantity_updated,
                f"Nueva cantidad: {updated_item.get('quantity') if updated_item else 'N/A'}"
            )
        else:
            log_test("Actualizar item", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Actualizar item", False, str(e))


def test_remove_wishlist_item():
    """CU-006: Eliminar item de wishlist"""
    print_section("CU-006: Eliminar Item")

    if not client_token or len(test_wishlist_item_ids) < 2:
        log_test("Eliminar item", False, "Faltan datos de prueba")
        return

    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        item_id = test_wishlist_item_ids[1]  # Eliminar segundo item

        response = requests.delete(
            f"{BASE_URL}/api/wishlist/items/{item_id}",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            wishlist = data.get('wishlist', {})
            items = wishlist.get('items', [])

            # Debe quedar solo 1 item
            log_test(
                "Eliminar item de wishlist",
                len(items) == 1,
                f"Items restantes: {len(items)}"
            )
        else:
            log_test("Eliminar item", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Eliminar item", False, str(e))


# ============================================================================
# CU-007: MOVER DE WISHLIST A RESERVA
# ============================================================================

def test_convert_wishlist_to_reservation():
    """CU-007: Convertir wishlist a reserva con validación"""
    print_section("CU-007: Convertir Wishlist a Reserva")

    if not client_token or not test_wishlist_item_ids:
        log_test("Convertir wishlist a reserva", False, "Faltan datos de prueba")
        return

    try:
        headers = {"Authorization": f"Bearer {client_token}"}

        # Primero obtener wishlist para ver items disponibles
        response = requests.get(f"{BASE_URL}/api/wishlist/", headers=headers)
        if response.status_code != 200:
            log_test("Convertir wishlist - obtener items", False, "No se pudo obtener wishlist")
            return

        wishlist_data = response.json()
        items = wishlist_data.get('items', [])

        if not items:
            log_test("Convertir wishlist a reserva", False, "No hay items en wishlist")
            return

        # Preparar items para convertir (solo el primero)
        item_to_convert = items[0]
        payload = {
            "items": [
                {
                    "item_id": item_to_convert.get('item_id'),
                    "quantity": min(item_to_convert.get('quantity'),
                                   item_to_convert.get('disponibilidad', 0))
                }
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/wishlist/convert-to-reservation",
            headers=headers,
            json=payload
        )

        if response.status_code == 201:
            data = response.json()
            reservation = data.get('reservation', {})

            # Guardar ID de reserva para pruebas posteriores
            global test_reservation_id
            test_reservation_id = reservation.get('_id')

            log_test(
                "Convertir wishlist a reserva",
                reservation.get('state') == 'Pendiente',
                f"Reserva creada: {test_reservation_id}, Estado: {reservation.get('state')}"
            )
        else:
            log_test("Convertir wishlist a reserva", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Convertir wishlist a reserva", False, str(e))


def test_convert_with_insufficient_stock():
    """CU-007: Validar error cuando no hay stock suficiente"""
    print_section("CU-007: Validación de Stock Insuficiente")

    if not client_token:
        log_test("Validación stock insuficiente", False, "No hay token de cliente")
        return

    try:
        headers = {"Authorization": f"Bearer {client_token}"}

        # Primero agregar un item con cantidad muy alta
        if test_variant_ids:
            add_payload = {
                "variant_id": test_variant_ids[0],
                "quantity": 999999  # Cantidad imposible
            }
            requests.post(f"{BASE_URL}/api/wishlist/items", headers=headers, json=add_payload)

        # Obtener wishlist actualizada
        response = requests.get(f"{BASE_URL}/api/wishlist/", headers=headers)
        if response.status_code == 200:
            items = response.json().get('items', [])
            if items:
                item = items[0]

                # Intentar convertir con cantidad mayor a disponible
                payload = {
                    "items": [
                        {
                            "item_id": item.get('item_id'),
                            "quantity": 999999
                        }
                    ]
                }

                response = requests.post(
                    f"{BASE_URL}/api/wishlist/convert-to-reservation",
                    headers=headers,
                    json=payload
                )

                # Debe fallar con 400
                log_test(
                    "Validación de stock insuficiente",
                    response.status_code == 400,
                    "Error detectado correctamente al intentar reservar sin stock"
                )
            else:
                log_test("Validación stock insuficiente", False, "No hay items en wishlist")
        else:
            log_test("Validación stock insuficiente", False, "No se pudo obtener wishlist")
    except Exception as e:
        log_test("Validación stock insuficiente", False, str(e))


# ============================================================================
# CU-008: CREAR RESERVA DIRECTA
# ============================================================================

def test_create_direct_reservation():
    """CU-008: Crear reserva directa (sin pasar por wishlist)"""
    print_section("CU-008: Crear Reserva Directa")

    if not client_token or not test_variant_ids:
        log_test("Crear reserva directa", False, "Faltan datos de prueba")
        return

    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        payload = {
            "items": [
                {
                    "variant_id": test_variant_ids[0],
                    "quantity": 2,
                    "price": 15000.00
                }
            ],
            "notes": "Reserva directa de prueba"
        }

        response = requests.post(f"{BASE_URL}/api/reservations/", headers=headers, json=payload)

        if response.status_code == 201:
            data = response.json()
            reservation = data.get('reservation', {})

            log_test(
                "Crear reserva directa",
                reservation.get('state') == 'Pendiente',
                f"Reserva ID: {reservation.get('_id')}, Estado: {reservation.get('state')}"
            )
        else:
            log_test("Crear reserva directa", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Crear reserva directa", False, str(e))


def test_create_reservation_validation():
    """CU-008: Validación al crear reserva sin stock"""
    print_section("CU-008: Validación de Disponibilidad")

    if not client_token or not test_variant_ids:
        log_test("Validación al crear reserva", False, "Faltan datos de prueba")
        return

    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        payload = {
            "items": [
                {
                    "variant_id": test_variant_ids[0],
                    "quantity": 999999,  # Cantidad imposible
                    "price": 15000.00
                }
            ]
        }

        response = requests.post(f"{BASE_URL}/api/reservations/", headers=headers, json=payload)

        # Debe fallar con 400
        log_test(
            "Validación de disponibilidad al crear reserva",
            response.status_code == 400,
            "Validación correcta de stock insuficiente"
        )
    except Exception as e:
        log_test("Validación al crear reserva", False, str(e))


# ============================================================================
# CU-009: CANCELAR RESERVA
# ============================================================================

def test_cancel_reservation_by_client():
    """CU-009: Cancelar reserva (por cliente)"""
    print_section("CU-009: Cancelar Reserva por Cliente")

    if not client_token or not test_reservation_id:
        log_test("Cancelar reserva cliente", False, "Faltan datos de prueba")
        return

    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.put(
            f"{BASE_URL}/api/reservations/{test_reservation_id}/cancel",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            reservation = data.get('reservation', {})

            log_test(
                "Cancelar reserva por cliente",
                reservation.get('state') == 'Cancelada',
                f"Estado: {reservation.get('state')}"
            )
        else:
            log_test("Cancelar reserva cliente", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Cancelar reserva cliente", False, str(e))


def test_cancel_reservation_inventory_release():
    """CU-009: Verificar liberación de inventario al cancelar"""
    print_section("CU-009: Verificar Liberación de Inventario")

    if not client_token or not test_variant_ids:
        log_test("Liberación de inventario", False, "Faltan datos de prueba")
        return

    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        variant_id = test_variant_ids[0]

        # 1. Obtener disponibilidad inicial
        response = requests.get(f"{BASE_URL}/api/products/search")
        if response.status_code != 200:
            log_test("Liberación - obtener stock inicial", False, "Error obteniendo productos")
            return

        products = response.json().get('products', [])
        initial_availability = None
        for product in products:
            for variant in product.get('variantes', []):
                if variant.get('_id') == variant_id:
                    initial_availability = variant.get('disponibilidad')
                    break

        if initial_availability is None:
            log_test("Liberación de inventario", False, "No se encontró disponibilidad inicial")
            return

        # 2. Crear reserva
        create_payload = {
            "items": [{"variant_id": variant_id, "quantity": 3, "price": 15000.00}]
        }
        response = requests.post(f"{BASE_URL}/api/reservations/", headers=headers, json=create_payload)

        if response.status_code != 201:
            log_test("Liberación - crear reserva", False, "Error creando reserva")
            return

        reservation_id = response.json().get('reservation', {}).get('_id')

        # 3. Cancelar reserva
        response = requests.put(
            f"{BASE_URL}/api/reservations/{reservation_id}/cancel",
            headers=headers
        )

        if response.status_code != 200:
            log_test("Liberación - cancelar reserva", False, "Error cancelando reserva")
            return

        # 4. Verificar que disponibilidad se restauró
        response = requests.get(f"{BASE_URL}/api/products/search")
        if response.status_code == 200:
            products = response.json().get('products', [])
            final_availability = None
            for product in products:
                for variant in product.get('variantes', []):
                    if variant.get('_id') == variant_id:
                        final_availability = variant.get('disponibilidad')
                        break

            inventory_released = final_availability == initial_availability

            log_test(
                "Liberación de inventario al cancelar",
                inventory_released,
                f"Disponibilidad inicial: {initial_availability}, Final: {final_availability}"
            )
        else:
            log_test("Liberación de inventario", False, "Error verificando stock final")
    except Exception as e:
        log_test("Liberación de inventario", False, str(e))


def test_cannot_cancel_already_cancelled():
    """CU-009: No se puede cancelar una reserva ya cancelada"""
    print_section("CU-009: Validar No Re-cancelar")

    if not client_token:
        log_test("No re-cancelar", False, "No hay token de cliente")
        return

    try:
        headers = {"Authorization": f"Bearer {client_token}"}

        # Crear nueva reserva
        payload = {
            "items": [
                {
                    "variant_id": test_variant_ids[0],
                    "quantity": 1,
                    "price": 15000.00
                }
            ]
        }
        response = requests.post(f"{BASE_URL}/api/reservations/", headers=headers, json=payload)

        if response.status_code != 201:
            log_test("No re-cancelar - crear", False, "Error creando reserva")
            return

        reservation_id = response.json().get('reservation', {}).get('_id')

        # Cancelar primera vez
        response = requests.put(
            f"{BASE_URL}/api/reservations/{reservation_id}/cancel",
            headers=headers
        )

        if response.status_code != 200:
            log_test("No re-cancelar - primera cancelación", False, "Error cancelando")
            return

        # Intentar cancelar segunda vez
        response = requests.put(
            f"{BASE_URL}/api/reservations/{reservation_id}/cancel",
            headers=headers
        )

        # Debe fallar con 400
        log_test(
            "No permitir re-cancelar reserva",
            response.status_code == 400,
            "Validación correcta: no se puede cancelar reserva ya cancelada"
        )
    except Exception as e:
        log_test("No re-cancelar", False, str(e))


# ============================================================================
# TESTS ADICIONALES DE INTEGRACIÓN
# ============================================================================

def test_clear_wishlist():
    """CU-006: Limpiar toda la wishlist"""
    print_section("CU-006: Limpiar Wishlist")

    if not client_token:
        log_test("Limpiar wishlist", False, "No hay token de cliente")
        return

    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.delete(f"{BASE_URL}/api/wishlist/clear", headers=headers)

        if response.status_code == 200:
            # Verificar que está vacía
            response = requests.get(f"{BASE_URL}/api/wishlist/", headers=headers)
            if response.status_code == 200:
                items = response.json().get('items', [])
                log_test(
                    "Limpiar wishlist",
                    len(items) == 0,
                    f"Wishlist limpiada, items restantes: {len(items)}"
                )
            else:
                log_test("Limpiar wishlist - verificar", False, "Error verificando")
        else:
            log_test("Limpiar wishlist", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Limpiar wishlist", False, str(e))


def test_admin_create_product():
    """CU-005: ADMIN puede crear productos"""
    print_section("ADMIN: Crear Producto")

    if not admin_token:
        log_test("ADMIN crear producto", False, "No hay token de admin")
        return

    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "nombre": "Producto de Prueba Automatizada",
            "imagen_url": "https://example.com/test.jpg",
            "categoria": "Test",
            "tags": ["automatizado", "prueba"],
            "estado": "activo",
            "descripcion_embalaje": "Producto creado por tests automatizados"
        }

        response = requests.post(f"{BASE_URL}/api/products/", headers=headers, json=payload)

        if response.status_code == 201:
            data = response.json()
            product = data.get('product', {})
            log_test(
                "ADMIN crear producto",
                product.get('nombre') == payload['nombre'],
                f"Producto creado: {product.get('_id')}"
            )
        else:
            log_test("ADMIN crear producto", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("ADMIN crear producto", False, str(e))


def test_client_cannot_create_product():
    """CU-005: CLIENT no puede crear productos (RBAC)"""
    print_section("RBAC: Cliente No Puede Crear Productos")

    if not client_token:
        log_test("RBAC crear producto", False, "No hay token de cliente")
        return

    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        payload = {
            "nombre": "Intento de Cliente",
            "imagen_url": "https://example.com/test.jpg",
            "categoria": "Test"
        }

        response = requests.post(f"{BASE_URL}/api/products/", headers=headers, json=payload)

        # Debe fallar con 403
        log_test(
            "RBAC: Cliente no puede crear productos",
            response.status_code == 403,
            "Permisos validados correctamente"
        )
    except Exception as e:
        log_test("RBAC crear producto", False, str(e))


# ============================================================================
# FUNCIÓN PRINCIPAL Y RESUMEN
# ============================================================================

def print_summary():
    """Imprime resumen de pruebas"""
    print_section("RESUMEN DE PRUEBAS")

    total = len(test_results)
    passed = sum(1 for r in test_results if r['success'])
    failed = total - passed
    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"\n{Fore.CYAN}Total de pruebas: {total}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Exitosas: {passed}{Style.RESET_ALL}")
    print(f"{Fore.RED}Fallidas: {failed}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Tasa de éxito: {success_rate:.1f}%{Style.RESET_ALL}\n")

    # Agrupar por caso de uso
    cu_summary = {}
    for result in test_results:
        test_name = result['test']
        # Intentar extraer CU del nombre del test
        if 'CU-005' in test_name or 'catálogo' in test_name.lower() or 'product' in test_name.lower():
            cu = 'CU-005: Buscar y Filtrar Catálogo'
        elif 'CU-006' in test_name or 'wishlist' in test_name.lower():
            cu = 'CU-006: Gestionar Wishlist'
        elif 'CU-007' in test_name or 'convert' in test_name.lower():
            cu = 'CU-007: Mover Wishlist a Reserva'
        elif 'CU-008' in test_name or 'directa' in test_name.lower():
            cu = 'CU-008: Crear Reserva Directa'
        elif 'CU-009' in test_name or 'cancel' in test_name.lower():
            cu = 'CU-009: Cancelar Reserva'
        else:
            cu = 'Otros Tests'

        if cu not in cu_summary:
            cu_summary[cu] = {'total': 0, 'passed': 0, 'failed': 0}

        cu_summary[cu]['total'] += 1
        if result['success']:
            cu_summary[cu]['passed'] += 1
        else:
            cu_summary[cu]['failed'] += 1

    print(f"{Fore.CYAN}Resumen por Caso de Uso:{Style.RESET_ALL}\n")
    for cu, stats in sorted(cu_summary.items()):
        rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        color = Fore.GREEN if rate == 100 else Fore.YELLOW if rate >= 70 else Fore.RED
        print(f"{color}{cu}: {stats['passed']}/{stats['total']} ({rate:.0f}%){Style.RESET_ALL}")

    if failed > 0:
        print(f"\n{Fore.YELLOW}Pruebas Fallidas:{Style.RESET_ALL}")
        for result in test_results:
            if not result['success']:
                print(f"  {Fore.RED}✗{Style.RESET_ALL} {result['test']}")
                if result['message']:
                    print(f"    {result['message']}")

    # Guardar log
    log_file = f"test_products_wishlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)

    print(f"\n{Fore.CYAN}Log guardado en: {log_file}{Style.RESET_ALL}\n")


def main():
    """Función principal"""
    print(f"\n{Fore.MAGENTA}{'='*80}")
    print("PRUEBAS AUTOMATIZADAS - PRODUCTOS, WISHLIST Y RESERVAS")
    print("CU-005, CU-006, CU-007, CU-008, CU-009")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL Base: {BASE_URL}\n")

    # Setup
    if not setup_authentication():
        print(f"\n{Fore.RED}Error en autenticación. Abortando pruebas.{Style.RESET_ALL}")
        return

    # CU-005: Buscar y Filtrar Catálogo
    test_search_catalog_all_products()
    test_search_by_text()
    test_search_by_category()
    test_search_with_availability()
    test_get_product_detail()
    test_get_categories()
    test_pagination()

    # CU-006: Gestionar Wishlist
    test_get_empty_wishlist()
    test_add_item_to_wishlist()
    test_add_duplicate_item_consolidation()
    test_add_second_item()
    test_get_wishlist_with_items()
    test_get_wishlist_summary()
    test_update_wishlist_item()
    test_remove_wishlist_item()

    # CU-007: Mover Wishlist a Reserva
    test_convert_wishlist_to_reservation()
    test_convert_with_insufficient_stock()

    # CU-008: Crear Reserva Directa
    test_create_direct_reservation()
    test_create_reservation_validation()

    # CU-009: Cancelar Reserva
    test_cancel_reservation_by_client()
    test_cancel_reservation_inventory_release()
    test_cannot_cancel_already_cancelled()

    # Tests adicionales
    test_clear_wishlist()
    test_admin_create_product()
    test_client_cannot_create_product()

    # Resumen
    print_summary()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Pruebas interrumpidas por el usuario{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error fatal: {str(e)}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
