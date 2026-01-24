from marshmallow import Schema, fields, validate, validates, ValidationError
from app.constants.states import ProductState


class VarianteInputSchema(Schema):
    """Schema para input de variante"""
    tamano_pieza = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    unidad = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=20)
    )


class VarianteOutputSchema(Schema):
    """Schema para output de variante con disponibilidad"""
    variante_index = fields.Int(required=True)
    tamano_pieza = fields.Str(required=True)
    unidad = fields.Str(required=True)
    stock_total = fields.Int(required=False)
    stock_retenido = fields.Int(required=False)
    disponibilidad = fields.Int(required=False)
    creado_en = fields.DateTime(required=False)


class CreateProductSchema(Schema):
    """Schema para crear producto"""
    nombre = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255)
    )
    imagen_url = fields.Url(required=False, allow_none=True)
    categoria = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
    tags = fields.List(
        fields.Str(validate=validate.Length(max=100)),
        required=False,
        missing=[]
    )
    estado = fields.Str(
        required=False,
        missing=ProductState.ACTIVE,
        validate=validate.OneOf(ProductState.all_states())
    )
    descripcion_embalaje = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=1000)
    )
    variantes = fields.List(
        fields.Nested(VarianteInputSchema),
        required=True,
        validate=validate.Length(min=1)
    )


class UpdateProductSchema(Schema):
    """Schema para actualizar producto"""
    nombre = fields.Str(
        required=False,
        validate=validate.Length(min=1, max=255)
    )
    imagen_url = fields.Url(required=False, allow_none=True)
    categoria = fields.Str(
        required=False,
        validate=validate.Length(min=1, max=100)
    )
    tags = fields.List(
        fields.Str(validate=validate.Length(max=100)),
        required=False
    )
    estado = fields.Str(
        required=False,
        validate=validate.OneOf(ProductState.all_states())
    )
    descripcion_embalaje = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=1000)
    )
    variantes = fields.List(
        fields.Nested(VarianteInputSchema),
        required=False
    )


class ProductResponseSchema(Schema):
    """Schema para respuesta de producto"""
    id = fields.Str(required=True)
    nombre = fields.Str(required=True)
    imagen_url = fields.Str(allow_none=True)
    categoria = fields.Str(required=True)
    tags = fields.List(fields.Str())
    estado = fields.Str(required=True)
    descripcion_embalaje = fields.Str(allow_none=True)
    variantes = fields.List(fields.Nested(VarianteOutputSchema))
    variantes_disponibilidad = fields.List(
        fields.Nested(VarianteOutputSchema),
        required=False
    )
    creado_en = fields.DateTime(required=True)
    actualizado_en = fields.DateTime(required=True)


class ProductListQuerySchema(Schema):
    """Schema para query params de listado de productos"""
    page = fields.Int(
        required=False,
        missing=1,
        validate=validate.Range(min=1)
    )
    per_page = fields.Int(
        required=False,
        missing=20,
        validate=validate.Range(min=1, max=100)
    )
    categoria = fields.Str(required=False)
    estado = fields.Str(
        required=False,
        validate=validate.OneOf(ProductState.all_states())
    )


class ChangeProductStateSchema(Schema):
    """Schema para cambiar estado de producto"""
    estado = fields.Str(
        required=True,
        validate=validate.OneOf(ProductState.all_states())
    )
