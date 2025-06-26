#!/bin/bash

# 🚀 Deploy JusCash API - VPS Hostinger
# Ubuntu 20.04 LTS - São Paulo, Brasil

set -e

echo "🚀 Iniciando deploy da JusCash API no VPS Hostinger..."
echo "📍 Servidor: srv525028.hstgr.cloud (77.37.68.178)"
echo "🖥️  SO: Ubuntu 20.04 LTS"

# 1. Atualizar sistema
echo "📦 Atualizando sistema..."
apt update && apt upgrade -y

# 2. Instalar dependências básicas
echo "🔧 Instalando dependências básicas..."
apt install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# 3. Instalar Python 3.11
echo "🐍 Instalando Python 3.11..."
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.11 python3.11-pip python3.11-venv python3.11-dev

# Criar link simbólico para python
ln -sf /usr/bin/python3.11 /usr/bin/python3
ln -sf /usr/bin/python3.11 /usr/bin/python

# 4. Instalar Docker
echo "🐳 Instalando Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Iniciar Docker
systemctl start docker
systemctl enable docker

# 5. Instalar Docker Compose
echo "🔧 Instalando Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 6. Instalar PostgreSQL (via Docker)
echo "🐘 Configurando PostgreSQL..."
mkdir -p /opt/juscash/postgres-data

# 7. Instalar Redis (via Docker)
echo "📦 Configurando Redis..."
mkdir -p /opt/juscash/redis-data

# 8. Configurar Nginx
echo "🌐 Instalando e configurando Nginx..."
apt install -y nginx
systemctl start nginx
systemctl enable nginx

# 9. Configurar firewall
echo "🔥 Configurando firewall..."
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5000/tcp  # Flask (temporário para testes)
ufw allow 5555/tcp  # Flower (temporário para testes)
ufw --force enable

# 10. Criar estrutura de diretórios
echo "📁 Criando estrutura de diretórios..."
mkdir -p /opt/juscash/{app,logs,backups,ssl}
cd /opt/juscash

# 11. Clonar código (será feito manualmente)
echo "📥 Preparando para receber código da aplicação..."
echo "⚠️  Execute manualmente: git clone <repo-url> app"

# 12. Configurar SSL (Let's Encrypt)
echo "🔒 Instalando Certbot para SSL..."
apt install -y snapd
snap install --classic certbot
ln -s /snap/bin/certbot /usr/bin/certbot

echo "✅ Setup básico do VPS concluído!"
echo ""
echo "📋 Próximos passos manuais:"
echo "1. git clone do repositório em /opt/juscash/app"
echo "2. Configurar variáveis de ambiente"
echo "3. Executar docker-compose up"
echo "4. Configurar SSL com certbot"
echo ""
echo "🎯 Servidor pronto para receber a aplicação!" 