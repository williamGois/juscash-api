#!/bin/bash

echo "🚀 Conectando ao VPS JusCash..."
echo

# Configurações do VPS
VPS_HOST="77.37.68.178"
VPS_USER="root"
VPS_PASSWORD="Syberya1989@@"
VPS_PROJECT_DIR="/var/www/juscash"

echo "📡 Host: $VPS_HOST"
echo "👤 Usuário: $VPS_USER"
echo "📁 Projeto: $VPS_PROJECT_DIR"
echo

# Verificar se sshpass está instalado
if ! command -v sshpass &> /dev/null; then
    echo "📦 sshpass não encontrado. Instalando..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            echo "🍺 Instalando via Homebrew..."
            brew install hudochenkov/sshpass/sshpass
        else
            echo "❌ Homebrew não encontrado"
            echo "💡 Conecte manualmente: ssh root@$VPS_HOST"
            echo "🔑 Senha: $VPS_PASSWORD"
            exit 1
        fi
    else
        # Linux
        echo "🐧 Instalando via apt..."
        sudo apt-get update && sudo apt-get install -y sshpass
    fi
fi

# Testar conectividade
echo "🔍 Testando conectividade..."
if ping -c 1 "$VPS_HOST" > /dev/null 2>&1; then
    echo "✅ VPS acessível"
else
    echo "❌ VPS não acessível - verifique sua conexão"
    exit 1
fi

# Conectar via SSH
echo "🔐 Conectando via SSH..."
echo "💡 Para sair: digite 'exit'"
echo

# Conectar e ir direto para o diretório do projeto
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" -t "cd $VPS_PROJECT_DIR 2>/dev/null || cd /root; bash" 