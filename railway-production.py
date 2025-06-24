#!/usr/bin/env python3
"""
Script de produção otimizado para Railway
"""

import os
import sys
from app import create_app, db

def main():
    """Função principal para produção"""
    
    # Verificar variáveis obrigatórias
    required_vars = ['DATABASE_URL', 'REDIS_URL', 'SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Variáveis obrigatórias não definidas: {missing_vars}")
        sys.exit(1)
    
    # Criar aplicação
    app = create_app('railway')
    
    # Verificar conectividade
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print("✅ Conectividade verificada!")
        except Exception as e:
            print(f"❌ Erro de conectividade: {e}")
            sys.exit(1)
    
    # Obter porta do Railway
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🚀 Iniciando aplicação na porta {port}")
    
    # Executar com gunicorn em produção
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        from gunicorn.app.wsgiapp import WSGIApplication
        
        sys.argv = [
            'gunicorn',
            '--bind', f'0.0.0.0:{port}',
            '--workers', '1',  # Railway tem limitações de memória
            '--worker-class', 'sync',
            '--worker-connections', '1000',
            '--timeout', '120',
            '--keepalive', '5',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            '--preload',
            'run:app'
        ]
        
        WSGIApplication().run()
    else:
        # Desenvolvimento local
        app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main() 