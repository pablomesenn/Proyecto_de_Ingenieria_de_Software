from marshmallow import Schema, fields, validate


class InventoryQuerySchema(Schema):
    variant_id = fields.Str(required=False, allow_none=True)
    skip = fields.Int(required=False, missing=0, validate=validate.Range(min=0))
    limit = fields.Int(required=False, missing=20, validate=validate.Range(min=1, max=100))


class CreateInventorySchema(Schema):
    variant_id = fields.Str(required=True)
    stock_total = fields.Int(required=True, validate=validate.Range(min=0))
    stock_retenido = fields.Int(required=False, missing=0, validate=validate.Range(min=0))


class UpdateInventoryStockSchema(Schema):
    stock_total = fields.Int(required=True, validate=validate.Range(min=0))


class AdjustInventorySchema(Schema):
    delta = fields.Int(required=True)  # Positivo = incremento, Negativo = decremento
    reason = fields.Str(required=True, validate=validate.Length(min=1, max=255))


class RetainStockSchema(Schema):
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    reason = fields.Str(required=False, allow_none=True)


class ReleaseStockSchema(Schema):
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    reason = fields.Str(required=False, allow_none=True)


class InventoryMovementQuerySchema(Schema):
    variant_id = fields.Str(required=False, allow_none=True)
    movement_type = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.OneOf(['retain', 'release', 'adjustment', 'initial'])
    )
    skip = fields.Int(required=False, missing=0, validate=validate.Range(min=0))
    limit = fields.Int(required=False, missing=50, validate=validate.Range(min=1, max=100))
