"""
Modelo de Wishlist
Define la estructura para listas de deseos de clientes
"""
from mongoengine import (
    Document, EmbeddedDocument, ReferenceField,
    IntField, DateTimeField, ListField, EmbeddedDocumentField
)
from datetime import datetime


class WishlistItem(EmbeddedDocument):
    """
    Ítem de wishlist

    Campos:
    - producto_id: referencia al producto
    - variante_index: índice de la variante seleccionada
    - cantidad: cantidad deseada
    - agregado_en: timestamp cuando se agregó
    """

    producto_id = ReferenceField('Product', required=True)
    variante_index = IntField(required=True, min_value=0)
    cantidad = IntField(required=True, min_value=1, default=1)
    agregado_en = DateTimeField(default=datetime.utcnow)

    def to_dict(self, include_product=False, include_availability=False):
        """
        Convierte el ítem a diccionario

        Args:
            include_product: Si incluir datos del producto
            include_availability: Si incluir disponibilidad
        """
        data = {
            'producto_id': str(self.producto_id.id),
            'variante_index': self.variante_index,
            'cantidad': self.cantidad,
            'agregado_en': self.agregado_en.isoformat() if self.agregado_en else None,
        }

        if include_product and self.producto_id:
            data['producto'] = self.producto_id.to_dict()
            if self.variante_index < len(self.producto_id.variantes):
                data['variante'] = self.producto_id.variantes[self.variante_index].to_dict()

        return data


class Wishlist(Document):
    """
    Wishlist del cliente
    Según Tabla 20 del ERS

    Campos:
    - id (automático)
    - usuario_id: referencia al usuario
    - items: lista de ítems
    - creado_en: timestamp de creación
    - actualizado_en: timestamp de última actualización
    """

    meta = {
        'collection': 'wishlists',
        'indexes': [
            {'fields': ['usuario_id'], 'unique': True},  # Una wishlist por usuario
            '-actualizado_en'
        ]
    }

    usuario_id = ReferenceField('User', required=True, unique=True)
    items = ListField(EmbeddedDocumentField(WishlistItem), default=list)
    creado_en = DateTimeField(default=datetime.utcnow)
    actualizado_en = DateTimeField(default=datetime.utcnow)

    def find_item_index(self, producto_id, variante_index):
        """
        Busca el índice de un ítem en la wishlist

        Args:
            producto_id: ID del producto
            variante_index: Índice de la variante

        Returns:
            int or None: Índice del ítem o None si no existe
        """
        for i, item in enumerate(self.items):
            if (str(item.producto_id.id) == str(producto_id) and
                item.variante_index == variante_index):
                return i
        return None

    def add_or_update_item(self, producto_id, variante_index, cantidad):
        """
        Agrega un ítem o actualiza la cantidad si ya existe (consolidación)
        Implementa RF-11: Detección de duplicados y consolidación

        Args:
            producto_id: ID del producto
            variante_index: Índice de la variante
            cantidad: Cantidad a agregar

        Returns:
            str: 'added' si se agregó nuevo, 'updated' si se consolidó
        """
        existing_index = self.find_item_index(producto_id, variante_index)

        if existing_index is not None:
            # Consolidar: aumentar cantidad del ítem existente
            self.items[existing_index].cantidad += cantidad
            self.actualizado_en = datetime.utcnow()
            self.save()
            return 'updated'
        else:
            # Agregar nuevo ítem
            from app.models.product import Product
            producto = Product.objects.get(id=producto_id)

            new_item = WishlistItem(
                producto_id=producto,
                variante_index=variante_index,
                cantidad=cantidad
            )
            self.items.append(new_item)
            self.actualizado_en = datetime.utcnow()
            self.save()
            return 'added'

    def update_item_quantity(self, producto_id, variante_index, cantidad):
        """
        Actualiza la cantidad de un ítem específico

        Args:
            producto_id: ID del producto
            variante_index: Índice de la variante
            cantidad: Nueva cantidad

        Returns:
            bool: True si se actualizó, False si no se encontró
        """
        existing_index = self.find_item_index(producto_id, variante_index)

        if existing_index is not None:
            if cantidad <= 0:
                # Eliminar si la cantidad es 0 o negativa
                del self.items[existing_index]
            else:
                self.items[existing_index].cantidad = cantidad

            self.actualizado_en = datetime.utcnow()
            self.save()
            return True

        return False

    def remove_item(self, producto_id, variante_index):
        """
        Elimina un ítem de la wishlist

        Args:
            producto_id: ID del producto
            variante_index: Índice de la variante

        Returns:
            bool: True si se eliminó, False si no se encontró
        """
        existing_index = self.find_item_index(producto_id, variante_index)

        if existing_index is not None:
            del self.items[existing_index]
            self.actualizado_en = datetime.utcnow()
            self.save()
            return True

        return False

    def clear(self):
        """Vacía la wishlist completamente"""
        self.items = []
        self.actualizado_en = datetime.utcnow()
        self.save()

    def get_total_items(self):
        """Obtiene el número total de ítems"""
        return len(self.items)

    def save(self, *args, **kwargs):
        """Override del método save para actualizar timestamp"""
        self.actualizado_en = datetime.utcnow()
        return super(Wishlist, self).save(*args, **kwargs)

    def to_dict(self, include_products=True, include_availability=False):
        """
        Convierte la wishlist a diccionario

        Args:
            include_products: Si incluir datos de productos
            include_availability: Si incluir disponibilidad
        """
        return {
            'id': str(self.id),
            'usuario_id': str(self.usuario_id.id),
            'items': [
                item.to_dict(
                    include_product=include_products,
                    include_availability=include_availability
                )
                for item in self.items
            ],
            'total_items': self.get_total_items(),
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
            'actualizado_en': self.actualizado_en.isoformat() if self.actualizado_en else None,
        }

    def __repr__(self):
        return f'<Wishlist usuario={self.usuario_id.id} items={len(self.items)}>'
