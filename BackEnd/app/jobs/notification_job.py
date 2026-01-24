from apscheduler.schedulers.background import BackgroundScheduler
from app.services.reservation_service import ReservationService
from app.services.notification_service import NotificationService
from app.repositories.reservation_repository import ReservationRepository
from app.config.database import get_db
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class NotificationJob:
    """
    Job para notificaciones de reservas por vencer
    CU-012: Notificacion "por vencer" (mismo dia)
    Se ejecuta diariamente a las 9:00 AM segun README
    """
    
    def __init__(self):
        self.reservation_service = ReservationService()
        self.notification_service = NotificationService()
        self.reservation_repo = ReservationRepository()
        self.db = get_db()
        
    def run(self):
        """Ejecuta el proceso de notificaciones"""
        logger.info("Iniciando proceso de notificaciones de reservas por vencer")
        
        try:
            # Obtener reservas que vencen hoy
            expiring_reservations = self.reservation_repo.find_expiring_today()
            
            results = {
                'notified': 0,
                'skipped': 0,
                'errors': 0
            }
            
            for reservation in expiring_reservations:
                try:
                    # Obtener usuario
                    user = self.db.users.find_one({'_id': ObjectId(reservation.user_id)})
                    
                    if not user:
                        logger.warning(f"Usuario no encontrado para reserva {reservation._id}")
                        results['errors'] += 1
                        continue
                    
                    # Verificar si ya se notifico para evitar duplicados
                    if self.notification_service.notification_repo.check_if_already_notified(
                        reservation._id,
                        'reservation_expiring_soon'
                    ):
                        logger.info(f"Reserva {reservation._id} ya fue notificada")
                        results['skipped'] += 1
                        continue
                    
                    # Enviar notificacion
                    self.notification_service.send_reservation_expiring_soon(user, reservation)
                    results['notified'] += 1
                    
                    logger.info(f"Notificacion enviada para reserva {reservation._id}")
                    
                except Exception as e:
                    logger.error(f"Error notificando reserva {reservation._id}: {str(e)}")
                    results['errors'] += 1
            
            logger.info(f"Notificaciones completadas: {results['notified']} enviadas, {results['skipped']} omitidas, {results['errors']} errores")
            
            # Procesar cola de notificaciones pendientes
            self._process_notification_queue()
            
            return results
            
        except Exception as e:
            logger.error(f"Error en job de notificaciones: {str(e)}")
            return {'notified': 0, 'skipped': 0, 'errors': 1, 'error': str(e)}
    
    def _process_notification_queue(self):
        """Procesa la cola de notificaciones pendientes"""
        try:
            results = self.notification_service.send_queued_notifications()
            logger.info(f"Cola de notificaciones procesada: {results['sent']} enviadas, {results['failed']} fallidas de {results['total']} total")
        except Exception as e:
            logger.error(f"Error procesando cola de notificaciones: {str(e)}")


def setup_notification_job(scheduler=None):
    """Configura el job de notificaciones en el scheduler"""
    if scheduler is None:
        scheduler = BackgroundScheduler()
    
    job = NotificationJob()
    
    # Ejecutar diariamente a las 9:00 AM segun README
    scheduler.add_job(
        func=job.run,
        trigger='cron',
        hour=9,
        minute=0,
        id='notification_job',
        name='Notificar reservas por vencer',
        replace_existing=True
    )
    
    logger.info("Job de notificaciones configurado (diario a las 9:00 AM)")
    
    return scheduler


def setup_notification_queue_processor(scheduler=None):
    """Configura un procesador adicional para la cola cada hora"""
    if scheduler is None:
        scheduler = BackgroundScheduler()
    
    job = NotificationJob()
    
    # Procesar cola cada hora
    scheduler.add_job(
        func=job._process_notification_queue,
        trigger='interval',
        hours=1,
        id='notification_queue_processor',
        name='Procesar cola de notificaciones',
        replace_existing=True
    )
    
    logger.info("Procesador de cola de notificaciones configurado (cada hora)")
    
    return scheduler