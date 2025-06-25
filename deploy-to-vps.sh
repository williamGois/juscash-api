#!/bin/bash

VPS_IP="77.37.68.178"
VPS_USER="root"
PROJECT_DIR="/var/www/juscash"
DOMAIN="cron.juscash.app"

echo "🚀 Deploy JusCash API para VPS Hostinger"
echo "========================================"

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Erro: Execute este script na raiz do projeto JusCash"
    exit 1
fi

echo "📦 Preparando arquivos para upload..."

# Criar arquivo temporário com lista de arquivos essenciais
cat > files_to_upload.txt << EOF
app/
migrations/
tests/
examples/
logs/
*.py
*.txt
*.yml
*.yaml
*.ini
*.md
Dockerfile*
Procfile*
docker-compose*
setup-vps.sh
generate-env-prod.sh
EOF

echo "📤 Fazendo upload dos arquivos para o servidor..."

# Criar diretório no servidor
ssh ${VPS_USER}@${VPS_IP} "mkdir -p ${PROJECT_DIR}"

# Upload dos arquivos usando rsync
rsync -avz --progress \
    --include-from=files_to_upload.txt \
    --exclude='*' \
    ./ ${VPS_USER}@${VPS_IP}:${PROJECT_DIR}/

echo "🔧 Configurando ambiente no servidor..."

# Executar comandos no servidor
ssh ${VPS_USER}@${VPS_IP} << REMOTE_COMMANDS

cd ${PROJECT_DIR}

# Gerar variáveis de ambiente
echo "🔐 Gerando configuração de produção..."
chmod +x generate-env-prod.sh
./generate-env-prod.sh

# Usar docker-compose de produção
echo "🐳 Configurando Docker Compose..."
cp docker-compose.prod.yml docker-compose.yml

# Criar diretórios necessários
mkdir -p logs

# Build e start dos containers
echo "🏗️  Fazendo build da aplicação..."
docker-compose build

echo "🚀 Iniciando serviços..."
docker-compose up -d

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

# Verificar status dos containers
echo "📊 Status dos containers:"
docker-compose ps

# Executar migrações do banco
echo "🗄️  Executando migrações do banco..."
docker-compose exec -T web python create-tables.py

# Verificar saúde da aplicação
echo "🏥 Verificando saúde da aplicação..."
curl -f http://localhost:5000/api/cron/health || echo "⚠️  Aplicação ainda não está respondendo"

REMOTE_COMMANDS

echo ""
echo "✅ Deploy básico concluído!"
echo ""
echo "🔧 Próximos passos manuais:"
echo "1. Configurar DNS do domínio ${DOMAIN} para ${VPS_IP}"
echo "2. Aguardar propagação DNS (pode levar até 24h)"
echo "3. Configurar SSL: ssh ${VPS_USER}@${VPS_IP} 'certbot --nginx -d ${DOMAIN}'"
echo ""
echo "🌐 URLs após configuração:"
echo "- API: https://${DOMAIN}"
echo "- Swagger: https://${DOMAIN}/docs/"
echo "- Flower (Celery): https://${DOMAIN}/flower"
echo ""
echo "🔍 Comandos úteis:"
echo "- Ver logs: ssh ${VPS_USER}@${VPS_IP} 'cd ${PROJECT_DIR} && docker-compose logs'"
echo "- Restart: ssh ${VPS_USER}@${VPS_IP} 'cd ${PROJECT_DIR} && docker-compose restart'"
echo "- Status: ssh ${VPS_USER}@${VPS_IP} 'cd ${PROJECT_DIR} && docker-compose ps'"

# Limpar arquivo temporário
rm -f files_to_upload.txt 