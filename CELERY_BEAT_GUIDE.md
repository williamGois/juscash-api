# 🕐 Guia Celery Beat Integrado - JusCash API

## ✅ **Configuração Atual:**
Usamos **Celery Beat** integrado ao serviço **worker** para agendamento de tarefas.

### **Vantagens:**
- ✅ **Menos serviços** no Railway (economia)
- ✅ **Configuração centralizada** em `celery_worker.py`
- ✅ **Controle total** via Python
- ✅ **Monitoramento fácil** via Flower

---

## 🚀 **Como Funciona:**

### **1. `celery_worker.py` - O Coração do Agendamento**
```python
# celery_worker.py
from celery.schedules import crontab

celery.conf.update(
    beat_schedule={
        'raspagem_diaria': {
            'task': 'app.tasks.scraping_tasks.extract_daily_publicacoes',
            'schedule': crontab(minute=0),  # A cada hora
        },
        'raspagem_completa': {
            'task': 'app.tasks.scraping_tasks.extract_full_period_publicacoes',
            'schedule': crontab(hour=3, minute=0, day_of_week='sunday'),
        },
        'limpeza_logs': {
            'task': 'app.tasks.maintenance_tasks.cleanup_old_logs',
            'schedule': crontab(hour=4, minute=0),
        },
    }
)
```

### **2. `Procfile` - Comando Mágico `-B`**
```
worker: celery -A celery_worker.celery worker -B --loglevel=info
```
- **`worker`**: Inicia o processador de tarefas
- **`-B`**: Inicia o agendador **Beat** no mesmo processo

### **3. `docker-compose.yml` - Simplificado**
```yaml
# Sem serviço "beat" separado
worker:
  command: ["celery", "-A", "celery_worker.celery", "worker", "-B", "--loglevel=info"]
```

---

## 🔧 **Como Modificar Agendamentos:**

### **Exemplos:**

#### **Mudar raspagem diária para 2 em 2 horas:**
```python
# celery_worker.py
'schedule': crontab(minute=0, hour='*/2'),
```

#### **Mudar limpeza para meia-noite:**
```python
# celery_worker.py
'schedule': crontab(hour=0, minute=0),
```

#### **Desativar uma tarefa:**
```python
# celery_worker.py
# Comente a tarefa desejada
# 'limpeza_logs': { ... }
```

### **Documentação `crontab`:**
Para mais opções, consulte a [documentação do Celery](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html#crontab-schedules).

---

## 📊 **Monitoramento:**

### **1. Flower Dashboard**
- **Acesse**: URL do serviço Flower
- **Verificar**: Aba "Tasks" → Tarefas agendadas

### **2. Logs do Worker**
- **Railway Dashboard** → **Serviço Worker** → **Logs**
- **Logs esperados:**
  ```
  [INFO/MainProcess] Beat: Waking up in 1m...
  [INFO/MainProcess] Beat: Waking up in 30s...
  [INFO/MainProcess] Scheduler: Sending due task raspagem_diaria (app.tasks.scraping_tasks.extract_daily_publicacoes)
  ```

### **3. API de Controle**
- `GET /api/cron/health`
- `POST /api/cron/scraping/daily` (executar manualmente)

---

## 🚨 **Troubleshooting:**

### **Tarefas não agendadas?**
- **Verificar `-B`**: Confirme que o `-B` está no comando do worker.
- **Verificar `beat_schedule`**: Confirme que está no `celery_worker.py`.
- **Verificar logs do worker**: Procurar por mensagens do `Scheduler`.
- **Verificar timezone**: Todas as datas são UTC por padrão.

### **Tarefas falhando?**
- **Verificar Flower**: Aba "Tasks" → Status "FAILURE".
- **Verificar logs do worker**: Procurar por `Traceback`.
- **Testar tarefa manualmente**: `POST /api/cron/scraping/daily`.

---

## 🎯 **Checklist de Implementação:**

- [✅] `celery_worker.py` atualizado com `beat_schedule`
- [✅] `Procfile` atualizado com comando `-B`
- [✅] `docker-compose.yml` simplificado
- [✅] Documentação atualizada
- [ ] **Ação do usuário**: Remover serviço `beat` e `Cron Jobs` do Railway

---

## 🎉 **Resultado Final:**

- **Agendamento Robusto**: Celery Beat integrado
- **Configuração Centralizada**: Tudo em um único arquivo
- **Economia de Recursos**: Menos um serviço no Railway
- **Fácil Manutenção**: Modificar agendamentos em Python

**Sistema otimizado para agendamento de tarefas!** 🚀 