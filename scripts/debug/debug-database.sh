#!/bin/bash

echo "=== DIAGNÓSTICO DO BANCO DE DADOS ==="
echo "Data: $(date)"
echo

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root (sudo)"
    exit 1
fi

# Ir para o diretório do projeto
cd /root/juscash-api 2>/dev/null || cd /home/*/juscash-api 2>/dev/null || { echo "❌ Diretório do projeto não encontrado"; exit 1; }

echo "📁 Diretório atual: $(pwd)"
echo

echo "🐳 Status dos containers Docker..."
echo "────────────────────────────────────"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(juscash|postgres|redis)" || echo "❌ Nenhum container JusCash encontrado"

echo
echo "🔍 Verificando container do banco de dados..."
echo "────────────────────────────────────"

# Verificar se container do BD existe
if docker ps -a | grep -q "juscash_db_prod"; then
    echo "✅ Container juscash_db_prod encontrado"
    
    # Status do container
    DB_STATUS=$(docker ps --format "{{.Status}}" -f name=juscash_db_prod)
    echo "📊 Status: $DB_STATUS"
    
    # Verificar health check
    DB_HEALTH=$(docker inspect juscash_db_prod --format "{{.State.Health.Status}}" 2>/dev/null || echo "unknown")
    echo "🏥 Health: $DB_HEALTH"
    
    # Logs recentes do banco
    echo
    echo "📋 Últimos logs do banco de dados:"
    docker logs juscash_db_prod --tail 10 2>/dev/null || echo "❌ Não foi possível acessar logs"
    
else
    echo "❌ Container juscash_db_prod não encontrado"
fi

echo
echo "🔌 Verificando conectividade de rede..."
echo "────────────────────────────────────"

# Verificar network do Docker
if docker network ls | grep -q "juscash"; then
    NETWORK_NAME=$(docker network ls | grep juscash | awk '{print $2}')
    echo "✅ Network encontrada: $NETWORK_NAME"
    
    # Listar containers na network
    echo "📡 Containers na network:"
    docker network inspect $NETWORK_NAME --format "{{range .Containers}}{{.Name}} - {{.IPv4Address}}{{println}}{{end}}" 2>/dev/null || echo "❌ Erro ao inspecionar network"
else
    echo "❌ Network juscash não encontrada"
fi

echo
echo "🗃️ Verificando dados persistentes..."
echo "────────────────────────────────────"

# Verificar volumes
if docker volume ls | grep -q "postgres_data"; then
    echo "✅ Volume postgres_data encontrado"
    
    # Tamanho do volume
    VOLUME_SIZE=$(docker system df -v | grep postgres_data | awk '{print $3}' || echo "unknown")
    echo "📊 Tamanho: $VOLUME_SIZE"
else
    echo "❌ Volume postgres_data não encontrado"
fi

echo
echo "🔐 Verificando variáveis de ambiente..."
echo "────────────────────────────────────"

# Verificar env do container web
if docker ps | grep -q "juscash_web_prod"; then
    echo "📋 Variáveis de ambiente do container web:"
    docker exec juscash_web_prod env | grep -E "(DATABASE_URL|POSTGRES_|REDIS_)" | sed 's/\(.*=.*\)\(.*\)/\1***/' 2>/dev/null || echo "❌ Não foi possível acessar variáveis"
else
    echo "❌ Container juscash_web_prod não está rodando"
fi

echo
echo "🔧 Teste de conectividade manual..."
echo "────────────────────────────────────"

# Testar conexão do container web para o banco
if docker ps | grep -q "juscash_web_prod"; then
    echo "🔌 Testando conexão web -> banco..."
    docker exec juscash_web_prod python3 -c "
import psycopg2
import os
try:
    database_url = os.environ.get('DATABASE_URL', '')
    if 'sslmode' not in database_url:
        database_url += '?sslmode=disable'
    
    conn = psycopg2.connect(database_url, connect_timeout=10)
    print('✅ Conexão com banco OK')
    
    cur = conn.cursor()
    cur.execute('SELECT version();')
    version = cur.fetchone()
    print(f'📊 Versão PostgreSQL: {version[0][:50]}...')
    
    cur.execute('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = \'public\';')
    tables = cur.fetchone()
    print(f'📋 Tabelas encontradas: {tables[0]}')
    
    conn.close()
except Exception as e:
    print(f'❌ Erro de conexão: {e}')
" 2>/dev/null || echo "❌ Erro ao executar teste de conexão"
else
    echo "❌ Container web não está rodando para teste"
fi

echo
echo "🔄 Verificando processo de inicialização..."
echo "────────────────────────────────────"

# Logs do container web relacionados ao banco
if docker ps | grep -q "juscash_web_prod"; then
    echo "📋 Logs de inicialização do container web:"
    docker logs juscash_web_prod --tail 20 | grep -E "(PostgreSQL|database|conexão|connection)" || echo "Nenhum log relacionado ao banco encontrado"
else
    echo "❌ Container web não está rodando"
fi

echo
echo "=== SOLUÇÕES RECOMENDADAS ==="
echo

# Analisar problemas e sugerir soluções
if ! docker ps | grep -q "juscash_db_prod"; then
    echo "🔧 PROBLEMA: Container do banco não está rodando"
    echo "   Solução: docker-compose -f docker-compose.prod.yml up -d db"
    echo
fi

if ! docker ps | grep -q "juscash_web_prod"; then
    echo "🔧 PROBLEMA: Container web não está rodando"
    echo "   Solução: docker-compose -f docker-compose.prod.yml up -d web"
    echo
fi

echo "🛠️ Comandos úteis para correção:"
echo "1. Reiniciar apenas o banco:"
echo "   docker-compose -f docker-compose.prod.yml restart db"
echo
echo "2. Reiniciar toda a stack:"
echo "   docker-compose -f docker-compose.prod.yml down && docker-compose -f docker-compose.prod.yml up -d"
echo
echo "3. Verificar logs em tempo real:"
echo "   docker-compose -f docker-compose.prod.yml logs -f db"
echo
echo "4. Executar migrações manualmente:"
echo "   docker exec juscash_web_prod flask db upgrade"
echo
echo "5. Conectar no banco manualmente:"
echo "   docker exec -it juscash_db_prod psql -U juscash -d juscash_db"
echo

echo "✅ Diagnóstico concluído!" 