#!/usr/bin/env python3
"""
Prueba endpoints de catálogo y auxiliares de productos.

Uso:
  python test_catalog_and_products_api.py

Variables de entorno:
  API_BASE  (default: http://localhost:5000/api)
  TOKEN     (JWT Bearer token de un ADMIN)  -> requerido para /catalog/*
"""

import os
import sys
import json
import requests
from typing import Any, Dict, Optional

API_BASE = os.getenv("API_BASE", "http://localhost:5000/api").rstrip("/")
TOKEN = os.getenv("TOKEN", "").strip()

TIMEOUT = 15


def _headers(auth: bool = False) -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if auth:
        if not TOKEN:
            raise RuntimeError("Falta TOKEN (JWT) para probar endpoints /catalog/*")
        headers["Authorization"] = f"Bearer {TOKEN}"
    return headers


def _print(title: str, payload: Any) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def get(path: str, auth: bool = False) -> Any:
    r = requests.get(f"{API_BASE}{path}", headers=_headers(auth), timeout=TIMEOUT)
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}
    return r.status_code, data


def post(path: str, body: Dict[str, Any], auth: bool = False) -> Any:
    r = requests.post(
        f"{API_BASE}{path}",
        headers=_headers(auth),
        data=json.dumps(body),
        timeout=TIMEOUT,
    )
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}
    return r.status_code, data


def put(path: str, body: Dict[str, Any], auth: bool = False) -> Any:
    r = requests.put(
        f"{API_BASE}{path}",
        headers=_headers(auth),
        data=json.dumps(body),
        timeout=TIMEOUT,
    )
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}
    return r.status_code, data


def delete(path: str, auth: bool = False) -> Any:
    r = requests.delete(f"{API_BASE}{path}", headers=_headers(auth), timeout=TIMEOUT)
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}
    return r.status_code, data


def main() -> int:
    # 1) Endpoints públicos auxiliares (derivados de productos)
    code, data = get("/products/categories")
    _print(f"GET /products/categories -> {code}", data)

    code, data = get("/products/tags")
    _print(f"GET /products/tags -> {code}", data)

    # 2) Endpoints de catálogo (requieren ADMIN)
    try:
        code, data = get("/catalog/categories", auth=True)
        _print(f"GET /catalog/categories -> {code}", data)

        code, data = get("/catalog/tags", auth=True)
        _print(f"GET /catalog/tags -> {code}", data)
    except RuntimeError as e:
        print(f"\n[WARN] {e}")
        return 0

    # 3) CRUD smoke test (crea -> renombra -> borra)
    #    Nota: si tu backend bloquea borrar por 'en uso', la prueba lo reporta.
    unique_cat = "CAT_TEST_API__BORRAR"
    unique_tag = "TAG_TEST_API__BORRAR"

    code, cat = post("/catalog/categories", {"name": unique_cat}, auth=True)
    _print(f"POST /catalog/categories -> {code}", cat)
    cat_id = (cat.get("category") or cat).get("_id") if isinstance(cat, dict) else None

    code, tag = post("/catalog/tags", {"name": unique_tag}, auth=True)
    _print(f"POST /catalog/tags -> {code}", tag)
    tag_id = (tag.get("tag") or tag).get("_id") if isinstance(tag, dict) else None

    if cat_id:
        code, upd = put(f"/catalog/categories/{cat_id}", {"name": unique_cat + "_REN"}, auth=True)
        _print(f"PUT /catalog/categories/{cat_id} -> {code}", upd)

        code, d = delete(f"/catalog/categories/{cat_id}", auth=True)
        _print(f"DELETE /catalog/categories/{cat_id} -> {code}", d)
    else:
        print("\n[WARN] No pude detectar _id de categoría creada; revisa respuesta del backend.")

    if tag_id:
        code, upd = put(f"/catalog/tags/{tag_id}", {"name": unique_tag + "_REN"}, auth=True)
        _print(f"PUT /catalog/tags/{tag_id} -> {code}", upd)

        code, d = delete(f"/catalog/tags/{tag_id}", auth=True)
        _print(f"DELETE /catalog/tags/{tag_id} -> {code}", d)
    else:
        print("\n[WARN] No pude detectar _id de tag creado; revisa respuesta del backend.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
