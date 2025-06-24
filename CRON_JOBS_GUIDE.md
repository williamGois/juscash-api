# 🕐 Guia de Cron Jobs - JusCash API

Este documento explica como configurar e gerenciar os cron jobs para automação da raspagem de dados do DJE.

## 🚀 Opções de Agendamento

A JusCash API oferece **duas formas** de configurar tarefas automáticas:

### 1. **Celery Beat** (Recomendado para Docker)
- ✅ Integrado com o Docker Compose
- ✅ Interface web com Flower
- ✅ Gerenciamento via API
- ✅ Logs centralizados

### 2. **Crontab do Sistema** (Para servidores Linux)
- ✅ Nativo do sistema operacional
- ✅ Independente do Docker
- ✅ Controle granular de horários

## 🐳 Configuração com Docker (Celery Beat)

### Estrutura dos Containers

```yaml
# docker-compose.yml inclui:
- web              # API Flask
- celery-worker    # Processador de tarefas
- celery-beat      # Agendador de tarefas
- celery-flower    # Interface de monitoramento
- redis            # Message broker
- db               # PostgreSQL
```

### Agendamentos Configurados

| Tarefa | Frequência | Horário | Descrição |
|--------|-----------|---------|-----------|
| **Raspagem Diária** | A cada hora | Configurável | Extrai publicações do dia anterior |
| **Raspagem Completa** | Semanal | Configurável | Extrai todo o período (01/10 - 29/11/2024) |
| **Limpeza de Logs** | Diária | Configurável | Remove logs antigos (>30 dias) |

### Variáveis de Ambiente

```env
# Agendamentos (em segundos)
DAILY_SCRAPING_SCHEDULE=3600    # 1 hora
WEEKLY_SCRAPING_SCHEDULE=604800 # 1 semana  
CLEANUP_SCHEDULE=86400          # 1 dia

# Controle
SCRAPING_ENABLED=true           # Habilitar/desabilitar
```

### Comandos Docker

```bash
# Executar todos os serviços
docker-compose up --build

# Ver logs específicos
docker-compose logs -f celery-beat
docker-compose logs -f celery-worker

# Monitoramento web (Flower)
# Acesse: http://localhost:5555

# Executar tarefa manual
docker-compose exec web python -c "
from app.tasks.scraping_tasks import extract_daily_publicacoes
extract_daily_publicacoes.delay()
"
```

## 🖥️ Configuração com Crontab (Sistema Linux)

### Instalação Automática

```bash
# Instalar cron jobs
python cron_schedule.py install

# Verificar status
python cron_schedule.py status

# Remover cron jobs
python cron_schedule.py remove
```

### Agendamentos Padrão

```cron
# Raspagem diária às 2:00 AM
0 2 * * * cd /path/to/juscash-api && python -c "..."

# Raspagem completa aos domingos às 3:00 AM  
0 3 * * 0 cd /path/to/juscash-api && python -c "..."

# Limpeza de logs às 4:00 AM
0 4 * * * cd /path/to/juscash-api && python -c "..."

# Health check a cada 6 horas
0 */6 * * * cd /path/to/juscash-api && python -c "..."
```

### Configuração Manual

```bash
# Editar crontab
crontab -e

# Adicionar entrada personalizada
# Min Hora Dia Mês DiaSemana Comando
0 8 * * 1-5 cd /path/to/juscash-api && python -c "from app.tasks.scraping_tasks import extract_daily_publicacoes; extract_daily_publicacoes.delay()"

# Ver crontab atual
crontab -l
```

## 📊 API de Gerenciamento de Cron Jobs

A API inclui endpoints para gerenciar tarefas manualmente:

### Endpoints Disponíveis

```http
# Execução Manual
POST /api/cron/scraping/daily
POST /api/cron/scraping/full-period
POST /api/cron/scraping/custom-period
POST /api/cron/maintenance/cleanup
POST /api/cron/maintenance/stats

# Monitoramento
GET /api/cron/health
GET /api/cron/tasks/{task_id}
```

### Exemplos de Uso

```bash
# Executar raspagem diária
curl -X POST http://localhost:5000/api/cron/scraping/daily

# Executar raspagem customizada
curl -X POST http://localhost:5000/api/cron/scraping/custom-period \
  -H "Content-Type: application/json" \
  -d '{"data_inicio": "2024-10-01", "data_fim": "2024-10-31"}'

# Verificar saúde do sistema
curl http://localhost:5000/api/cron/health

# Verificar status de tarefa
curl http://localhost:5000/api/cron/tasks/task-id-aqui
```

## 🔍 Monitoramento e Logs

### Flower (Interface Web)

```bash
# Acessar Flower
http://localhost:5555

# Funcionalidades:
- ✅ Tasks em execução
- ✅ Histórico de execuções  
- ✅ Estatísticas de performance
- ✅ Controle de workers
```

### Logs do Sistema

```bash
# Docker logs
docker-compose logs -f celery-beat
docker-compose logs -f celery-worker

# Logs do sistema (crontab)
tail -f /var/log/juscash-daily.log
tail -f /var/log/juscash-weekly.log
tail -f /var/log/juscash-cleanup.log
tail -f /var/log/juscash-health.log
```

### Health Check

```bash
# Via API
curl http://localhost:5000/api/cron/health

# Via comando direto
docker-compose exec web python -c "
from app.tasks.maintenance_tasks import health_check
print(health_check.delay().get())
"
```

## ⚙️ Configurações Avançadas

### Personalizar Horários

```python
# config.py
DAILY_SCRAPING_SCHEDULE = 1800  # 30 minutos
WEEKLY_SCRAPING_SCHEDULE = 259200  # 3 dias
CLEANUP_SCHEDULE = 43200  # 12 horas
```

### Desabilitar Raspagem

```env
SCRAPING_ENABLED=false
```

### Configurar Retry e Timeout

```python
# app/tasks/scraping_tasks.py
@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def extract_daily_publicacoes(self):
    # ... código da tarefa
```

## 🚨 Troubleshooting

### Problemas Comuns

**1. Tarefa não executa**
```bash
# Verificar se worker está rodando
docker-compose ps
celery -A celery_worker.celery inspect active

# Verificar logs
docker-compose logs celery-beat
```

**2. Erro de conexão com banco**
```bash
# Verificar variáveis de ambiente
docker-compose exec web env | grep DATABASE

# Testar conexão
docker-compose exec web python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    print(db.engine.execute('SELECT 1').scalar())
"
```

**3. Crontab não funciona**
```bash
# Verificar se cron está rodando
sudo systemctl status cron

# Ver logs do cron
tail -f /var/log/syslog | grep CRON

# Testar comando manualmente
cd /path/to/juscash-api && python -c "..."
```

**4. Flower não carrega**
```bash
# Verificar se Redis está rodando
docker-compose exec redis redis-cli ping

# Reiniciar flower
docker-compose restart celery-flower
```

### Comandos de Diagnóstico

```bash
# Status completo do sistema
curl http://localhost:5000/api/cron/health

# Tasks ativas
docker-compose exec web celery -A celery_worker.celery inspect active

# Estatísticas
docker-compose exec web celery -A celery_worker.celery inspect stats

# Configuração atual
docker-compose exec web python -c "
from app import create_app
app = create_app()
print(app.config['DAILY_SCRAPING_SCHEDULE'])
"
```

## 📋 Checklist de Produção

### Antes do Deploy

- [ ] Configurar variáveis de ambiente
- [ ] Definir horários apropriados
- [ ] Configurar alertas de falha
- [ ] Testar todas as tarefas manualmente
- [ ] Configurar monitoramento (Flower)
- [ ] Configurar backup do Redis
- [ ] Documentar procedimentos

### Monitoramento Contínuo

- [ ] Verificar logs diariamente
- [ ] Monitorar performance via Flower
- [ ] Acompanhar health checks
- [ ] Validar dados extraídos
- [ ] Verificar espaço em disco
- [ ] Monitorar uso de CPU/RAM

## 🎯 Resumo dos Comandos

```bash
# Docker (Recomendado)
docker-compose up --build                    # Iniciar todos os serviços
docker-compose logs -f celery-beat          # Logs do agendador
http://localhost:5555                       # Interface Flower

# Crontab (Alternativo)
python cron_schedule.py install            # Instalar cron jobs
python cron_schedule.py status             # Ver status
crontab -l                                 # Listar entradas

# API Manual
curl -X POST http://localhost:5000/api/cron/scraping/daily
curl http://localhost:5000/api/cron/health
```

Agora você tem um sistema completo de automação para manter sua base de dados sempre atualizada! 🚀 