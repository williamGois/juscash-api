#!/bin/bash

echo "=== DEBUG DO BANCO DE DADOS ==="
echo ""

cd /var/www/juscash

echo "1. Status dos containers:"
docker-compose ps
echo ""

echo "2. Verificando conectividade do banco:"
docker-compose exec -T db pg_isready -U juscash && echo "✓ Banco está acessível" || echo "✗ Banco não está acessível"
echo ""

echo "3. Listando usuários do PostgreSQL:"
docker-compose exec -T db psql -U postgres -c "\du" 2>/dev/null || {
    echo "Não foi possível conectar com usuário postgres, tentando com juscash..."
    docker-compose exec -T db psql -U juscash -d postgres -c "\du" 2>/dev/null || echo "✗ Erro ao listar usuários"
}
echo ""

echo "4. Listando bancos de dados:"
docker-compose exec -T db psql -U postgres -c "\l" 2>/dev/null || {
    echo "Não foi possível conectar com usuário postgres, tentando com juscash..."
    docker-compose exec -T db psql -U juscash -d postgres -c "\l" 2>/dev/null || echo "✗ Erro ao listar bancos"
}
echo ""

echo "5. Testando conexão com as credenciais da aplicação:"
docker-compose exec -T db psql -U juscash -d juscash_db -c "SELECT current_database(), current_user, version();" 2>&1
echo ""

echo "6. Verificando variáveis de ambiente do container web:"
docker-compose exec -T web env | grep -E "(DATABASE_URL|POSTGRES)" | sort
echo ""

echo "7. Últimas 20 linhas do log do banco:"
docker-compose logs --tail=20 db
echo ""

echo "8. Últimas 20 linhas do log da aplicação:"
docker-compose logs --tail=20 web
echo ""

echo "9. Verificando volumes Docker:"
docker volume ls | grep juscash
echo ""

echo "10. Informações do volume do PostgreSQL:"
docker volume inspect juscash-api_postgres_data 2>/dev/null || echo "Volume não encontrado"
echo ""

echo "=== FIM DO DEBUG ===" 