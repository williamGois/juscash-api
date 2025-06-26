#!/bin/bash

# Script de configuração automática do ambiente JusCash API
# Gera SECRET_KEY automaticamente e cria arquivo .env se não existir

set -e

echo "🔧 Configurando ambiente JusCash API..."

# Função para gerar SECRET_KEY
generate_secret_key() {
    python3 -c "import secrets; print(secrets.token_urlsafe(64))"
}

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env..."
    
    # Gerar SECRET_KEY automaticamente
    SECRET_KEY=$(generate_secret_key)
    
    # Criar arquivo .env
    cat > .env << EOF
# Configurações da aplicação
SECRET_KEY=${SECRET_KEY}
FLASK_ENV=development

# Banco de dados PostgreSQL
DATABASE_URL=postgresql://juscash:juscash123@localhost:5432/juscash_db

# Redis para Celery
REDIS_URL=redis://localhost:6379/0

# Configurações do DJE
DJE_BASE_URL=https://dje.tjsp.jus.br/cdje

# Configurações Docker (para docker-compose)
POSTGRES_DB=juscash_db
POSTGRES_USER=juscash
POSTGRES_PASSWORD=juscash123
EOF

    echo "✅ Arquivo .env criado com SECRET_KEY gerada automaticamente!"
    echo "🔐 SECRET_KEY: ${SECRET_KEY}"
    
else
    echo "📄 Arquivo .env já existe."
    
    # Verificar se SECRET_KEY existe no .env
    if ! grep -q "SECRET_KEY=" .env; then
        echo "🔐 Adicionando SECRET_KEY ao .env existente..."
        SECRET_KEY=$(generate_secret_key)
        echo "SECRET_KEY=${SECRET_KEY}" >> .env
        echo "✅ SECRET_KEY adicionada!"
        echo "🔐 SECRET_KEY: ${SECRET_KEY}"
    else
        echo "✅ SECRET_KEY já configurada no .env"
    fi
fi

echo ""
echo "🚀 Configuração concluída!"
echo "📋 Para usar:"
echo "   Desenvolvimento local: python run.py"
echo "   Docker:               docker-compose up --build"
echo ""