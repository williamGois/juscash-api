#!/bin/bash

echo "🚀 DEPLOY MANUAL - QUANDO CI/CD FALHAR"
echo "====================================="

LAST_COMMIT=$(git log --oneline -1 | awk '{print $1}')
echo "📋 Último commit local: $LAST_COMMIT"

echo -e "\n🔧 Aplicando mudança manualmente na VPS..."
ssh -i ~/.ssh/juscash_cicd root@77.37.68.178 << EOF
cd /var/www/juscash

echo "📥 Atualizando código..."
git stash || true
git clean -fd
git fetch origin
git reset --hard origin/master

echo "✅ Commit atual: \$(git log --oneline -1)"

echo "🔒 Corrigindo permissões..."
chmod +x docker-entrypoint.sh

echo "🔄 Restart containers..."
docker-compose restart web worker

echo "⏳ Aguardando restart..."
sleep 15

echo "🧪 Testando API:"
curl -s http://localhost:5000/api/simple/ping

echo -e "\n✅ Deploy manual concluído!"
EOF

echo -e "\n✅ USE ESTE SCRIPT quando o CI/CD não funcionar:"
echo "chmod +x deploy-manual-fix.sh && ./deploy-manual-fix.sh" 