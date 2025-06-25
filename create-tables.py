#!/usr/bin/env python
"""
Script específico para criar tabelas no Railway
"""

import os
import sys
import time

def force_create_tables():
    """Força a criação das tabelas do banco"""
    print("🔧 Script de Criação de Tabelas - JusCash")
    
    try:
        # Importar app
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
            
            # Importar modelo explicitamente
            from app.infrastructure.database.models import PublicacaoModel
            print("📋 Modelo PublicacaoModel carregado")
            
            # Verificar tabelas atuais
            inspector = db.inspect(db.engine)
            tables_before = inspector.get_table_names()
            print(f"📊 Tabelas antes: {tables_before}")
            
            # Forçar criação de todas as tabelas
            print("🔧 Forçando criação de tabelas...")
            db.create_all()
            
            # Verificar se foram criadas
            time.sleep(2)  # Aguardar um pouco
            tables_after = db.inspect(db.engine).get_table_names()
            print(f"📊 Tabelas depois: {tables_after}")
            
            # Verificar especificamente a tabela publicacoes
            if 'publicacoes' in tables_after:
                print("✅ Tabela 'publicacoes' criada com sucesso!")
                
                # Testar uma query simples
                result = db.session.execute(db.text('SELECT COUNT(*) FROM publicacoes'))
                count = result.scalar()
                print(f"📝 Registros na tabela: {count}")
                
            else:
                print("❌ Tabela 'publicacoes' não foi criada!")
                return False
            
            print("✅ Todas as tabelas configuradas com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        print(f"🔍 Tipo do erro: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = force_create_tables()
    sys.exit(0 if success else 1) 