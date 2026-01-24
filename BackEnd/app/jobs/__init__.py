from apscheduler.schedulers.background import BackgroundScheduler
from app.jobs.reservation_expiration_job import setup_expiration_job
from app.jobs.notification_job import setup_notification_job, setup_notification_queue_processor
import logging
import atexit

logger = logging.getLogger(__name__)


def init_scheduler():
    """
    Inicializa y configura el scheduler de jobs
    Retorna el scheduler configurado
    """
    scheduler = BackgroundScheduler()
    
    # Configurar job de expiracion de reservas (cada 5 minutos)
    setup_expiration_job(scheduler)
    
    # Configurar job de notificaciones (diario a las 9:00 AM)
    setup_notification_job(scheduler)
    
    # Configurar procesador de cola de notificaciones (cada hora)
    setup_notification_queue_processor(scheduler)
    
    # Iniciar scheduler
    scheduler.start()
    
    # Asegurar que el scheduler se detenga al cerrar la aplicacion
    atexit.register(lambda: scheduler.shutdown())
    
    logger.info("Scheduler de jobs iniciado exitosamente")
    
    return scheduler