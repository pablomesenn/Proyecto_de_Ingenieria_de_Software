from marshmallow import Schema, fields, validate, pre_load


class ProductSearchSchema(Schema):
    search_text = fields.Str(required=False, allow_none=True)
    categoria = fields.Str(required=False, allow_none=True)
    tags = fields.List(fields.Str(), required=False, allow_none=True)
    disponibilidad = fields.Bool(required=False, missing=True)
    skip = fields.Int(required=False, missing=0, validate=validate.Range(min=0))
    limit = fields.Int(required=False, missing=20, validate=validate.Range(min=1, max=100))

    @pre_load
    def process_tags(self, data, **kwargs):
        """Convert tags from ImmutableMultiDict to list"""
        # Create a mutable copy since request.args is immutable
        if hasattr(data, 'to_dict'):
            # It's an ImmutableMultiDict from Flask
            mutable_data = {}
            for key in data.keys():
                values = data.getlist(key)
                # If it's tags and has multiple values, keep as list
                if key == 'tags' and len(values) > 0:
                    mutable_data[key] = values
                else:
                    # For other fields, take the first value
                    mutable_data[key] = values[0] if values else None
            return mutable_data
        return data


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
