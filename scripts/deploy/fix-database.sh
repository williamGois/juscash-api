#!/bin/bash

echo "🔧 Corrigindo banco de dados na VPS"

cd /var/www/juscash

# 1. Parar apenas o web
echo "🛑 Parando container web..."
docker-compose stop web

# 2. Recriar banco se necessário
echo "🗄️ Verificando banco de dados..."
docker-compose exec -T db psql -U postgres -c "SELECT 1 FROM pg_database WHERE datname='juscash_db'" | grep -q 1 || {
    echo "📝 Criando banco de dados..."
    docker-compose exec -T db psql -U postgres <<EOF
CREATE USER juscash WITH PASSWORD 'juscash123';
CREATE DATABASE juscash_db OWNER juscash;
GRANT ALL PRIVILEGES ON DATABASE juscash_db TO juscash;
EOF
}

# 3. Reiniciar web
echo "🚀 Reiniciando web..."
docker-compose up -d web

# 4. Aguardar
echo "⏳ Aguardando..."
sleep 10

# 5. Aplicar migrações
echo "🗄️ Aplicando migrações..."
docker-compose exec -T web flask db upgrade

# 6. Testar
echo "🏥 Testando API..."
curl -f http://localhost:5000/api/simple/ping && echo "✅ API funcionando!" || echo "❌ API com problemas" 