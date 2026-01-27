from bson import ObjectId
from datetime import datetime


class Inventory:
    """
    Modelo de Inventario para variantes de productos
    """
    def __init__(self, variant_id, stock_total=0, stock_retenido=0):
        self.variant_id = ObjectId(variant_id) if isinstance(variant_id, str) else variant_id
        self.stock_total = stock_total
        self.stock_retenido = stock_retenido
        self.creado_en = datetime.utcnow()
        self.actualizado_en = datetime.utcnow()

    def to_dict(self):
        """Convierte el modelo a diccionario para MongoDB"""
        return {
            'variant_id': self.variant_id,
            'stock_total': self.stock_total,
            'stock_retenido': self.stock_retenido,
            'creado_en': self.creado_en,
            'actualizado_en': self.actualizado_en
        }

    @staticmethod
    def from_dict(data):
        """Crea una instancia desde un diccionario de MongoDB"""
        inventory = Inventory(
            variant_id=data['variant_id'],
            stock_total=data.get('stock_total', 0),
            stock_retenido=data.get('stock_retenido', 0)
        )
        inventory.creado_en = data.get('creado_en', datetime.utcnow())
        inventory.actualizado_en = data.get('actualizado_en', datetime.utcnow())
        return inventory

    def get_disponibilidad(self):
        """Calcula el stock disponible (total - retenido)"""
        return max(0, self.stock_total - self.stock_retenido)

    def __repr__(self):
        return f"<Inventory variant_id={self.variant_id} total={self.stock_total} retenido={self.stock_retenido}>"