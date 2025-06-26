#!/bin/bash

echo "🔧 Script de Correção SSH para CI/CD"
echo "===================================="

# Executar na VPS
if [ ! -f ~/.ssh/github_actions ]; then
    echo "📝 Gerando nova chave SSH..."
    ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions -N ""
    
    echo "🔐 Adicionando ao authorized_keys..."
    cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    chmod 700 ~/.ssh
fi

echo ""
echo "📋 INSTRUÇÕES PARA GITHUB:"
echo "=========================="
echo ""
echo "1. Acesse: https://github.com/williamGois/juscash-api/settings/secrets/actions"
echo ""
echo "2. Crie/Atualize os seguintes secrets:"
echo ""
echo "VPS_HOST:"
echo "$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')"
echo ""
echo "VPS_USER:"
echo "$(whoami)"
echo ""
echo "VPS_SSH_KEY (copie TUDO, incluindo BEGIN e END):"
echo "------- INÍCIO DA CHAVE -------"
cat ~/.ssh/github_actions
echo "------- FIM DA CHAVE -------"
echo ""
echo "3. Após configurar, faça um commit para testar"
echo ""
echo "✅ Script concluído!" 