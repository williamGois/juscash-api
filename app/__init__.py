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