from mongoengine import (
    Document, EmbeddedDocument, StringField,
    ListField, DateTimeField, ReferenceField,
    EmbeddedDocumentField, IntField
)
from datetime import datetime
from app.constants.states import ProductState


class Variant(EmbeddedDocument):
    """
    Variante de producto (por tamaño)
    Según Tabla 20 del ERS

    Campos:
    - id (generado automáticamente)
    - tamano_pieza: tamaño de la pieza
    - unidad: unidad de medida (ej: "cm", "m")
    - creado_en: timestamp de creación
    """

    tamano_pieza = StringField(required=True, max_length=100)
    unidad = StringField(required=True, max_length=20)
    creado_en = DateTimeField(default=datetime.utcnow)

    def to_dict(self):
        """Convierte la variante a diccionario"""
        return {
            'tamano_pieza': self.tamano_pieza,
            'unidad': self.unidad,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }


class Product(Document):
    """
    Modelo de Producto según Tabla 20 del ERS

    Campos:
    - id (automático por MongoDB)
    - nombre
    - imagen_url
    - categoria
    - tags[]
    - estado (activo/inactivo/agotado)
    - descripcion_embalaje
    - variantes[] (embedded)
    - creado_en
    - actualizado_en
    """

    meta = {
        'collection': 'products',
        'indexes': [
            'nombre',
            'categoria',
            'tags',
            'estado',
            '-creado_en',
            {
                'fields': ['$nombre', '$descripcion_embalaje'],
                'default_language': 'spanish',
                'weights': {'nombre': 10, 'descripcion_embalaje': 5}
            }
        ]
    }

    nombre = StringField(required=True, max_length=255)
    imagen_url = StringField(max_length=500)
    categoria = StringField(required=True, max_length=100)
    tags = ListField(StringField(max_length=100), default=list)
    estado = StringField(
        required=True,
        choices=ProductState.all_states(),
        default=ProductState.ACTIVE
    )
    descripcion_embalaje = StringField(max_length=1000)
    variantes = ListField(EmbeddedDocumentField(Variant), default=list)

    creado_en = DateTimeField(default=datetime.utcnow)
    actualizado_en = DateTimeField(default=datetime.utcnow)

    def is_visible(self):
        """Verifica si el producto es visible para clientes"""
        return self.estado in ProductState.visible_states()

    def save(self, *args, **kwargs):
        """Override del método save para actualizar timestamp"""
        self.actualizado_en = datetime.utcnow()
        return super(Product, self).save(*args, **kwargs)

    def to_dict(self, include_variants=True, include_availability=False):
        """
        Convierte el producto a diccionario

        Args:
            include_variants: Si incluir variantes
            include_availability: Si incluir disponibilidad (requiere consulta adicional)

        Returns:
            dict: Representación del producto
        """
        data = {
            'id': str(self.id),
            'nombre': self.nombre,
            'imagen_url': self.imagen_url,
            'categoria': self.categoria,
            'tags': self.tags,
            'estado': self.estado,
            'descripcion_embalaje': self.descripcion_embalaje,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
            'actualizado_en': self.actualizado_en.isoformat() if self.actualizado_en else None,
        }

        if include_variants:
            data['variantes'] = [v.to_dict() for v in self.variantes]

        return data

    def __repr__(self):
        return f'<Product {self.nombre} ({self.estado})>'

    def __str__(self):
        return self.nombre
