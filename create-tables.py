#!/usr/bin/env python
"""
Script específico para executar migrações no Railway
"""

import os
import sys
import time

def execute_migrations():
    """Executa as migrações Flask-Migrate no Railway"""
    print("🔧 Script de Migrações - JusCash API")
    
    try:
        # Configurar variáveis de ambiente
        os.environ['FLASK_APP'] = 'run.py'
        
        # Importar aplicação
        from app import create_app, db
        
        # Criar aplicação
        app = create_app()
        
        with app.app_context():
            print("🔍 Testando conexão PostgreSQL...")
            
            # Testar conexão
            with db.engine.connect() as conn:
                result = conn.execute(db.text('SELECT version()'))
                version = result.fetchone()[0]
                print(f"✅ PostgreSQL: {version[:60]}...")
            
            # Verificar tabelas atuais
            inspector = db.inspect(db.engine)
            tables_before = inspector.get_table_names()
            print(f"📊 Tabelas antes: {len(tables_before)} - {tables_before}")
            
            # Executar migrações
            print("🚀 Executando migrações Flask-Migrate...")
            
            try:
                from flask_migrate import upgrade
                
                # Verificar se diretório migrations existe
                if not os.path.exists('migrations'):
                    print("📁 Diretório migrations não encontrado, criando...")
                    from flask_migrate import init
                    init()
                
                # Executar upgrade das migrações
                print("⬆️ Aplicando migrações...")
                upgrade()
                print("✅ Migrações aplicadas com sucesso!")
                
            except Exception as migrate_error:
                print(f"⚠️ Erro nas migrações: {migrate_error}")
                print("🔄 Tentando método alternativo...")
                
                # Método alternativo: executar SQL da migração diretamente
                try:
                    # Criar extensões PostgreSQL
                    print("🔧 Criando extensões PostgreSQL...")
                    db.session.execute(db.text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
                    db.session.execute(db.text('CREATE EXTENSION IF NOT EXISTS "pg_trgm"'))
                    
                    # Importar modelo
                    from app.infrastructure.database.models import PublicacaoModel
                    print("📋 Modelo PublicacaoModel carregado")
                    
                    # Criar tabelas básicas
                    print("🔧 Criando tabelas...")
                    db.create_all()
                    
                    # Criar índices avançados
                    print("📊 Criando índices avançados...")
                    db.session.execute(db.text('''
                        CREATE INDEX IF NOT EXISTS idx_publicacoes_conteudo_gin 
                        ON publicacoes USING gin (conteudo_completo gin_trgm_ops)
                    '''))
                    db.session.execute(db.text('''
                        CREATE INDEX IF NOT EXISTS idx_publicacoes_autores_gin 
                        ON publicacoes USING gin (autores gin_trgm_ops)
                    '''))
                    db.session.execute(db.text('''
                        CREATE INDEX IF NOT EXISTS idx_publicacoes_advogados_gin 
                        ON publicacoes USING gin (advogados gin_trgm_ops)
                    '''))
                    
                    # Criar função e trigger para updated_at
                    print("⚡ Criando triggers...")
                    db.session.execute(db.text('''
                        CREATE OR REPLACE FUNCTION update_updated_at_column()
                        RETURNS TRIGGER AS $$
                        BEGIN
                            NEW.updated_at = CURRENT_TIMESTAMP;
                            RETURN NEW;
                        END;
                        $$ language 'plpgsql';
                    '''))
                    
                    db.session.execute(db.text('''
                        DROP TRIGGER IF EXISTS update_publicacoes_updated_at ON publicacoes;
                        CREATE TRIGGER update_publicacoes_updated_at 
                            BEFORE UPDATE ON publicacoes 
                            FOR EACH ROW 
                            EXECUTE FUNCTION update_updated_at_column();
                    '''))
                    
                    db.session.commit()
                    print("✅ Estrutura avançada criada!")
                    
                except Exception as alt_error:
                    print(f"❌ Erro no método alternativo: {alt_error}")
                    db.session.rollback()
            
            # Verificar resultado final
            time.sleep(2)
            tables_after = db.inspect(db.engine).get_table_names()
            print(f"📊 Tabelas depois: {len(tables_after)} - {tables_after}")
            
            # Verificar especificamente a tabela publicacoes
            if 'publicacoes' in tables_after:
                print("✅ Tabela 'publicacoes' criada com sucesso!")
                
                # Testar uma query simples
                result = db.session.execute(db.text('SELECT COUNT(*) FROM publicacoes'))
                count = result.scalar()
                print(f"📝 Registros na tabela: {count}")
                
                # Verificar índices
                indices_result = db.session.execute(db.text('''
                    SELECT indexname FROM pg_indexes 
                    WHERE tablename = 'publicacoes' AND indexname LIKE '%gin%'
                '''))
                gin_indices = [row[0] for row in indices_result]
                print(f"📊 Índices GIN: {len(gin_indices)}")
                
            else:
                print("❌ Tabela 'publicacoes' não foi criada!")
                return False
            
            print("🎉 Banco de dados configurado completamente!")
            return True
            
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        print(f"🔍 Tipo do erro: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = execute_migrations()
    sys.exit(0 if success else 1) 