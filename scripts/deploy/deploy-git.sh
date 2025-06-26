#!/bin/bash

echo "🚀 Deploy JusCash API via Git"
echo "============================"

# Configurações
REPO_URL="https://github.com/SEU_USUARIO/juscash-api.git"  # Substitua pelo seu repositório
PROJECT_DIR="/var/www/juscash"
DOMAIN="cron.juscash.app"

# Adicionar todos os arquivos ao Git
echo "📦 Preparando repositório Git..."
git add .
git commit -m "Deploy para VPS Hostinger - $(date '+%Y-%m-%d %H:%M:%S')" || echo "Nada para commitar"

echo "📤 Fazendo push para GitHub..."
echo "⚠️  IMPORTANTE: Configure seu repositório GitHub primeiro!"
echo "1. Crie um repositório em: https://github.com/new"
echo "2. Execute: git remote add origin URL_DO_REPOSITORIO"
echo "3. Execute: git push -u origin main"
echo ""
read -p "Pressione ENTER após configurar o repositório no GitHub..."

echo "🔧 Configurando servidor via SSH..."

# Executar comandos no servidor
ssh juscash-vps << 'REMOTE_COMMANDS'

echo "🖥️  Configurando servidor..."

# Atualizar sistema
apt update && apt upgrade -y

# Instalar dependências
apt install -y curl wget git ufw nginx certbot python3-certbot-nginx software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# Instalar Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Iniciar Docker
systemctl start docker
systemctl enable docker

# Configurar firewall
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

# Configurar Nginx
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
nginx -t
systemctl restart nginx
systemctl enable nginx

echo "✅ Servidor configurado! Agora clone o repositório..."

REMOTE_COMMANDS

echo ""
echo "🎯 Próximos passos:"
echo "1. ✅ SSH configurado (use: ssh juscash-vps)"
echo "2. ✅ Servidor básico configurado"
echo "3. 📋 Agora execute no servidor:"
echo ""
echo "   ssh juscash-vps"
echo "   cd /var/www"
echo "   git clone URL_DO_SEU_REPOSITORIO juscash"
echo "   cd juscash"
echo "   ./setup-projeto.sh"
echo ""
echo "4. 🌐 Configure DNS: cron.juscash.app → 77.37.68.178"
echo "5. 🔒 Configure SSL: certbot --nginx -d cron.juscash.app" 