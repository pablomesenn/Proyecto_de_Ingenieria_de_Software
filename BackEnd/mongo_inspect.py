#!/usr/bin/env python3
"""
mongo_inspector.py
Script para inspeccionar MongoDB (listar colecciones y ver documentos).

Ejemplos:
  # Ver colecciones de una DB
  python mongo_inspector.py --uri "mongodb://localhost:27017" --db pisos_kermy_db --list

  # Ver documentos de la colección users (limit 5)
  python mongo_inspector.py --uri "mongodb://localhost:27017" --db pisos_kermy_db --collection users --limit 5

  # Ver TODOS los documentos de una colección (cuidado en DB grandes)
  python mongo_inspector.py --uri "mongodb://localhost:27017" --db pisos_kermy_db --collection users --all

  # Ver todas las colecciones (muestra primeros N docs por colección)
  python mongo_inspector.py --uri "mongodb://localhost:27017" --db pisos_kermy_db --all-collections --limit 3

  # Filtrar con query JSON (por ejemplo state=activo)
  python mongo_inspector.py --uri "mongodb://localhost:27017" --db pisos_kermy_db --collection users \
    --query '{"state":"activo"}' --limit 10

  # Proyección (campos a incluir) en JSON
  python mongo_inspector.py --uri "mongodb://localhost:27017" --db pisos_kermy_db --collection users \
    --projection '{"email":1,"name":1,"role":1,"state":1}' --limit 10
"""

import argparse
import json
import os
import sys
from pprint import pprint
from typing import Any, Dict, Optional

from pymongo import MongoClient
from bson import ObjectId
from bson.json_util import dumps


def parse_json_arg(value: Optional[str], default: Dict[str, Any]) -> Dict[str, Any]:
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON inválido: {value}\nDetalle: {exc}") from exc


def normalize_object_ids(query: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte {"_id":"..."} a ObjectId si aplica.
    También soporta {"_id":{"$in":["...","..."]}}.
    """
    if "_id" in query:
        val = query["_id"]

        def to_oid(x: Any) -> Any:
            if isinstance(x, str):
                try:
                    return ObjectId(x)
                except Exception:
                    return x
            return x

        if isinstance(val, str):
            query["_id"] = to_oid(val)
        elif isinstance(val, dict):
            # $in, $eq, etc.
            for k, v in list(val.items()):
                if k == "$in" and isinstance(v, list):
                    val["$in"] = [to_oid(i) for i in v]
                elif isinstance(v, str):
                    val[k] = to_oid(v)
            query["_id"] = val
    return query


def safe_print_docs(docs, max_docs: int) -> None:
    count = 0
    for doc in docs:
        count += 1
        # Usar dumps para imprimir bien ObjectId/fechas
        print(dumps(doc, indent=2, ensure_ascii=False))
        print("-" * 80)
        if max_docs and count >= max_docs:
            break


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspector simple de MongoDB (PyMongo)")
    parser.add_argument("--uri", default=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
                        help="URI de MongoDB. Default: env MONGODB_URI o mongodb://localhost:27017")
    parser.add_argument("--db", default=os.getenv("MONGODB_DB", None),
                        help="Nombre de la base de datos (requerido si no está en MONGODB_DB)")
    parser.add_argument("--list", action="store_true", help="Listar colecciones de la DB")
    parser.add_argument("--collection", help="Nombre de la colección a inspeccionar")
    parser.add_argument("--all-collections", action="store_true",
                        help="Recorrer todas las colecciones y mostrar documentos")
    parser.add_argument("--limit", type=int, default=10, help="Cantidad de documentos a mostrar (default 10)")
    parser.add_argument("--all", action="store_true", help="Mostrar TODOS los documentos (ignora --limit)")
    parser.add_argument("--query", default=None,
                        help="Query JSON (string). Ej: '{\"state\":\"activo\"}'")
    parser.add_argument("--projection", default=None,
                        help="Proyección JSON (string). Ej: '{\"email\":1,\"name\":1}'")
    parser.add_argument("--sort", default=None,
                        help="Sort JSON (string). Ej: '{\"created_at\":-1}'")
    parser.add_argument("--count", action="store_true", help="Mostrar conteo total además de imprimir docs")

    args = parser.parse_args()

    if not args.db:
        print("Error: Debes indicar --db o definir MONGODB_DB en variables de entorno.", file=sys.stderr)
        return 2

    # Conectar
    client = MongoClient(args.uri)
    db = client[args.db]

    # Listar colecciones
    if args.list:
        cols = db.list_collection_names()
        print(f"DB: {args.db}")
        print("Colecciones:")
        for c in sorted(cols):
            print(f" - {c}")
        return 0

    # Preparar query/projection/sort
    query = normalize_object_ids(parse_json_arg(args.query, {}))
    projection = parse_json_arg(args.projection, {}) if args.projection else None
    sort = parse_json_arg(args.sort, {}) if args.sort else None

    # Elegir modo
    if args.all_collections:
        cols = db.list_collection_names()
        print(f"DB: {args.db} | Total colecciones: {len(cols)}")
        for c in sorted(cols):
            print("\n" + "=" * 80)
            print(f"Colección: {c}")
            col = db[c]

            if args.count:
                total = col.count_documents(query)
                print(f"Total documentos (query aplicada): {total}")

            cursor = col.find(query, projection)
            if sort:
                cursor = cursor.sort(list(sort.items()))
            if not args.all:
                cursor = cursor.limit(args.limit)

            safe_print_docs(cursor, 0 if args.all else args.limit)
        return 0

    # Colección específica
    if not args.collection:
        print("Error: Debes usar --collection <nombre> o --all-collections o --list.", file=sys.stderr)
        return 2

    col = db[args.collection]
    print(f"DB: {args.db} | Colección: {args.collection}")
    if args.count:
        total = col.count_documents(query)
        print(f"Total documentos (query aplicada): {total}")

    cursor = col.find(query, projection)
    if sort:
        cursor = cursor.sort(list(sort.items()))
    if not args.all:
        cursor = cursor.limit(args.limit)

    safe_print_docs(cursor, 0 if args.all else args.limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
