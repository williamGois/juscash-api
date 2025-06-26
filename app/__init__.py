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
        description='API para web scraping do Diário da Justiça Eletrônico v1 (DJE)',
        doc='/docs/',
        prefix='/api'
    )
    
    from app.presentation.routes import register_namespaces
    register_namespaces(api)
    
    return app

def make_celery(app):
    # CORREÇÃO ROBUSTA: Múltiplas tentativas para obter REDIS_URL
    redis_url = None
    
    # Tentativa 1: app.config
    if app.config.get('REDIS_URL'):
        redis_url = app.config['REDIS_URL']
        print(f"DEBUG: Redis URL obtida do app.config: {redis_url[:20]}***")
    
    # Tentativa 2: os.environ diretamente
    if not redis_url and os.environ.get('REDIS_URL'):
        redis_url = os.environ['REDIS_URL']
        print(f"DEBUG: Redis URL obtida do os.environ: {redis_url[:20]}***")
    
    # Tentativa 3: Verificar variáveis específicas do Railway
    if not redis_url:
        railway_vars = ['REDIS_URL', 'REDISURL', 'REDIS_PRIVATE_URL', 'REDIS_PUBLIC_URL']
        for var in railway_vars:
            if os.environ.get(var):
                redis_url = os.environ[var]
                print(f"DEBUG: Redis URL obtida de {var}: {redis_url[:20]}***")
                break
    
    # Fallback final
    if not redis_url:
        redis_url = 'redis://localhost:6379/0'
        print("DEBUG: Usando Redis URL fallback: redis://localhost:6379/0")
    
    print(f"DEBUG: Criando Celery com Redis URL: {redis_url[:30]}***")
    
    celery = Celery(
        app.import_name,
        backend=redis_url,
        broker=redis_url
    )
    
    # CONFIGURAÇÃO FORÇADA - Garantir que as URLs sejam definidas
    celery.conf.update({
        'broker_url': redis_url,
        'result_backend': redis_url,
        'task_serializer': 'json',
        'accept_content': ['json'],
        'result_serializer': 'json',
        'timezone': 'America/Sao_Paulo',
        'enable_utc': True,
        'broker_connection_retry_on_startup': True,
        'worker_disable_rate_limits': True,
        'task_acks_late': True,
        'worker_prefetch_multiplier': 1,
        'broker_transport_options': {
            'retry_on_timeout': True,
            'socket_connect_timeout': 30,
            'socket_timeout': 30,
        },
        'result_backend_transport_options': {
            'retry_on_timeout': True,
            'socket_connect_timeout': 30,
            'socket_timeout': 30,
        }
    })
    
    # VERIFICAÇÃO FINAL - Log das configurações
    print(f"DEBUG: Celery configurado com:")
    print(f"  - broker_url: {str(celery.conf.broker_url)[:30]}***")
    print(f"  - result_backend: {str(celery.conf.result_backend)[:30]}***")
    print(f"  - task_serializer: {celery.conf.task_serializer}")
    print(f"  - timezone: {celery.conf.timezone}")
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery 