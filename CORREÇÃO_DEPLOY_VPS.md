# 🚨 CORREÇÃO URGENTE - Deploy VPS Hostinger

## Problema Identificado
O deploy está usando `docker-compose.yml` ao invés de `docker-compose.vps.yml`, causando erro de autenticação no PostgreSQL.

## 🔧 Correção Imediata

### 1. Parar containers atuais
```bash
cd /opt/juscash/app
docker-compose down
```

### 2. Usar o arquivo correto
```bash
# Usar docker-compose.vps.yml com variáveis de ambiente corretas
docker-compose -f docker-compose.vps.yml --env-file env.vps up -d
```

### 3. Verificar status
```bash
docker-compose -f docker-compose.vps.yml ps
docker-compose -f docker-compose.vps.yml logs web
```

## 📋 Configurações Corrigidas

### Arquivo env.vps ✅
- Senhas configuradas com valores seguros
- Usuário PostgreSQL: `juscash_user` 
- Banco de dados: `juscash_db`

### docker-compose.vps.yml ✅
- Usuário correto: `juscash_user`
- Senhas via variáveis de ambiente
- Healthchecks configurados
- Volumes persistentes

## 🚀 Deploy Correto

```bash
# 1. Ir para o diretório da aplicação
cd /opt/juscash/app

# 2. Parar containers antigos
docker-compose down

# 3. Limpar containers antigos se necessário
docker system prune -f

# 4. Fazer deploy com arquivo correto
docker-compose -f docker-compose.vps.yml --env-file env.vps up -d --build

# 5. Verificar logs
docker-compose -f docker-compose.vps.yml logs -f web
```

## 🔍 Verificação Final

```bash
# Status dos containers
docker-compose -f docker-compose.vps.yml ps

# Logs do banco
docker-compose -f docker-compose.vps.yml logs postgres

# Teste de conectividade
curl http://localhost:5000/api/health
```

## ⚠️ Importante
- Sempre usar `-f docker-compose.vps.yml` no VPS
- Não usar `docker-compose.yml` em produção
- Arquivo `env.vps` com senhas seguras configuradas 