"""
Servicio de envío de correos electrónicos usando yagmail
"""
import yagmail
import os
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para enviar correos electrónicos con yagmail"""
    
    @staticmethod
    def send_password_reset_email(user_email: str, user_name: str, temp_password: str) -> bool:
        """
        Envía correo con contraseña temporal usando yagmail
        
        Args:
            user_email: Email del usuario
            user_name: Nombre del usuario
            temp_password: Contraseña temporal generada
            
        Returns:
            True si se envió correctamente, False si hubo error
        """
        try:
            # Obtener credenciales de variables de entorno
            sender_email = os.getenv('SMTP_USERNAME', 'kermypisos@gmail.com')
            sender_password = os.getenv('SMTP_PASSWORD', '')
            
            if not sender_email or not sender_password:
                logger.error("❌ Credenciales SMTP no configuradas")
                logger.error("   Asegúrate de tener en .env:")
                logger.error("   SMTP_USERNAME=kermypisos@gmail.com")
                logger.error("   SMTP_PASSWORD=tu_contraseña_de_app_gmail")
                return False
            
            # Crear conexión SMTP
            yag = yagmail.SMTP(sender_email, sender_password)
            
            # Crear contenido del email en HTML
            subject = '🔐 Contraseña Temporal - Pisos Kermy'
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Recuperación de Contraseña - Pisos Kermy</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f9f9f9;
                        border-radius: 8px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        border-radius: 8px 8px 0 0;
                        text-align: center;
                    }}
                    .logo {{
                        font-size: 28px;
                        font-weight: bold;
                        margin-bottom: 10px;
                    }}
                    .content {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 0 0 8px 8px;
                    }}
                    .greeting {{
                        font-size: 16px;
                        margin-bottom: 20px;
                    }}
                    .password-box {{
                        background-color: #f0f0f0;
                        border-left: 4px solid #667eea;
                        padding: 20px;
                        margin: 30px 0;
                        font-family: monospace;
                        font-size: 18px;
                        letter-spacing: 2px;
                        text-align: center;
                        border-radius: 4px;
                    }}
                    .password {{
                        color: #667eea;
                        font-weight: bold;
                    }}
                    .instructions {{
                        background-color: #e8f4f8;
                        padding: 15px;
                        border-radius: 4px;
                        margin: 20px 0;
                        border-left: 4px solid #17a2b8;
                    }}
                    .instructions li {{
                        margin: 8px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #ddd;
                        font-size: 12px;
                        color: #666;
                    }}
                    .warning {{
                        color: #e74c3c;
                        font-weight: bold;
                        margin: 15px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🏗️ Pisos Kermy</div>
                        <div>Jacó S.A.</div>
                    </div>
                    <div class="content">
                        <div class="greeting">
                            ¡Hola {user_name}!
                        </div>
                        
                        <p>Hemos recibido una solicitud para recuperar tu contraseña. Aquí te proporcionamos una contraseña temporal para que puedas acceder a tu cuenta:</p>
                        
                        <div class="password-box">
                            Contraseña temporal:<br>
                            <span class="password">{temp_password}</span>
                        </div>
                        
                        <div class="instructions">
                            <strong>Pasos para recuperar tu acceso:</strong>
                            <ol>
                                <li>Ingresa a nuestro sitio web</li>
                                <li>Usa tu correo: <strong>{user_email}</strong></li>
                                <li>Usa la contraseña temporal mostrada arriba</li>
                                <li>Una vez dentro, dirígete a tu perfil</li>
                                <li>Cambia tu contraseña por una nueva de tu preferencia</li>
                            </ol>
                        </div>
                        
                        <div class="warning">
                            ⚠️ Por seguridad, esta contraseña temporal expirará en 24 horas. Si no la utilizas en ese tiempo, deberás solicitar una nueva.
                        </div>
                        
                        <p><strong>Requisitos para tu nueva contraseña:</strong></p>
                        <ul>
                            <li>Mínimo 10 caracteres</li>
                            <li>Al menos 1 caracter especial (!@#$%^&*)</li>
                        </ul>
                        
                        <div class="footer">
                            <p>Si no solicitaste recuperar tu contraseña, por favor ignora este correo y tu cuenta permanecerá segura.</p>
                            <p>© 2024-2026 Pisos Kermy Jacó S.A. Todos los derechos reservados.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Enviar email
            yag.send(
                to=user_email,
                subject=subject,
                contents=html_content
            )
            
            logger.info(f"✓ Email de recuperación enviado a {user_email}")
            return True
            
        except yagmail.YagauthError as e:
            logger.error(f"❌ Error de autenticación Gmail: {str(e)}")
            logger.error("   Verifica que SMTP_PASSWORD sea una 'contraseña de aplicación'")
            logger.error("   Genera una en: https://myaccount.google.com/apppasswords")
            return False
        except Exception as e:
            logger.error(f"❌ Error al enviar email a {user_email}: {str(e)}")
            return False

