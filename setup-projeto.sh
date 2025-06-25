#!/bin/bash

echo "⚙️  Configurando Projeto JusCash API"
echo "=================================="

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Erro: Execute este script no diretório do projeto clonado!"
    exit 1
fi

echo "🔐 Gerando configuração de ambiente..."

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

# URLs de conexão
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

echo "🐳 Configurando Docker Compose..."
cp docker-compose.prod.yml docker-compose.yml

echo "📁 Criando diretórios necessários..."
mkdir -p logs

echo "🏗️  Fazendo build da aplicação..."
docker-compose build

echo "🚀 Iniciando serviços..."
docker-compose up -d

echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

echo "📊 Status dos containers:"
docker-compose ps

echo "🗄️  Executando migrações do banco..."
docker-compose exec -T web python create-tables.py

echo "🏥 Verificando saúde da aplicação..."
sleep 10
curl -f http://localhost:5000/api/cron/health || echo "⚠️  Aplicação ainda não está respondendo (normal nos primeiros minutos)"

echo ""
echo "✅ Projeto configurado com sucesso!"
echo ""
echo "🔒 Credenciais geradas:"
echo "SECRET_KEY: ${SECRET_KEY:0:20}..."
echo "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:0:10}..."
echo "REDIS_PASSWORD: ${REDIS_PASSWORD:0:10}..."
echo ""
echo "🌐 URLs da aplicação (após configurar SSL):"
echo "- API: https://cron.juscash.app"
echo "- Swagger: https://cron.juscash.app/docs/"
echo "- Flower: https://cron.juscash.app/flower"
echo ""
echo "🔧 Próximos passos:"
echo "1. Configure DNS: cron.juscash.app → 77.37.68.178"
echo "2. Configure SSL: certbot --nginx -d cron.juscash.app"
echo ""
echo "📋 Comandos úteis:"
echo "- Ver logs: docker-compose logs -f web"
echo "- Restart: docker-compose restart"
echo "- Status: docker-compose ps" 