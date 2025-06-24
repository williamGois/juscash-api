# 🚂 Guia Rápido - Setup Railway

## 🔐 1. Gerar SECRET_KEY

```bash
# Execute este comando:
python generate_secret_key.py

# Ou direto:
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## 🚀 2. Configurar no Railway

### Criar Projeto
1. [Railway.app](https://railway.app) → "New Project"
2. "Deploy from GitHub repo"
3. Selecione seu repositório

### Adicionar PostgreSQL
1. Dashboard → "New +"
2. "Database" → "PostgreSQL"
3. Aguarde criação (auto-gera DATABASE_URL)

### Adicionar Redis
1. "New +" → "Database" → "Redis"  
2. Aguarde criação (auto-gera REDIS_URL)

### Configurar Variáveis
Dashboard → Variables → Add:

```env
SECRET_KEY=sua-chave-gerada-aqui
FLASK_ENV=production
RAILWAY_ENVIRONMENT=true
SCRAPING_ENABLED=true
DAILY_SCRAPING_SCHEDULE=3600
WEEKLY_SCRAPING_SCHEDULE=604800
CLEANUP_SCHEDULE=86400
DB_POOL_SIZE=2
DB_POOL_RECYCLE=300
```

## ✅ 3. Deploy

Railway fará deploy automático após:
- Adicionar variáveis
- PostgreSQL e Redis estarem prontos
- Aguarde 5-10 minutos

## 🧪 4. Testar

```bash
# Health check
curl https://seu-app.up.railway.app/api/cron/health

# Swagger
https://seu-app.up.railway.app/docs/

# Executar raspagem
curl -X POST https://seu-app.up.railway.app/api/cron/scraping/daily
```

## 🚨 Troubleshooting

### Build Failed
- Verifique se todas as variáveis estão configuradas
- PostgreSQL e Redis devem estar "Active"

### App Crashes
- Ver logs: Dashboard → Deployments → View Logs
- Procurar por "SECRET_KEY", "DATABASE_URL", "REDIS_URL"

### Selenium Error
- Normal na primeira execução
- Railway instala Chrome automaticamente
- Aguarde alguns minutos

## 📋 Checklist Final

- [ ] SECRET_KEY configurada
- [ ] PostgreSQL addon ativo
- [ ] Redis addon ativo
- [ ] Todas as variáveis definidas
- [ ] Deploy concluído com sucesso
- [ ] Health check retornando 200
- [ ] Swagger acessível

**🎉 Sucesso! Sua API está no ar!** 