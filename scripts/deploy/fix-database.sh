#!/bin/bash

set -e

echo "=== CORRIGINDO BANCO DE DADOS ==="

cd /var/www/juscash

echo "1. Parando containers..."
docker-compose stop

echo "2. Removendo container do banco..."
docker-compose rm -f db

echo "3. Removendo volume do banco para recriá-lo..."
docker volume rm juscash-api_postgres_data || true

echo "4. Iniciando banco de dados limpo..."
docker-compose up -d db

echo "5. Aguardando banco ficar pronto..."
for i in {1..30}; do
    if docker-compose exec -T db pg_isready -U juscash > /dev/null 2>&1; then
        echo "✓ Banco de dados está pronto!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "✗ ERRO: Banco de dados não ficou pronto"
        docker-compose logs db
        exit 1
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "6. Verificando criação do banco..."
docker-compose exec -T db psql -U juscash -d juscash_db -c "SELECT version();" || {
    echo "✗ ERRO: Banco não foi criado corretamente"
    docker-compose logs db
    exit 1
}

echo "7. Iniciando Redis..."
docker-compose up -d redis

echo "8. Aguardando Redis..."
sleep 5

echo "9. Iniciando aplicação web..."
docker-compose up -d web

echo "10. Aguardando aplicação..."
sleep 10

echo "11. Verificando status..."
docker-compose ps

echo "12. Testando API..."
curl -s http://localhost:5000/api/simple/ping || echo "API ainda não está respondendo"

echo ""
echo "=== BANCO DE DADOS CORRIGIDO ==="
echo "Use 'docker-compose logs -f' para acompanhar os logs" 