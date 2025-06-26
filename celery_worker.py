import os
from celery import Celery
from app import create_app

def create_celery(app=None):
    if app is None:
        app = create_app()
    
    celery = Celery(
        app.import_name,
        backend=os.getenv('REDIS_URL', 'redis://redis:6379/0'),
        broker=os.getenv('REDIS_URL', 'redis://redis:6379/0')
    )
    
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='America/Sao_Paulo',
        enable_utc=True,
        result_expires=3600,
        worker_concurrency=1,
        worker_max_tasks_per_child=100,
        task_routes={
            'app.tasks.scraping_tasks.*': {'queue': 'scraping'},
            'app.tasks.maintenance_tasks.*': {'queue': 'maintenance'},
        },
        task_default_queue='default',
        beat_schedule={
            'scrape-dje-daily': {
                'task': 'app.tasks.scraping_tasks.scrape_dje_task',
                'schedule': 3600.0,
            },
            'cleanup-old-data': {
                'task': 'app.tasks.maintenance_tasks.cleanup_old_data',
                'schedule': 86400.0,
            },
        }
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = create_celery() 