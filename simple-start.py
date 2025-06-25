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
            
            # Teste de conexão
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print("✅ PostgreSQL conectado!")
            
            # Criar tabelas
            db.create_all()
            print("✅ Tabelas configuradas!")
            
        except Exception as e:
            print(f"⚠️ Aviso configuração banco: {e}")
            # Continuar mesmo assim
    
    print(f"🌐 Iniciando servidor na porta {port}")
    print("📚 Docs: /docs/")
    
    # Iniciar aplicação
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main() 