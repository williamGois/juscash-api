#!/bin/bash

echo "🔧 Iniciando Celery Worker no Railway..."

# Definir variáveis de ambiente
export FLASK_APP=run.py
export PYTHONPATH=/app

# Aguardar um pouco para que o banco esteja pronto
echo "⏳ Aguardando banco de dados..."
sleep 10

# Testar conectividade
python -c "
from app import create_app, db
try:
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            conn.execute(db.text('SELECT 1'))
    print('✅ Worker: Banco conectado!')
except Exception as e:
    print(f'❌ Worker: Erro de conexão: {e}')
    exit(1)
"

echo "🎉 Iniciando worker..."
exec celery -A celery_worker.celery worker --loglevel=info --concurrency=1 