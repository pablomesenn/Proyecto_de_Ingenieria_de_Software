from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
from app.schemas.catalog_schema import CreateCatalogItemSchema, UpdateCatalogItemSchema
from app.services.catalog_service import CatalogService
from app.constants.roles import UserRole
import logging

logger = logging.getLogger(__name__)

catalog_bp = Blueprint("catalog", __name__)
catalog_service = CatalogService()

def require_admin(f):
    def wrapper(*args, **kwargs):
        role = get_jwt().get("role")
        if role != UserRole.ADMIN:
            return jsonify({"error": "Permisos insuficientes"}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# ----------- Categories -----------
@catalog_bp.route("/categories", methods=["GET"])
@jwt_required()
@require_admin
def list_categories():
    try:
        cats = catalog_service.list_categories()
        for c in cats:
            c["_id"] = str(c["_id"])
        return jsonify({"categories": cats}), 200
    except Exception as e:
        logger.error(f"Error listando categorías: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

@catalog_bp.route("/categories", methods=["POST"])
@jwt_required()
@require_admin
def create_category():
    try:
        admin_id = get_jwt_identity()
        data = CreateCatalogItemSchema().load(request.get_json())
        cat = catalog_service.create_category(data["name"], admin_id)
        cat["_id"] = str(cat["_id"])
        return jsonify({"message": "Categoría creada", "category": cat}), 201
    except ValidationError as e:
        return jsonify({"error": "Datos inválidos", "details": e.messages}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        logger.error(f"Error creando categoría: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

@catalog_bp.route("/categories/<category_id>", methods=["PUT"])
@jwt_required()
@require_admin
def update_category(category_id):
    try:
        admin_id = get_jwt_identity()
        data = UpdateCatalogItemSchema().load(request.get_json())
        cat = catalog_service.update_category(category_id, data["name"], admin_id)
        cat["_id"] = str(cat["_id"])
        return jsonify({"message": "Categoría actualizada", "category": cat}), 200
    except ValidationError as e:
        return jsonify({"error": "Datos inválidos", "details": e.messages}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        logger.error(f"Error actualizando categoría: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

@catalog_bp.route("/categories/<category_id>", methods=["DELETE"])
@jwt_required()
@require_admin
def delete_category(category_id):
    try:
        admin_id = get_jwt_identity()
        ok = catalog_service.delete_category(category_id, admin_id)
        return jsonify({"message": "Categoría eliminada" if ok else "No se pudo eliminar"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        logger.error(f"Error eliminando categoría: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# ----------- Tags -----------
@catalog_bp.route("/tags", methods=["GET"])
@jwt_required()
@require_admin
def list_tags():
    try:
        tags = catalog_service.list_tags()
        for t in tags:
            t["_id"] = str(t["_id"])
        return jsonify({"tags": tags}), 200
    except Exception as e:
        logger.error(f"Error listando tags: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

@catalog_bp.route("/tags", methods=["POST"])
@jwt_required()
@require_admin
def create_tag():
    try:
        admin_id = get_jwt_identity()
        data = CreateCatalogItemSchema().load(request.get_json())
        t = catalog_service.create_tag(data["name"], admin_id)
        t["_id"] = str(t["_id"])
        return jsonify({"message": "Etiqueta creada", "tag": t}), 201
    except ValidationError as e:
        return jsonify({"error": "Datos inválidos", "details": e.messages}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        logger.error(f"Error creando tag: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

@catalog_bp.route("/tags/<tag_id>", methods=["PUT"])
@jwt_required()
@require_admin
def update_tag(tag_id):
    try:
        admin_id = get_jwt_identity()
        data = UpdateCatalogItemSchema().load(request.get_json())
        t = catalog_service.update_tag(tag_id, data["name"], admin_id)
        t["_id"] = str(t["_id"])
        return jsonify({"message": "Etiqueta actualizada", "tag": t}), 200
    except ValidationError as e:
        return jsonify({"error": "Datos inválidos", "details": e.messages}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        logger.error(f"Error actualizando tag: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

@catalog_bp.route("/tags/<tag_id>", methods=["DELETE"])
@jwt_required()
@require_admin
def delete_tag(tag_id):
    try:
        admin_id = get_jwt_identity()
        ok = catalog_service.delete_tag(tag_id, admin_id)
        return jsonify({"message": "Etiqueta eliminada" if ok else "No se pudo eliminar"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        logger.error(f"Error eliminando tag: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

@catalog_bp.route("/", methods=["GET"])
def public_catalog():
    """
    Catálogo público de productos
    Usado por tests y vista general
    """
    try:
        products = catalog_service.list_public_products()

        # Normalizar IDs
        for p in products:
            p["_id"] = str(p["_id"])
            if "variants" in p:
                for v in p["variants"]:
                    if "_id" in v:
                        v["_id"] = str(v["_id"])

        return jsonify({
            "products": products
        }), 200

    except Exception as e:
        logger.error(f"Error obteniendo catálogo público: {str(e)}")
        return jsonify({
            "products": []
        }), 200

