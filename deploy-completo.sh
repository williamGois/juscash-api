#!/bin/bash

echo "🚀 Deploy Completo JusCash API - VPS Hostinger"
echo "=============================================="

VPS_HOST="juscash-vps"  # Usando a configuração SSH que criamos
PROJECT_DIR="/var/www/juscash"

echo "📋 Este script vai:"
echo "1. ✅ Instalar Docker, Git e dependências no servidor"
echo "2. ✅ Fazer upload de todos os arquivos do projeto"
echo "3. ✅ Configurar Nginx e Firewall"
echo "4. ✅ Gerar configurações de ambiente seguras"
echo "5. ✅ Executar o projeto com Docker"
echo ""
read -p "Continuar? (Enter para sim, Ctrl+C para cancelar): "

echo ""
echo "🔧 PASSO 1: Configurando servidor e instalando dependências..."

# Instalar tudo no servidor
ssh $VPS_HOST << 'REMOTE_SETUP'

echo "🖥️  Atualizando sistema Ubuntu..."
apt update && apt upgrade -y

echo "📦 Instalando dependências básicas..."
apt install -y \
    curl \
    wget \
    git \
    ufw \
    nginx \
    certbot \
    python3-certbot-nginx \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    python3 \
    python3-pip

echo "🐳 Instalando Docker..."
# Remover versões antigas
apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null

# Adicionar chave GPG do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adicionar repositório
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Instalar Docker Compose standalone
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Iniciar e habilitar Docker
systemctl start docker
systemctl enable docker

echo "🔥 Configurando Firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

echo "🌐 Configurando Nginx..."
cat > /etc/nginx/sites-available/juscash << 'EOF'
server {
    listen 80;
    server_name cron.juscash.app;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /flower {
        proxy_pass http://localhost:5555;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        rewrite ^/flower/?(.*)$ /$1 break;
    }
}
EOF

# Ativar site
ln -sf /etc/nginx/sites-available/juscash /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Testar e reiniciar Nginx
nginx -t
systemctl restart nginx
systemctl enable nginx

echo "📁 Criando diretório do projeto..."
mkdir -p /var/www/juscash
cd /var/www/juscash

echo "✅ Servidor configurado com sucesso!"

REMOTE_SETUP

echo ""
echo "📤 PASSO 2: Fazendo upload dos arquivos do projeto..."

# Fazer upload de todos os arquivos essenciais
rsync -avz --progress \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='logs/*' \
    --exclude='*.log' \
    ./ $VPS_HOST:$PROJECT_DIR/

echo ""
echo "⚙️  PASSO 3: Configurando e executando projeto no servidor..."

# Configurar e executar projeto
ssh $VPS_HOST << REMOTE_PROJECT

cd $PROJECT_DIR

echo "🔐 Gerando configuração de ambiente segura..."

# Gerar senhas seguras
SECRET_KEY=\$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
POSTGRES_PASSWORD=\$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
REDIS_PASSWORD=\$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Criar arquivo .env
cat > .env << EOF
# Configuração de Produção - JusCash API
# Gerado automaticamente em \$(date)

# Aplicação
PRODUCTION=true
FLASK_ENV=production
SECRET_KEY=\${SECRET_KEY}

# PostgreSQL
POSTGRES_DB=juscash_db
POSTGRES_USER=juscash
POSTGRES_PASSWORD=\${POSTGRES_PASSWORD}

# Redis
REDIS_PASSWORD=\${REDIS_PASSWORD}

# URLs de conexão
DATABASE_URL=postgresql://juscash:\${POSTGRES_PASSWORD}@db:5432/juscash_db
REDIS_URL=redis://:\${REDIS_PASSWORD}@redis:6379/0

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

echo "🐳 Preparando Docker Compose..."
cp docker-compose.prod.yml docker-compose.yml

echo "📁 Criando diretórios necessários..."
mkdir -p logs

echo "🏗️  Fazendo build da aplicação..."
docker-compose build

echo "🚀 Iniciando serviços..."
docker-compose up -d

echo "⏳ Aguardando serviços ficarem prontos..."
sleep 45

echo "📊 Status dos containers:"
docker-compose ps

echo "🗄️  Executando migrações do banco..."
sleep 15
docker-compose exec -T web python create-tables.py

echo "🏥 Verificando saúde da aplicação..."
sleep 10
curl -f http://localhost:5000/api/cron/health

echo ""
echo "🔒 Credenciais geradas:"
echo "SECRET_KEY: \${SECRET_KEY:0:20}..."
echo "POSTGRES_PASSWORD: \${POSTGRES_PASSWORD:0:10}..."
echo "REDIS_PASSWORD: \${REDIS_PASSWORD:0:10}..."

REMOTE_PROJECT

echo ""
echo "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
echo "================================"
echo ""
echo "✅ Servidor configurado"
echo "✅ Docker instalado e rodando"
echo "✅ Projeto configurado e executando"
echo "✅ Nginx configurado"
echo "✅ Firewall configurado"
echo ""
echo "🌐 URLs da aplicação:"
echo "- API (HTTP): http://77.37.68.178"
echo "- Swagger: http://77.37.68.178/docs/"
echo "- Flower: http://77.37.68.178/flower"
echo ""
echo "🔧 Próximos passos:"
echo "1. 🌐 Configure DNS: cron.juscash.app → 77.37.68.178"
echo "2. 🔒 Configure SSL: ssh $VPS_HOST 'certbot --nginx -d cron.juscash.app'"
echo ""
echo "📋 Comandos úteis:"
echo "- Conectar: ssh $VPS_HOST"
echo "- Ver logs: ssh $VPS_HOST 'cd $PROJECT_DIR && docker-compose logs -f web'"
echo "- Restart: ssh $VPS_HOST 'cd $PROJECT_DIR && docker-compose restart'"
echo "- Status: ssh $VPS_HOST 'cd $PROJECT_DIR && docker-compose ps'"
echo ""
echo "🎯 URLs finais (após DNS + SSL):"
echo "- API: https://cron.juscash.app"
echo "- Swagger: https://cron.juscash.app/docs/"
echo "- Flower: https://cron.juscash.app/flower" 