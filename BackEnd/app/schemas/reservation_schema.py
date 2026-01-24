from marshmallow import Schema, fields, validate, validates, ValidationError
from app.constants.states import ReservationState


class ReservationItemSchema(Schema):
    """Schema para items de una reserva"""
    variant_id = fields.Str(required=True)
    product_name = fields.Str(required=False)
    variant_size = fields.Str(required=False)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    price = fields.Float(required=False)

    @validates('variant_id')
    def validate_variant_id(self, value):
        """Valida que sea un ObjectId válido"""
        from bson import ObjectId
        try:
            ObjectId(value)
        except:
            raise ValidationError("variant_id debe ser un ObjectId válido")


class CreateReservationSchema(Schema):
    """Schema para crear una reserva"""
    items = fields.List(
        fields.Nested(ReservationItemSchema),
        required=True,
        validate=validate.Length(min=1)
    )
    notes = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=500)
    )


class UpdateReservationStateSchema(Schema):
    """Schema para actualizar el estado de una reserva"""
    admin_notes = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=500)
    )

class CancelReservationSchema(Schema):
    """Schema para cancelar reserva (CU-009)"""
    reason = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=200)
    )


class ReservationFilterSchema(Schema):
    """Schema para filtros de busqueda de reservas"""
    state = fields.Str(
        required=False,
        validate=validate.OneOf(ReservationState.all_states())
    )
    user_id = fields.Str(required=False)
    skip = fields.Int(required=False, missing=0, validate=validate.Range(min=0))
    limit = fields.Int(required=False, missing=20, validate=validate.Range(min=1, max=100))

    @validates('user_id')
    def validate_user_id(self, value):
        """Valida que sea un ObjectId válido si se proporciona"""
        if value:
            from bson import ObjectId
            try:
                ObjectId(value)
            except:
                raise ValidationError("user_id debe ser un ObjectId válido")


class ReservationResponseSchema(Schema):
    """Schema para respuesta de reserva"""
    id = fields.Str()
    user_id = fields.Str()
    items = fields.List(fields.Nested(ReservationItemSchema))
    state = fields.Str()
    created_at = fields.DateTime()
    expires_at = fields.DateTime()
    approved_at = fields.DateTime(allow_none=True)
    cancelled_at = fields.DateTime(allow_none=True)
    rejected_at = fields.DateTime(allow_none=True)
    expired_at = fields.DateTime(allow_none=True)
    notes = fields.Str(allow_none=True)
    admin_notes = fields.Str(allow_none=True)

class ReservationListResponseSchema(Schema):
    """Schema para respuesta de lista de reservas"""
    reservations = fields.List(fields.Nested(ReservationResponseSchema))
    count = fields.Int(required=True)
    total = fields.Int(required=False)
    page = fields.Int(required=False)
    per_page = fields.Int(required=False)
