#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              🔍 DEBUG VPS - MONITORAMENTO LOGS               ║"
echo "╚══════════════════════════════════════════════════════════════╝"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd /var/www/juscash

echo -e "${BLUE}📋 INFORMAÇÕES GERAIS${NC}"
echo "🕐 Data/Hora: $(date)"
echo "📁 Diretório: $(pwd)"
echo "👤 Usuário: $(whoami)"
echo ""

echo -e "${BLUE}📊 STATUS DOS CONTAINERS${NC}"
docker-compose ps
echo ""

echo -e "${BLUE}🔍 ESTADO DO GIT${NC}"
echo "Branch atual: $(git branch --show-current 2>/dev/null || echo 'desconhecido')"
echo "Último commit: $(git log --oneline -1 2>/dev/null || echo 'erro')"
echo "Status: $(git status --porcelain 2>/dev/null | wc -l) arquivos modificados"
echo "Remote URL: $(git remote get-url origin 2>/dev/null || echo 'sem remote')"
echo ""

echo -e "${BLUE}📄 ARQUIVO VERSION${NC}"
if [ -f VERSION ]; then
    echo -e "${GREEN}✅ Arquivo VERSION encontrado no host${NC}"
    echo "Conteúdo: $(cat VERSION)"
    echo "Permissões: $(ls -la VERSION)"
else
    echo -e "${RED}❌ Arquivo VERSION não encontrado no host${NC}"
fi
echo ""

echo -e "${BLUE}🐳 VERIFICAÇÃO NO CONTAINER${NC}"
if docker-compose exec -T web ls -la /app/VERSION 2>/dev/null; then
    echo -e "${GREEN}✅ Arquivo VERSION encontrado no container${NC}"
    echo "Conteúdo no container: $(docker-compose exec -T web cat /app/VERSION 2>/dev/null || echo 'erro ao ler')"
else
    echo -e "${RED}❌ Arquivo VERSION não encontrado no container${NC}"
fi

echo "Variável DEPLOY_VERSION:"
docker-compose exec -T web env | grep DEPLOY_VERSION 2>/dev/null || echo -e "${RED}❌ Variável não encontrada${NC}"
echo ""

echo -e "${BLUE}🏥 TESTE DA API${NC}"
echo "Testando endpoint de saúde..."
if curl -f -s --max-time 10 http://localhost:5000/api/simple/ping > /tmp/api_test.json 2>&1; then
    echo -e "${GREEN}✅ API respondendo${NC}"
    echo "Resposta:"
    cat /tmp/api_test.json | python3 -m json.tool 2>/dev/null || cat /tmp/api_test.json
    
    API_VERSION=$(cat /tmp/api_test.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('version', 'unknown'))" 2>/dev/null || echo "unknown")
    echo "Versão atual da API: $API_VERSION"
else
    echo -e "${RED}❌ API não está respondendo${NC}"
    echo "Erro: $(cat /tmp/api_test.json 2>/dev/null || echo 'sem detalhes')"
fi
echo ""

echo -e "${BLUE}📋 LOGS RECENTES DOS CONTAINERS${NC}"
echo "--- Logs do container web (últimas 20 linhas) ---"
docker-compose logs web --tail=20 2>/dev/null || echo -e "${RED}❌ Erro ao obter logs do web${NC}"
echo ""

echo "--- Logs do container db (últimas 10 linhas) ---"
docker-compose logs db --tail=10 2>/dev/null || echo -e "${RED}❌ Erro ao obter logs do db${NC}"
echo ""

echo -e "${BLUE}🗂️ LOGS DE DEPLOY RECENTES${NC}"
echo "Logs de deploy mais recentes:"
ls -lt /var/www/juscash/deploy_*.log 2>/dev/null | head -3 || echo -e "${YELLOW}⚠️ Nenhum log de deploy encontrado${NC}"
echo ""

echo -e "${BLUE}📊 USO DE RECURSOS${NC}"
echo "Memória:"
free -h
echo ""
echo "Espaço em disco:"
df -h /var/www/juscash
echo ""
echo "Processos Docker:"
ps aux | grep docker | grep -v grep | wc -l
echo ""

echo -e "${BLUE}🔄 OPÇÕES DISPONÍVEIS${NC}"
echo "1. Ver log de deploy mais recente: tail -f /var/www/juscash/deploy_$(ls -t /var/www/juscash/deploy_*.log 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo 'nenhum.log')"
echo "2. Acompanhar logs do container web: docker-compose logs -f web"
echo "3. Executar deploy manual: ./deploy-optimized.sh"
echo "4. Reiniciar containers: docker-compose restart"
echo "5. Ver status detalhado: docker-compose ps && docker stats --no-stream"
echo ""

echo -e "${GREEN}✅ Debug concluído!${NC}"
echo "Para monitoramento contínuo, execute: watch -n 30 './debug-vps-logs.sh'" 