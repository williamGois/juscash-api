#!/bin/bash

# Script simples de deploy para VPS
# Uso: ./simple-deploy.sh

set -e

echo "🚀 Iniciando deploy..."

cd /var/www/juscash

# 1. Backup do banco
echo "💾 Fazendo backup..."
docker-compose exec -T db pg_dump -U juscash juscash_db > /tmp/backup_$(date +%Y%m%d_%H%M%S).sql || true

# 2. Atualizar código
echo "📥 Atualizando código..."
git stash --include-untracked
git fetch origin
git reset --hard origin/master

# 3. Rebuild
echo "🔨 Reconstruindo containers..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 4. Migrações
echo "🗄️ Aplicando migrações..."
sleep 10
docker-compose exec -T web flask db upgrade || true

# 5. Verificar
echo "✅ Verificando..."
sleep 5
curl -f http://localhost:5000/api/simple/ping && echo "✅ Deploy concluído!" || echo "❌ Falha no deploy" 