from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api
from celery import Celery
from config import config

db = SQLAlchemy()
migrate = Migrate()
celery = Celery(__name__)

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Importar modelos para que o Flask-Migrate os reconheça
    from app.infrastructure.database.models import PublicacaoModel
    
    celery.conf.update(
        broker_url=app.config['REDIS_URL'],
        result_backend=app.config['REDIS_URL'],
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='America/Sao_Paulo',
        enable_utc=True,
        beat_schedule={
            'raspagem-diaria': {
                'task': 'app.tasks.scraping_tasks.extract_daily_publicacoes',
                'schedule': app.config.get('DAILY_SCRAPING_SCHEDULE', 3600.0),  # 1 hora padrão
            },
            'raspagem-periodo-completo': {
                'task': 'app.tasks.scraping_tasks.extract_full_period_publicacoes',
                'schedule': app.config.get('WEEKLY_SCRAPING_SCHEDULE', 604800.0),  # 1 semana padrão
            },
            'limpeza-logs': {
                'task': 'app.tasks.maintenance_tasks.cleanup_old_logs',
                'schedule': app.config.get('CLEANUP_SCHEDULE', 86400.0),  # 1 dia padrão
            },
        },
        beat_scheduler='django_celery_beat.schedulers:DatabaseScheduler' if app.config.get('USE_DB_SCHEDULER', False) else None,
    )
    
    api = Api(
        app,
        version='1.0',
        title='JusCash API',
        description='API para web scraping do Diário da Justiça Eletrônico (DJE)',
        doc='/docs/',
        prefix='/api'
    )
    
    from app.presentation.routes import register_namespaces
    register_namespaces(api)
    
    return app

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['REDIS_URL'],
        broker=app.config['REDIS_URL']
    )
    celery.conf.update(app.config)
    return celery 