#!/usr/bin/env python3
"""
Script para inspeccionar la base de datos
Lista todas las colecciones y muestra sus documentos
Modo SOLO LECTURA
"""

import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

# ======================================================
# Cargar variables de entorno
# ======================================================

load_dotenv()

# Agregar directorio raíz al path (por consistencia con tu seed)
sys.path.insert(0, os.path.abspath('.'))


# ======================================================
# Helpers
# ======================================================

def json_serializer(obj):
    """Convierte tipos no serializables a JSON"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    return str(obj)


def get_db():
    """
    Obtiene conexión directa a MongoDB usando PyMongo
    Compatible con Atlas o local
    """
    mongodb_uri = os.getenv(
        'MONGODB_URI',
        'mongodb://localhost:27017/pisos_kermy_db'
    )
    db_name = os.getenv('MONGODB_DB', 'pisos_kermy_db')

    print(f"🔌 Conectando a MongoDB...")
    print(f"   URI: {mongodb_uri}")
    print(f"   DB : {db_name}")

    client = MongoClient(
        mongodb_uri,
        serverSelectionTimeoutMS=5000
    )

    # Verificar conexión
    client.admin.command("ping")

    return client[db_name]


# ======================================================
# Inspección
# ======================================================

def inspect_database(db):
    """
    Lista todas las colecciones y sus documentos
    """
    collections = db.list_collection_names()

    print("\n" + "=" * 80)
    print("📦 COLECCIONES EN LA BASE DE DATOS")
    print("=" * 80)

    if not collections:
        print("⚠️  No hay colecciones en la base de datos")
        return

    for collection_name in collections:
        print("\n" + "-" * 80)
        print(f"📁 Colección: {collection_name}")
        print("-" * 80)

        collection = db[collection_name]
        count = collection.count_documents({})

        print(f"📊 Total de documentos: {count}")

        if count == 0:
            print("⚠️  Colección vacía")
            continue

        print("\n📄 Documentos:\n")

        for idx, doc in enumerate(collection.find(), start=1):
            print(f"--- Documento #{idx} ---")
            print(
                json.dumps(
                    doc,
                    indent=2,
                    ensure_ascii=False,
                    default=json_serializer
                )
            )
            print()


# ======================================================
# Main
# ======================================================

def main():
    print("=" * 80)
    print("INSPECCIÓN COMPLETA DE BASE DE DATOS")
    print("=" * 80)

    try:
        db = get_db()
        inspect_database(db)

        print("\n" + "=" * 80)
        print("✅ INSPECCIÓN FINALIZADA")
        print("=" * 80)
        return 0

    except Exception as e:
        print("\n❌ ERROR DURANTE LA INSPECCIÓN")
        print("-" * 80)
        print(str(e))
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
