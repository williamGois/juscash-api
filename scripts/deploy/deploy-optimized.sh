#!/bin/bash

# Script otimizado de deploy para JusCash API
# Este script pode ser executado localmente para fazer deploy manual

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
VPS_USER="${VPS_USER:-root}"
VPS_HOST="${VPS_HOST}"
PROJECT_DIR="/var/www/juscash"

# Função para imprimir com cor
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Verificar variáveis necessárias
if [ -z "$VPS_HOST" ]; then
    print_color $RED "❌ Erro: VPS_HOST não está definido!"
    echo "Por favor, defina a variável de ambiente VPS_HOST"
    echo "Exemplo: export VPS_HOST=seu-servidor.com"
    exit 1
fi

print_color $BLUE "╔══════════════════════════════════════════════════════════════╗"
print_color $BLUE "║           🚀 DEPLOY OTIMIZADO - JUSCASH API                  ║"
print_color $BLUE "╚══════════════════════════════════════════════════════════════╝"

# Obter informações do Git local
CURRENT_BRANCH=$(git branch --show-current)
CURRENT_COMMIT=$(git rev-parse --short HEAD)

print_color $YELLOW "📋 Informações do Deploy:"
echo "   🌿 Branch: $CURRENT_BRANCH"
echo "   🔖 Commit: $CURRENT_COMMIT"
echo "   🖥️  Servidor: $VPS_USER@$VPS_HOST"
echo ""

# Confirmar deploy
read -p "Deseja continuar com o deploy? (s/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    print_color $RED "❌ Deploy cancelado!"
    exit 1
fi

# Executar deploy
print_color $GREEN "🚀 Iniciando deploy..."

ssh $VPS_USER@$VPS_HOST << 'ENDSSH'
set -e

# Cores para output remoto
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

cd /var/www/juscash

print_color $BLUE "📁 Diretório: $(pwd)"

# Backup
print_color $YELLOW "💾 Criando backup..."
mkdir -p backups
if docker-compose exec -T db pg_dump -U juscash juscash_db > backups/backup_$(date +%Y%m%d_%H%M%S).sql 2>/dev/null; then
    print_color $GREEN "✅ Backup criado"
else
    print_color $YELLOW "⚠️  Backup falhou (continuando...)"
fi

# Atualizar código
print_color $YELLOW "📥 Atualizando código..."
git fetch origin --prune
BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "detached")
git reset --hard origin/$BRANCH

# Criar arquivo VERSION
COMMIT=$(git rev-parse --short HEAD)
echo $COMMIT > VERSION
print_color $GREEN "✅ Versão: $COMMIT"

# Build otimizado
print_color $YELLOW "🔨 Construindo imagens Docker..."

# Usar BuildKit para build mais rápido
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Pull das imagens base
docker-compose -f docker-compose.prod.yml pull --quiet || true

# Build com cache
if docker-compose -f docker-compose.prod.yml build --parallel; then
    print_color $GREEN "✅ Build concluído"
else
    print_color $RED "❌ Erro no build!"
    exit 1
fi

# Parar containers graciosamente
print_color $YELLOW "⏹️  Parando containers..."
docker-compose -f docker-compose.prod.yml stop

# Remover containers antigos
docker-compose -f docker-compose.prod.yml rm -f

# Iniciar novos containers
print_color $YELLOW "🚀 Iniciando containers..."
if docker-compose -f docker-compose.prod.yml up -d; then
    print_color $GREEN "✅ Containers iniciados"
else
    print_color $RED "❌ Erro ao iniciar containers!"
    exit 1
fi

# Aguardar inicialização
print_color $YELLOW "⏳ Aguardando serviços..."
sleep 20

# Executar migrações
print_color $YELLOW "🗄️  Aplicando migrações..."
docker-compose -f docker-compose.prod.yml exec -T web flask db upgrade || print_color $YELLOW "⚠️  Erro nas migrações"

# Health check
print_color $YELLOW "🏥 Verificando saúde da aplicação..."
MAX_ATTEMPTS=5
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    if curl -f -s http://localhost:5000/api/simple/ping > /tmp/health.json; then
        API_VERSION=$(cat /tmp/health.json | python3 -c "import sys, json; print(json.load(sys.stdin).get('version', 'unknown'))" 2>/dev/null || echo "parse_error")
        FILE_VERSION=$(cat VERSION)
        
        if [ "$API_VERSION" = "$FILE_VERSION" ]; then
            print_color $GREEN "✅ Deploy verificado! Versão: $API_VERSION"
            break
        else
            print_color $YELLOW "⚠️  Versões não coincidem (API: $API_VERSION, File: $FILE_VERSION)"
        fi
    else
        print_color $YELLOW "⚠️  Tentativa $ATTEMPT/$MAX_ATTEMPTS falhou"
    fi
    
    if [ $ATTEMPT -lt $MAX_ATTEMPTS ]; then
        sleep 10
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
done

# Limpeza
print_color $YELLOW "🧹 Limpando recursos antigos..."
docker image prune -f --filter "until=24h" || true
docker volume prune -f || true

# Manter apenas 5 backups
cd backups && ls -t backup_*.sql 2>/dev/null | tail -n +6 | xargs -r rm || true
cd ..

# Status final
print_color $BLUE "📊 Status dos containers:"
docker-compose -f docker-compose.prod.yml ps

print_color $GREEN "✅ Deploy concluído com sucesso!"
ENDSSH

# Verificar resultado
if [ $? -eq 0 ]; then
    print_color $GREEN "✅ Deploy realizado com sucesso!"
    
    # Verificar API externa
    print_color $YELLOW "🌐 Verificando API externa..."
    sleep 5
    
    if curl -f -s https://cron.juscash.app/api/simple/ping > /dev/null; then
        print_color $GREEN "✅ API está acessível em https://cron.juscash.app"
    else
        print_color $YELLOW "⚠️  API não está acessível externamente ainda"
    fi
else
    print_color $RED "❌ Deploy falhou!"
    exit 1
fi 