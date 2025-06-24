import os
from app import create_app, make_celery

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
celery = make_celery(app)

if __name__ == '__main__':
    celery.start() 