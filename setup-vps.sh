#!/bin/bash

echo "🚀 Configuração Completa VPS Hostinger - JusCash API"
echo "=================================================="

# Atualizar sistema
echo "📦 Atualizando sistema Ubuntu..."
apt update && apt upgrade -y

# Instalar dependências básicas
echo "🔧 Instalando dependências básicas..."
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
    lsb-release

# Instalar Docker
echo "🐳 Instalando Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Instalar Docker Compose standalone
echo "📝 Instalando Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Iniciar Docker
systemctl start docker
systemctl enable docker

# Configurar firewall
echo "🔥 Configurando firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

# Criar diretório do projeto
echo "📁 Criando estrutura de diretórios..."
mkdir -p /var/www/juscash
cd /var/www/juscash

# Clonar projeto (se não existir)
if [ ! -d ".git" ]; then
    echo "📥 Clonando projeto..."
    # Como não temos um repositório remoto, vamos criar a estrutura
    git init
    echo "# JusCash API" > README.md
    git add README.md
    git config user.email "deploy@juscash.app"
    git config user.name "Deploy Script"
    git commit -m "Initial commit"
fi

# Configurar Nginx
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

# Testar configuração Nginx
nginx -t
systemctl restart nginx
systemctl enable nginx

echo "✅ Configuração básica concluída!"
echo ""
echo "🔧 Próximos passos:"
echo "1. Configurar DNS do domínio cron.juscash.app para 77.37.68.5"
echo "2. Executar: certbot --nginx -d cron.juscash.app"
echo "3. Fazer upload dos arquivos do projeto"
echo "4. Configurar variáveis de ambiente"
echo "5. Executar docker-compose up -d"
echo ""
echo "📝 Logs importantes:"
echo "- Nginx: /var/log/nginx/"
echo "- Docker: docker logs <container>"
echo "- Sistema: /var/log/syslog" 