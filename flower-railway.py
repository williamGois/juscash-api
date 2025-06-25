#!/usr/bin/env python
"""
Script simples para Flower no Railway
"""
import os
import subprocess
import sys

def main():
    print("🌸 Flower Railway Starter")
    
    # Construir URL Redis usando variáveis Railway
    redis_host = os.environ.get('REDISHOST', 'redis.railway.internal')
    redis_port = os.environ.get('REDISPORT', '6379')
    redis_user = os.environ.get('REDISUSER', 'default')
    redis_password = os.environ.get('REDISPASSWORD', '')
    
    # URL do Redis
    if redis_password:
        redis_url = f"redis://{redis_user}:{redis_password}@{redis_host}:{redis_port}"
    else:
        # Fallback para Railway
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    print(f"🔗 Redis: redis://{redis_user}:***@{redis_host}:{redis_port}")
    
    # Comando Flower direto
    cmd = [
        'flower',
        '-A', 'celery_worker.celery',
        '--broker=' + redis_url,
        '--port=5555',
        '--basic_auth=admin:admin123',
        '--logging=info'
    ]
    
    print("🚀 Executando:", ' '.join(cmd[:3] + ['--broker=***', '--port=5555']))
    
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("📦 Instalando Flower...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'flower==2.0.1'])
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 