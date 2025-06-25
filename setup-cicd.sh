#!/bin/bash

echo "🔧 Setup CI/CD - JusCash API"
echo "=============================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

VPS_HOST="77.37.68.178"
VPS_USER="root"
PROJECT_PATH="/var/www/juscash"

echo ""
echo -e "${BLUE}📋 Este script vai configurar:${NC}"
echo "1. ✅ Chave SSH para deploy automático"
echo "2. ✅ Configurar Git no servidor"
echo "3. ✅ Preparar ambiente para CI/CD"
echo "4. ✅ Gerar secrets para GitHub Actions"
echo ""
read -p "Continuar? (Enter para sim, Ctrl+C para cancelar): "

echo ""
echo -e "${YELLOW}🔐 PASSO 1: Gerando chave SSH para CI/CD...${NC}"

# Verificar se já existe chave SSH
if [ ! -f ~/.ssh/juscash_cicd ]; then
    echo "Gerando nova chave SSH..."
    ssh-keygen -t ed25519 -f ~/.ssh/juscash_cicd -N "" -C "juscash-cicd@github-actions"
    echo -e "${GREEN}✅ Chave SSH gerada em ~/.ssh/juscash_cicd${NC}"
else
    echo -e "${YELLOW}⚠️  Chave SSH já existe em ~/.ssh/juscash_cicd${NC}"
fi

echo ""
echo -e "${YELLOW}🔧 PASSO 2: Configurando servidor para CI/CD...${NC}"

# Enviar chave pública para o servidor
echo "Enviando chave pública para o servidor..."
ssh-copy-id -i ~/.ssh/juscash_cicd.pub $VPS_USER@$VPS_HOST

# Configurar Git no servidor
ssh $VPS_USER@$VPS_HOST << 'EOF'
echo "🔧 Configurando Git no servidor..."

cd /var/www/juscash

# Configurar Git
git config --global user.name "CI/CD Deploy"
git config --global user.email "cicd@juscash.app"
git config --global init.defaultBranch main

# Verificar se é um repositório Git
if [ ! -d .git ]; then
    echo "❌ Não é um repositório Git. Inicializando..."
    git init
    git remote add origin https://github.com/USERNAME/juscash-api.git  # VOCÊ PRECISA AJUSTAR ISSO
    git branch -M main
else
    echo "✅ Repositório Git já configurado"
fi

# Configurar permissões
chown -R root:root /var/www/juscash
chmod -R 755 /var/www/juscash

# Instalar GitHub CLI (opcional)
if ! command -v gh &> /dev/null; then
    echo "📦 Instalando GitHub CLI..."
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
    chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    apt update
    apt install -y gh
fi

echo "✅ Servidor configurado para CI/CD!"
EOF

echo ""
echo -e "${YELLOW}📋 PASSO 3: Gerando informações para GitHub Secrets...${NC}"

echo ""
echo -e "${BLUE}🔐 GITHUB SECRETS NECESSÁRIOS:${NC}"
echo ""
echo -e "${GREEN}SSH_PRIVATE_KEY:${NC}"
echo "=================="
cat ~/.ssh/juscash_cicd
echo ""
echo "=================="

echo ""
echo -e "${GREEN}VPS_HOST:${NC}"
echo "$VPS_HOST"

echo ""
echo -e "${GREEN}VPS_USER:${NC}"
echo "$VPS_USER"

echo ""
echo -e "${YELLOW}📱 PASSO 4: Configurando webhook Discord (opcional)...${NC}"
read -p "Quer configurar notificações Discord? (y/n): " configure_discord

if [[ $configure_discord =~ ^[Yy]$ ]]; then
    echo ""
    echo "Para configurar Discord:"
    echo "1. Vá no seu servidor Discord"
    echo "2. Settings → Integrations → Webhooks"
    echo "3. Create Webhook"
    echo "4. Copy Webhook URL"
    echo ""
    read -p "Cole a URL do webhook aqui: " discord_webhook
    echo ""
    echo -e "${GREEN}DISCORD_WEBHOOK:${NC}"
    echo "$discord_webhook"
else
    echo "Discord webhook ignorado."
fi

echo ""
echo -e "${BLUE}🎯 PRÓXIMOS PASSOS:${NC}"
echo ""
echo "1. 📁 Vá para seu repositório GitHub"
echo "2. ⚙️  Settings → Secrets and variables → Actions"
echo "3. 🔐 Adicione os seguintes Repository Secrets:"
echo ""
echo "   📝 SSH_PRIVATE_KEY = (conteúdo da chave privada acima)"
echo "   📝 VPS_HOST = $VPS_HOST"
echo "   📝 VPS_USER = $VPS_USER"
if [[ $configure_discord =~ ^[Yy]$ ]]; then
    echo "   📝 DISCORD_WEBHOOK = $discord_webhook"
fi
echo ""
echo "4. 🔄 Faça um commit e push para testar:"
echo "   git add ."
echo "   git commit -m \"feat: configure CI/CD\""
echo "   git push origin main"
echo ""
echo "5. 👀 Monitore em: GitHub → Actions"
echo "6. 🌐 Acesse: https://cron.juscash.app após deploy"

echo ""
echo -e "${GREEN}✅ CONFIGURAÇÃO CI/CD CONCLUÍDA!${NC}"

# Salvar informações em arquivo
cat > cicd-secrets.txt << EOF
# GitHub Secrets para CI/CD - JusCash API
# Adicione estes secrets no GitHub: Settings → Secrets and variables → Actions

SSH_PRIVATE_KEY:
$(cat ~/.ssh/juscash_cicd)

VPS_HOST: $VPS_HOST
VPS_USER: $VPS_USER
$(if [[ $configure_discord =~ ^[Yy]$ ]]; then echo "DISCORD_WEBHOOK: $discord_webhook"; fi)

# Como usar:
# 1. Copie cada valor acima
# 2. Adicione como Repository Secret no GitHub
# 3. Faça um push para testar o CI/CD

# URLs importantes:
# - Repositório: https://github.com/USERNAME/juscash-api
# - Actions: https://github.com/USERNAME/juscash-api/actions
# - Produção: https://cron.juscash.app
EOF

echo ""
echo -e "${BLUE}💾 Secrets salvos em: cicd-secrets.txt${NC}"
echo -e "${YELLOW}⚠️  IMPORTANTE: Mantenha este arquivo seguro e delete após configurar!${NC}" 