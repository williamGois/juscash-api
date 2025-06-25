import os
import warnings
from app import create_app, make_celery
from celery.schedules import crontab

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
celery = make_celery(app)

from app.tasks.scraping_tasks import (
    extract_publicacoes_task,
    extract_daily_publicacoes,
    extract_full_period_publicacoes,
    extract_custom_period_publicacoes
)

from app.tasks.maintenance_tasks import (
    cleanup_old_logs,
    generate_daily_stats,
    health_check
)

celery.task(extract_publicacoes_task, bind=True, name='app.tasks.scraping_tasks.extract_publicacoes_task')
celery.task(extract_daily_publicacoes, name='app.tasks.scraping_tasks.extract_daily_publicacoes')
celery.task(extract_full_period_publicacoes, name='app.tasks.scraping_tasks.extract_full_period_publicacoes')
celery.task(extract_custom_period_publicacoes, name='app.tasks.scraping_tasks.extract_custom_period_publicacoes')

celery.task(cleanup_old_logs, name='app.tasks.maintenance_tasks.cleanup_old_logs')
celery.task(generate_daily_stats, name='app.tasks.maintenance_tasks.generate_daily_stats')
celery.task(health_check, name='app.tasks.maintenance_tasks.health_check')

celery.conf.update(
    beat_schedule={
        'raspagem_diaria': {
            'task': 'app.tasks.scraping_tasks.extract_daily_publicacoes',
            'schedule': crontab(minute=0),
        },
        'raspagem_completa': {
            'task': 'app.tasks.scraping_tasks.extract_full_period_publicacoes',
            'schedule': crontab(hour=3, minute=0, day_of_week='sunday'),
        },
        'limpeza_logs': {
            'task': 'app.tasks.maintenance_tasks.cleanup_old_logs',
            'schedule': crontab(hour=4, minute=0),
        },
    }
)

# Suprimir warnings de segurança (normal em containers)
warnings.filterwarnings('ignore', category=UserWarning, module='celery.platforms')

if __name__ == '__main__':
    celery.start() 