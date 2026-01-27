#!/usr/bin/env python3
import os
import json
import sys
import requests

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000/api")
TOKEN = os.getenv("f7790677-7c06-4507-9c95-0aa9cad994c5")  # JWT ADMIN
VARIANT_ID = os.getenv("VARIANT_ID")  # opcional

def headers():
    h = {"Content-Type": "application/json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h

def pretty(r: requests.Response):
    print(f"== {r.request.method} {r.request.url} -> {r.status_code} ==")
    try:
        print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(r.text)
    print()

def fail(msg: str):
    print(f"[ERROR] {msg}")
    sys.exit(1)

def main():
    if not TOKEN:
        print("[WARN] Falta TOKEN (JWT) ADMIN. Algunos endpoints darán 401/403.")
        print("      Exporta TOKEN y vuelve a ejecutar.\n")

    # 1) List inventory (admin)
    r = requests.get(f"{BASE_URL}/inventory/?skip=0&limit=5", headers=headers(), timeout=20)
    pretty(r)

    picked_variant_id = None
    if r.ok:
        data = r.json()
        inv_list = data.get("inventory") or []
        if inv_list:
            picked_variant_id = inv_list[0].get("variant_id")

    # Si no pudo obtener por /inventory, usar VARIANT_ID
    variant_id = VARIANT_ID or picked_variant_id
    if not variant_id:
        fail("No pude determinar variant_id. Define VARIANT_ID en tu entorno (export VARIANT_ID=...).")

    print(f"[INFO] Usando variant_id: {variant_id}\n")

    # 2) Get inventory by variant (public)
    r = requests.get(f"{BASE_URL}/inventory/variant/{variant_id}", headers=headers(), timeout=20)
    pretty(r)

    # 3) Adjust +5
    r = requests.post(
        f"{BASE_URL}/inventory/variant/{variant_id}/adjust",
        headers=headers(),
        data=json.dumps({"delta": 5, "reason": "test_increment"}),
        timeout=20
    )
    pretty(r)

    # 4) Retain 2
    r = requests.post(
        f"{BASE_URL}/inventory/variant/{variant_id}/retain",
        headers=headers(),
        data=json.dumps({"quantity": 2, "reason": "test_retain"}),
        timeout=20
    )
    pretty(r)

    # 5) Release 2
    r = requests.post(
        f"{BASE_URL}/inventory/variant/{variant_id}/release",
        headers=headers(),
        data=json.dumps({"quantity": 2, "reason": "test_release"}),
        timeout=20
    )
    pretty(r)

    # 6) Movements detailed (jwt_required)
    r = requests.get(
        f"{BASE_URL}/inventory/movements?skip=0&limit=10&variant_id={variant_id}",
        headers=headers(),
        timeout=20
    )
    pretty(r)

    # 7) Low stock
    r = requests.get(f"{BASE_URL}/inventory/low-stock?threshold=10", headers=headers(), timeout=20)
    pretty(r)

    print("[OK] Pruebas finalizadas.")

if __name__ == "__main__":
    main()
