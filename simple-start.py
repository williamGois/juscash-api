#!/usr/bin/env python
"""
Script de inicialização simples - JusCash API
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

def create_basic_table_only(db):
    """Criar apenas a tabela básica sem índices avançados"""
    print("🔧 Criando tabela básica (sem extensões PostgreSQL)...")
    
    try:
        from sqlalchemy import text
        
        db.session.execute(text('''
            CREATE TABLE IF NOT EXISTS publicacoes (
                id SERIAL PRIMARY KEY,
                uuid UUID DEFAULT gen_random_uuid(),
                numero_processo VARCHAR(50) NOT NULL UNIQUE,
                data_disponibilizacao TIMESTAMP NOT NULL,
                autores TEXT NOT NULL,
                advogados TEXT NOT NULL,
                conteudo_completo TEXT NOT NULL,
                valor_principal_bruto NUMERIC(12,2),
                valor_principal_liquido NUMERIC(12,2),
                valor_juros_moratorios NUMERIC(12,2),
                honorarios_advocaticios NUMERIC(12,2),
                reu VARCHAR(255) NOT NULL DEFAULT 'Instituto Nacional do Seguro Social - INSS',
                status VARCHAR(20) NOT NULL DEFAULT 'nova',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT chk_status CHECK (status IN ('nova', 'lida', 'processada'))
            )
        '''))
        
        db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_publicacoes_numero_processo ON publicacoes(numero_processo)'))
        db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_publicacoes_data_disponibilizacao ON publicacoes(data_disponibilizacao)'))
        db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_publicacoes_status ON publicacoes(status)'))
        db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_publicacoes_reu ON publicacoes(reu)'))
        
        db.session.commit()
        print("✅ Tabela básica criada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela básica: {e}")
        db.session.rollback()
        return False

def main():
    """Iniciar aplicação de forma direta"""
    print("=" * 60)
    print("🚀 JusCash API - Inicialização Simples")
    print("=" * 60)
    
    if not check_dependencies():
        print("❌ Dependências faltando. Saindo...")
        sys.exit(1)
    
    print("⏳ Aguardando estabilização dos serviços...")
    time.sleep(5)
    
    port = int(os.environ.get('PORT', 5000))
    production_env = os.environ.get('PRODUCTION', False)
    
    print(f"🌐 Ambiente de produção: {production_env}")
    print(f"🚪 Porta configurada: {port}")
    
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
    
    with app.app_context():
        try:
            print("🔧 Configurando banco de dados...")
            
            database_url = os.environ.get('DATABASE_URL')
            if database_url:
                print(f"✅ DATABASE_URL configurada: {database_url[:50]}...")
            else:
                print("⚠️ DATABASE_URL não encontrada, usando padrão local")
            
            print("🔍 Testando conexão PostgreSQL...")
            with db.engine.connect() as conn:
                result = conn.execute(db.text('SELECT version()'))
                version = result.fetchone()[0]
                print(f"✅ PostgreSQL conectado: {version[:60]}...")
            
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Tabelas existentes: {len(tables)} - {tables}")
            
            if 'publicacoes' not in tables:
                print("🔧 Tabela publicacoes não encontrada...")
                
                try:
                    print("📋 Importando modelo SQLAlchemy...")
                    from app.infrastructure.database.models import PublicacaoModel
                    
                    print("🔧 Tentando criar com SQLAlchemy...")
                    db.create_all()
                    
                    tables_after = db.inspect(db.engine).get_table_names()
                    if 'publicacoes' in tables_after:
                        print("✅ Tabela criada com SQLAlchemy!")
                    else:
                        raise Exception("Tabela não foi criada")
                        
                except Exception as sqlalchemy_error:
                    print(f"⚠️ SQLAlchemy falhou: {sqlalchemy_error}")
                    print("🔄 Tentando método SQL direto...")
                    
                    if not create_basic_table_only(db):
                        print("❌ Falha ao criar tabela básica")
                        sys.exit(1)
                    
            else:
                print("✅ Tabela publicacoes já existe!")
            
            try:
                count = db.session.execute(db.text('SELECT COUNT(*) FROM publicacoes')).scalar()
                print(f"📝 Registros na tabela publicacoes: {count}")
            except Exception as count_error:
                print(f"⚠️ Aviso ao contar registros: {count_error}")
            
            print("✅ Banco de dados configurado com sucesso!")
            
        except Exception as db_error:
            print(f"⚠️ Aviso configuração banco: {db_error}")
            print(f"🔍 Tipo do erro: {type(db_error).__name__}")
            
            if "does not exist" in str(db_error).lower() and "operator class" in str(db_error).lower():
                print("⚠️ Erro de extensão PostgreSQL - usando tabela básica")
                try:
                    if create_basic_table_only(db):
                        print("✅ Tabela básica criada, continuando...")
                    else:
                        print("❌ Não foi possível criar nem tabela básica")
                        sys.exit(1)
                except:
                    print("❌ Erro crítico, não pode continuar")
                    sys.exit(1)
            elif "connection" in str(db_error).lower():
                print("❌ Erro crítico de conexão, não pode continuar")
                sys.exit(1)
            else:
                print("⚠️ Erro não crítico, continuando...")
    
    print(f"🌐 Iniciando servidor Flask na porta {port}")
    print("📚 Documentação Swagger disponível em: /docs/")
    print("⚡ API JusCash pronta para uso!")
    print("💡 Para funcionalidades avançadas, execute create-tables.py")
    print("=" * 60)
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as server_error:
        print(f"❌ Erro ao iniciar servidor: {server_error}")
        sys.exit(1)

if __name__ == '__main__':
    main() 