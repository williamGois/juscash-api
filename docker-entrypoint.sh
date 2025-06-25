#!/bin/bash

# Script de inicialização para o container da API JusCash

set -e

echo "🚀 Iniciando JusCash API..."

# Verificar e gerar SECRET_KEY se não existir
if [ -z "$SECRET_KEY" ]; then
    echo "🔐 SECRET_KEY não encontrada, gerando automaticamente..."
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
    echo "✅ SECRET_KEY gerada: ${SECRET_KEY:0:20}..."
    
    # Adicionar ao .env se existir
    if [ -f ".env" ]; then
        if ! grep -q "SECRET_KEY=" .env; then
            echo "SECRET_KEY=${SECRET_KEY}" >> .env
            echo "📝 SECRET_KEY adicionada ao .env"
        fi
    fi
else
    echo "✅ SECRET_KEY encontrada: ${SECRET_KEY:0:20}..."
fi

# Aguardar PostgreSQL estar disponível
echo "⏳ Aguardando PostgreSQL..."
while ! python3 -c "
import psycopg2
import sys
try:
    conn = psycopg2.connect(host='db', port=5432, user='juscash', password='juscash123', database='juscash', connect_timeout=5)
    conn.close()
    print('PostgreSQL conectado!')
    sys.exit(0)
except:
    sys.exit(1)
" 2>/dev/null; do
  echo "PostgreSQL não está pronto - aguardando..."
  sleep 2
done

echo "✅ PostgreSQL conectado!"

# Aguardar Redis estar disponível
echo "⏳ Aguardando Redis..."
while ! python3 -c "
import redis
import sys
try:
    r = redis.Redis(host='redis', port=6379, socket_connect_timeout=5)
    r.ping()
    print('Redis conectado!')
    sys.exit(0)
except:
    sys.exit(1)
" 2>/dev/null; do
  echo "Redis não está pronto - aguardando..."
  sleep 2
done

echo "✅ Redis conectado!"

# Executar migrações do banco de dados
echo "🔧 Executando migrações do banco de dados..."

# Verificar se já existe repositório de migrações
if [ ! -d "migrations" ]; then
    echo "📁 Inicializando repositório de migrações..."
    flask init-migrations
fi

# Verificar se há migrações para aplicar
echo "⬆️ Aplicando migrações..."
flask upgrade-db

echo "🎉 Tudo pronto! Iniciando aplicação..."

# Executar aplicação
exec "$@" 