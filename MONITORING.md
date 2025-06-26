# 🐳 Dashboard Visual - JusCash Docker Monitoring

Implementei várias ferramentas de monitoramento visual para os containers Docker, similares ao Railway!

## 🎛️ **Ferramentas Disponíveis**

### 1. **Portainer** - Interface Visual Principal
- **URL**: `https://portainer.juscash.app` 🌐
- **Fallback**: `http://77.37.68.178:9000`
- **Descrição**: Interface gráfica completa para gerenciar Docker
- **Funcionalidades**:
  - ✅ Visualizar todos os containers
  - ✅ Iniciar/parar containers
  - ✅ Ver logs em tempo real
  - ✅ Monitorar recursos (CPU, RAM)
  - ✅ Gerenciar volumes e redes
  - ✅ Interface tipo Railway

### 2. **cAdvisor** - Métricas Detalhadas
- **URL**: `https://cadvisor.juscash.app` 🌐
- **Fallback**: `http://77.37.68.178:8080`
- **Descrição**: Monitoramento de performance dos containers
- **Funcionalidades**:
  - 📊 Gráficos de CPU e memória
  - 📈 Histórico de performance
  - 🔍 Métricas detalhadas por container
  - 📱 Interface responsiva

### 3. **Flower** - Monitor Celery
- **URL**: `https://flower.juscash.app` 🌐
- **Fallback**: `http://77.37.68.178:5555`
- **Descrição**: Monitoramento das tarefas Celery
- **Funcionalidades**:
  - 🌸 Tasks em execução
  - ⏱️ Histórico de execuções
  - 🔄 Status dos workers

### 4. **Dashboard Customizado** - Visão Geral
- **URL**: `https://cron.juscash.app/api/simple/dashboard-ui`
- **JSON API**: `https://cron.juscash.app/api/simple/dashboard`
- **Funcionalidades**:
  - 🎨 Interface visual moderna
  - 📱 Responsivo para mobile
  - 🔄 Auto-refresh a cada 30s
  - 🔗 Links para todas as ferramentas

## 🚀 **Como Ativar**

### 1. Deploy na VPS
```bash
# Na VPS, fazer pull e restart
cd /root/juscash-api
git pull origin master
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Configurar Portainer (primeira vez)
```bash
# Acessar http://77.37.68.178:9000
# Criar usuário admin na primeira visita
# Conectar ao Docker local
```

### 3. Configurar Nginx (se necessário)
```nginx
# Adicionar ao nginx para acesso externo
location /portainer/ {
    proxy_pass http://127.0.0.1:9000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

location /cadvisor/ {
    proxy_pass http://127.0.0.1:8080/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## 🔍 **Recursos de Cada Ferramenta**

### Portainer - Gestão Completa
```
🎛️ Dashboard principal
📋 Lista de containers com status
🔄 Controles start/stop/restart
📊 Uso de recursos em tempo real
📁 Gerenciamento de volumes
🌐 Configuração de redes
📜 Logs streaming
🔧 Terminal dentro dos containers
```

### cAdvisor - Performance
```
📈 Gráficos de CPU por container
💾 Uso de memória detalhado
💿 I/O de disco
🌐 Tráfego de rede
⏱️ Latência e throughput
📊 Comparação entre containers
```

### Dashboard Customizado
```
🎨 Interface moderna e limpa
📱 Responsivo para mobile
🔄 Auto-refresh automático
🔗 Links diretos para ferramentas
📊 Status resumido do sistema
❤️ Health checks integrados
```

## 📱 **Acesso Mobile**

Todas as interfaces são responsivas e funcionam bem em:
- 📱 Smartphones
- 💻 Tablets
- 🖥️ Desktops

## 🔒 **Segurança**

### Configurações Aplicadas:
- 🔒 Bind apenas em localhost (127.0.0.1)
- 🛡️ Security constraints nos containers
- 📊 Logs limitados para não consumir disco
- 🔐 Flower com autenticação básica

### Para Produção:
```bash
# Configurar autenticação no nginx
# Usar HTTPS com certificados
# Restringir IPs se necessário
```

## 🛠️ **Troubleshooting**

### Se Portainer não iniciar:
```bash
# Verificar logs
docker-compose -f docker-compose.prod.yml logs portainer

# Restart específico
docker-compose -f docker-compose.prod.yml restart portainer
```

### Se cAdvisor der erro:
```bash
# Verificar permissões
ls -la /var/run/docker.sock

# Restart com rebuild
docker-compose -f docker-compose.prod.yml up --build cadvisor
```

### Se Dashboard customizado não carregar:
```bash
# Verificar se template existe
ls -la templates/dashboard.html

# Testar endpoint JSON
curl https://cron.juscash.app/api/simple/dashboard
```

## 🎯 **URLs de Acesso Rápido**

| Ferramenta | URL Principal | URL Fallback | Descrição |
|------------|---------------|--------------|-----------|
| 🎛️ **Portainer** | https://portainer.juscash.app | http://77.37.68.178:9000 | Interface Docker principal |
| 📊 **cAdvisor** | https://cadvisor.juscash.app | http://77.37.68.178:8080 | Métricas de performance |
| 🌸 **Flower** | https://flower.juscash.app | http://77.37.68.178:5555 | Monitor Celery |
| 🎨 **Dashboard** | https://cron.juscash.app/api/simple/dashboard-ui | - | Dashboard customizado |
| 📚 **API Docs** | https://cron.juscash.app/docs/ | - | Documentação Swagger |

## 🌐 **Configuração de Subdomínios**

### Para ativar os subdomínios na VPS:

```bash
# 1. Fazer pull das configurações
cd /root/juscash-api
git pull origin master

# 2. Executar script de configuração (como root)
sudo ./scripts/setup-subdomains.sh

# 3. Verificar status dos certificados SSL
sudo certbot certificates

# 4. Testar configuração nginx
sudo nginx -t && sudo systemctl reload nginx
```

### Configurações DNS necessárias:

Adicione estes registros A no seu provedor DNS:
```
portainer.juscash.app    A    77.37.68.178
cadvisor.juscash.app     A    77.37.68.178  
flower.juscash.app       A    77.37.68.178
```

## 🔄 **Auto-Deploy**

O GitHub Actions já está configurado para fazer deploy automático das ferramentas de monitoramento junto com a aplicação principal.

# 🎯 Guia Completo de Monitoramento - JusCash API

## 📋 Como Monitorar Cron Jobs em Execução

### 1. 🌸 **Flower - Monitor Celery (RECOMENDADO)**

**URL**: https://flower.juscash.app  
**Usuário**: admin  
**Senha**: juscash2024  

**No Flower você pode ver:**
- ✅ Tarefas ativas em tempo real
- 📊 Histórico de execuções
- ⏱️ Tempos de execução
- 📈 Estatísticas dos workers
- 🔄 Filas de tarefas (queue)
- 📊 Gráficos de performance

**Principais abas do Flower:**
- **Tasks**: Lista todas as tarefas executadas
- **Workers**: Status dos workers Celery
- **Broker**: Informações do Redis
- **Monitor**: Visualização em tempo real

### 2. 📊 **Logs dos Containers Docker**

```bash
# Via SSH no VPS
ssh root@77.37.68.178
cd /var/www/juscash

# Logs do Worker Celery
docker logs juscash_worker_prod --tail 50 -f

# Logs da API principal
docker logs juscash_web_prod --tail 50 -f

# Logs do Flower
docker logs juscash_flower_prod --tail 20

# Ver todos os containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### 3. 🎯 **API Endpoints de Monitoramento**

#### Executar Tarefas Manualmente

```bash
# Raspagem diária
curl -X POST 'https://cron.juscash.app/api/cron/scraping/daily'

# Raspagem de período customizado
curl -X POST 'https://cron.juscash.app/api/cron/scraping/custom-period' \
  -H 'Content-Type: application/json' \
  -d '{
    "data_inicio": "2024-10-01",
    "data_fim": "2024-10-31"
  }'

# Limpeza de logs
curl -X POST 'https://cron.juscash.app/api/cron/maintenance/cleanup'

# Gerar estatísticas diárias
curl -X POST 'https://cron.juscash.app/api/cron/maintenance/stats'
```

#### Verificar Status de Tarefas

```bash
# Status de uma tarefa específica
curl -X GET 'https://cron.juscash.app/api/cron/tasks/{TASK_ID}'

# Exemplo:
curl -X GET 'https://cron.juscash.app/api/cron/tasks/a6102a28-85b0-4e22-9fdd-f00da25918d3'
```

**Resposta de exemplo:**
```json
{
  "state": "SUCCESS",
  "status": "Tarefa executada sincronamente",
  "result": "Consulte a resposta original da requisição para detalhes"
}
```

#### Health Check

```bash
# Verificar saúde geral do sistema
curl -X GET 'https://cron.juscash.app/api/cron/health'
```

### 4. 📋 **Swagger UI - Documentação Interativa**

**URL**: https://cron.juscash.app/docs/

**No Swagger você pode:**
- 📚 Ver toda a documentação da API
- 🧪 Testar endpoints diretamente
- 👀 Ver exemplos de requisições
- 📖 Verificar modelos de dados

### 5. 🐍 **Script Python para Monitoramento**

```python
import requests
import time
import json

API_BASE = "https://cron.juscash.app/api/cron"

def executar_raspagem_diaria():
    """Executa raspagem diária e monitora"""
    response = requests.post(f"{API_BASE}/scraping/daily")
    data = response.json()
    
    if response.status_code == 200:
        task_id = data['task_id']
        print(f"🚀 Tarefa iniciada: {task_id}")
        
        # Monitorar execução
        while True:
            status_response = requests.get(f"{API_BASE}/tasks/{task_id}")
            status_data = status_response.json()
            
            print(f"Status: {status_data['state']}")
            
            if status_data['state'] in ['SUCCESS', 'FAILURE']:
                break
                
            time.sleep(10)
        
        print(f"✅ Tarefa finalizada: {status_data}")
    else:
        print(f"❌ Erro: {data}")

# Executar
executar_raspagem_diaria()
```

### 6. 🔍 **Comandos de Diagnóstico**

```bash
# Verificar se workers estão rodando
ssh root@77.37.68.178 "cd /var/www/juscash && docker exec juscash_worker_prod celery -A celery_worker.celery status"

# Verificar configuração do Celery
ssh root@77.37.68.178 "cd /var/www/juscash && docker exec juscash_worker_prod python -c 'from celery_worker import celery; print(celery.conf)'"

# Testar Redis
ssh root@77.37.68.178 "cd /var/www/juscash && docker exec juscash_redis_prod redis-cli ping"

# Ver métricas dos containers
ssh root@77.37.68.178 "cd /var/www/juscash && docker stats --no-stream"
```

### 7. 📊 **cAdvisor - Métricas de Containers**

**URL**: https://cadvisor.juscash.app

**Métricas disponíveis:**
- 💾 Uso de memória por container
- 💻 Uso de CPU
- 📊 I/O de disco
- 🌐 Tráfego de rede
- 📈 Histórico de performance

### 8. 🐳 **Portainer - Gerenciamento Docker**

**URL**: https://portainer.juscash.app

**Funcionalidades:**
- 🐳 Gerenciar containers
- 📊 Ver logs em tempo real
- 🔄 Restart de serviços
- 📈 Monitorar recursos
- 🛠️ Console interativo

## 🚨 **Alertas e Notificações**

### Problemas Comuns e Soluções

**1. Worker não responde**
```bash
# Restart do worker
ssh root@77.37.68.178 "cd /var/www/juscash && docker-compose -f docker-compose.prod.yml restart worker"
```

**2. Redis indisponível**
```bash
# Restart do Redis
ssh root@77.37.68.178 "cd /var/www/juscash && docker-compose -f docker-compose.prod.yml restart redis"
```

**3. Flower não carrega**
```bash
# Restart do Flower
ssh root@77.37.68.178 "cd /var/www/juscash && docker-compose -f docker-compose.prod.yml restart flower"
```

### Estados das Tarefas

- **PENDING**: Tarefa na fila aguardando execução
- **STARTED**: Tarefa iniciando execução
- **PROGRESS**: Tarefa em progresso
- **SUCCESS**: Tarefa concluída com sucesso
- **FAILURE**: Tarefa falhou
- **RETRY**: Tarefa sendo reexecutada
- **REVOKED**: Tarefa cancelada

## 📅 **Tarefas Agendadas (Cron)**

### Configuração Atual

**Configuração via docker-compose.prod.yml:**
- Worker rodando com beat scheduler
- Fila padrão para tarefas síncronas
- Fila separada para scraping
- Fila de manutenção

### Horários Padrão (se configurado)

- **Raspagem diária**: Todo dia às 07:00 UTC
- **Limpeza de logs**: Toda segunda-feira às 02:00 UTC
- **Estatísticas**: Todo dia às 23:00 UTC

## 🔧 **Troubleshooting**

### 1. Verificar Stack Completa

```bash
ssh root@77.37.68.178 "cd /var/www/juscash && docker-compose -f docker-compose.prod.yml ps"
```

### 2. Logs Detalhados

```bash
# Todos os logs juntos
ssh root@77.37.68.178 "cd /var/www/juscash && docker-compose -f docker-compose.prod.yml logs --tail=100"
```

### 3. Restart Completo

```bash
# Restart de todo o stack
ssh root@77.37.68.178 "cd /var/www/juscash && docker-compose -f docker-compose.prod.yml down && docker-compose -f docker-compose.prod.yml up -d"
```

---

## 🎯 **Resumo Rápido**

**Para monitorar cron jobs rapidamente:**

1. **🌸 Acesse o Flower**: https://flower.juscash.app (admin:juscash2024)
2. **📊 Verifique logs**: `docker logs juscash_worker_prod --tail 20`
3. **🧪 Teste via API**: Use os endpoints `/api/cron/` no Swagger
4. **📈 Métricas avançadas**: https://cadvisor.juscash.app

**Status atual:** ✅ Todos os serviços funcionando corretamente!