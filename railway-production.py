#!/usr/bin/env python
"""
Script de produção Railway - JusCash API
Configuração robusta do banco + inicialização da aplicação
"""

import os
import sys
import time

def setup_database():
    """Configurar banco de dados de forma robusta"""
    print("🔧 Configurando banco de dados...")
    
    try:
        from app import create_app, db
        
        # Criar aplicação
        app = create_app(os.getenv('FLASK_CONFIG') or 'default')
        
        with app.app_context():
            # Testar conexão
            print("🔍 Testando conexão PostgreSQL...")
            with db.engine.connect() as conn:
                result = conn.execute(db.text('SELECT version()'))
                version = result.fetchone()[0]
                print(f"✅ PostgreSQL: {version[:60]}...")
            
            # Verificar estrutura
            print("📋 Verificando estrutura do banco...")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Tabelas existentes: {len(tables)}")
            
            # Criar tabelas se necessário
            if 'publicacoes' not in tables:
                print("🔧 Criando tabelas...")
                db.create_all()
                print("✅ Tabelas criadas!")
            else:
                print("✅ Estrutura do banco OK")
            
            # Verificar dados
            try:
                from app.infrastructure.database.models import PublicacaoModel
                count = db.session.query(PublicacaoModel).count()
                print(f"📝 Registros no banco: {count}")
            except Exception as e:
                print(f"⚠️ Aviso: {e}")
            
            print("✅ Banco configurado com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro na configuração do banco: {e}")
        return False

def start_application():
    """Iniciar aplicação Flask"""
    print("🚀 Iniciando aplicação JusCash...")
    
    try:
        from app import create_app
        
        # Configurações Railway
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'
        
        # Criar app
        app = create_app(os.getenv('FLASK_CONFIG') or 'default')
        
        print(f"🌐 Servidor iniciando em {host}:{port}")
        print("📚 Swagger docs disponível em /docs/")
        print("⚡ API pronta para uso!")
        
        # Iniciar servidor
        app.run(host=host, port=port, debug=False)
        
    except Exception as e:
        print(f"❌ Erro ao iniciar aplicação: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    print("🚀 JusCash API - Inicialização Railway")
    print("=" * 50)
    
    # Aguardar serviços
    print("⏳ Aguardando serviços Railway...")
    time.sleep(8)
    
    # Configurar banco
    if not setup_database():
        print("❌ Falha na configuração do banco")
        sys.exit(1)
    
    # Iniciar aplicação
    start_application()

if __name__ == '__main__':
    main() 