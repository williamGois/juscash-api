#!/bin/bash

# Script para monitorar o deploy em tempo real

EXPECTED_VERSION="9f1299a"
API_URL="https://cron.juscash.app/api/simple/ping"
MAX_ATTEMPTS=30
INTERVAL=10

echo "🔍 Monitorando deploy da versão: $EXPECTED_VERSION"
echo "🌐 URL: $API_URL"
echo "⏱️  Verificando a cada $INTERVAL segundos..."
echo ""

for i in $(seq 1 $MAX_ATTEMPTS); do
    echo -n "[$i/$MAX_ATTEMPTS] $(date '+%H:%M:%S') - "
    
    if RESPONSE=$(curl -f -s --max-time 10 "$API_URL" 2>/dev/null); then
        # Extrair versão da resposta
        VERSION=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('version', 'unknown'))" 2>/dev/null || echo "unknown")
        
        if [ "$VERSION" = "$EXPECTED_VERSION" ]; then
            echo "✅ SUCESSO! Versão atualizada para: $VERSION"
            echo ""
            echo "📋 Resposta completa:"
            echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
            exit 0
        else
            echo "⚠️  Versão atual: $VERSION (esperado: $EXPECTED_VERSION)"
        fi
    else
        echo "❌ API não está respondendo"
    fi
    
    if [ $i -lt $MAX_ATTEMPTS ]; then
        sleep $INTERVAL
    fi
done

echo ""
echo "⏰ Timeout atingido após $((MAX_ATTEMPTS * INTERVAL)) segundos"
echo "🔍 Última versão detectada: $VERSION"

if [ "$VERSION" != "unknown" ] && [ "$VERSION" != "$EXPECTED_VERSION" ]; then
    echo "⚠️  A API está respondendo, mas com versão antiga"
    echo "💡 Possíveis causas:"
    echo "   - Deploy ainda em andamento"
    echo "   - Erro no processo de build"
    echo "   - Cache do proxy reverso"
fi 