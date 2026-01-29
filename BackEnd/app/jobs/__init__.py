"""
Inicializacion del modulo de jobs programados
"""
from app.jobs.notification_job import setup_notification_job
from app.jobs.reservation_expiration_job import setup_expiration_job
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logger = logging.getLogger(__name__)


def init_scheduler():
    """
    Inicializa el scheduler con todos los jobs
    """
    scheduler = BackgroundScheduler()
    
    # Configurar job de expiracion de reservas (cada 5 minutos)
    setup_expiration_job(scheduler)
    
    # Configurar job de notificaciones diarias (9:00 AM)
    setup_notification_job(scheduler)
    
    # Iniciar el scheduler
    scheduler.start()
    
    logger.info("Scheduler inicializado con todos los jobs")
    
    return scheduler