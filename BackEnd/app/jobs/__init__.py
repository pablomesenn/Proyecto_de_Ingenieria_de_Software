"""
Inicializacion de jobs programados
"""
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logger = logging.getLogger(__name__)


def init_scheduler():
    """
    Inicializa el scheduler con todos los jobs configurados
    
    Jobs configurados:
    - reservation_expiration_job: Expira reservas vencidas (cada 5 min)
    - notification_job: Notifica reservas por vencer (diario 9 AM)
    """
    logger.info("Inicializando scheduler de jobs...")
    
    scheduler = BackgroundScheduler()
    
    try:
        # Importar y configurar job de expiracion de reservas
        from app.jobs.reservation_expiration_job import setup_expiration_job
        setup_expiration_job(scheduler)
        logger.info("Job de expiracion de reservas configurado")
        
        # Importar y configurar job de notificaciones
        from app.jobs.notification_job import setup_notification_job
        setup_notification_job(scheduler)
        logger.info("Job de notificaciones configurado")
        
        # Iniciar scheduler
        scheduler.start()
        logger.info("Scheduler iniciado exitosamente")
        
        return scheduler
        
    except Exception as e:
        logger.error(f"Error inicializando scheduler: {str(e)}")
        raise


# Export para facilitar imports
__all__ = ['init_scheduler']