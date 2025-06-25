#!/bin/bash

echo "🚀 Iniciando JusCash API no Railway..."

# Definir variáveis de ambiente
export FLASK_APP=run.py
export PYTHONPATH=/app

# Aguardar serviços estarem prontos
echo "⏳ Aguardando serviços..."
sleep 5

# Executar migrações usando Python diretamente
echo "🔧 Executando migrações do banco de dados..."
python -c "
import os
from app import create_app, db
from flask_migrate import upgrade
import sys

try:
    app = create_app()
    with app.app_context():
        print('📊 Aplicando migrações...')
        upgrade()
        print('✅ Migrações aplicadas com sucesso!')
except Exception as e:
    print(f'❌ Erro nas migrações: {e}')
    sys.exit(1)
"

# Verificar se migrações foram bem-sucedidas
if [ $? -eq 0 ]; then
    echo "✅ Banco de dados configurado!"
else
    echo "❌ Falha na configuração do banco"
    exit 1
fi

# Verificar conectividade
echo "🔍 Testando conectividade final..."
python -c "
from app import create_app, db
import os
try:
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            result = conn.execute(db.text('SELECT 1'))
            print('✅ Banco conectado e funcionando!')
        
        # Verificar tabelas
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f'📊 Tabelas encontradas: {len(tables)}')
        
except Exception as e:
    print(f'❌ Erro na conectividade: {e}')
    exit(1)
"

echo "🎉 Iniciando aplicação..."
exec python run.py 