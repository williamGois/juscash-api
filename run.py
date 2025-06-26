import os
import sys
import traceback
from app import create_app, db

def main():
    try:
        print("=== INICIANDO APLICAÇÃO JUSCASH ===")
        
        # Configuração de ambiente
        flask_env = os.getenv('FLASK_ENV', 'production')
        print(f"FLASK_ENV: {flask_env}")
        
        # Verificar variáveis essenciais
        database_url = os.getenv('DATABASE_URL')
        redis_url = os.getenv('REDIS_URL')
        secret_key = os.getenv('SECRET_KEY')
        
        print(f"DATABASE_URL: {database_url[:30]}..." if database_url else "DATABASE_URL: None")
        print(f"REDIS_URL: {redis_url[:30]}..." if redis_url else "REDIS_URL: None")
        print(f"SECRET_KEY: {'SET' if secret_key else 'NOT SET'}")
        
        # Criar aplicação
        print("Criando aplicação Flask...")
        app = create_app(flask_env)
        print("✓ Aplicação Flask criada")
        
        # Configurar banco de dados
        print("Configurando banco de dados...")
        with app.app_context():
            try:
                # Testar conexão com banco
                db.engine.execute('SELECT 1')
                print("✓ Conexão com banco de dados OK")
                
                # Criar tabelas se necessário
                db.create_all()
                print("✓ Tabelas criadas/verificadas")
                
            except Exception as db_error:
                print(f"⚠️ Erro no banco de dados: {db_error}")
                print("Continuando sem configuração do banco...")
        
        print("=== APLICAÇÃO PRONTA PARA INICIAR ===")
        print("Iniciando servidor Flask...")
        
        # Iniciar aplicação
        app.run(
            host='0.0.0.0', 
            port=5000,
            debug=False,
            threaded=True
        )
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO na inicialização: {e}")
        print("Traceback completo:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main() 