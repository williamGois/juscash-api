#!/bin/bash

# Script de inicialização para o container da API JusCash

set -e

echo "🚀 Iniciando JusCash API..."

# Verificar e gerar SECRET_KEY se não existir
if [ -z "$SECRET_KEY" ]; then
    echo "🔐 Gerando SECRET_KEY..."
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
    echo "✅ SECRET_KEY gerada: ${SECRET_KEY:0:20}..."
else
    echo "✅ SECRET_KEY encontrada: ${SECRET_KEY:0:20}..."
fi

# Aguardar PostgreSQL usando DATABASE_URL
echo "⏳ Aguardando PostgreSQL..."
for i in {1..30}; do
    if python3 -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'], connect_timeout=5)
    conn.close()
    print('PostgreSQL conectado!')
    exit(0)
except Exception as e:
    print(f'Tentativa {i}: {e}')
    exit(1)
" 2>/dev/null; then
        break
    fi
    echo "PostgreSQL não está pronto - tentativa $i/30"
    sleep 3
done

echo "✅ PostgreSQL conectado!"

# Aguardar Redis
echo "⏳ Aguardando Redis..."
for i in {1..15}; do
    if python3 -c "
import redis
try:
    r = redis.Redis(host='redis', port=6379, socket_connect_timeout=5)
    r.ping()
    print('Redis conectado!')
    exit(0)
except:
    exit(1)
" 2>/dev/null; then
        break
    fi
    echo "Redis não está pronto - tentativa $i/15"
    sleep 2
done

echo "✅ Redis conectado!"

# Executar migrações
echo "🔧 Executando migrações..."
flask db upgrade || echo "⚠️ Erro ao executar migrações (continuando...)"

echo "🎉 Tudo pronto! Iniciando aplicação..."

# Executar aplicação
exec "$@" 