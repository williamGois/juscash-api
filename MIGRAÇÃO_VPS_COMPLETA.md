# 🚀 Migração Completa para VPS Hostinger

## 🚨 PROBLEMA ATUAL - CORREÇÃO URGENTE

### Erro Identificado
```
FATAL: password authentication failed for user "juscash"
```

**Causa:** Deploy usando `docker-compose.yml` ao invés de `docker-compose.vps.yml`

## 🔧 CORREÇÃO IMEDIATA

### 1. Conectar no VPS
```bash
ssh root@srv525028.hstgr.cloud
```

### 2. Ir para diretório da aplicação
```bash
cd /opt/juscash/app
```

### 3. Parar containers atuais
```bash
docker-compose down
docker system prune -f
```

### 4. Verificar arquivos necessários
```bash
ls -la docker-compose.vps.yml
ls -la env.vps
```

### 5. Deploy correto
```bash
# Usar o arquivo específico para VPS
docker-compose -f docker-compose.vps.yml --env-file env.vps up -d --build
```

### 6. Verificar status
```bash
# Status dos containers
docker-compose -f docker-compose.vps.yml ps

# Logs do web
docker-compose -f docker-compose.vps.yml logs -f web

# Logs do banco
docker-compose -f docker-compose.vps.yml logs postgres
```

## 📋 Configurações Corretas

### docker-compose.vps.yml ✅
- **Usuário PostgreSQL:** `juscash_user` (não `juscash`)
- **Banco:** `juscash_db`
- **Containers:** `juscash_postgres`, `juscash_web`, etc.

### env.vps ✅ (Configurado)
```env
SECRET_KEY=juscash_2025_super_secret_key_vps_production_789456123
DB_PASSWORD=juscash_db_password_2025
REDIS_PASSWORD=juscash_redis_password_2025
DATABASE_URL=postgresql://juscash_user:juscash_db_password_2025@postgres:5432/juscash_db
```

## 🔍 Verificação Final

### Teste de Conectividade
```bash
# Teste local
curl http://localhost:5000/api/health

# Teste externo
curl http://srv525028.hstgr.cloud:5000/api/health
```

### Logs Detalhados
```bash
# Todos os containers
docker-compose -f docker-compose.vps.yml logs

# Apenas web
docker-compose -f docker-compose.vps.yml logs web

# Apenas postgres
docker-compose -f docker-compose.vps.yml logs postgres
```

## 🚀 Deploy Automatizado (Para próximas vezes)

### Script de Deploy Correto
```bash
#!/bin/bash
cd /opt/juscash/app

# Parar containers
docker-compose -f docker-compose.vps.yml down

# Atualizar código
git pull origin master

# Deploy com arquivo correto
docker-compose -f docker-compose.vps.yml --env-file env.vps up -d --build

# Verificar
docker-compose -f docker-compose.vps.yml ps
```

## ⚠️ REGRAS IMPORTANTES

1. **SEMPRE usar:** `docker-compose -f docker-compose.vps.yml`
2. **SEMPRE usar:** `--env-file env.vps`
3. **NUNCA usar:** `docker-compose.yml` em produção
4. **Verificar logs** após cada deploy

## 🏆 Resultado Esperado

Após a correção, você deve ver:
```
NAME                  STATUS
juscash_postgres     Up (healthy)
juscash_redis        Up (healthy)
juscash_web          Up
juscash_worker       Up
juscash_beat         Up
juscash_flower       Up
```

E não mais erros de autenticação PostgreSQL. 