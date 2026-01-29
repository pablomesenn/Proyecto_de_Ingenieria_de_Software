from apscheduler.schedulers.background import BackgroundScheduler
from app.services.reservation_service import ReservationService
from app.services.notification_service import NotificationService
from app.services.user_service import UserService
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
        self.user_service = UserService()
        self.reservation_repo = ReservationRepository()
        self.db = get_db()
        
    def run(self):
        """Ejecuta el proceso de notificaciones"""
        logger.info("=== INICIANDO JOB DE NOTIFICACIONES (RESERVAS POR VENCER) ===")
        
        try:
            # Obtener reservas que vencen hoy
            expiring_reservations = self.reservation_repo.find_expiring_today()
            
            results = {
                'notified': 0,
                'skipped': 0,
                'errors': 0
            }
            
            logger.info(f"Reservas por vencer encontradas: {len(expiring_reservations)}")
            
            for reservation in expiring_reservations:
                try:
                    # Obtener usuario usando UserService (devuelve dict)
                    user = self.user_service.get_user_by_id(str(reservation.user_id))
                    
                    if not user:
                        logger.warning(f"Usuario no encontrado para reserva {reservation._id}")
                        results['errors'] += 1
                        continue
                    
                    # Enviar notificacion (ahora funciona con dict)
                    self.notification_service.send_reservation_expiring_soon(user, reservation)
                    results['notified'] += 1
                    
                    logger.info(f"Notificacion enviada para reserva {reservation._id}")
                    
                except Exception as e:
                    logger.error(f"Error notificando reserva {reservation._id}: {str(e)}")
                    results['errors'] += 1
            
            logger.info(f"Notificaciones completadas: {results['notified']} enviadas, {results['skipped']} omitidas, {results['errors']} errores")
            
            return results
            
        except Exception as e:
            logger.error(f"Error en job de notificaciones: {str(e)}")
            return {'notified': 0, 'skipped': 0, 'errors': 1, 'error': str(e)}


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