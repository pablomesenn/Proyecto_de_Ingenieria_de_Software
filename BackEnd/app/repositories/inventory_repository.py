from bson import ObjectId
from app.config.database import get_db
from datetime import datetime


class InventoryRepository:
    """Repositorio para operaciones de inventario"""
    
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.inventory
        self.movements_collection = self.db.inventory_movements
        
    def find_by_variant_id(self, variant_id):
        """Busca inventario por ID de variante"""
        return self.collection.find_one({'variant_id': ObjectId(variant_id)})
    
    def get_available_stock(self, variant_id):
        """Calcula stock disponible (total - retenido)"""
        inventory = self.find_by_variant_id(variant_id)
        if not inventory:
            return 0
        
        total_stock = inventory.get('stock_total', 0)
        retained_stock = inventory.get('stock_retenido', 0)
        return max(0, total_stock - retained_stock)
    
    def increase_retained_stock(self, variant_id, quantity, reason='reservation_created'):
        """Incrementa el stock retenido"""
        result = self.collection.update_one(
            {'variant_id': ObjectId(variant_id)},
            {
                '$inc': {'stock_retenido': quantity},
                '$set': {'updated_at': datetime.utcnow()}
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
        """Disminuye el stock retenido"""
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
                    'updated_at': datetime.utcnow()
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
        inventory = self.find_by_variant_id(variant_id)
        if not inventory:
            return False
        
        current_stock = inventory.get('stock_total', 0)
        new_stock = current_stock + delta
        
        if new_stock < 0:
            return False
        
        result = self.collection.update_one(
            {'variant_id': ObjectId(variant_id)},
            {
                '$set': {
                    'stock_total': new_stock,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            self._log_movement(
                variant_id=variant_id,
                quantity=delta,
                movement_type='adjustment',
                reason=reason,
                actor_id=actor_id
            )
            
        return result.modified_count > 0
    
    def _log_movement(self, variant_id, quantity, movement_type, reason, actor_id=None):
        """Registra un movimiento de inventario en la bitacora"""
        movement = {
            'variant_id': ObjectId(variant_id),
            'quantity': quantity,
            'movement_type': movement_type,
            'reason': reason,
            'actor_id': ObjectId(actor_id) if actor_id else None,
            'created_at': datetime.utcnow()
        }
        self.movements_collection.insert_one(movement)
    
    def get_movements(self, variant_id=None, skip=0, limit=50):
        """Obtiene el historial de movimientos"""
        query = {}
        if variant_id:
            query['variant_id'] = ObjectId(variant_id)
        
        cursor = self.movements_collection.find(query).sort('created_at', -1).skip(skip).limit(limit)
        return list(cursor)
    
    def validate_availability(self, variant_id, quantity):
        """Valida si hay suficiente stock disponible"""
        available = self.get_available_stock(variant_id)
        return available >= quantity