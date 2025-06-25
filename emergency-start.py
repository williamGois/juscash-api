#!/usr/bin/env python
"""
Script de EMERGÊNCIA - Mínimas dependências
"""

import os
import sys

def emergency_install():
    """Instalar dependências básicas"""
    print("🚨 MODO EMERGÊNCIA - Instalando dependências críticas...")
    
    import subprocess
    
    packages = [
        "Flask==2.3.3",
        "SQLAlchemy==2.0.21", 
        "Flask-SQLAlchemy==3.0.5",
        "Flask-RESTX==1.3.0",
        "psycopg2-binary==2.9.7"
    ]
    
    for package in packages:
        try:
            print(f"📦 Instalando {package}...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", package, "--quiet"
            ], check=True)
            print(f"✅ {package} instalado")
        except Exception as e:
            print(f"❌ Erro ao instalar {package}: {e}")

def minimal_app():
    """Criar app Flask mínimo para teste"""
    print("🔧 Criando aplicação Flask mínima...")
    
    try:
        from flask import Flask, jsonify
        
        app = Flask(__name__)
        
        @app.route('/')
        def health():
            return jsonify({
                "status": "emergency_mode",
                "message": "JusCash API em modo de emergência",
                "timestamp": "2024-01-01T00:00:00Z"
            })
        
        @app.route('/health')
        def health_check():
            return jsonify({
                "database": "not_connected", 
                "status": "emergency",
                "environment": os.environ.get('ENVIRONMENT', 'unknown')
            })
        
        port = int(os.environ.get('PORT', 5000))
        print(f"🌐 Iniciando app de emergência na porta {port}")
        print("⚠️  ATENÇÃO: Este é um modo de emergência!")
        print("🔗 Health check: /health")
        
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ Erro crítico no app de emergência: {e}")
        sys.exit(1)

def debug_environment():
    """Mostrar todas as variáveis de ambiente"""
    print("🔍 DEBUG - Variáveis de Ambiente:")
    
    important_vars = [
        'DATABASE_URL',
        'REDIS_URL', 
        'ENVIRONMENT',
        'PORT',
        'SECRET_KEY'
    ]
    
    for var in important_vars:
        value = os.environ.get(var, 'NÃO DEFINIDA')
        if var == 'SECRET_KEY' and value != 'NÃO DEFINIDA':
            print(f"{var}: {value[:20]}...")
        elif var in ['DATABASE_URL', 'REDIS_URL'] and value != 'NÃO DEFINIDA':
            print(f"{var}: {value[:50]}...")
        else:
            print(f"{var}: {value}")
    
    print(f"🐍 Python: {sys.version}")
    print(f"📂 Working Directory: {os.getcwd()}")
    
    # Listar arquivos principais
    files = ['requirements.txt', 'run.py', 'config.py', 'create-tables.py']
    for file in files:
        exists = "✅" if os.path.exists(file) else "❌"
        print(f"{exists} {file}")

if __name__ == '__main__':
    print("🚨" * 30)
    print("🚨 JUSCASH API - MODO DE EMERGÊNCIA")
    print("🚨" * 30)
    
    debug_environment()
    
    print("\n⚠️  Este script é para DEBUG apenas!")
    print("⚠️  NÃO usar em produção!")
    
    try:
        import flask
        print("✅ Flask já disponível")
    except ImportError:
        print("❌ Flask não encontrado, instalando...")
        emergency_install()
    
    minimal_app() 