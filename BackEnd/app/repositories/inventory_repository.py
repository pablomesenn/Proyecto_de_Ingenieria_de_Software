"""
Inventory Repository with proper lazy database loading
This prevents creating new connections on every instantiation
"""
from bson import ObjectId
from app.config.database import get_db
from app.models.inventory import Inventory
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class InventoryRepository:
    def __init__(self):
        self._db = None

    # ============================================================================
    # LAZY LOADING PROPERTIES - Database is only accessed when needed
    # ============================================================================
    @property
    def db(self):
        """Lazy load database connection - reuses existing connection pool"""
        if self._db is None:
            self._db = get_db()  # This now returns the SHARED database instance
        return self._db

    @property
    def collection(self):
        """Get inventory collection (lazy loaded)"""
        return self.db.inventory

    @property
    def movements_collection(self):
        """Get inventory movements collection (lazy loaded)"""
        return self.db.inventory_movements

    # ============================================================================
    # REPOSITORY METHODS - Now use properties instead of direct access
    # ============================================================================
    def find_by_variant_id(self, variant_id):
        return self.collection.find_one({'variant_id': ObjectId(variant_id)})

    def find_by_id(self, inventory_id):
        return self.collection.find_one({'_id': ObjectId(inventory_id)})

    def get_all(self, skip=0, limit=20):
        cursor = self.collection.find({}).sort('actualizado_en', -1).skip(skip).limit(limit)
        return list(cursor)

    def get_all_with_details(self, skip=0, limit=20):
        pipeline = [
            {
                '$lookup': {
                    'from': 'variants',
                    'localField': 'variant_id',
                    'foreignField': '_id',
                    'as': 'variant_details'
                }
            },
            {'$unwind': '$variant_details'},
            {
                '$lookup': {
                    'from': 'products',
                    'localField': 'variant_details.product_id',
                    'foreignField': '_id',
                    'as': 'product_details'
                }
            },
            {'$unwind': '$product_details'},
            {
                '$project': {
                    '_id': 1,
                    'variant_id': 1,
                    'stock_total': 1,
                    'stock_retenido': 1,
                    'actualizado_en': 1,
                    'creado_en': 1,
                    'product_name': '$product_details.nombre',
                    'variant_size': '$variant_details.tamano_pieza',
                    'variant_price': '$variant_details.precio'
                }
            },
            {'$sort': {'actualizado_en': -1}},
            {'$skip': skip},
            {'$limit': limit}
        ]

        return list(self.collection.aggregate(pipeline))

    def create_initial_stock(self, variant_id, initial_stock, actor_id, reason='Inventario inicial'):
        """Crea un registro de inventario inicial para una variante nueva"""
        from app.models.inventory import Inventory
        
        # Verificar si ya existe un registro de inventario para esta variante
        existing = self.find_by_variant_id(variant_id)
        if existing:
            # Si ya existe, ajustar el stock
            return self.adjust_stock(variant_id, initial_stock, reason, actor_id)
        
        # Crear nuevo registro de inventario
        inventory = Inventory(
            variant_id=ObjectId(variant_id),
            stock_total=initial_stock,
            stock_retenido=0
        )
        
        result = self.collection.insert_one(inventory.to_dict())
        
        # Registrar movimiento
        if initial_stock > 0:
            self._log_movement(
                variant_id=variant_id,
                quantity=initial_stock,
                movement_type='initial',
                reason=reason,
                actor_id=actor_id
            )
        
        return self.collection.find_one({'_id': result.inserted_id})

    def create(self, inventory):
        result = self.collection.insert_one(inventory.to_dict())

        # Registrar movimiento inicial
        self._log_movement(
            variant_id=inventory.variant_id,
            quantity=inventory.stock_total,
            movement_type='initial',
            reason='initial_stock'
        )

        return self.collection.find_one({'_id': result.inserted_id})

    def update_stock_total(self, variant_id, new_stock_total):
        result = self.collection.update_one(
            {'variant_id': ObjectId(variant_id)},
            {
                '$set': {
                    'stock_total': new_stock_total,
                    'actualizado_en': datetime.utcnow()
                }
            }
        )

        return result.modified_count > 0

    def get_available_stock(self, variant_id):
        """Calcula stock disponible (total - retenido)"""
        inventory = self.find_by_variant_id(variant_id)
        if not inventory:
            return 0

        total_stock = inventory.get('stock_total', 0)
        retained_stock = inventory.get('stock_retenido', 0)
        return max(0, total_stock - retained_stock)

    def increase_retained_stock(self, variant_id, quantity, reason='reservation_created'):
        result = self.collection.update_one(
            {'variant_id': ObjectId(variant_id)},
            {
                '$inc': {'stock_retenido': quantity},
                '$set': {'actualizado_en': datetime.utcnow()}
            }
        )

        if result.modified_count > 0:
            self._log_movement(
                variant_id=variant_id,
                quantity=quantity,
                movement_type='retain',
                reason=reason
            )

        return result.modified_count > 0

    def decrease_retained_stock(self, variant_id, quantity, reason='reservation_released'):
        inventory = self.find_by_variant_id(variant_id)
        if not inventory:
            return False

        current_retained = inventory.get('stock_retenido', 0)
        new_retained = max(0, current_retained - quantity)

        result = self.collection.update_one(
            {'variant_id': ObjectId(variant_id)},
            {
                '$set': {
                    'stock_retenido': new_retained,
                    'actualizado_en': datetime.utcnow()
                }
            }
        )

        if result.modified_count > 0:
            self._log_movement(
                variant_id=variant_id,
                quantity=-quantity,
                movement_type='release',
                reason=reason
            )

        return result.modified_count > 0

    def adjust_stock(self, variant_id, delta, reason, actor_id=None):
        """Ajusta el stock total (no el retenido)"""
        logger.info(f"Ajustando stock - Variante: {variant_id}, Delta: {delta}, Razón: {reason}")
        
        inventory = self.find_by_variant_id(variant_id)
        if not inventory:
            logger.error(f"Inventario no encontrado para variante: {variant_id}")
            return False

        current_stock = inventory.get('stock_total', 0)
        new_stock = current_stock + delta

        if new_stock < 0:
            logger.warning(f"Stock resultante sería negativo: {new_stock}")
            return False

        result = self.collection.update_one(
            {'variant_id': ObjectId(variant_id)},
            {
                '$set': {
                    'stock_total': new_stock,
                    'actualizado_en': datetime.utcnow()
                }
            }
        )

        logger.info(f"Stock actualizado: {current_stock} -> {new_stock}. Documentos modificados: {result.modified_count}")

        if result.modified_count > 0:
            movement_id = self._log_movement(
                variant_id=variant_id,
                quantity=delta,
                movement_type='adjustment',
                reason=reason,
                actor_id=actor_id
            )
            logger.info(f"Movimiento registrado con ID: {movement_id}")
        else:
            logger.warning("No se modificó ningún documento, no se registró movimiento")

        return result.modified_count > 0

    def _log_movement(self, variant_id, quantity, movement_type, reason, actor_id=None):
        """Registra un movimiento de inventario en la bitácora"""
        try:
            movement = {
                'variant_id': ObjectId(variant_id) if not isinstance(variant_id, ObjectId) else variant_id,
                'quantity': quantity,
                'movement_type': movement_type,
                'reason': reason,
                'actor_id': ObjectId(actor_id) if actor_id and not isinstance(actor_id, ObjectId) else actor_id,
                'creado_en': datetime.utcnow()
            }
            result = self.movements_collection.insert_one(movement)
            logger.info(f"Movimiento registrado: {movement_type} - Variante: {variant_id} - Cantidad: {quantity}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error registrando movimiento de inventario: {str(e)}")
            logger.error(f"Datos del movimiento: variant_id={variant_id}, quantity={quantity}, type={movement_type}")
            return None

    def get_movements(self, variant_id=None, movement_type=None, skip=0, limit=50):
        """Obtiene el historial de movimientos"""
        query = {}
        if variant_id:
            query['variant_id'] = ObjectId(variant_id)
        if movement_type:
            query['movement_type'] = movement_type

        cursor = self.movements_collection.find(query).sort('creado_en', -1).skip(skip).limit(limit)
        return list(cursor)

    def validate_availability(self, variant_id, quantity):
        """Valida si hay suficiente stock disponible"""
        available = self.get_available_stock(variant_id)
        return available >= quantity

    def count(self):
        """Cuenta el total de registros de inventario"""
        return self.collection.count_documents({})