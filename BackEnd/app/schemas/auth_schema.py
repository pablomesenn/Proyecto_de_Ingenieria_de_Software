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


class ForgotPasswordSchema(Schema):
    """Schema para solicitud de recuperación de contraseña"""
    email = fields.Email(required=True, error_messages={
        'required': 'El email es requerido',
        'invalid': 'Email inválido'
    })


class RegisterSchema(Schema):
    """Schema para registro de nuevo usuario"""
    email = fields.Email(required=True, error_messages={
        'required': 'El email es requerido',
        'invalid': 'Email inválido'
    })
    password = fields.Str(
        required=True,
        validate=validate.Length(min=10, error="La contraseña debe tener al menos 10 caracteres")
    )
    confirm_password = fields.Str(required=True)
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100, error="El nombre debe tener entre 1 y 100 caracteres")
    )
    phone = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(min=8, max=20, error="El teléfono debe tener entre 8 y 20 caracteres")
    )