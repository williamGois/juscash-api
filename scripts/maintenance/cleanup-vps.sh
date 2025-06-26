#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                🧹 LIMPEZA COMPLETA DA VPS                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"

cd /var/www/juscash

echo "🛑 Parando containers..."
docker-compose down --remove-orphans || true

echo "🧹 Limpando arquivos de backup..."
rm -f backup_*.sql
rm -rf backups/
rm -f celerybeat-schedule
rm -f *.pid

echo "🧹 Limpando logs de deploy..."
rm -f deploy_*.log

echo "🧹 Limpando arquivos temporários..."
rm -f VERSION
rm -f .deploy-test
rm -f .trigger_deploy
rm -f .railway-deploy

echo "📦 Fazendo stash de mudanças locais..."
git stash push -m "Cleanup stash $(date)" --include-untracked || echo "⚠️ Nada para fazer stash"

echo "🗑️ Removendo arquivos não rastreados..."
git clean -fd

echo "🔄 Atualizando código..."
git fetch origin
git reset --hard origin/master

echo "🔍 Estado final:"
git status

echo "✅ Limpeza concluída! VPS pronta para deploy."
echo "🚀 Para iniciar containers: docker-compose up -d" 