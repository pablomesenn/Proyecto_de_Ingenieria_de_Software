# 1. Populate database first (IMPORTANT!)
python seed_database.py

# 2. Make sure server is running
python run.py

# 3. Run the tests
python CU5to9_test.py
```

### **Expected Output:**
```
================================================================================
PRUEBAS AUTOMATIZADAS - PRODUCTOS, WISHLIST Y RESERVAS
CU-005, CU-006, CU-007, CU-008, CU-009
================================================================================

✓ PASS Buscar todos los productos
  Encontrados: 2 productos

✓ PASS Consolidación automática de duplicados
  Items consolidados correctamente, cantidad total: 8

...

RESUMEN DE PRUEBAS
Total de pruebas: 27
Exitosas: 27
Fallidas: 0
Tasa de éxito: 100.0%

Resumen por Caso de Uso:
CU-005: Buscar y Filtrar Catálogo: 7/7 (100%)
CU-006: Gestionar Wishlist: 9/9 (100%)
CU-007: Mover Wishlist a Reserva: 2/2 (100%)
CU-008: Crear Reserva Directa: 2/2 (100%)
CU-009: Cancelar Reserva: 3/3 (100%)
