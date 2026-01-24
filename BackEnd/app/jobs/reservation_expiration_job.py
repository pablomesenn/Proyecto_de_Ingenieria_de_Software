from apscheduler.schedulers.background import BackgroundScheduler
from app.services.reservation_service import ReservationService
from app.services.notification_service import NotificationService
from app.repositories.reservation_repository import ReservationRepository
from app.config.database import get_db
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class ReservationExpirationJob:
    """
    Job para expiracion automatica de reservas
    CU-011: Expiracion automatica de reservas
    Se ejecuta cada 5 minutos segun configuracion del README
    """
    
    def __init__(self):
        self.reservation_service = ReservationService()
        self.notification_service = NotificationService()
        self.reservation_repo = ReservationRepository()
        self.db = get_db()
        
    def run(self):
        """Ejecuta el proceso de expiracion"""
        logger.info("Iniciando proceso de expiracion de reservas")
        
        try:
            # Expirar reservas vencidas
            results = self.reservation_service.expire_reservations()
            
            logger.info(f"Expiracion completada: {results['processed']} procesadas, {results['errors']} errores")
            
            # Enviar notificaciones de reservas expiradas
            if results['processed'] > 0:
                self._send_expiration_notifications()
            
            return results
            
        except Exception as e:
            logger.error(f"Error en job de expiracion: {str(e)}")
            return {'processed': 0, 'errors': 1, 'error': str(e)}
    
    def _send_expiration_notifications(self):
        """Envia notificaciones de reservas expiradas"""
        from datetime import datetime, timedelta
        
        # Buscar reservas que expiraron en la ultima hora
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        expired_recently = self.db.reservations.find({
            'state': 'Expirada',
            'expired_at': {'$gte': one_hour_ago}
        })
        
        for reservation in expired_recently:
            try:
                # Obtener usuario
                user = self.db.users.find_one({'_id': ObjectId(reservation['user_id'])})
                
                if user:
                    # Convertir a objeto Reservation
                    from app.models.reservation import Reservation
                    res_obj = Reservation.from_dict(reservation)
                    
                    # Enviar notificacion
                    self.notification_service.send_reservation_expired(user, res_obj)
                    
            except Exception as e:
                logger.error(f"Error enviando notificacion de expiracion para reserva {reservation['_id']}: {str(e)}")


def setup_expiration_job(scheduler=None):
    """Configura el job de expiracion en el scheduler"""
    if scheduler is None:
        scheduler = BackgroundScheduler()
    
    job = ReservationExpirationJob()
    
    # Ejecutar cada 5 minutos segun README
    scheduler.add_job(
        func=job.run,
        trigger='interval',
        minutes=5,
        id='reservation_expiration_job',
        name='Expirar reservas vencidas',
        replace_existing=True
    )
    
    logger.info("Job de expiracion de reservas configurado (cada 5 minutos)")
    
    return scheduler