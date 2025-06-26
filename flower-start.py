#!/usr/bin/env python3
import os
import sys
import time
import redis
from celery import Celery
from flower import Flower

def wait_for_redis(redis_url, max_attempts=15):
    """Aguarda Redis estar disponível"""
    attempts = 0
    while attempts < max_attempts:
        try:
            r = redis.from_url(redis_url)
            r.ping()
            print("Redis conectado!")
            return True
        except Exception as e:
            attempts += 1
            print(f"Redis não está pronto - tentativa {attempts}/{max_attempts}")
            if attempts >= max_attempts:
                print(f"Redis não conectou após {max_attempts} tentativas: {e}")
                return False
            time.sleep(2)
    return False

def main():
    redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    
    if not wait_for_redis(redis_url):
        sys.exit(1)
    
    app = Celery('juscash')
    app.config_from_object('config')
    
    flower_app = Flower(capp=app, address='0.0.0.0', port=5555)
    
    basic_auth = os.getenv('FLOWER_BASIC_AUTH')
    if basic_auth:
        flower_app.options.basic_auth = [basic_auth]
    
    print("Iniciando Flower na porta 5555...")
    flower_app.start()

if __name__ == '__main__':
    main() 