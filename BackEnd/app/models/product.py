from datetime import datetime
from bson import ObjectId

""" File para los productos, las variates y los wishlist"""

class Product:
    def __init__(
        self,
        nombre,
        imagen_url,
        categoria,
        tags=None,
        estado='activo',
        descripcion_embalaje=None,
        variantes=None,
        created_at=None,
        updated_at=None,
        _id=None
    ):
        self._id = _id or ObjectId()
        self.nombre = nombre
        self.imagen_url = imagen_url
        self.categoria = categoria
        self.tags = tags or []
        self.estado = estado  # activo, inactivo, agotado
        self.descripcion_embalaje = descripcion_embalaje
        self.variantes = variantes or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        """Convierte el modelo a diccionario para MongoDB"""
        return {
            '_id': self._id,
            'nombre': self.nombre,
            'imagen_url': self.imagen_url,
            'categoria': self.categoria,
            'tags': self.tags,
            'estado': self.estado,
            'descripcion_embalaje': self.descripcion_embalaje,
            'variantes': self.variantes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data):
        """Crea una instancia desde un diccionario"""
        if not data:
            return None
        return Product(
            nombre=data.get('nombre'),
            imagen_url=data.get('imagen_url'),
            categoria=data.get('categoria'),
            tags=data.get('tags', []),
            estado=data.get('estado', 'activo'),
            descripcion_embalaje=data.get('descripcion_embalaje'),
            variantes=data.get('variantes', []),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            _id=data.get('_id')
        )

    def is_visible(self):
        """Verifica si el producto es visible para clientes"""
        return self.estado == 'activo'


class Variant:
    """
    Modelo de Variante de Producto que varía únicamente por tamaño
    """

    def __init__(
        self,
        product_id,
        tamano_pieza,
        unidad='m²',
        precio=None,
        created_at=None,
        _id=None
    ):
        self._id = _id or ObjectId()
        self.product_id = ObjectId(product_id) if not isinstance(product_id, ObjectId) else product_id
        self.tamano_pieza = tamano_pieza
        self.unidad = unidad
        self.precio = precio
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        """Convierte el modelo a diccionario para MongoDB"""
        return {
            '_id': self._id,
            'product_id': self.product_id,
            'tamano_pieza': self.tamano_pieza,
            'unidad': self.unidad,
            'precio': self.precio,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data):
        """Crea una instancia desde un diccionario"""
        if not data:
            return None
        return Variant(
            product_id=data.get('product_id'),
            tamano_pieza=data.get('tamano_pieza'),
            unidad=data.get('unidad', 'm²'),
            precio=data.get('precio'),
            created_at=data.get('created_at'),
            _id=data.get('_id')
        )


class Wishlist:
    """
    Modelo de Wishlist según ERS
    Lista de deseos de un cliente
    """

    def __init__(
        self,
        user_id,
        items=None,
        created_at=None,
        updated_at=None,
        _id=None
    ):
        self._id = _id or ObjectId()
        self.user_id = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
        self.items = items or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        """Convierte el modelo a diccionario para MongoDB"""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'items': self.items,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data):
        """Crea una instancia desde un diccionario"""
        if not data:
            return None
        return Wishlist(
            user_id=data.get('user_id'),
            items=data.get('items', []),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            _id=data.get('_id')
        )

    def add_item(self, variant_id, quantity=1):
        """Agrega o consolida un item en la wishlist"""
        # Buscar si el item ya existe
        for item in self.items:
            if str(item['variant_id']) == str(variant_id):
                # Consolidar: incrementar cantidad
                item['quantity'] += quantity
                item['updated_at'] = datetime.utcnow()
                return item

        # Si no existe, agregar nuevo item
        new_item = {
            'item_id': ObjectId(),
            'variant_id': ObjectId(variant_id) if not isinstance(variant_id, ObjectId) else variant_id,
            'quantity': quantity,
            'added_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        self.items.append(new_item)
        return new_item

    def remove_item(self, item_id):
        """Elimina un item de la wishlist"""
        self.items = [item for item in self.items if str(item['item_id']) != str(item_id)]

    def update_item_quantity(self, item_id, quantity):
        """Actualiza la cantidad de un item"""
        for item in self.items:
            if str(item['item_id']) == str(item_id):
                item['quantity'] = quantity
                item['updated_at'] = datetime.utcnow()
                return item
        return None

    def clear(self):
        """Limpia todos los items de la wishlist"""
        self.items = []
