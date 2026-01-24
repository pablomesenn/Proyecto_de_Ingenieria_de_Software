from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    """Schema para inicio de sesion"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))


class RefreshTokenSchema(Schema):
    """Schema para refrescar token (no requiere campos adicionales)"""
    pass


class LoginResponseSchema(Schema):
    """Schema para respuesta de login"""
    access_token = fields.Str()
    refresh_token = fields.Str()
    user = fields.Dict()


class RefreshResponseSchema(Schema):
    """Schema para respuesta de refresh"""
    access_token = fields.Str()
    refresh_token = fields.Str()


class LogoutResponseSchema(Schema):
    """Schema para respuesta de logout"""
    message = fields.Str()