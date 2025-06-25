#!/usr/bin/env python
"""
Script para iniciar Flower com configuração Railway
"""
import os
import sys

def debug_environment():
    """Debug das variáveis de ambiente"""
    print("🔍 DEBUG - Variáveis de Ambiente:")
    print(f"REDIS_URL: {os.environ.get('REDIS_URL', 'NÃO DEFINIDA')}")
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'NÃO DEFINIDA')}")
    print(f"RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'NÃO DEFINIDA')}")
    
    # Listar todas as variáveis que começam com REDIS
    redis_vars = {k: v for k, v in os.environ.items() if 'REDIS' in k.upper()}
    print(f"🔗 Variáveis Redis encontradas: {redis_vars}")
    
    # Listar todas as variáveis Railway
    railway_vars = {k: v for k, v in os.environ.items() if 'RAILWAY' in k.upper()}
    print(f"🚂 Variáveis Railway: {railway_vars}")

def get_redis_url():
    """Obter URL do Redis com múltiplas tentativas"""
    
    # Tentativa 1: REDIS_URL direta
    redis_url = os.environ.get('REDIS_URL')
    if redis_url:
        print(f"✅ REDIS_URL encontrada: {redis_url[:50]}...")
        return redis_url
    
    # Tentativa 2: Variáveis separadas do Railway
    redis_host = os.environ.get('REDISHOST')
    redis_port = os.environ.get('REDISPORT', '6379')
    redis_user = os.environ.get('REDISUSER', 'default')
    redis_password = os.environ.get('REDISPASSWORD')
    
    if redis_host and redis_password:
        redis_url = f"redis://{redis_user}:{redis_password}@{redis_host}:{redis_port}"
        print(f"✅ Redis URL construída: redis://{redis_user}:***@{redis_host}:{redis_port}")
        return redis_url
    
    # Tentativa 3: Railway internal URL
    railway_redis = os.environ.get('RAILWAY_REDIS_URL')
    if railway_redis:
        print(f"✅ Railway Redis URL: {railway_redis[:50]}...")
        return railway_redis
    
    # Tentativa 4: Verificar se estamos em desenvolvimento local
    if not os.environ.get('RAILWAY_ENVIRONMENT'):
        local_url = 'redis://localhost:6379/0'
        print(f"⚠️ Usando Redis local: {local_url}")
        return local_url
    
    print("❌ Nenhuma URL Redis encontrada!")
    return None

def start_flower():
    """Iniciar Flower com configuração robusta"""
    
    print("🌸 Iniciando Flower no Railway...")
    
    # Debug do ambiente
    debug_environment()
    
    # Obter URL do Redis
    redis_url = get_redis_url()
    
    if not redis_url:
        print("❌ REDIS_URL não pôde ser determinada!")
        print("💡 Verifique se as variáveis estão configuradas no Railway:")
        print("   - REDIS_URL=${{Redis.REDIS_URL}}")
        print("   - Ou as variáveis individuais do Redis")
        sys.exit(1)
    
    print(f"🔗 Usando Redis: {redis_url[:30]}...")
    
    try:
        # Tentar importar Flower
        from flower.command import FlowerCommand
        from celery import Celery
        
        # Configurar Celery app com a URL correta
        celery_app = Celery('celery_worker')
        celery_app.config_from_object({
            'broker_url': redis_url,
            'result_backend': redis_url,
            'task_serializer': 'json',
            'accept_content': ['json'],
            'result_serializer': 'json',
        })
        
        # Testar conexão antes de iniciar Flower
        print("🔍 Testando conexão Redis...")
        try:
            # Importar Redis e testar ping
            import redis
            r = redis.from_url(redis_url)
            r.ping()
            print("✅ Conexão Redis OK!")
        except Exception as e:
            print(f"⚠️ Aviso - Teste Redis falhou: {e}")
            print("🔄 Continuando mesmo assim...")
        
        # Preparar argumentos do Flower
        flower_args = [
            'flower',
            '--broker=' + redis_url,
            '--port=5555',
            '--basic_auth=admin:admin123',
            '--logging=info',
            '--url_prefix=flower'  # Para Railway
        ]
        
        # Configurar argumentos da linha de comando
        sys.argv = flower_args
        
        print("🚀 Iniciando Flower na porta 5555...")
        print("🔐 Login: admin / admin123")
        
        # Iniciar Flower
        flower = FlowerCommand()
        flower.execute_from_commandline()
        
    except ImportError as e:
        print(f"❌ Flower não encontrado: {e}")
        print("📦 Tentando instalar flower...")
        os.system("pip install flower==2.0.1")
        
        # Tentar novamente após instalação
        start_flower()
        
    except Exception as e:
        print(f"❌ Erro ao iniciar Flower: {e}")
        print("🔍 Verificações:")
        print("1. REDIS_URL está configurada?")
        print("2. Redis está acessível?")
        print("3. Flower está instalado?")
        sys.exit(1)

if __name__ == '__main__':
    start_flower() 