# 🚂 Deploy no Railway - JusCash API

Guia completo para fazer deploy da JusCash API no Railway.

## 🎯 Pré-requisitos

- Conta no [Railway](https://railway.app)
- Código da JusCash API
- Git configurado

## 🚀 Passo a Passo

### 1. Preparar o Projeto

```bash
# Certifique-se de estar no diretório do projeto
cd juscash-api

# Commit todas as mudanças
git add .
git commit -m "Preparação para deploy Railway"
```

### 2. Criar Projeto no Railway

1. Acesse [Railway](https://railway.app)
2. Clique em "Start a New Project"
3. Selecione "Deploy from GitHub repo"
4. Conecte sua conta GitHub e selecione o repositório

### 3. Adicionar Banco de Dados PostgreSQL

1. No dashboard do Railway, clique em "New +"
2. Selecione "Database" → "PostgreSQL"
3. Aguarde a criação (alguns minutos)
4. A variável `DATABASE_URL` será criada automaticamente

### 4. Adicionar Redis

1. Clique em "New +" novamente  
2. Selecione "Database" → "Redis"
3. Aguarde a criação
4. A variável `REDIS_URL` será criada automaticamente

### 5. Configurar Variáveis de Ambiente

No painel do Railway, vá para o serviço da aplicação → Variables e adicione:

```env
# Obrigatórias
SECRET_KEY=sua-chave-secreta-muito-segura-aqui
FLASK_ENV=production
RAILWAY_ENVIRONMENT=true

# Scraping
SCRAPING_ENABLED=true
DAILY_SCRAPING_SCHEDULE=3600
WEEKLY_SCRAPING_SCHEDULE=604800
CLEANUP_SCHEDULE=86400

# Database (otimizações Railway)
DB_POOL_SIZE=2
DB_POOL_RECYCLE=300
```

### 6. Configurar Serviços Múltiplos

O Railway permite múltiplos serviços. Configure:

#### Serviço Principal (Web API)
```bash
# Start Command:
chmod +x railway-start.sh && ./railway-start.sh

# Ou diretamente:
flask upgrade-db && python run.py
```

#### Serviço Worker (Opcional)
Para ter worker separado:
```bash
# Start Command:
chmod +x railway-worker.sh && ./railway-worker.sh
```

#### Serviço Beat (Opcional)  
Para ter agendador separado:
```bash
# Start Command:
chmod +x railway-beat.sh && ./railway-beat.sh
```

### 7. Deploy

1. Clique em "Deploy" no Railway
2. Aguarde o build (5-10 minutos)
3. Verifique os logs para erros
4. Acesse a URL fornecida

## 🔧 Configuração Avançada

### Dockerfile Railway

O projeto inclui `Dockerfile.railway` otimizado:

```dockerfile
# Otimizado para Railway
FROM python:3.11-slim
# ... configurações específicas
```

### Scripts de Inicialização

- `railway-start.sh` - Aplicação principal
- `railway-worker.sh` - Worker Celery  
- `railway-beat.sh` - Agendador

### Procfile

```
web: flask upgrade-db && python run.py
worker: celery -A celery_worker.celery worker --loglevel=info
beat: celery -A celery_worker.celery beat --loglevel=info
```

## 📊 Monitoramento

### URLs de Acesso

Após deploy, você terá:
- **API Principal**: `https://seu-app.up.railway.app`
- **Swagger Docs**: `https://seu-app.up.railway.app/docs/`
- **Health Check**: `https://seu-app.up.railway.app/api/cron/health`

### Logs

```bash
# Ver logs no Railway
# Dashboard → Serviço → Deployments → Ver logs

# Exemplos de logs importantes:
# ✅ "Banco PostgreSQL conectado!"
# ✅ "Migrações aplicadas com sucesso!"
# ✅ "Iniciando aplicação..."
```

## 🧪 Testar Deploy

### 1. Health Check
```bash
curl https://seu-app.up.railway.app/api/cron/health
```

### 2. API Básica
```bash
curl https://seu-app.up.railway.app/api/publicacoes/stats
```

### 3. Swagger
Acesse: `https://seu-app.up.railway.app/docs/`

### 4. Executar Raspagem Manual
```bash
curl -X POST https://seu-app.up.railway.app/api/cron/scraping/daily
```

## ⚠️ Limitações do Railway

### Plano Gratuito
- **CPU**: Limitado
- **RAM**: 512MB-1GB
- **Bandwidth**: 100GB/mês
- **Build time**: 500 horas/mês
- **Conexões DB**: Limitadas

### Otimizações Aplicadas
- Pool de conexões reduzido (`DB_POOL_SIZE=2`)
- Worker único para Celery
- Chrome headless otimizado
- Logs reduzidos

## 🚨 Troubleshooting

### Erro de Memória
```bash
# Se der erro de memória, reduza workers:
# No Railway: Configure CELERY_CONCURRENCY=1
```

### Erro de Conexão DB
```bash
# Verifique se PostgreSQL addon foi criado
# Verifique se DATABASE_URL está definida
```

### Chrome/Selenium Não Funciona
```bash
# Logs mostrarão erro de Chrome
# Verificar se dependências estão instaladas
# Dockerfile.railway já inclui Chrome
```

### Timeout de Deploy
```bash
# Railway tem timeout de build
# Se der timeout, simplifique build
# Remova dependências desnecessárias
```

## 🔄 CI/CD Automático

### Auto Deploy
Railway faz deploy automático quando:
- Push para branch main/master
- Merge de Pull Request
- Commit direto no repositório

### Verificar Deploy
```bash
# Sempre verifique após deploy:
curl https://seu-app.up.railway.app/api/cron/health

# Exemplo de resposta saudável:
{
  "database_connection": "ok",
  "total_publicacoes": 0,
  "publicacoes_ultima_semana": 0,
  "timestamp": "2024-01-15T12:00:00Z",
  "status": "healthy"
}
```

## 💰 Custos

### Plano Gratuito
- $5 de crédito/mês
- Ideal para testes
- Suficiente para uso leve

### Plano Pago
- $10/mês por serviço
- Recursos ilimitados
- Recomendado para produção

## 📋 Checklist Final

- [ ] Repositório GitHub atualizado
- [ ] Variáveis de ambiente configuradas
- [ ] PostgreSQL addon criado
- [ ] Redis addon criado
- [ ] Deploy realizado com sucesso
- [ ] Health check funcionando
- [ ] API respondendo
- [ ] Swagger acessível
- [ ] Logs sem erros críticos

## 🎉 Sucesso!

Após completar estes passos, sua JusCash API estará rodando no Railway com:

- ✅ API REST completa
- ✅ Banco PostgreSQL
- ✅ Cache Redis
- ✅ Tarefas agendadas
- ✅ Documentação Swagger
- ✅ Monitoramento
- ✅ Deploy automático

**URL da sua API**: `https://seu-app.up.railway.app` 🚀 