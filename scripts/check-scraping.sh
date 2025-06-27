#!/bin/bash

echo "============================================================"
echo "🔍 ANÁLISE COMPLETA DO WEB SCRAPING - JUSCASH"
echo "============================================================"

SSH_CMD="sshpass -p 'Syberya1989@@' ssh -o StrictHostKeyChecking=no root@77.37.68.178"
API_BASE="https://cron.juscash.app/api"

echo ""
echo "📋 Testando Conectividade da API"
echo "----------------------------------------"
if curl -s -f "${API_BASE}/simple/ping" > /dev/null; then
    echo "✅ API está respondendo"
else
    echo "❌ API não está respondendo"
fi

echo ""
echo "📋 Status dos Containers Docker"
echo "----------------------------------------"
$SSH_CMD "cd /var/www/juscash && docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

echo ""
echo "📋 Verificando Dependências do Selenium"
echo "----------------------------------------"
echo "🔍 Testando Selenium:"
if $SSH_CMD "cd /var/www/juscash && docker exec juscash_worker_prod python -c 'from selenium import webdriver; print(\"Selenium OK\")'" 2>/dev/null; then
    echo "✅ Selenium está funcionando"
else
    echo "❌ Erro no Selenium"
fi

echo ""
echo "🔍 Verificando Chrome/Chromium:"
CHROME_FOUND=false

for cmd in "google-chrome --version" "chromium-browser --version" "chromium --version"; do
    if $SSH_CMD "cd /var/www/juscash && docker exec juscash_worker_prod $cmd" 2>/dev/null; then
        echo "✅ Chrome/Chromium encontrado: $cmd"
        CHROME_FOUND=true
        break
    fi
done

if [ "$CHROME_FOUND" = false ]; then
    echo "🚨 PROBLEMA CRÍTICO: Chrome/Chromium não encontrado no container!"
    echo "💡 Solução: Usar Dockerfile.alternative que inclui Chrome"
fi

echo ""
echo "📋 Testando Conectividade com DJE"
echo "----------------------------------------"
if $SSH_CMD "cd /var/www/juscash && docker exec juscash_worker_prod curl -I -s -m 10 https://dje.tjsp.jus.br/cdje/index.do" | grep -q "200 OK"; then
    echo "✅ Site do DJE está acessível"
else
    echo "❌ Problema ao acessar o site do DJE"
fi

echo ""
echo "📋 Análise do Banco de Dados"
echo "----------------------------------------"
DB_RESPONSE=$(curl -s "${API_BASE}/publicacoes/?limit=5")
if echo "$DB_RESPONSE" | grep -q '"id":'; then
    if echo "$DB_RESPONSE" | grep -q '"status":"error"'; then
        echo "❌ Erro no banco de dados"
    else
        echo "✅ Banco de dados está respondendo"
        echo "📊 Amostra dos dados:"
        echo "$DB_RESPONSE" | head -3
    fi
else
    echo "❌ Problema com o banco de dados"
fi

echo ""
echo "📋 Logs Recentes do Worker"
echo "----------------------------------------"
echo "📋 Últimos logs do worker (filtrados):"
$SSH_CMD "cd /var/www/juscash && docker logs juscash_worker_prod --tail 20 | grep -E '(scraping|extract|publicacao|selenium|chrome|DJE|SUCCESS|FAILURE|ERROR|extract_publicacoes)'"

echo ""
echo "📋 Teste de Execução do Scraping"
echo "----------------------------------------"
ONTEM=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v -1d +%Y-%m-%d)
echo "🚀 Iniciando teste de scraping para $ONTEM..."

RESPONSE=$(curl -s -X POST "${API_BASE}/scraping/extract" \
    -H 'Content-Type: application/json' \
    -d "{\"data_inicio\": \"${ONTEM}T00:00:00\", \"data_fim\": \"${ONTEM}T23:59:59\"}")

if echo "$RESPONSE" | grep -q "task_id"; then
    TASK_ID=$(echo "$RESPONSE" | grep -o '"task_id":"[^"]*"' | cut -d'"' -f4)
    echo "✅ Tarefa iniciada: $TASK_ID"
    
    echo "⏳ Aguardando 30 segundos..."
    sleep 30
    
    STATUS_RESPONSE=$(curl -s "${API_BASE}/cron/tasks/${TASK_ID}")
    if echo "$STATUS_RESPONSE" | grep -q "SUCCESS"; then
        echo "🎉 Sucesso! Scraping funcionou"
    elif echo "$STATUS_RESPONSE" | grep -q "FAILURE"; then
        echo "❌ Falha na execução do scraping"
    elif echo "$STATUS_RESPONSE" | grep -q "PENDING\|PROGRESS"; then
        echo "⏳ Ainda em execução"
    else
        echo "❓ Estado desconhecido"
        echo "Resposta: $STATUS_RESPONSE"
    fi
else
    echo "❌ Erro ao iniciar scraping"
    echo "Resposta: $RESPONSE"
fi

echo ""
echo "============================================================"
echo "📊 RESUMO EXECUTIVO"
echo "============================================================"

echo ""
echo "🎯 PARA VERIFICAR RAPIDAMENTE SE O SCRAPING ESTÁ FUNCIONANDO:"
echo ""
echo "1. 🌸 Flower: https://flower.juscash.app (admin:juscash2024)"
echo "   - Verificar tarefas 'extract_' com status SUCCESS"
echo ""
echo "2. 📋 Logs: docker logs juscash_worker_prod --tail 20 | grep extract"
echo ""
echo "3. 🧪 Teste manual:"
echo "   curl -X POST 'https://cron.juscash.app/api/scraping/extract' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"data_inicio\": \"2024-12-25T00:00:00\", \"data_fim\": \"2024-12-25T23:59:59\"}'"
echo ""
echo "4. 📊 Dados: curl 'https://cron.juscash.app/api/publicacoes/?limit=5'"
echo ""

echo "✅ INDICADORES DE SAÚDE:"
echo "- Tarefas SUCCESS no Flower nas últimas 24h"
echo "- Logs sem erros críticos"
echo "- Publicações novas sendo salvas"
echo "- Tempo de execução < 30 minutos por dia"
echo ""

echo "🚨 ALERTAS CRÍTICOS:"
echo "- 0 publicações extraídas por > 2 dias"
echo "- Erros de Chrome/Selenium constantes"
echo "- Timeout em > 50% das execuções"
echo "- Campos vazios em > 80% dos dados"
echo ""

if [ "$CHROME_FOUND" = false ]; then
    echo "🔧 AÇÃO NECESSÁRIA:"
    echo "Chrome não está instalado no container. Para corrigir:"
    echo "1. Editar docker-compose.prod.yml"
    echo "2. Alterar 'dockerfile: Dockerfile' para 'dockerfile: Dockerfile.alternative'"
    echo "3. Fazer rebuild: docker-compose -f docker-compose.prod.yml up --build -d"
fi

echo ""
echo "📚 DOCUMENTAÇÃO COMPLETA:"
echo "- SCRAPING_MONITORING.md: Guia detalhado de monitoramento"
echo "- MONITORING.md: Guia geral de monitoramento"
echo ""
echo "Análise concluída em $(date)" 