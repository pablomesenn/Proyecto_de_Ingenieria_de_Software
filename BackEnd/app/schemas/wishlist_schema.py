from marshmallow import Schema, fields, validate


class AddWishlistItemSchema(Schema):
    variant_id = fields.Str(required=True)
    quantity = fields.Int(required=False, missing=1, validate=validate.Range(min=1))


class UpdateWishlistItemSchema(Schema):
    quantity = fields.Int(required=True, validate=validate.Range(min=0))


class ConvertWishlistItemSchema(Schema):
    item_id = fields.Str(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))


class ConvertWishlistToReservationSchema(Schema):
    items = fields.List(
        fields.Nested(ConvertWishlistItemSchema),
        required=True,
        validate=validate.Length(min=1)
    )
    notes = fields.Str(required=False, allow_none=True)
