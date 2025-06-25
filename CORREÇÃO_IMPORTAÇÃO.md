# 🔧 Correção: Erro de Importação do Celery

## 🚨 Problema Identificado

**Erro**: `ImportError: cannot import name 'celery' from 'app'`

**Causa**: Após remover a instância global `celery` do `app/__init__.py`, alguns arquivos ainda tentavam importá-la diretamente.

## ✅ Arquivos Corrigidos

### 1. `app/tasks/maintenance_tasks.py`
**ANTES**:
```python
from app import celery, create_app

@celery.task
def cleanup_old_logs():
    # ...
```

**DEPOIS**:
```python
from app import create_app

def cleanup_old_logs():
    # Função simples, sem decorator
```

### 2. `app/presentation/cron_routes.py`
**ANTES**:
```python
from app.tasks.maintenance_tasks import cleanup_old_logs
task = cleanup_old_logs.delay()
```

**DEPOIS**:
```python
from celery import current_app as celery_app
task = celery_app.send_task('app.tasks.maintenance_tasks.cleanup_old_logs')
```

### 3. `celery_worker.py`
**ADICIONADO**:
```python
from app.tasks.maintenance_tasks import (
    cleanup_old_logs,
    generate_daily_stats,
    health_check
)

# Registro das tasks de manutenção
celery.task(cleanup_old_logs, name='app.tasks.maintenance_tasks.cleanup_old_logs')
celery.task(generate_daily_stats, name='app.tasks.maintenance_tasks.generate_daily_stats')
celery.task(health_check, name='app.tasks.maintenance_tasks.health_check')
```

## 🎯 Estratégia Aplicada

1. **Funções simples**: Todas as tasks agora são funções Python normais
2. **Registro externo**: Tasks registradas no `celery_worker.py`
3. **send_task**: Uso de `send_task` nos endpoints ao invés de `.delay()`
4. **Sem importação circular**: Remoção de todas as importações diretas do `celery`

## 🧪 Como Testar

```bash
# 1. Verificar se não há erros de importação
python -c "from app import create_app; app = create_app(); print('✅ Importações OK')"

# 2. Subir a aplicação
docker compose up --build

# 3. Testar endpoints de cron
curl -X POST http://localhost:5000/api/cron/maintenance/cleanup
```

## 📊 Resultado Esperado

- ✅ Aplicação inicia sem erros de importação
- ✅ Celery worker conecta corretamente
- ✅ Tasks podem ser executadas via API
- ✅ Flower dashboard funcional

---

**Status**: ✅ CORRIGIDO - Todas as dependências circulares removidas 