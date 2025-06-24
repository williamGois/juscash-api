# 🕐 Exemplos Práticos - Cron Jobs API

Exemplos de como usar os endpoints de agendamento e as funcionalidades de cron job da JusCash API.

## 🚀 Execução Manual de Tarefas

### Raspagem Diária

```bash
# Executar raspagem do dia anterior
curl -X POST http://localhost:5000/api/cron/scraping/daily \
  -H "Content-Type: application/json"

# Resposta esperada:
{
  "task_id": "abc123-def456-ghi789",
  "status": "started",
  "message": "Raspagem diária iniciada"
}
```

### Raspagem do Período Completo

```bash
# Executar raspagem de todo o período (01/10 - 29/11/2024)
curl -X POST http://localhost:5000/api/cron/scraping/full-period \
  -H "Content-Type: application/json"

# Resposta esperada:
{
  "task_id": "xyz987-uvw654-rst321",
  "status": "started", 
  "message": "Raspagem do período completo iniciada"
}
```

### Raspagem Período Customizado

```bash
# Executar raspagem de outubro de 2024
curl -X POST http://localhost:5000/api/cron/scraping/custom-period \
  -H "Content-Type: application/json" \
  -d '{
    "data_inicio": "2024-10-01",
    "data_fim": "2024-10-31"
  }'

# Resposta esperada:
{
  "task_id": "custom123-456789-abc",
  "status": "started",
  "message": "Raspagem customizada iniciada para período 2024-10-01 a 2024-10-31"
}
```

## 🔧 Tarefas de Manutenção

### Limpeza de Logs

```bash
# Executar limpeza de logs antigos
curl -X POST http://localhost:5000/api/cron/maintenance/cleanup \
  -H "Content-Type: application/json"

# Resposta esperada:
{
  "task_id": "cleanup123-456",
  "status": "started",
  "message": "Limpeza de logs iniciada"
}
```

### Gerar Estatísticas

```bash
# Gerar estatísticas diárias
curl -X POST http://localhost:5000/api/cron/maintenance/stats \
  -H "Content-Type: application/json"

# Resposta esperada:
{
  "task_id": "stats789-012",
  "status": "started",
  "message": "Geração de estatísticas iniciada"
}
```

## 🩺 Monitoramento

### Health Check

```bash
# Verificar saúde do sistema
curl http://localhost:5000/api/cron/health

# Resposta esperada:
{
  "database_connection": "ok",
  "total_publicacoes": 1250,
  "publicacoes_ultima_semana": 75,
  "timestamp": "2024-01-15T10:30:00Z",
  "status": "healthy"
}
```

### Status de Tarefa

```bash
# Verificar status de uma tarefa específica
curl http://localhost:5000/api/cron/tasks/abc123-def456-ghi789

# Resposta para tarefa em execução:
{
  "state": "PROGRESS",
  "current": 50,
  "total": 100,
  "status": "Processando dados..."
}

# Resposta para tarefa concluída:
{
  "state": "SUCCESS",
  "result": "Raspagem diária concluída: 25 publicações extraídas do dia 2024-01-14"
}

# Resposta para tarefa com erro:
{
  "state": "FAILURE",
  "error": "Erro de conexão com o site do DJE"
}
```

## 🐍 Exemplos em Python

### Script Básico

```python
import requests
import time

API_BASE = "http://localhost:5000/api/cron"

def executar_raspagem_diaria():
    """Executa raspagem diária e monitora progresso"""
    # Iniciar tarefa
    response = requests.post(f"{API_BASE}/scraping/daily")
    data = response.json()
    
    if response.status_code == 200:
        task_id = data['task_id']
        print(f"Tarefa iniciada: {task_id}")
        
        # Monitorar progresso
        while True:
            status_response = requests.get(f"{API_BASE}/tasks/{task_id}")
            status_data = status_response.json()
            
            state = status_data['state']
            print(f"Status: {state}")
            
            if state == 'SUCCESS':
                print(f"Concluído: {status_data['result']}")
                break
            elif state == 'FAILURE':
                print(f"Erro: {status_data['error']}")
                break
            elif state == 'PROGRESS':
                current = status_data.get('current', 0)
                total = status_data.get('total', 1)
                print(f"Progresso: {current}/{total}")
            
            time.sleep(5)  # Aguardar 5 segundos
    else:
        print(f"Erro ao iniciar tarefa: {data}")

if __name__ == "__main__":
    executar_raspagem_diaria()
```

### Script de Monitoramento

```python
import requests
import json
from datetime import datetime

def verificar_saude_sistema():
    """Verifica saúde do sistema e exibe relatório"""
    try:
        response = requests.get("http://localhost:5000/api/cron/health")
        data = response.json()
        
        print("=" * 50)
        print("RELATÓRIO DE SAÚDE DO SISTEMA")
        print("=" * 50)
        print(f"Status: {data['status'].upper()}")
        print(f"Conexão com banco: {data['database_connection']}")
        print(f"Total de publicações: {data['total_publicacoes']:,}")
        print(f"Publicações última semana: {data['publicacoes_ultima_semana']}")
        print(f"Última verificação: {data['timestamp']}")
        
        # Alertas
        if data['status'] == 'warning':
            print("\n⚠️ ATENÇÃO: Sistema com avisos")
        elif data['status'] == 'error':
            print("\n❌ ERRO: Sistema com problemas")
        else:
            print("\n✅ Sistema funcionando normalmente")
            
    except Exception as e:
        print(f"❌ Erro ao verificar saúde: {e}")

def executar_raspagem_customizada(data_inicio, data_fim):
    """Executa raspagem de período customizado"""
    payload = {
        "data_inicio": data_inicio,
        "data_fim": data_fim
    }
    
    response = requests.post(
        "http://localhost:5000/api/cron/scraping/custom-period",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['message']}")
        print(f"🆔 Task ID: {data['task_id']}")
        return data['task_id']
    else:
        print(f"❌ Erro: {response.json()}")
        return None

# Exemplo de uso
if __name__ == "__main__":
    verificar_saude_sistema()
    
    # Executar raspagem customizada
    task_id = executar_raspagem_customizada("2024-10-15", "2024-10-20")
    if task_id:
        print(f"Monitore o progresso em: /api/cron/tasks/{task_id}")
```

## 📊 Scripts de Automação

### Agendamento com crontab

```bash
#!/bin/bash
# Script: /home/user/juscash_daily.sh

# Configurações
API_BASE="http://localhost:5000/api/cron"
LOG_FILE="/var/log/juscash_automation.log"

# Função de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
}

# Executar raspagem diária
log "Iniciando raspagem diária automática"

RESPONSE=$(curl -s -X POST $API_BASE/scraping/daily)
TASK_ID=$(echo $RESPONSE | jq -r '.task_id')

if [ "$TASK_ID" != "null" ]; then
    log "Tarefa iniciada: $TASK_ID"
    
    # Aguardar conclusão
    while true; do
        STATUS=$(curl -s $API_BASE/tasks/$TASK_ID | jq -r '.state')
        
        if [ "$STATUS" = "SUCCESS" ]; then
            RESULT=$(curl -s $API_BASE/tasks/$TASK_ID | jq -r '.result')
            log "Sucesso: $RESULT"
            break
        elif [ "$STATUS" = "FAILURE" ]; then
            ERROR=$(curl -s $API_BASE/tasks/$TASK_ID | jq -r '.error')
            log "Erro: $ERROR"
            break
        fi
        
        sleep 30
    done
else
    log "Erro ao iniciar tarefa"
fi

log "Raspagem diária finalizada"
```

### Configuração no crontab

```bash
# Editar crontab
crontab -e

# Adicionar entrada para execução diária às 2:00
0 2 * * * /home/user/juscash_daily.sh

# Verificar se foi adicionado
crontab -l
```

## 🐳 Docker Compose com Monitoramento

### docker-compose.monitoring.yml

```yaml
version: '3.8'

services:
  # ... outros serviços ...

  monitoring:
    build: .
    command: python monitoring_script.py
    volumes:
      - .:/app
      - ./logs:/app/logs
    depends_on:
      - web
      - celery-beat
    environment:
      - API_BASE_URL=http://web:5000
      - CHECK_INTERVAL=300  # 5 minutos
    restart: unless-stopped
```

### Script de Monitoramento Contínuo

```python
# monitoring_script.py
import requests
import time
import os
import logging
from datetime import datetime

# Configuração
API_BASE = os.getenv('API_BASE_URL', 'http://localhost:5000')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 300))  # 5 minutos

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/monitoring.log'),
        logging.StreamHandler()
    ]
)

def check_system_health():
    """Verifica saúde do sistema periodicamente"""
    try:
        response = requests.get(f"{API_BASE}/api/cron/health", timeout=30)
        data = response.json()
        
        if data['status'] == 'healthy':
            logging.info(f"Sistema saudável - {data['total_publicacoes']} publicações")
        else:
            logging.warning(f"Sistema com avisos - Status: {data['status']}")
            
        return True
        
    except Exception as e:
        logging.error(f"Erro ao verificar saúde: {e}")
        return False

def main():
    """Loop principal de monitoramento"""
    logging.info("Iniciando monitoramento automático")
    
    while True:
        try:
            check_system_health()
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            logging.info("Monitoramento interrompido pelo usuário")
            break
        except Exception as e:
            logging.error(f"Erro no monitoramento: {e}")
            time.sleep(60)  # Aguardar 1 minuto em caso de erro

if __name__ == "__main__":
    main()
```

## 📈 Dashboard Simples

### Exemplo com Flask

```python
# dashboard.py
from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)
API_BASE = "http://localhost:5000/api"

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    try:
        # Obter estatísticas das publicações
        pub_response = requests.get(f"{API_BASE}/publicacoes/stats")
        pub_stats = pub_response.json()
        
        # Obter saúde do sistema
        health_response = requests.get(f"{API_BASE}/cron/health")
        health_data = health_response.json()
        
        return jsonify({
            'publicacoes': pub_stats,
            'health': health_data,
            'timestamp': health_data.get('timestamp')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)
```

Agora você tem exemplos completos para usar todos os recursos de cron jobs da JusCash API! 🚀 