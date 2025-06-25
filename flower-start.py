#!/usr/bin/env python
"""
Script para iniciar Flower com configuração Railway
"""
import os
import sys
from celery import Celery

def start_flower():
    # Obter URL do Redis
    redis_url = os.environ.get('REDIS_URL')
    if not redis_url:
        print("❌ REDIS_URL não configurada!")
        sys.exit(1)
    
    print(f"🌸 Iniciando Flower...")
    print(f"🔗 Redis URL: {redis_url[:30]}...")
    
    # Configurar Celery app
    celery_app = Celery('celery_worker')
    celery_app.config_from_object({
        'broker_url': redis_url,
        'result_backend': redis_url,
    })
    
    # Iniciar Flower
    try:
        from flower.command import FlowerCommand
        flower = FlowerCommand()
        
        # Argumentos do Flower
        sys.argv = [
            'flower',
            '--broker=' + redis_url,
            '--port=5555',
            '--basic_auth=admin:admin123',
            '--logging=info'
        ]
        
        print("🚀 Flower iniciando na porta 5555...")
        flower.execute_from_commandline()
        
    except ImportError:
        print("❌ Flower não instalado! Instalando...")
        os.system("pip install flower")
        start_flower()
    except Exception as e:
        print(f"❌ Erro ao iniciar Flower: {e}")
        sys.exit(1)

if __name__ == '__main__':
    start_flower() 