"""
Schemas para Catálogo
Validación de datos para CU-005: Buscar y filtrar catálogo
"""
from marshmallow import Schema, fields, validate, validates, ValidationError


class ProductSearchSchema(Schema):
    """Schema para búsqueda de productos"""
    texto = fields.Str(required=False, allow_none=True)
    categoria = fields.Str(required=False, allow_none=True)
    tags = fields.Str(required=False, allow_none=True)  # Separados por coma
    disponible = fields.Bool(required=False, missing=False)
    page = fields.Int(required=False, missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(
        required=False,
        missing=20,
        validate=validate.Range(min=1, max=100)
    )


class ProductFilterSchema(Schema):
    """Schema para filtros de productos"""
    q = fields.Str(required=True, validate=validate.Length(min=1))
    categoria = fields.Str(required=False, allow_none=True)
    tags = fields.Str(required=False, allow_none=True)
    disponible = fields.Bool(required=False, missing=False)
    page = fields.Int(required=False, missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(
        required=False,
        missing=20,
        validate=validate.Range(min=1, max=100)
    )


class VarianteSchema(Schema):
    """Schema para variante de producto"""
    variante_index = fields.Int(required=True, validate=validate.Range(min=0))
    tamano_pieza = fields.Str(required=True)
    unidad = fields.Str(required=True)
    stock_total = fields.Int(required=False)
    stock_retenido = fields.Int(required=False)
    disponibilidad = fields.Int(required=False)


class ProductDetailSchema(Schema):
    """Schema para detalle de producto"""
    id = fields.Str(required=True)
    nombre = fields.Str(required=True)
    imagen_url = fields.Str(required=False, allow_none=True)
    categoria = fields.Str(required=True)
    tags = fields.List(fields.Str(), required=False)
    estado = fields.Str(required=True)
    descripcion_embalaje = fields.Str(required=False, allow_none=True)
    variantes = fields.List(fields.Nested(VarianteSchema), required=False)
    variantes_disponibilidad = fields.List(
        fields.Nested(VarianteSchema),
        required=False
    )
    creado_en = fields.DateTime(required=False)
    actualizado_en = fields.DateTime(required=False)


class ProductListResponseSchema(Schema):
    """Schema para respuesta de listado de productos"""
    products = fields.List(fields.Nested(ProductDetailSchema))
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    total_pages = fields.Int()
