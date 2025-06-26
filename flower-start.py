#!/usr/bin/env python3
import os
import sys
import time
import redis

def wait_for_redis(redis_url, max_attempts=5):
    """Aguarda Redis estar disponível"""
    for attempt in range(max_attempts):
        try:
            r = redis.from_url(redis_url)
            r.ping()
            print("✅ Redis conectado!")
            return True
        except Exception as e:
            print(f"⏳ Aguardando Redis... tentativa {attempt + 1}/{max_attempts}")
            if attempt == max_attempts - 1:
                print(f"❌ Redis não conectou após {max_attempts} tentativas: {e}")
                return False
            time.sleep(3)
    return False

def main():
    redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    
    print("🌸 Iniciando Flower...")
    
    if not wait_for_redis(redis_url):
        sys.exit(1)
    
    print("📱 Carregando configuração do Celery...")
    try:
        from celery_worker import celery
        print("✅ Celery configurado!")
    except ImportError as e:
        print(f"❌ Erro ao importar celery_worker: {e}")
        sys.exit(1)
    
    print("🚀 Iniciando Flower na porta 5555...")
    
    from flower.command import FlowerCommand
    flower_command = FlowerCommand()
    
    args = [
        '--broker=' + redis_url,
        '--address=0.0.0.0',
        '--port=5555'
    ]
    
    basic_auth = os.getenv('FLOWER_BASIC_AUTH')
    if basic_auth:
        args.append(f'--basic_auth={basic_auth}')
    
    flower_command.run_from_argv(['flower'] + args)

if __name__ == '__main__':
    main() 