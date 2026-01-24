"""
Schemas para Wishlist
Validación de datos para CU-006 y CU-007
"""
from marshmallow import Schema, fields, validate, validates, ValidationError


class AddWishlistItemSchema(Schema):
    """Schema para agregar ítem a wishlist (CU-006)"""
    producto_id = fields.Str(required=True, validate=validate.Length(min=1))
    variante_index = fields.Int(required=True, validate=validate.Range(min=0))
    cantidad = fields.Int(required=False, missing=1, validate=validate.Range(min=1))

    @validates('producto_id')
    def validate_producto_id(self, value):
        """Valida que sea un ObjectId válido"""
        from bson import ObjectId
        try:
            ObjectId(value)
        except:
            raise ValidationError("producto_id debe ser un ObjectId válido")


class UpdateWishlistItemSchema(Schema):
    """Schema para actualizar ítem de wishlist (CU-006)"""
    producto_id = fields.Str(required=True, validate=validate.Length(min=1))
    variante_index = fields.Int(required=True, validate=validate.Range(min=0))
    cantidad = fields.Int(required=True, validate=validate.Range(min=0))

    @validates('producto_id')
    def validate_producto_id(self, value):
        from bson import ObjectId
        try:
            ObjectId(value)
        except:
            raise ValidationError("producto_id debe ser un ObjectId válido")


class RemoveWishlistItemSchema(Schema):
    """Schema para eliminar ítem de wishlist (CU-006)"""
    producto_id = fields.Str(required=True, validate=validate.Length(min=1))
    variante_index = fields.Int(required=True, validate=validate.Range(min=0))

    @validates('producto_id')
    def validate_producto_id(self, value):
        from bson import ObjectId
        try:
            ObjectId(value)
        except:
            raise ValidationError("producto_id debe ser un ObjectId válido")


class WishlistItemQuantitySchema(Schema):
    """Schema para cantidades de ítems al convertir a reserva"""
    producto_id = fields.Str(required=True)
    variante_index = fields.Int(required=True, validate=validate.Range(min=0))
    cantidad = fields.Int(required=True, validate=validate.Range(min=1))


class ConvertToReservationSchema(Schema):
    """Schema para convertir wishlist a reserva (CU-007)"""
    item_quantities = fields.Dict(
        keys=fields.Str(),
        values=fields.Dict(),
        required=False,
        allow_none=True
    )
    notes = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))


class WishlistItemResponseSchema(Schema):
    """Schema para respuesta de ítem de wishlist"""
    producto_id = fields.Str(required=True)
    variante_index = fields.Int(required=True)
    cantidad = fields.Int(required=True)
    agregado_en = fields.DateTime(required=True)
    producto = fields.Dict(required=False)
    variante = fields.Dict(required=False)
    disponibilidad = fields.Dict(required=False)


class WishlistResponseSchema(Schema):
    """Schema para respuesta de wishlist completa"""
    id = fields.Str(required=True)
    usuario_id = fields.Str(required=True)
    items = fields.List(fields.Nested(WishlistItemResponseSchema))
    total_items = fields.Int(required=True)
    creado_en = fields.DateTime(required=True)
    actualizado_en = fields.DateTime(required=True)


class ValidateWishlistResponseSchema(Schema):
    """Schema para respuesta de validación de wishlist"""
    valid = fields.Bool(required=True)
    items = fields.List(fields.Dict())
    errors = fields.List(fields.Dict())
