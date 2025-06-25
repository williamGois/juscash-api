#!/usr/bin/env python3

import os
import sys
import traceback

def test_celery_config():
    """Testa se a configuração do Celery está correta"""
    try:
        print("🔄 Testando configuração do Celery...")
        
        from app import create_app, make_celery
        
        app = create_app('development')
        celery = make_celery(app)
        
        print(f"✅ Celery broker: {celery.conf.broker_url}")
        print(f"✅ Celery backend: {celery.conf.result_backend}")
        
        if 'redis://' in str(celery.conf.broker_url):
            print("✅ Redis configurado corretamente como broker")
            return True
        else:
            print("❌ Redis não configurado corretamente")
            return False
            
    except Exception as e:
        print(f"❌ Erro na configuração do Celery: {e}")
        traceback.print_exc()
        return False

def test_selenium_imports():
    """Testa se as importações do Selenium estão funcionando"""
    try:
        print("🔄 Testando importações do Selenium...")
        
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("✅ Importações do Selenium OK")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro no Selenium: {e}")
        return False

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    try:
        print("🔄 Testando conexão com o banco...")
        
        from app import create_app, db
        
        app = create_app('development')
        
        with app.app_context():
            result = db.session.execute(db.text('SELECT 1')).scalar()
            if result == 1:
                print("✅ Conexão com PostgreSQL OK")
                return True
            else:
                print("❌ Problema na conexão")
                return False
                
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        return False

def test_tasks_import():
    """Testa se as tasks podem ser importadas"""
    try:
        print("🔄 Testando importação das tasks...")
        
        from app.tasks.scraping_tasks import (
            extract_publicacoes_task,
            extract_daily_publicacoes,
            extract_full_period_publicacoes
        )
        
        print("✅ Tasks importadas com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao importar tasks: {e}")
        traceback.print_exc()
        return False

def main():
    print("🧪 Executando testes de correção da JusCash API...\n")
    
    tests = [
        ("Celery Config", test_celery_config),
        ("Selenium Imports", test_selenium_imports),
        ("Database Connection", test_database_connection),
        ("Tasks Import", test_tasks_import)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Testando {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Falha crítica em {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n📊 Resumo dos Testes:")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:20} | {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n🎯 Resultado Final: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todas as correções funcionaram!")
        print("\n💡 Próximos passos:")
        print("1. Execute: docker-compose up --build")
        print("2. Teste a API: http://localhost:5000/docs")
        print("3. Teste o Flower: http://localhost:5555")
    else:
        print("⚠️  Alguns problemas ainda precisam ser resolvidos")

if __name__ == "__main__":
    main() 