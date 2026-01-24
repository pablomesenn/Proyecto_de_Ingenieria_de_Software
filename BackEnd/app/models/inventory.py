"""
Modelos de Inventario
Define la estructura para inventario y movimientos
"""
from mongoengine import (
    Document, StringField, IntField,
    DateTimeField, ReferenceField
)
from datetime import datetime
from app.constants.states import InventoryAdjustmentReason


class Inventory(Document):
    """
    Inventario por variante
    Según Tabla 20 del ERS

    Campos:
    - id (automático)
    - producto_id: referencia al producto
    - variante_index: índice de la variante en el producto
    - stock_total: stock físico total
    - stock_retenido: stock retenido por reservas activas
    - actualizado_en: timestamp de última actualización

    Disponibilidad calculada: stock_total - stock_retenido
    """

    meta = {
        'collection': 'inventory',
        'indexes': [
            'producto_id',
            ('producto_id', 'variante_index'),  # Índice compuesto único
            '-actualizado_en'
        ]
    }

    producto_id = ReferenceField('Product', required=True)
    variante_index = IntField(required=True, min_value=0)
    stock_total = IntField(required=True, min_value=0, default=0)
    stock_retenido = IntField(required=True, min_value=0, default=0)
    actualizado_en = DateTimeField(default=datetime.utcnow)

    def get_disponibilidad(self):
        """Calcula la disponibilidad real"""
        return max(0, self.stock_total - self.stock_retenido)

    def can_reserve(self, cantidad):
        """Verifica si hay disponibilidad para reservar"""
        return self.get_disponibilidad() >= cantidad

    def reserve_stock(self, cantidad):
        """
        Retiene stock para una reserva

        Args:
            cantidad: Cantidad a retener

        Returns:
            bool: True si se pudo retener, False si no hay disponibilidad
        """
        if not self.can_reserve(cantidad):
            return False

        self.stock_retenido += cantidad
        self.actualizado_en = datetime.utcnow()
        self.save()
        return True

    def release_stock(self, cantidad):
        """
        Libera stock retenido

        Args:
            cantidad: Cantidad a liberar
        """
        self.stock_retenido = max(0, self.stock_retenido - cantidad)
        self.actualizado_en = datetime.utcnow()
        self.save()

    def adjust_total(self, delta):
        """
        Ajusta el stock total

        Args:
            delta: Cambio en el stock (puede ser positivo o negativo)

        Returns:
            bool: True si el ajuste es válido, False si resultaría en stock negativo
        """
        new_total = self.stock_total + delta
        if new_total < 0:
            return False

        self.stock_total = new_total
        self.actualizado_en = datetime.utcnow()
        self.save()
        return True

    def save(self, *args, **kwargs):
        """Override del método save para actualizar timestamp"""
        self.actualizado_en = datetime.utcnow()
        return super(Inventory, self).save(*args, **kwargs)

    def to_dict(self):
        """Convierte el inventario a diccionario"""
        return {
            'id': str(self.id),
            'producto_id': str(self.producto_id.id),
            'variante_index': self.variante_index,
            'stock_total': self.stock_total,
            'stock_retenido': self.stock_retenido,
            'disponibilidad': self.get_disponibilidad(),
            'actualizado_en': self.actualizado_en.isoformat() if self.actualizado_en else None,
        }

    def __repr__(self):
        return f'<Inventory producto={self.producto_id.id} variante={self.variante_index} disponible={self.get_disponibilidad()}>'


class InventoryMovement(Document):
    """
    Movimiento de inventario (bitácora)
    Según Tabla 20 del ERS

    Campos:
    - id (automático)
    - inventario_id: referencia al inventario
    - motivo: razón del ajuste
    - delta: cambio en el stock (+/-)
    - actor_id: quién realizó el cambio
    - fecha: timestamp del movimiento
    - referencia: referencia opcional (ej: ID de reserva)
    """

    meta = {
        'collection': 'inventory_movements',
        'indexes': [
            'inventario_id',
            'actor_id',
            '-fecha',
            'motivo'
        ]
    }

    inventario_id = ReferenceField('Inventory', required=True)
    motivo = StringField(
        required=True,
        choices=InventoryAdjustmentReason.all_reasons()
    )
    delta = IntField(required=True)
    actor_id = ReferenceField('User', required=True)
    fecha = DateTimeField(default=datetime.utcnow)
    referencia = StringField(max_length=255)  # Ej: reservation_id

    def to_dict(self):
        """Convierte el movimiento a diccionario"""
        return {
            'id': str(self.id),
            'inventario_id': str(self.inventario_id.id),
            'motivo': self.motivo,
            'delta': self.delta,
            'actor_id': str(self.actor_id.id),
            'actor_nombre': self.actor_id.nombre if self.actor_id else None,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'referencia': self.referencia,
        }

    def __repr__(self):
        return f'<InventoryMovement {self.motivo} delta={self.delta} at {self.fecha}>'
