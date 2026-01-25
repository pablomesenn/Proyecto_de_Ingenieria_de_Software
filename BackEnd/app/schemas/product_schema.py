from marshmallow import Schema, fields, validate


class ProductSearchSchema(Schema):
    search_text = fields.Str(required=False, allow_none=True)
    categoria = fields.Str(required=False, allow_none=True)
    tags = fields.List(fields.Str(), required=False, allow_none=True)
    disponibilidad = fields.Bool(required=False, missing=True)
    skip = fields.Int(required=False, missing=0, validate=validate.Range(min=0))
    limit = fields.Int(required=False, missing=20, validate=validate.Range(min=1, max=100))


class CreateProductSchema(Schema):
    nombre = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    imagen_url = fields.Str(required=True)
    categoria = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    tags = fields.List(fields.Str(), required=False, missing=[])
    estado = fields.Str(
        required=False,
        missing='activo',
        validate=validate.OneOf(['activo', 'inactivo', 'agotado'])
    )
    descripcion_embalaje = fields.Str(required=False, allow_none=True)


class UpdateProductSchema(Schema):
    nombre = fields.Str(required=False, validate=validate.Length(min=1, max=255))
    imagen_url = fields.Str(required=False)
    categoria = fields.Str(required=False, validate=validate.Length(min=1, max=100))
    tags = fields.List(fields.Str(), required=False)
    estado = fields.Str(
        required=False,
        validate=validate.OneOf(['activo', 'inactivo', 'agotado'])
    )
    descripcion_embalaje = fields.Str(required=False, allow_none=True)


class UpdateProductStateSchema(Schema):
    estado = fields.Str(
        required=True,
        validate=validate.OneOf(['activo', 'inactivo', 'agotado'])
    )


class CreateVariantSchema(Schema):
    product_id = fields.Str(required=True)
    tamano_pieza = fields.Str(required=True)
    unidad = fields.Str(required=False, missing='m²')
    precio = fields.Float(required=False, allow_none=True, validate=validate.Range(min=0))


class UpdateVariantSchema(Schema):
    tamano_pieza = fields.Str(required=False)
    unidad = fields.Str(required=False)
    precio = fields.Float(required=False, allow_none=True, validate=validate.Range(min=0))
