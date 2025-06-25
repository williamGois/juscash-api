#!/bin/bash

echo "🚀 Iniciando JusCash API no Railway..."

# Definir variáveis de ambiente
export FLASK_APP=run.py
export PYTHONPATH=/app

# Aguardar serviços estarem prontos
echo "⏳ Aguardando serviços..."
sleep 10

# Verificar se Flask-Migrate está disponível
echo "🔍 Verificando Flask-Migrate..."
python -c "
try:
    import flask_migrate
    print('✅ Flask-Migrate disponível')
except ImportError:
    print('❌ Flask-Migrate não encontrado')
    print('📦 Instalando Flask-Migrate...')
    import subprocess
    subprocess.run(['pip', 'install', 'Flask-Migrate==4.0.5'])
    print('✅ Flask-Migrate instalado')
"

# Executar migrações usando Python diretamente (método robusto)
echo "🔧 Executando migrações do banco de dados..."
python -c "
import os
import sys
from app import create_app, db

print('📊 Configurando aplicação Flask...')
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

with app.app_context():
    try:
        print('🔍 Testando conexão com banco...')
        with db.engine.connect() as conn:
            result = conn.execute(db.text('SELECT 1'))
            print('✅ Conexão PostgreSQL OK!')
        
        print('📋 Verificando estrutura do banco...')
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f'📊 Tabelas existentes: {len(tables)}')
        
        if 'publicacoes' not in tables:
            print('🔧 Criando tabelas do banco...')
            db.create_all()
            print('✅ Tabelas criadas com sucesso!')
        else:
            print('✅ Tabela publicacoes já existe')
            
        # Verificar se há dados
        try:
            from app.infrastructure.database.models import PublicacaoModel
            count = db.session.query(PublicacaoModel).count()
            print(f'📝 Publicações no banco: {count}')
        except Exception as e:
            print(f'⚠️ Aviso ao contar registros: {e}')
        
        print('✅ Banco de dados configurado com sucesso!')
        
    except Exception as e:
        print(f'❌ Erro na configuração do banco: {e}')
        print('💡 Tentando criar tabelas básicas...')
        try:
            db.create_all()
            print('✅ Tabelas básicas criadas!')
        except Exception as e2:
            print(f'❌ Falha crítica: {e2}')
            sys.exit(1)
"

# Verificar se configuração foi bem-sucedida
if [ $? -eq 0 ]; then
    echo "✅ Banco de dados configurado!"
else
    echo "❌ Falha na configuração do banco"
    exit 1
fi

# Verificar conectividade final
echo "🔍 Teste final de conectividade..."
python -c "
from app import create_app, db
import os

try:
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            result = conn.execute(db.text('SELECT version()'))
            version = result.fetchone()[0]
            print(f'✅ PostgreSQL conectado: {version[:50]}...')
        
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f'📊 Total de tabelas: {len(tables)}')
        
        if 'publicacoes' in tables:
            print('✅ Tabela principal (publicacoes) existe')
        
except Exception as e:
    print(f'❌ Erro na conectividade final: {e}')
    exit(1)
"

echo "🎉 Iniciando aplicação..."
exec python run.py 