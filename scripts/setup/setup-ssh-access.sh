#!/bin/bash

echo "=== CONFIGURAÇÃO SSH PARA VPS JUSCASH ==="
echo "Data: $(date)"
echo

# Configurações do VPS
VPS_HOST="77.37.68.178"
VPS_USER="root"
VPS_PASSWORD="Syberya1989@@"
VPS_PROJECT_DIR="/var/www/juscash"

echo "🔧 Configurando acesso SSH para o VPS JusCash"
echo "📡 Host: $VPS_HOST"
echo "👤 Usuário: $VPS_USER"
echo "📁 Diretório do projeto: $VPS_PROJECT_DIR"
echo

# Verificar se o SSH está instalado
if ! command -v ssh &> /dev/null; then
    echo "❌ SSH não está instalado"
    echo "Instale com: sudo apt-get install openssh-client"
    exit 1
fi

if ! command -v sshpass &> /dev/null; then
    echo "📦 Instalando sshpass para autenticação por senha..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install hudochenkov/sshpass/sshpass
        else
            echo "❌ Homebrew não encontrado. Instale manualmente o sshpass"
            echo "Ou use: ssh root@$VPS_HOST e digite a senha manualmente"
        fi
    else
        # Linux
        sudo apt-get update && sudo apt-get install -y sshpass
    fi
fi

# Função para executar comandos SSH
ssh_exec() {
    local command="$1"
    echo "🔄 Executando: $command"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$command"
}

# Função para conectar via SSH
ssh_connect() {
    echo "🔗 Conectando ao VPS..."
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST"
}

# Testar conectividade
echo "🔍 Testando conectividade com o VPS..."
if ping -c 1 "$VPS_HOST" > /dev/null 2>&1; then
    echo "✅ VPS acessível"
else
    echo "❌ VPS não acessível - verifique a conexão"
    exit 1
fi

# Testar SSH
echo "🔐 Testando acesso SSH..."
if sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$VPS_USER@$VPS_HOST" "echo 'SSH OK'" 2>/dev/null; then
    echo "✅ Acesso SSH funcionando"
else
    echo "❌ Erro no acesso SSH - verifique credenciais"
    exit 1
fi

# Verificar diretório do projeto
echo "📁 Verificando diretório do projeto..."
if ssh_exec "[ -d '$VPS_PROJECT_DIR' ]"; then
    echo "✅ Diretório $VPS_PROJECT_DIR existe"
    
    # Listar conteúdo
    echo "📋 Conteúdo do diretório:"
    ssh_exec "ls -la $VPS_PROJECT_DIR"
else
    echo "❌ Diretório $VPS_PROJECT_DIR não existe"
    echo "🔧 Criando diretório..."
    ssh_exec "mkdir -p $VPS_PROJECT_DIR"
    echo "✅ Diretório criado"
fi

# Verificar se é um repositório git
echo "🔍 Verificando repositório git..."
if ssh_exec "[ -d '$VPS_PROJECT_DIR/.git' ]"; then
    echo "✅ Repositório git encontrado"
    
    # Verificar status
    echo "📊 Status do repositório:"
    ssh_exec "cd $VPS_PROJECT_DIR && git status --porcelain"
    
    # Verificar branch
    CURRENT_BRANCH=$(ssh_exec "cd $VPS_PROJECT_DIR && git branch --show-current")
    echo "🌿 Branch atual: $CURRENT_BRANCH"
else
    echo "❌ Não é um repositório git"
    echo "🔧 Clonando repositório..."
    ssh_exec "cd /var/www && git clone https://github.com/williamGois/juscash-api.git juscash"
    echo "✅ Repositório clonado"
fi

# Verificar Docker
echo "🐳 Verificando Docker..."
if ssh_exec "command -v docker > /dev/null"; then
    echo "✅ Docker instalado"
    
    # Verificar containers
    echo "📋 Containers ativos:"
    ssh_exec "docker ps --format 'table {{.Names}}\t{{.Status}}'"
else
    echo "❌ Docker não instalado"
fi

# Criar alias para fácil acesso
echo "🔧 Criando alias para acesso rápido..."

# Arquivo de alias local
cat > ~/.juscash_ssh_config << EOF
# Configuração SSH JusCash VPS
alias juscash-ssh="sshpass -p '$VPS_PASSWORD' ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST"
alias juscash-scp="sshpass -p '$VPS_PASSWORD' scp -o StrictHostKeyChecking=no"
alias juscash-logs="sshpass -p '$VPS_PASSWORD' ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST 'cd $VPS_PROJECT_DIR && docker-compose -f docker-compose.prod.yml logs -f'"
alias juscash-status="sshpass -p '$VPS_PASSWORD' ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST 'cd $VPS_PROJECT_DIR && docker ps'"
alias juscash-deploy="sshpass -p '$VPS_PASSWORD' ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST 'cd $VPS_PROJECT_DIR && git pull origin master && docker-compose -f docker-compose.prod.yml up -d --build'"
EOF

echo "✅ Aliases criados em ~/.juscash_ssh_config"

# Adicionar ao .bashrc ou .zshrc
SHELL_RC=""
if [ -f ~/.zshrc ]; then
    SHELL_RC="~/.zshrc"
elif [ -f ~/.bashrc ]; then
    SHELL_RC="~/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
    if ! grep -q "juscash_ssh_config" "$SHELL_RC"; then
        echo "source ~/.juscash_ssh_config" >> "$SHELL_RC"
        echo "✅ Aliases adicionados ao $SHELL_RC"
    fi
fi

echo
echo "=== COMANDOS DISPONÍVEIS ==="
echo "Para usar, execute: source ~/.juscash_ssh_config"
echo
echo "📌 Comandos rápidos:"
echo "juscash-ssh           # Conectar via SSH"
echo "juscash-status        # Ver status dos containers"
echo "juscash-logs          # Ver logs em tempo real"
echo "juscash-deploy        # Deploy automático"
echo
echo "📌 Conexão manual:"
echo "ssh root@$VPS_HOST"
echo "Senha: $VPS_PASSWORD"
echo
echo "📁 Diretório do projeto no VPS: $VPS_PROJECT_DIR"
echo

# Perguntar se quer conectar agora
read -p "🤔 Deseja conectar ao VPS agora? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Conectando ao VPS..."
    ssh_connect
fi

echo "✅ Configuração SSH concluída!" 