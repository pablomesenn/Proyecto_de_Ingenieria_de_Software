from marshmallow import Schema, fields, validate


class UpdateProfileSchema(Schema):
    """Schema para actualizar perfil de usuario"""
    name = fields.Str(required=False, validate=validate.Length(min=1, max=100))
    phone = fields.Str(required=False, allow_none=True, validate=validate.Length(min=8, max=20))
    address = fields.Str(required=False, allow_none=True)
    preferences = fields.Dict(required=False, allow_none=True)
    email = fields.Email(required=False)


class CreateUserSchema(Schema):
    """Schema para crear usuario (ADMIN)"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=10))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    phone = fields.Str(required=False, allow_none=True)
    role = fields.Str(
        required=False,
        missing='CLIENT',
        validate=validate.OneOf(['ADMIN', 'CLIENT'])
    )


class UpdateUserSchema(Schema):
    """Schema para actualizar usuario (ADMIN)"""
    email = fields.Email(required=False)
    password = fields.Str(required=False, validate=validate.Length(min=10))
    name = fields.Str(required=False, validate=validate.Length(min=1, max=100))
    phone = fields.Str(required=False, allow_none=True)
    role = fields.Str(
        required=False,
        validate=validate.OneOf(['ADMIN', 'CLIENT'])
    )
    state = fields.Str(
        required=False,
        validate=validate.OneOf(['activo', 'inactivo'])
    )


class UserResponseSchema(Schema):
    """Schema para respuesta de usuario"""
    id = fields.Str()
    email = fields.Email()
    name = fields.Str()
    phone = fields.Str(allow_none=True)
    role = fields.Str()
    state = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_login = fields.DateTime(allow_none=True)


class UserListQuerySchema(Schema):
    """Schema para parametros de busqueda de usuarios"""
    skip = fields.Int(required=False, missing=0, validate=validate.Range(min=0))
    limit = fields.Int(required=False, missing=20, validate=validate.Range(min=1, max=100))