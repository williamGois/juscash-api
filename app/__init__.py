import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api
from celery import Celery
from flasgger import Swagger
from config import config
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    """Factory para criar aplicação Flask"""
    
    app = Flask(__name__)
    
    # Configuração baseada no ambiente
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')
    
    # Carregar configuração específica para VPS
    if config_name == 'production':
        from config import ProductionConfig
        app.config.from_object(ProductionConfig)
    elif config_name == 'development':
        from config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    else:
        from config import Config
        app.config.from_object(Config)
    
    # Configurar logging para VPS
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s %(message)s',
            handlers=[
                logging.FileHandler('/app/logs/juscash.log'),
                logging.StreamHandler()
            ]
        )
    
    # Inicializar extensões
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['*']))
    migrate.init_app(app, db=None)  # DB será inicializado depois
    
    # Configurar Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/api/swagger.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/swaggerui",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }
    Swagger(app, config=swagger_config, template=app.config.get('SWAGGER', {}))
    
    # Registrar blueprints
    from app.presentation.routes import main_bp
    from app.presentation.cron_routes import cron_bp
    
    app.register_blueprint(main_bp, url_prefix='/api')
    app.register_blueprint(cron_bp, url_prefix='/cron')
    
    # Health check para VPS
    @app.route('/health')
    @app.route('/api/health')
    def health_check():
        return {
            'status': 'healthy',
            'server': 'VPS Hostinger',
            'location': 'São Paulo, Brasil',
            'environment': app.config.get('FLASK_ENV', 'production')
        }
    
    # Root endpoint
    @app.route('/')
    def root():
        return {
            'message': 'JusCash API - VPS Hostinger',
            'status': 'running',
            'docs': '/docs/',
            'health': '/health'
        }
    
    return app

def make_celery(app):
    """Factory para criar instância do Celery"""
    
    # Configuração do Celery para VPS
    celery = Celery(
        app.import_name,
        backend=app.config.get('CELERY_RESULT_BACKEND'),
        broker=app.config.get('CELERY_BROKER_URL'),
        include=['app.tasks.scraping_tasks', 'app.tasks.maintenance_tasks']
    )
    
    # Configurações otimizadas para VPS
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='America/Sao_Paulo',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutos
        task_soft_time_limit=25 * 60,  # 25 minutos
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
        result_expires=3600,  # 1 hora
        broker_connection_retry_on_startup=True,
        broker_connection_retry=True,
        broker_connection_max_retries=10,
        task_acks_late=True,
        worker_disable_rate_limits=True,
        task_reject_on_worker_lost=True
    )
    
    # Context task para executar em contexto Flask
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery 