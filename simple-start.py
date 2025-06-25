#!/usr/bin/env python
"""
Script ultra-simples para Railway - JusCash API
"""

import os
import time

def main():
    """Iniciar aplicação de forma direta"""
    print("🚀 JusCash API - Inicialização Simples")
    
    # Aguardar um pouco
    time.sleep(5)
    
    # Configurar variáveis
    port = int(os.environ.get('PORT', 5000))
    
    # Importar e criar app
    from app import create_app, db
    
    print("📊 Criando aplicação...")
    app = create_app()
    
    # Configurar banco (sem Flask-Migrate)
    with app.app_context():
        try:
            print("🔧 Configurando banco...")
            
            # IMPORTANTE: Importar modelo ANTES de db.create_all()
            from app.infrastructure.database.models import PublicacaoModel
            print("📋 Modelo PublicacaoModel importado")
            
            # Teste de conexão
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print("✅ PostgreSQL conectado!")
            
            # Verificar se tabela já existe
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Tabelas existentes: {tables}")
            
            if 'publicacoes' not in tables:
                print("🔧 Criando tabela publicacoes...")
                db.create_all()
                print("✅ Tabela publicacoes criada!")
            else:
                print("✅ Tabela publicacoes já existe!")
            
            # Verificar se foi criada
            tables_after = db.inspect(db.engine).get_table_names()
            print(f"📊 Tabelas após criação: {tables_after}")
            
        except Exception as e:
            print(f"⚠️ Aviso configuração banco: {e}")
            print(f"🔍 Tipo do erro: {type(e).__name__}")
            # Continuar mesmo assim
    
    print(f"🌐 Iniciando servidor na porta {port}")
    print("📚 Docs: /docs/")
    
    # Iniciar aplicação
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main() 