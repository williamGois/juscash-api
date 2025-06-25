#!/usr/bin/env python3

import os
import sys

def test_celery_config():
    """Testa se a configuração do Celery está pegando a REDIS_URL corretamente"""
    
    print("🧪 Testando configuração do Celery...")
    
    try:
        # Simular ambiente Railway
        os.environ['REDIS_URL'] = 'redis://default:password@redis.railway.internal:6379'
        os.environ['RAILWAY_ENVIRONMENT'] = 'production'
        
        from app import create_app, make_celery
        
        app = create_app('railway')
        celery = make_celery(app)
        
        print(f"✅ App config REDIS_URL: {app.config.get('REDIS_URL')}")
        print(f"✅ Celery broker_url: {celery.conf.broker_url}")
        print(f"✅ Celery result_backend: {celery.conf.result_backend}")
        
        # Verificar se as URLs estão corretas
        if celery.conf.broker_url and celery.conf.result_backend:
            if str(celery.conf.broker_url) != 'None' and str(celery.conf.result_backend) != 'None':
                print("✅ Configuração do Celery está correta!")
                return True
            else:
                print("❌ URLs do Celery estão como None")
                return False
        else:
            print("❌ Configuração do Celery não foi definida")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    print("🔧 Teste de Correção do Redis/Celery\n")
    
    if test_celery_config():
        print("\n🎉 Correção funcionou! O Celery deve funcionar no Railway agora.")
        print("\n💡 Próximos passos:")
        print("1. Faça deploy da correção no Railway")
        print("2. Teste: curl https://sua-app.railway.app/api/scraping/debug")
        print("3. Verifique se broker_url e result_backend não são mais null")
        print("4. Teste o scraping: POST /api/scraping/extract")
    else:
        print("\n❌ Ainda há problemas na configuração.")
        print("Verifique os logs acima para mais detalhes.")

if __name__ == "__main__":
    main() 