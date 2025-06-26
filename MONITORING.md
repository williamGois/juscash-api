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