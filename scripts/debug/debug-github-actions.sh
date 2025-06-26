#!/bin/bash

echo "🔍 DIAGNÓSTICO COMPLETO DO GITHUB ACTIONS"
echo "=========================================="

REPO="williamGois/juscash-api"
LAST_COMMIT=$(git log --oneline -1 | awk '{print $1}')

echo "📋 Informações básicas:"
echo "Repositório: $REPO"
echo "Último commit: $LAST_COMMIT"
echo "Branch atual: $(git branch --show-current)"
echo

echo "🔍 1. VERIFICANDO WORKFLOW:"
echo "-------------------------"
if [ -f ".github/workflows/deploy.yml" ]; then
    echo "✅ Workflow existe: .github/workflows/deploy.yml"
    echo "📋 Triggers configurados:"
    grep -A 10 "on:" .github/workflows/deploy.yml
else
    echo "❌ Workflow não encontrado!"
fi

echo
echo "🔍 2. VERIFICANDO SECRETS LOCAIS:"
echo "--------------------------------"
if [ -f "cicd-secrets.txt" ]; then
    echo "✅ Arquivo de secrets existe"
    echo "📋 Secrets definidas:"
    grep -E "^[A-Z_]+:" cicd-secrets.txt | cut -d: -f1
else
    echo "❌ Arquivo de secrets não encontrado!"
fi

echo
echo "🔍 3. VERIFICANDO PERMISSÕES DO REPOSITÓRIO:"
echo "-------------------------------------------"
echo "🌐 Links para verificar manualmente:"
echo "• Actions: https://github.com/$REPO/settings/actions"
echo "• Secrets: https://github.com/$REPO/settings/secrets/actions" 
echo "• Workflows: https://github.com/$REPO/actions"

echo
echo "🔍 4. VERIFICANDO HISTÓRICO DE WORKFLOWS:"
echo "----------------------------------------"
echo "💡 Para ver se há workflows executando:"
echo "curl -s https://api.github.com/repos/$REPO/actions/runs | jq '.workflow_runs[] | {id, status, conclusion, created_at}'"

echo
echo "🔍 5. POSSÍVEIS PROBLEMAS IDENTIFICADOS:"
echo "---------------------------------------"

echo "❓ Verificar se o repositório tem as seguintes configurações:"
echo "1. Actions habilitadas (Settings → Actions → Allow all actions)"
echo "2. Write permissions (Settings → Actions → Workflow permissions → Read and write)"
echo "3. Secrets configuradas corretamente (não devem ter espaços ou caracteres especiais)"

echo
echo "🔍 6. TESTE MANUAL DO WORKFLOW:"
echo "------------------------------"
echo "Para testar se o problema é o trigger automático:"
echo "1. Acesse: https://github.com/$REPO/actions"
echo "2. Clique no workflow 'CI/CD - Deploy JusCash API'"
echo "3. Clique em 'Run workflow' → 'Run workflow'"
echo "4. Se funcionar manualmente, o problema é o trigger automático"

echo
echo "🔍 7. LOGS DE DEBUG:"
echo "------------------"
echo "Últimos 5 commits:"
git log --oneline -5

echo
echo "✅ PRÓXIMOS PASSOS:"
echo "=================="
echo "1. Verificar links acima no GitHub"
echo "2. Se Actions estiver desabilitado, habilitar"
echo "3. Se secrets estiverem incorretas, reconfigurar"
echo "4. Testar workflow manual"
echo "5. Se ainda não funcionar, verificar logs do workflow no GitHub" 