#!/bin/bash

echo "🔐 Gerando configuração de produção para JusCash API"
echo "=================================================="

# Gerar senhas seguras
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
POSTGRES_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
REDIS_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Criar arquivo .env
cat > .env << EOF
# Configuração de Produção - JusCash API
# Gerado automaticamente em $(date)

# Aplicação
PRODUCTION=true
FLASK_ENV=production
SECRET_KEY=${SECRET_KEY}

# PostgreSQL
POSTGRES_DB=juscash_db
POSTGRES_USER=juscash
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# Redis
REDIS_PASSWORD=${REDIS_PASSWORD}

# URLs de conexão (geradas automaticamente pelo Docker)
DATABASE_URL=postgresql://juscash:${POSTGRES_PASSWORD}@db:5432/juscash_db
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# Configurações da aplicação
DJE_BASE_URL=https://dje.tjsp.jus.br/cdje
SCRAPING_ENABLED=true

# Agendamentos (em segundos)
DAILY_SCRAPING_SCHEDULE=3600
WEEKLY_SCRAPING_SCHEDULE=604800
CLEANUP_SCHEDULE=86400

# Banco de dados
DB_POOL_SIZE=10
DB_POOL_RECYCLE=300
EOF

echo "✅ Arquivo .env criado com senhas seguras!"
echo ""
echo "🔒 Senhas geradas:"
echo "SECRET_KEY: ${SECRET_KEY:0:20}..."
echo "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:0:10}..."
echo "REDIS_PASSWORD: ${REDIS_PASSWORD:0:10}..."
echo ""
echo "⚠️  IMPORTANTE: Mantenha essas senhas seguras!" 