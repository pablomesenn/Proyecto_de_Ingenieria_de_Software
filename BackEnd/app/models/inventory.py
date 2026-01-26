from datetime import datetime
from bson import ObjectId


class Inventory:

    def __init__(self, variant_id, stock_total=0, stock_retenido=0,
                 actualizado_en=None, creado_en=None, _id=None):
        """
        Inicializa una instancia de Inventory

        Args:
            variant_id: ID de la variante de producto
            stock_total: Stock total disponible en inventario
            stock_retenido: Stock retenido por reservas activas
            actualizado_en: Fecha de última actualización
            creado_en: Fecha de creación
            _id: ID del documento (generado por MongoDB)
        """
        self._id = _id
        self.variant_id = ObjectId(variant_id) if not isinstance(variant_id, ObjectId) else variant_id
        self.stock_total = stock_total
        self.stock_retenido = stock_retenido
        self.actualizado_en = actualizado_en or datetime.utcnow()
        self.creado_en = creado_en or datetime.utcnow()

    def to_dict(self):
        doc = {
            'variant_id': self.variant_id,
            'stock_total': self.stock_total,
            'stock_retenido': self.stock_retenido,
            'actualizado_en': self.actualizado_en,
            'creado_en': self.creado_en
        }

        if self._id:
            doc['_id'] = self._id

        return doc

    @staticmethod
    def from_dict(data):
        """
        Crea una instancia de Inventory desde un diccionario de MongoDB
        """
        if not data:
            return None

        return Inventory(
            _id=data.get('_id'),
            variant_id=data.get('variant_id'),
            stock_total=data.get('stock_total', 0),
            stock_retenido=data.get('stock_retenido', 0),
            actualizado_en=data.get('actualizado_en'),
            creado_en=data.get('creado_en')
        )

    def get_disponibilidad(self):
        """
        Calcula el stock disponible (stock total - stock retenido)

        Returns:
            int: Stock disponible para nuevas reservas
        """
        return max(0, self.stock_total - self.stock_retenido)

    def puede_retener(self, quantity):
        """
        Verifica si se puede retener la cantidad solicitada

        Args:
            quantity: Cantidad a retener

        Returns:
            bool: True si hay suficiente stock disponible
        """
        return self.get_disponibilidad() >= quantity

    def __repr__(self):
        return (f"Inventory(variant_id={self.variant_id}, "
                f"stock_total={self.stock_total}, "
                f"stock_retenido={self.stock_retenido}, "
                f"disponibilidad={self.get_disponibilidad()})")
