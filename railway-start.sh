#!/bin/bash

echo "🚀 Iniciando JusCash API no Railway..."

# Definir variáveis de ambiente
export FLASK_APP=run.py
export PYTHONPATH=/app

# Aguardar serviços estarem prontos
echo "⏳ Aguardando serviços..."
sleep 5

# Executar migrações
echo "🔧 Executando migrações do banco de dados..."
flask upgrade-db

# Verificar se migrações foram bem-sucedidas
if [ $? -eq 0 ]; then
    echo "✅ Migrações aplicadas com sucesso!"
else
    echo "❌ Erro nas migrações"
    exit 1
fi

# Verificar conectividade
echo "🔍 Testando conectividade..."
python -c "
from app import create_app, db
import os
try:
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            conn.execute(db.text('SELECT 1'))
    print('✅ Banco conectado!')
except Exception as e:
    print(f'❌ Erro: {e}')
    exit(1)
"

echo "🎉 Iniciando aplicação..."
exec python run.py 