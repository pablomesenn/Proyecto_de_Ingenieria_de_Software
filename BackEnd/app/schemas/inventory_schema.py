from marshmallow import Schema, fields, validate, validates, ValidationError
from app.constants.states import InventoryAdjustmentReason


class AdjustInventorySchema(Schema):
    """Schema para ajustar inventario (RF-06)"""
    variant_id = fields.Str(required=True, validate=validate.Length(min=1))
    delta = fields.Int(required=True)
    reason = fields.Str(
        required=True,
        validate=validate.OneOf(InventoryAdjustmentReason.all_reasons())
    )
    referencia = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=255)
    )

    @validates('variant_id')
    def validate_variant_id(self, value):
        """Valida que sea un ObjectId válido"""
        from bson import ObjectId
        try:
            ObjectId(value)
        except:
            raise ValidationError("variant_id debe ser un ObjectId válido")

    @validates('delta')
    def validate_delta(self, value):
        """Valida que el delta no sea cero"""
        if value == 0:
            raise ValidationError("El delta no puede ser cero")


class InventoryResponseSchema(Schema):
    """Schema para respuesta de inventario"""
    id = fields.Str(required=True)
    variant_id = fields.Str(required=True)
    stock_total = fields.Int(required=True)
    stock_retenido = fields.Int(required=True)
    disponibilidad = fields.Int(required=True)
    actualizado_en = fields.DateTime(required=True)


class InventoryMovementResponseSchema(Schema):
    """Schema para respuesta de movimiento de inventario (RF-09)"""
    id = fields.Str(required=True)
    variant_id = fields.Str(required=True)
    quantity = fields.Int(required=True)
    movement_type = fields.Str(required=True)
    reason = fields.Str(required=True)
    actor_id = fields.Str(allow_none=True)
    created_at = fields.DateTime(required=True)


class InventoryHistoryQuerySchema(Schema):
    """Schema para query de historial de inventario (RF-09)"""
    variant_id = fields.Str(required=False)
    skip = fields.Int(
        required=False,
        missing=0,
        validate=validate.Range(min=0)
    )
    limit = fields.Int(
        required=False,
        missing=50,
        validate=validate.Range(min=1, max=200)
    )

    @validates('variant_id')
    def validate_variant_id(self, value):
        """Valida que sea un ObjectId válido si se proporciona"""
        if value:
            from bson import ObjectId
            try:
                ObjectId(value)
            except:
                raise ValidationError("variant_id debe ser un ObjectId válido")


class CreateInventorySchema(Schema):
    """Schema para crear registro de inventario inicial"""
    variant_id = fields.Str(required=True, validate=validate.Length(min=1))
    stock_total = fields.Int(
        required=True,
        validate=validate.Range(min=0)
    )

    @validates('variant_id')
    def validate_variant_id(self, value):
        from bson import ObjectId
        try:
            ObjectId(value)
        except:
            raise ValidationError("variant_id debe ser un ObjectId válido")


class BulkAdjustInventorySchema(Schema):
    """Schema para ajustes masivos de inventario"""
    adjustments = fields.List(
        fields.Nested(AdjustInventorySchema),
        required=True,
        validate=validate.Length(min=1, max=100)
    )
