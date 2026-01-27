from marshmallow import Schema, fields, validate

class CreateCatalogItemSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))

class UpdateCatalogItemSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
