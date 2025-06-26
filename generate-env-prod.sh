#!/bin/bash

echo "🔐 Gerando configuração segura para JusCash API"
echo "==============================================="

# Verificar se já existe .env
if [ -f ".env" ]; then
    echo "⚠️  Arquivo .env já existe!"
    read -p "Deseja sobrescrever? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Operação cancelada."
        exit 1
    fi
fi

# Gerar senhas seguras
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
POSTGRES_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
FLOWER_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")

# Criar arquivo .env
cat > .env << EOF
# ================================================================================
# JUSCASH API - Configuração de Produção
# Gerado automaticamente em $(date)
# ================================================================================

# Aplicação
PRODUCTION=true
FLASK_ENV=production
SECRET_KEY=${SECRET_KEY}

# PostgreSQL - Credenciais seguras
POSTGRES_DB=juscash_db
POSTGRES_USER=juscash
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# URLs de conexão
DATABASE_URL=postgresql://juscash:${POSTGRES_PASSWORD}@db:5432/juscash_db
REDIS_URL=redis://redis:6379/0

# Configurações da aplicação
DJE_BASE_URL=https://dje.tjsp.jus.br/cdje
SCRAPING_ENABLED=true

# Flower (Celery Monitoring)
FLOWER_USER=admin
FLOWER_PASSWORD=${FLOWER_PASSWORD}

# ================================================================================
# IMPORTANTE: 
# - Este arquivo contém credenciais sensíveis
# - NUNCA comite este arquivo no Git
# - Mantenha backup seguro das senhas
# ================================================================================
EOF

echo "✅ Arquivo .env criado com credenciais seguras!"
echo ""
echo "🔒 Credenciais geradas:"
echo "SECRET_KEY: ${SECRET_KEY:0:20}..."
echo "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:0:10}..."
echo "FLOWER_PASSWORD: ${FLOWER_PASSWORD:0:8}..."
echo ""
echo "⚠️  IMPORTANTE:"
echo "   - Backup seguro das senhas"
echo "   - Arquivo .env NÃO será commitado no Git"
echo "   - Use na VPS: ./generate-env-prod.sh" 