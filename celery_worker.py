import os
import warnings
from app import create_app, make_celery
from celery.schedules import crontab

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
celery = make_celery(app)

# Configurações para Railway/Docker
celery.conf.update(
    broker_connection_retry_on_startup=True,
    worker_disable_rate_limits=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_backend=app.config['REDIS_URL'],
    beat_schedule={
        'raspagem_diaria': {
            'task': 'app.tasks.scraping_tasks.extract_daily_publicacoes',
            'schedule': crontab(minute=0),  # A cada hora
        },
        'raspagem_completa': {
            'task': 'app.tasks.scraping_tasks.extract_full_period_publicacoes',
            'schedule': crontab(hour=3, minute=0, day_of_week='sunday'),  # Domingo às 3h
        },
        'limpeza_logs': {
            'task': 'app.tasks.maintenance_tasks.cleanup_old_logs',
            'schedule': crontab(hour=4, minute=0),  # Todo dia às 4h
        },
    }
)

# Suprimir warnings de segurança (normal em containers)
warnings.filterwarnings('ignore', category=UserWarning, module='celery.platforms')

if __name__ == '__main__':
    celery.start() 