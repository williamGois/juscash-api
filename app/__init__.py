from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api
from celery import Celery
from config import config
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Importar modelos para que o Flask-Migrate os reconheça
    from app.infrastructure.database.models import PublicacaoModel
    
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
    # Garantir que a REDIS_URL seja corretamente configurada
    redis_url = app.config.get('REDIS_URL') or os.environ.get('REDIS_URL')
    
    if not redis_url:
        # Fallback para localhost se não houver Redis configurado
        redis_url = 'redis://localhost:6379/0'
    
    celery = Celery(
        app.import_name,
        backend=redis_url,
        broker=redis_url
    )
    
    # Configuração robusta para Railway
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='America/Sao_Paulo',
        enable_utc=True,
        broker_connection_retry_on_startup=True,
        worker_disable_rate_limits=True,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        # Configurações específicas para Railway
        broker_url=redis_url,
        result_backend=redis_url,
        broker_transport_options={
            'retry_on_timeout': True,
            'socket_connect_timeout': 30,
            'socket_timeout': 30,
        },
        result_backend_transport_options={
            'retry_on_timeout': True,
            'socket_connect_timeout': 30,
            'socket_timeout': 30,
        }
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery 