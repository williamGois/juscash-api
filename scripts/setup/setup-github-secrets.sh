#!/bin/bash

echo "🔧 CONFIGURAÇÃO AUTOMÁTICA DAS SECRETS DO GITHUB"
echo "=================================================="

REPO="williamGois/juscash-api"
VPS_HOST="77.37.68.178"
VPS_USER="root"

echo "📋 Informações das Secrets:"
echo "Repositório: $REPO"
echo "VPS Host: $VPS_HOST"
echo "VPS User: $VPS_USER"
echo

echo "🔑 SSH Private Key:"
echo "-------------------"
cat ~/.ssh/juscash_cicd
echo
echo "-------------------"

echo
echo "📝 INSTRUÇÕES PARA CONFIGURAR NO GITHUB:"
echo "========================================="
echo
echo "1. 🌐 Acesse: https://github.com/$REPO/settings/actions"
echo "   ✅ Verifique se 'Actions permissions' está em 'Allow all actions'"
echo
echo "2. 🔐 Acesse: https://github.com/$REPO/settings/secrets/actions"
echo "   ✅ Clique em 'New repository secret' para cada secret abaixo:"
echo
echo "3. 📋 Configure estas 3 secrets:"
echo
echo "   🔑 SSH_PRIVATE_KEY"
echo "   Valor: (copie TODA a chave SSH acima, incluindo BEGIN e END)"
echo
echo "   🌐 VPS_HOST"
echo "   Valor: $VPS_HOST"
echo
echo "   👤 VPS_USER"
echo "   Valor: $VPS_USER"
echo
echo "4. 🚀 Teste o workflow:"
echo "   Acesse: https://github.com/$REPO/actions"
echo "   Veja se há workflows rodando após commits"
echo
echo "💡 COMO TESTAR SE FUNCIONOU:"
echo "============================="
echo "1. Faça qualquer mudança no código"
echo "2. git add . && git commit -m 'test: CI/CD'"
echo "3. git push origin master"
echo "4. Acesse https://github.com/$REPO/actions"
echo "5. Veja o workflow executando em tempo real"
echo
echo "✅ Após 5-7 minutos, a API deveria refletir as mudanças!" 