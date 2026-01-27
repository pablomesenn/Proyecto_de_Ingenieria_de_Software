from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.repositories.inventory_repository import InventoryRepository
from app.services.inventory_service import InventoryService
from app.schemas.inventory_schema import (
    InventoryQuerySchema,
    CreateInventorySchema,
    UpdateInventoryStockSchema,
    AdjustInventorySchema,
    RetainStockSchema,
    ReleaseStockSchema,
    InventoryMovementQuerySchema
)
from marshmallow import ValidationError
from app.constants.roles import UserRole
import logging

logger = logging.getLogger(__name__)

inventory_bp = Blueprint('inventory', __name__)
inventory_service = InventoryService()


def require_role(required_role):
    """Decorador para verificar rol de usuario"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            jwt_data = get_jwt()
            user_role = jwt_data.get('role')

            if user_role != required_role and user_role != UserRole.ADMIN:
                return jsonify({'error': 'Permisos insuficientes'}), 403

            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


@inventory_bp.route('/', methods=['GET'])
@jwt_required()
@require_role(UserRole.ADMIN)
def get_all_inventory():
    """
    Obtiene todo el inventario con detalles (ADMIN)
    Query params: skip, limit
    """
    try:
        # Validar parámetros
        schema = InventoryQuerySchema()
        params = schema.load(request.args)

        # Obtener inventario
        inventory = inventory_service.get_all_inventory(
            skip=params.get('skip', 0),
            limit=params.get('limit', 20)
        )

        return jsonify({
            'inventory': inventory,
            'count': len(inventory)
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Parámetros inválidos', 'details': e.messages}), 400
    except Exception as e:
        logger.error(f"Error obteniendo inventario: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@inventory_bp.route('/variant/<variant_id>', methods=['GET'])
def get_inventory_by_variant(variant_id):
    """
    Obtiene el inventario de una variante específica
    Disponible para todos (incluye disponibilidad)
    """
    try:
        inventory = inventory_service.get_inventory_by_variant(variant_id)
        return jsonify(inventory), 200

    except Exception as e:
        logger.error(f"Error obteniendo inventario de variante: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@inventory_bp.route('/', methods=['POST'])
@jwt_required()
@require_role(UserRole.ADMIN)
def create_inventory():
    """
    Crea un nuevo registro de inventario (ADMIN)
    """
    try:
        admin_id = get_jwt_identity()

        # Validar datos
        schema = CreateInventorySchema()
        data = schema.load(request.get_json())

        # Crear inventario
        inventory = inventory_service.create_inventory(
            variant_id=data['variant_id'],
            stock_total=data['stock_total'],
            stock_retenido=data.get('stock_retenido', 0),
            admin_id=admin_id
        )

        return jsonify({
            'message': 'Inventario creado exitosamente',
            'inventory': inventory
        }), 201

    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando inventario: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@inventory_bp.route('/variant/<variant_id>/stock', methods=['PUT'])
@jwt_required()
@require_role(UserRole.ADMIN)
def update_stock_total(variant_id):
    """
    Actualiza el stock total de una variante (ADMIN)
    Reemplaza el stock total por un nuevo valor
    """
    try:
        admin_id = get_jwt_identity()

        # Validar datos
        schema = UpdateInventoryStockSchema()
        data = schema.load(request.get_json())

        # Actualizar stock
        inventory = inventory_service.update_stock_total(
            variant_id=variant_id,
            new_stock_total=data['stock_total'],
            admin_id=admin_id
        )

        return jsonify({
            'message': 'Stock actualizado exitosamente',
            'inventory': inventory
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error actualizando stock: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@inventory_bp.route('/variant/<variant_id>/adjust', methods=['POST'])
@jwt_required()
@require_role(UserRole.ADMIN)
def adjust_inventory(variant_id):
    """
    Ajusta el inventario (incrementa o decrementa) (ADMIN)
    Body: { "delta": 10, "reason": "Recepción de mercancía" }
    delta positivo = incremento, delta negativo = decremento
    """
    try:
        admin_id = get_jwt_identity()

        # Validar datos
        schema = AdjustInventorySchema()
        data = schema.load(request.get_json())

        # Ajustar inventario
        inventory = inventory_service.adjust_inventory(
            variant_id=variant_id,
            delta=data['delta'],
            reason=data['reason'],
            admin_id=admin_id
        )

        action = 'incrementado' if data['delta'] > 0 else 'decrementado'

        return jsonify({
            'message': f'Inventario {action} exitosamente',
            'inventory': inventory
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error ajustando inventario: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@inventory_bp.route('/variant/<variant_id>/retain', methods=['POST'])
@jwt_required()
@require_role(UserRole.ADMIN)
def retain_stock(variant_id):
    """
    Retiene stock manualmente (ADMIN)
    Útil para casos especiales fuera del flujo de reservas
    """
    try:
        admin_id = get_jwt_identity()

        # Validar datos
        schema = RetainStockSchema()
        data = schema.load(request.get_json())

        # Retener stock
        inventory = inventory_service.retain_stock(
            variant_id=variant_id,
            quantity=data['quantity'],
            reason=data.get('reason', 'manual_retention'),
            actor_id=admin_id
        )

        return jsonify({
            'message': 'Stock retenido exitosamente',
            'inventory': inventory
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error reteniendo stock: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@inventory_bp.route('/variant/<variant_id>/release', methods=['POST'])
@jwt_required()
@require_role(UserRole.ADMIN)
def release_stock(variant_id):
    """
    Libera stock retenido manualmente (ADMIN)
    Útil para casos especiales fuera del flujo de reservas
    """
    try:
        admin_id = get_jwt_identity()

        # Validar datos
        schema = ReleaseStockSchema()
        data = schema.load(request.get_json())

        # Liberar stock
        inventory = inventory_service.release_stock(
            variant_id=variant_id,
            quantity=data['quantity'],
            reason=data.get('reason', 'manual_release'),
            actor_id=admin_id
        )

        return jsonify({
            'message': 'Stock liberado exitosamente',
            'inventory': inventory
        }), 200

    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error liberando stock: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@inventory_bp.route("/movements", methods=["GET"])
def movements():
    skip = int(request.args.get("skip", 0))
    limit = int(request.args.get("limit", 50))
    variant_id = request.args.get("variant_id")
    movement_type = request.args.get("movement_type")

    filters = {}
    if variant_id:
        filters["variant_id"] = variant_id
    if movement_type:
        filters["movement_type"] = movement_type

    repo = InventoryRepository()
    data = repo.get_movements_detailed(skip=skip, limit=limit, filters=filters)

    # Convertir ObjectId a string
    for m in data:
        m["_id"] = str(m["_id"])
        m["variant_id"] = str(m["variant_id"])
        if m.get("actor_id"):
            m["actor_id"] = str(m["actor_id"])

    return jsonify({"movements": data}), 200




@inventory_bp.route('/low-stock', methods=['GET'])
@jwt_required()
@require_role(UserRole.ADMIN)
def get_low_stock_alerts():
    """
    Obtiene alertas de stock bajo (ADMIN)
    Query param: threshold (default: 10)
    """
    try:
        threshold = int(request.args.get('threshold', 10))

        low_stock = inventory_service.get_low_stock_alerts(threshold=threshold)

        return jsonify({
            'low_stock_items': low_stock,
            'count': len(low_stock),
            'threshold': threshold
        }), 200

    except ValueError:
        return jsonify({'error': 'Threshold debe ser un número entero'}), 400
    except Exception as e:
        logger.error(f"Error obteniendo alertas de stock bajo: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
