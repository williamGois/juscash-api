#!/bin/bash

echo "⏰ Iniciando Celery Beat no Railway..."

# Definir variáveis de ambiente
export FLASK_APP=run.py
export PYTHONPATH=/app

# Aguardar mais tempo para que worker esteja pronto
echo "⏳ Aguardando worker..."
sleep 15

# Testar conectividade
python -c "
from app import create_app, db
try:
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            conn.execute(db.text('SELECT 1'))
    print('✅ Beat: Banco conectado!')
except Exception as e:
    print(f'❌ Beat: Erro de conexão: {e}')
    exit(1)
"

echo "🎉 Iniciando agendador..."
exec celery -A celery_worker.celery beat --loglevel=info 