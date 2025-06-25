#!/usr/bin/env python
"""
Script ultra-simples para Railway - JusCash API
"""

import os
import sys
import time

def check_dependencies():
    """Verificar se todas as dependências estão disponíveis"""
    print("🔍 Verificando dependências críticas...")
    
    missing = []
    
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except ImportError:
        missing.append("flask")
        
    try:
        import sqlalchemy  
        print(f"✅ SQLAlchemy {sqlalchemy.__version__}")
    except ImportError:
        missing.append("sqlalchemy")
        
    try:
        import flask_sqlalchemy
        print(f"✅ Flask-SQLAlchemy {flask_sqlalchemy.__version__}")
    except ImportError:
        missing.append("flask-sqlalchemy")
        
    try:
        import flask_restx
        print(f"✅ Flask-RESTX {flask_restx.__version__}")
    except ImportError:
        missing.append("flask-restx")
    
    if missing:
        print(f"❌ Dependências faltando: {', '.join(missing)}")
        return False
    
    print("✅ Todas as dependências encontradas!")
    return True

def main():
    """Iniciar aplicação de forma direta"""
    print("=" * 60)
    print("🚀 JusCash API - Inicialização Simples Railway")
    print("=" * 60)
    
    # Verificar dependências primeiro
    if not check_dependencies():
        print("❌ Dependências faltando. Saindo...")
        sys.exit(1)
    
    # Aguardar um pouco para estabilizar
    print("⏳ Aguardando estabilização dos serviços...")
    time.sleep(5)
    
    # Configurar variáveis
    port = int(os.environ.get('PORT', 5000))
    railway_env = os.environ.get('RAILWAY_ENVIRONMENT', False)
    
    print(f"🌐 Ambiente Railway: {railway_env}")
    print(f"🚪 Porta configurada: {port}")
    
    # Importar e criar app
    try:
        print("📦 Importando módulos da aplicação...")
        from app import create_app, db
        print("✅ Módulos importados com sucesso!")
    except Exception as import_error:
        print(f"❌ Erro ao importar aplicação: {import_error}")
        print(f"🔍 Tipo do erro: {type(import_error).__name__}")
        sys.exit(1)
    
    print("📊 Criando aplicação Flask...")
    try:
        app = create_app()
        print("✅ Aplicação Flask criada!")
    except Exception as app_error:
        print(f"❌ Erro ao criar aplicação: {app_error}")
        sys.exit(1)
    
    # Configurar banco (sem Flask-Migrate)
    with app.app_context():
        try:
            print("🔧 Configurando banco de dados...")
            
            # Testar variáveis de ambiente
            database_url = os.environ.get('DATABASE_URL')
            if database_url:
                print(f"✅ DATABASE_URL configurada: {database_url[:50]}...")
            else:
                print("⚠️ DATABASE_URL não encontrada, usando padrão local")
            
            # IMPORTANTE: Importar modelo ANTES de db.create_all()
            from app.infrastructure.database.models import PublicacaoModel
            print("📋 Modelo PublicacaoModel importado")
            
            # Teste de conexão
            print("🔍 Testando conexão PostgreSQL...")
            with db.engine.connect() as conn:
                result = conn.execute(db.text('SELECT version()'))
                version = result.fetchone()[0]
                print(f"✅ PostgreSQL conectado: {version[:60]}...")
            
            # Verificar se tabela já existe
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Tabelas existentes: {len(tables)} - {tables}")
            
            if 'publicacoes' not in tables:
                print("🔧 Tabela publicacoes não encontrada, criando...")
                db.create_all()
                
                # Verificar se foi criada
                tables_after = db.inspect(db.engine).get_table_names()
                if 'publicacoes' in tables_after:
                    print("✅ Tabela publicacoes criada com sucesso!")
                else:
                    print("❌ Falha ao criar tabela publicacoes")
                    
            else:
                print("✅ Tabela publicacoes já existe!")
            
            # Verificar se tabela está acessível
            try:
                count = db.session.execute(db.text('SELECT COUNT(*) FROM publicacoes')).scalar()
                print(f"📝 Registros na tabela publicacoes: {count}")
            except Exception as count_error:
                print(f"⚠️ Aviso ao contar registros: {count_error}")
            
            print("✅ Banco de dados configurado com sucesso!")
            
        except Exception as db_error:
            print(f"⚠️ Aviso configuração banco: {db_error}")
            print(f"🔍 Tipo do erro: {type(db_error).__name__}")
            
            # Verificar se é erro crítico ou pode continuar
            if "does not exist" in str(db_error).lower() or "connection" in str(db_error).lower():
                print("❌ Erro crítico de banco, não pode continuar")
                sys.exit(1)
            else:
                print("⚠️ Erro não crítico, continuando...")
    
    print(f"🌐 Iniciando servidor Flask na porta {port}")
    print("📚 Documentação Swagger disponível em: /docs/")
    print("⚡ API JusCash pronta para uso!")
    print("=" * 60)
    
    try:
        # Iniciar aplicação
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as server_error:
        print(f"❌ Erro ao iniciar servidor: {server_error}")
        sys.exit(1)

if __name__ == '__main__':
    main() 