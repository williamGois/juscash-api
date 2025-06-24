#!/bin/bash

# Script de inicialização para o container da API JusCash

set -e

echo "🚀 Iniciando JusCash API..."

# Aguardar PostgreSQL estar disponível
echo "⏳ Aguardando PostgreSQL..."
while ! pg_isready -h db -p 5432 -U juscash; do
  echo "PostgreSQL não está pronto - aguardando..."
  sleep 2
done

echo "✅ PostgreSQL conectado!"

# Aguardar Redis estar disponível
echo "⏳ Aguardando Redis..."
while ! redis-cli -h redis ping > /dev/null 2>&1; do
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