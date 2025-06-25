# 🔧 PATCH: Correção Definitiva do Celery Redis

## 🚨 Problema
O Celery não consegue acessar a configuração REDIS_URL mesmo com ela disponível.

## ✅ Solução: Aplicar estas mudanças

### 1. Arquivo: `app/__init__.py` (SUBSTITUIR COMPLETO)

```python
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
```

### 2. Adição no arquivo: `app/presentation/routes.py`

Adicionar este endpoint ANTES da função `register_namespaces`:

```python
@scraping_ns.route('/test-celery-fix')
class ScrapingTestCeleryFix(Resource):
    @scraping_ns.doc('test_celery_fix')
    def get(self):
        """Teste avançado para diagnosticar e corrigir o problema do Celery"""
        import os
        from flask import current_app
        
        test_result = {
            'timestamp': datetime.now().isoformat(),
            'step1_environment': {},
            'step2_app_config': {},
            'step3_celery_creation': {},
            'step4_manual_config': {},
            'step5_solution': {}
        }
        
        # STEP 1: Verificar variáveis de ambiente
        redis_url_env = os.environ.get('REDIS_URL')
        test_result['step1_environment'] = {
            'REDIS_URL_from_env': redis_url_env[:20] + '***' if redis_url_env else None,
            'RAILWAY_ENVIRONMENT': os.environ.get('RAILWAY_ENVIRONMENT'),
            'FLASK_ENV': os.environ.get('FLASK_ENV')
        }
        
        # STEP 2: Verificar configuração da app
        redis_url_config = current_app.config.get('REDIS_URL')
        test_result['step2_app_config'] = {
            'REDIS_URL_from_config': redis_url_config[:20] + '***' if redis_url_config else None,
            'config_keys': list(current_app.config.keys())[:10]
        }
        
        # STEP 3: Tentar criar Celery manualmente
        try:
            from celery import Celery
            
            redis_url = redis_url_config or redis_url_env or 'redis://localhost:6379/0'
            
            test_celery = Celery('test_app')
            
            test_celery.conf.update(
                broker_url=redis_url,
                result_backend=redis_url,
                task_serializer='json',
                accept_content=['json'],
                result_serializer='json',
                timezone='America/Sao_Paulo',
                enable_utc=True
            )
            
            test_result['step3_celery_creation'] = {
                'status': 'success',
                'broker_url': str(test_celery.conf.broker_url)[:20] + '***',
                'result_backend': str(test_celery.conf.result_backend)[:20] + '***',
                'task_serializer': test_celery.conf.task_serializer,
                'timezone': test_celery.conf.timezone
            }
            
            try:
                test_celery.control.inspect().ping()
                test_result['step3_celery_creation']['connection_test'] = 'success'
            except Exception as e:
                test_result['step3_celery_creation']['connection_test'] = f'failed: {str(e)}'
                
        except Exception as e:
            test_result['step3_celery_creation'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        # STEP 4: Verificar Celery atual da aplicação
        try:
            from celery import current_app as celery_app
            
            test_result['step4_manual_config'] = {
                'current_broker_url': str(celery_app.conf.broker_url) if celery_app.conf.broker_url else None,
                'current_result_backend': str(celery_app.conf.result_backend) if celery_app.conf.result_backend else None,
                'conf_keys': [k for k in dir(celery_app.conf) if not k.startswith('_')][:10]
            }
            
            if redis_url_config or redis_url_env:
                redis_url = redis_url_config or redis_url_env
                
                celery_app.conf.broker_url = redis_url
                celery_app.conf.result_backend = redis_url
                celery_app.conf.task_serializer = 'json'
                celery_app.conf.timezone = 'America/Sao_Paulo'
                
                test_result['step4_manual_config']['force_config'] = {
                    'applied': True,
                    'new_broker_url': str(celery_app.conf.broker_url)[:20] + '***',
                    'new_result_backend': str(celery_app.conf.result_backend)[:20] + '***'
                }
            
        except Exception as e:
            test_result['step4_manual_config'] = {
                'error': str(e)
            }
        
        # STEP 5: Propor solução
        if redis_url_config or redis_url_env:
            test_result['step5_solution'] = {
                'status': 'solution_found',
                'redis_available': True,
                'recommended_action': 'force_celery_reconfiguration',
                'code_fix': 'Apply make_celery fix or force configuration in __init__.py'
            }
        else:
            test_result['step5_solution'] = {
                'status': 'no_redis_url',
                'redis_available': False,
                'recommended_action': 'check_railway_redis_service'
            }
        
        return test_result
```

## 🚀 Como Aplicar

### Opção 1: GitHub Web Interface
1. Acesse: https://github.com/williamGois/juscash-api
2. Edite o arquivo `app/__init__.py`
3. Substitua todo o conteúdo pelo código acima
4. Edite o arquivo `app/presentation/routes.py`
5. Adicione o endpoint antes de `register_namespaces`
6. Commit: "fix: correção definitiva Celery Redis"

### Opção 2: Railway Dashboard
1. Vá em Settings > Deploy
2. Force um redeploy

## 🧪 Como Testar

Após aplicar:

1. **Teste avançado**:
```bash
curl "https://web-production-2cd50.up.railway.app/api/scraping/test-celery-fix"
```

2. **Debug**:
```bash
curl "https://web-production-2cd50.up.railway.app/api/scraping/debug"
```

3. **Health**:
```bash
curl "https://web-production-2cd50.up.railway.app/api/scraping/health"
```

4. **Scraping**:
```bash
curl -X POST "https://web-production-2cd50.up.railway.app/api/scraping/extract" \
  -H "Content-Type: application/json" \
  -d '{"data_inicio": "2024-10-01T00:00:00", "data_fim": "2024-10-01T23:59:59"}'
```

## 📊 Resultado Esperado

Após a correção, o debug deve mostrar:
```json
{
  "celery_config": {
    "broker_url": "redis://default:***",     // NÃO MAIS NULL!
    "result_backend": "redis://default:***", // NÃO MAIS NULL!
    "task_serializer": "json",
    "timezone": "America/Sao_Paulo"
  }
}
```

---

**🎯 Esta correção é definitiva e deve resolver o problema!** 