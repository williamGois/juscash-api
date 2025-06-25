#!/usr/bin/env python3

import os
import requests
import time
from datetime import datetime

def test_api_connection():
    """Testa conectividade básica da API"""
    try:
        response = requests.get('http://localhost:5000/api/publicacoes/stats', timeout=10)
        print(f"✅ API respondendo: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Erro na API: {e}")
        return False

def test_celery_task():
    """Testa se as tasks do Celery estão funcionando"""
    try:
        data = {
            "data_inicio": "2024-10-01T00:00:00",
            "data_fim": "2024-10-01T23:59:59"
        }
        
        response = requests.post(
            'http://localhost:5000/api/scraping/extract',
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get('task_id')
            print(f"✅ Task criada: {task_id}")
            
            time.sleep(2)
            
            status_response = requests.get(
                f'http://localhost:5000/api/scraping/status/{task_id}',
                timeout=10
            )
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                print(f"✅ Status da task: {status_result}")
                return True
            else:
                print(f"❌ Erro ao verificar status: {status_response.status_code}")
                return False
        else:
            print(f"❌ Erro ao criar task: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de Celery: {e}")
        return False

def test_selenium_config():
    """Testa se o Selenium está configurado corretamente"""
    try:
        from app.infrastructure.scraping.dje_scraper import DJEScraper
        
        print("🔄 Testando configuração do Selenium...")
        scraper = DJEScraper()
        print("✅ Driver do Selenium configurado com sucesso")
        scraper.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro no Selenium: {e}")
        return False

def main():
    print("🧪 Executando testes de correção...\n")
    
    tests = [
        ("API Connection", test_api_connection),
        ("Celery Task", test_celery_task),
        ("Selenium Config", test_selenium_config)
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
    else:
        print("⚠️  Alguns problemas ainda precisam ser resolvidos")

if __name__ == "__main__":
    main() 