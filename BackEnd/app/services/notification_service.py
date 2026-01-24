import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config.config import Config
from app.repositories.notification_repository import NotificationRepository
from app.models.notification import EmailNotification
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Servicio para envio de notificaciones por email"""
    
    def __init__(self):
        self.notification_repo = NotificationRepository()
        self.smtp_username = Config.SMTP_USERNAME
        self.smtp_password = Config.SMTP_PASSWORD
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        
    def send_email(self, to_email, subject, body, html=False):
        """Envia un email utilizando SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            return True
        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {str(e)}")
            return False
    
    def queue_notification(self, user_id, email_to, notification_type, subject, body, related_entity_id=None):
        """Encola una notificacion para envio posterior"""
        
        # Evitar duplicados para ciertos tipos
        if related_entity_id:
            if self.notification_repo.check_if_already_notified(related_entity_id, notification_type):
                logger.info(f"Notificacion {notification_type} ya enviada para {related_entity_id}")
                return None
        
        notification = EmailNotification(
            user_id=user_id,
            email_to=email_to,
            notification_type=notification_type,
            subject=subject,
            body=body,
            related_entity_id=related_entity_id
        )
        
        return self.notification_repo.create(notification)
    
    def send_queued_notifications(self, max_retries=3):
        """Procesa notificaciones pendientes"""
        notifications = self.notification_repo.find_pending()
        
        results = {
            'sent': 0,
            'failed': 0,
            'total': len(notifications)
        }
        
        for notification in notifications:
            if notification.retry_count >= max_retries:
                self.notification_repo.mark_as_failed(
                    notification._id,
                    f"Maximo de reintentos alcanzado ({max_retries})"
                )
                results['failed'] += 1
                continue
            
            success = self.send_email(
                notification.email_to,
                notification.subject,
                notification.body
            )
            
            if success:
                self.notification_repo.mark_as_sent(notification._id)
                results['sent'] += 1
            else:
                self.notification_repo.increment_retry_count(notification._id)
                results['failed'] += 1
                
        return results
    
    def send_reservation_created(self, user, reservation):
        """Envia notificacion de reserva creada"""
        subject = "Reserva creada - Pisos Kermy"
        body = f"""
Hola {user.get('name', 'Cliente')},

Tu reserva ha sido creada exitosamente.

Numero de reserva: {str(reservation._id)}
Estado: {reservation.state}
Fecha de vencimiento: {reservation.expires_at.strftime('%Y-%m-%d %H:%M')}

Por favor, coordina con nosotros antes de que venza tu reserva para completar el proceso.

Saludos,
Equipo Pisos Kermy
        """
        
        return self.queue_notification(
            user_id=user['_id'],
            email_to=user['email'],
            notification_type=EmailNotification.TYPE_RESERVATION_CREATED,
            subject=subject,
            body=body,
            related_entity_id=reservation._id
        )
    
    def send_reservation_approved(self, user, reservation):
        """Envia notificacion de reserva aprobada"""
        subject = "Reserva aprobada - Pisos Kermy"
        body = f"""
Hola {user.get('name', 'Cliente')},

Tu reserva ha sido APROBADA.

Numero de reserva: {str(reservation._id)}
Estado: {reservation.state}

Puedes pasar a retirar tus productos en el horario de atencion.

Saludos,
Equipo Pisos Kermy
        """
        
        return self.queue_notification(
            user_id=user['_id'],
            email_to=user['email'],
            notification_type=EmailNotification.TYPE_RESERVATION_APPROVED,
            subject=subject,
            body=body,
            related_entity_id=reservation._id
        )
    
    def send_reservation_rejected(self, user, reservation):
        """Envia notificacion de reserva rechazada"""
        subject = "Reserva rechazada - Pisos Kermy"
        body = f"""
Hola {user.get('name', 'Cliente')},

Lamentablemente tu reserva ha sido RECHAZADA.

Numero de reserva: {str(reservation._id)}
Razon: {reservation.admin_notes or 'No especificada'}

El inventario reservado ha sido liberado.

Saludos,
Equipo Pisos Kermy
        """
        
        return self.queue_notification(
            user_id=user['_id'],
            email_to=user['email'],
            notification_type=EmailNotification.TYPE_RESERVATION_REJECTED,
            subject=subject,
            body=body,
            related_entity_id=reservation._id
        )
    
    def send_reservation_cancelled(self, user, reservation):
        """Envia notificacion de reserva cancelada"""
        subject = "Reserva cancelada - Pisos Kermy"
        body = f"""
Hola {user.get('name', 'Cliente')},

Tu reserva ha sido CANCELADA.

Numero de reserva: {str(reservation._id)}

El inventario reservado ha sido liberado.

Saludos,
Equipo Pisos Kermy
        """
        
        return self.queue_notification(
            user_id=user['_id'],
            email_to=user['email'],
            notification_type=EmailNotification.TYPE_RESERVATION_CANCELLED,
            subject=subject,
            body=body,
            related_entity_id=reservation._id
        )
    
    def send_reservation_expired(self, user, reservation):
        """Envia notificacion de reserva expirada"""
        subject = "Reserva expirada - Pisos Kermy"
        body = f"""
Hola {user.get('name', 'Cliente')},

Tu reserva ha EXPIRADO por vencimiento del tiempo de retencion (24 horas).

Numero de reserva: {str(reservation._id)}

El inventario reservado ha sido liberado. Si aun estas interesado, puedes crear una nueva reserva.

Saludos,
Equipo Pisos Kermy
        """
        
        return self.queue_notification(
            user_id=user['_id'],
            email_to=user['email'],
            notification_type=EmailNotification.TYPE_RESERVATION_EXPIRED,
            subject=subject,
            body=body,
            related_entity_id=reservation._id
        )
    
    def send_reservation_expiring_soon(self, user, reservation):
        """Envia notificacion de reserva por vencer"""
        subject = "Tu reserva vence hoy - Pisos Kermy"
        body = f"""
Hola {user.get('name', 'Cliente')},

Este es un recordatorio de que tu reserva VENCE HOY.

Numero de reserva: {str(reservation._id)}
Fecha de vencimiento: {reservation.expires_at.strftime('%Y-%m-%d %H:%M')}

Por favor, coordina con nosotros lo antes posible para completar el proceso antes de que expire.

Saludos,
Equipo Pisos Kermy
        """
        
        return self.queue_notification(
            user_id=user['_id'],
            email_to=user['email'],
            notification_type=EmailNotification.TYPE_RESERVATION_EXPIRING_SOON,
            subject=subject,
            body=body,
            related_entity_id=reservation._id
        )