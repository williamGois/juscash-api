import os
import warnings
from app import create_app, make_celery

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
celery = make_celery(app)

# Configurações para Railway/Docker
celery.conf.update(
    broker_connection_retry_on_startup=True,
    worker_disable_rate_limits=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Suprimir warnings de segurança (normal em containers)
warnings.filterwarnings('ignore', category=UserWarning, module='celery.platforms')

if __name__ == '__main__':
    celery.start() 