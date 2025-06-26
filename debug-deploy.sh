#!/bin/bash

# Script de diagnóstico para problemas de deploy
# Execute este script diretamente na sua VPS

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_color $BLUE "🔍 DIAGNÓSTICO DE DEPLOY - JUSCASH API"
print_color $BLUE "========================================"

# 1. Verificar diretório atual
print_color $YELLOW "1. Verificando diretório atual..."
pwd
ls -la

# 2. Verificar Git
print_color $YELLOW "2. Verificando status do Git..."
echo "Branch atual: $(git branch --show-current)"
echo "Último commit: $(git log --oneline -1)"
echo "Status: $(git status --porcelain)"

# 3. Verificar arquivo VERSION
print_color $YELLOW "3. Verificando arquivo VERSION..."
if [ -f "VERSION" ]; then
    echo "✅ Arquivo VERSION existe"
    echo "Conteúdo: $(cat VERSION)"
else
    echo "❌ Arquivo VERSION não existe!"
fi

# 4. Verificar containers Docker
print_color $YELLOW "4. Verificando containers Docker..."
echo "Containers rodando:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\nTodos os containers:"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"

# 5. Verificar docker-compose
print_color $YELLOW "5. Verificando docker-compose..."
if [ -f "docker-compose.yml" ]; then
    echo "✅ docker-compose.yml existe"
    echo "Status dos serviços:"
    docker-compose ps
else
    echo "❌ docker-compose.yml não existe!"
fi

if [ -f "docker-compose.prod.yml" ]; then
    echo "✅ docker-compose.prod.yml existe"
    echo "Status dos serviços (prod):"
    docker-compose -f docker-compose.prod.yml ps
else
    echo "❌ docker-compose.prod.yml não existe!"
fi

# 6. Testar API
print_color $YELLOW "6. Testando API..."
if curl -f -s http://localhost:5000/api/simple/ping > /tmp/api_response.json; then
    echo "✅ API está respondendo"
    echo "Resposta:"
    cat /tmp/api_response.json | python3 -m json.tool 2>/dev/null || cat /tmp/api_response.json
else
    echo "❌ API não está respondendo"
    
    # Verificar logs do container web
    echo "Logs do container web:"
    if docker-compose ps web | grep -q "web"; then
        docker-compose logs web --tail=20
    elif docker-compose -f docker-compose.prod.yml ps web | grep -q "web"; then
        docker-compose -f docker-compose.prod.yml logs web --tail=20
    else
        echo "Container web não encontrado"
    fi
fi

# 7. Verificar imagens Docker
print_color $YELLOW "7. Verificando imagens Docker..."
echo "Imagens locais:"
docker images | grep -E "(juscash|<none>)" || echo "Nenhuma imagem juscash encontrada"

# 8. Verificar volumes
print_color $YELLOW "8. Verificando volumes..."
docker volume ls | grep -E "(juscash|postgres|redis)" || echo "Nenhum volume relacionado encontrado"

# 9. Verificar rede
print_color $YELLOW "9. Verificando conectividade..."
echo "Testando conexão com banco:"
if docker-compose exec -T db pg_isready -U juscash -d juscash_db 2>/dev/null; then
    echo "✅ PostgreSQL está acessível"
else
    echo "❌ PostgreSQL não está acessível"
fi

echo "Testando conexão com Redis:"
if docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
    echo "✅ Redis está acessível"
else
    echo "❌ Redis não está acessível"
fi

# 10. Verificar processos
print_color $YELLOW "10. Verificando processos..."
echo "Processos Python rodando:"
ps aux | grep python | grep -v grep || echo "Nenhum processo Python encontrado"

print_color $BLUE "========================================"
print_color $GREEN "✅ Diagnóstico concluído!"

# Sugestões
print_color $YELLOW "💡 SUGESTÕES:"
echo "1. Se a API não está respondendo, execute: docker-compose restart web"
echo "2. Se a versão não está correta, execute: docker-compose build --no-cache web"
echo "3. Para forçar rebuild completo: docker-compose down && docker-compose up -d --build"
echo "4. Para ver logs em tempo real: docker-compose logs -f web" 