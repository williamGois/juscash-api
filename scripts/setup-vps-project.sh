#!/bin/bash

echo "=== SETUP COMPLETO DO PROJETO NO VPS ==="
echo "Data: $(date)"
echo

# Configurações
VPS_HOST="77.37.68.178"
VPS_USER="root"
VPS_PASSWORD="Syberya1989@@"
VPS_PROJECT_DIR="/var/www/juscash"
REPO_URL="https://github.com/williamGois/juscash-api.git"

# Verificar se sshpass está disponível
if ! command -v sshpass &> /dev/null; then
    echo "❌ sshpass não encontrado"
    echo "💡 Use: ssh root@$VPS_HOST"
    echo "🔑 Senha: $VPS_PASSWORD"
    exit 1
fi

# Função para executar comandos no VPS
vps_exec() {
    local command="$1"
    echo "🔄 Executando: $command"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$command"
}

# Testar conexão
echo "🔍 Testando conexão com VPS..."
if ! vps_exec "echo 'Conexão OK'"; then
    echo "❌ Erro na conexão SSH"
    exit 1
fi
echo "✅ Conexão SSH OK"

# Verificar se diretório existe
echo "📁 Verificando diretório do projeto..."
if vps_exec "[ -d '$VPS_PROJECT_DIR' ]"; then
    echo "✅ Diretório $VPS_PROJECT_DIR existe"
    
    # Verificar se é repositório git
    if vps_exec "[ -d '$VPS_PROJECT_DIR/.git' ]"; then
        echo "✅ Repositório git encontrado"
        echo "🔄 Atualizando código..."
        vps_exec "cd $VPS_PROJECT_DIR && git stash && git pull origin master"
    else
        echo "❌ Não é um repositório git"
        echo "🗑️  Removendo diretório antigo..."
        vps_exec "rm -rf $VPS_PROJECT_DIR"
        echo "📥 Clonando repositório..."
        vps_exec "git clone $REPO_URL $VPS_PROJECT_DIR"
    fi
else
    echo "📥 Clonando repositório..."
    vps_exec "mkdir -p /var/www && git clone $REPO_URL $VPS_PROJECT_DIR"
fi

# Verificar estrutura do projeto
echo "📋 Verificando estrutura do projeto..."
vps_exec "cd $VPS_PROJECT_DIR && ls -la"

# Verificar se Docker está instalado
echo "🐳 Verificando Docker..."
if vps_exec "command -v docker > /dev/null"; then
    echo "✅ Docker instalado"
    
    # Verificar Docker Compose
    if vps_exec "command -v docker-compose > /dev/null"; then
        echo "✅ Docker Compose instalado"
    else
        echo "❌ Docker Compose não encontrado"
        echo "📦 Instalando Docker Compose..."
        vps_exec "curl -L \"https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose"
    fi
else
    echo "❌ Docker não instalado"
    echo "📦 Instalando Docker..."
    vps_exec "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && systemctl start docker && systemctl enable docker"
fi

# Verificar arquivo .env
echo "🔧 Verificando configurações..."
if vps_exec "[ -f '$VPS_PROJECT_DIR/.env' ]"; then
    echo "✅ Arquivo .env encontrado"
else
    echo "❌ Arquivo .env não encontrado"
    echo "📝 Criando .env básico..."
    vps_exec "cd $VPS_PROJECT_DIR && cp env.vps .env"
fi

# Verificar containers
echo "📊 Status dos containers..."
vps_exec "cd $VPS_PROJECT_DIR && docker-compose -f docker-compose.prod.yml ps"

# Oferecer opções
echo
echo "=== OPÇÕES DISPONÍVEIS ==="
echo "1. Iniciar containers: docker-compose -f docker-compose.prod.yml up -d"
echo "2. Rebuild containers: docker-compose -f docker-compose.prod.yml up -d --build"
echo "3. Ver logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "4. Parar containers: docker-compose -f docker-compose.prod.yml down"
echo

read -p "🤔 Deseja iniciar os containers agora? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Iniciando containers..."
    vps_exec "cd $VPS_PROJECT_DIR && docker-compose -f docker-compose.prod.yml up -d"
    
    echo "⏳ Aguardando containers inicializarem..."
    sleep 10
    
    echo "📊 Status final:"
    vps_exec "cd $VPS_PROJECT_DIR && docker-compose -f docker-compose.prod.yml ps"
fi

echo
echo "=== INFORMAÇÕES ÚTEIS ==="
echo "🌐 Acesso SSH: ssh root@$VPS_HOST"
echo "🔑 Senha: $VPS_PASSWORD"
echo "📁 Diretório: $VPS_PROJECT_DIR"
echo "🐳 Logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "📱 API: http://$VPS_HOST:5000"
echo
echo "✅ Setup concluído!" 