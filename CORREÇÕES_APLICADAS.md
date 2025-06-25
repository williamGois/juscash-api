# Correções Aplicadas - JusCash API

## 🚨 Problemas Identificados

### 1. Erro de Backend do Celery
**Erro**: `AttributeError: 'DisabledBackend' object has no attribute '_get_task_meta_for'`

**Causa**: Configuração duplicada e conflitante do Celery no `app/__init__.py`

**Correção**: 
- ✅ Removida instância global `celery = Celery(__name__)`
- ✅ Mantida apenas função `make_celery(app)` com configuração completa
- ✅ Implementado `ContextTask` para execução em contexto Flask
- ✅ Corrigido `celery_worker.py` para usar `make_celery` corretamente

### 2. Erro do Selenium no Docker
**Erro**: Stacktrace do Chrome indicando falha na inicialização do driver

**Causa**: Dependências faltantes no Docker e configuração inadequada do Chrome

**Correção**:
- ✅ Adicionadas todas as dependências necessárias no `Dockerfile`
- ✅ Configuração robusta do Chrome com fallbacks múltiplos
- ✅ Variável de ambiente `DISPLAY=:99` para execução headless
- ✅ Opções de Chrome otimizadas para containers Docker

## 📁 Arquivos Modificados

### `app/__init__.py`
```python
# ANTES: Instância global conflitante
celery = Celery(__name__)

# DEPOIS: Apenas função make_celery com configuração completa
def make_celery(app):
    celery = Celery(...)
    # Configuração completa aqui
    return celery
```

### `Dockerfile`
```dockerfile
# ANTES: Dependências mínimas
RUN apt-get install -y google-chrome-stable

# DEPOIS: Dependências completas para Chrome
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget gnupg ca-certificates curl \
    libnss3 libgconf-2-4 libxi6 libxrandr2 libasound2 \
    libpangocairo-1.0-0 libatk1.0-0 libcairo-gobject2 \
    # ... muitas outras dependências
ENV DISPLAY=:99
```

### `app/infrastructure/scraping/dje_scraper.py`
```python
# ADICIONADO: Configuração robusta com fallbacks
def _setup_driver(self):
    # Múltiplas opções do Chrome
    # Fallbacks para diferentes cenários
    # Tratamento de erros aprimorado
```

### `celery_worker.py`
```python
# ANTES: Configuração duplicada
celery.conf.update(
    broker_connection_retry_on_startup=True,
    result_backend=app.config['REDIS_URL'],
    # ... outras configurações
)

# DEPOIS: Registro correto das tasks
from app.tasks.scraping_tasks import (...)
celery.task(extract_publicacoes_task, bind=True, name='...')
```

### `app/presentation/routes.py`
```python
# ANTES: Uso direto da task
task = extract_publicacoes_task.delay(...)

# DEPOIS: Uso via celery_app
from celery import current_app as celery_app
task = celery_app.send_task('app.tasks.scraping_tasks.extract_publicacoes_task', ...)
```

### `app/tasks/scraping_tasks.py`
```python
# ANTES: Decoradores @celery.task
@celery.task(bind=True)
def extract_publicacoes_task(self, ...):

# DEPOIS: Funções simples registradas externamente
def extract_publicacoes_task(...):
    # Imports dentro do contexto
    # Verificações de current_task
```

## 🧪 Arquivo de Teste Criado

**`test_corrections.py`**: Script para verificar se todas as correções funcionaram

```bash
# Executar teste
python test_corrections.py
```

## 🐳 Comandos Docker Atualizados

```bash
# Rebuildar com correções
docker-compose down
docker-compose up --build

# Verificar logs específicos
docker-compose logs web
docker-compose logs worker
docker-compose logs redis
```

## 🔧 Configurações Principais

### Redis/Celery
- ✅ Backend: `redis://redis:6379/0`
- ✅ Broker: `redis://redis:6379/0`
- ✅ Serialização: JSON
- ✅ Timezone: America/Sao_Paulo

### Chrome/Selenium
- ✅ Headless mode
- ✅ No sandbox
- ✅ Disable dev shm usage
- ✅ Múltiplas opções de performance
- ✅ Fallbacks para diferentes ambientes

## 📊 Resultado Esperado

Após as correções:
1. ✅ Endpoint `/api/scraping/extract` funcionando
2. ✅ Endpoint `/api/scraping/status/{task_id}` retornando status correto
3. ✅ Selenium funcionando no Docker
4. ✅ Tasks do Celery executando corretamente
5. ✅ Cron jobs agendados funcionando

## 🚀 Próximos Passos

1. **Testar**: Execute `python test_corrections.py`
2. **Subir serviços**: `docker-compose up --build`
3. **Verificar API**: Acesse http://localhost:5000/docs
4. **Monitorar**: Acesse http://localhost:5555 (Flower)
5. **Testar scraping**: Faça POST para `/api/scraping/extract` 