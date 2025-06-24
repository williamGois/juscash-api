import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database - Railway PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'postgresql://juscash:juscash123@localhost:5432/juscash_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 5)),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 120)),
        'pool_pre_ping': True,
        'connect_args': {
            'sslmode': 'require'
        } if os.environ.get('RAILWAY_ENVIRONMENT') else {}
    }
    
    # Redis - Railway Redis
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # DJE Settings
    DJE_BASE_URL = 'https://dje.tjsp.jus.br/cdje'
    
    # Railway específico
    PORT = int(os.environ.get('PORT', 5000))
    RAILWAY_ENVIRONMENT = os.environ.get('RAILWAY_ENVIRONMENT', False)
    
    # Cron Job Schedules (em segundos)
    DAILY_SCRAPING_SCHEDULE = float(os.environ.get('DAILY_SCRAPING_SCHEDULE', 3600))  # 1 hora
    WEEKLY_SCRAPING_SCHEDULE = float(os.environ.get('WEEKLY_SCRAPING_SCHEDULE', 604800))  # 1 semana  
    CLEANUP_SCHEDULE = float(os.environ.get('CLEANUP_SCHEDULE', 86400))  # 1 dia
    
    # Scraping Config
    SCRAPING_ENABLED = os.environ.get('SCRAPING_ENABLED', 'true').lower() == 'true'
    
    # Chrome/Selenium config para Railway
    CHROME_OPTIONS = [
        '--headless',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-web-security',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-images',
        '--disable-javascript',
        '--memory-pressure-off',
        '--max_old_space_size=4096'
    ]

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    
    # Configurações específicas para produção
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 3)),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 300)),
        'pool_pre_ping': True,
        'connect_args': {
            'sslmode': 'require'
        }
    }

class RailwayConfig(ProductionConfig):
    """Configuração específica para Railway"""
    # Railway otimizações
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 2,  # Railway tem limitações de conexão
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_timeout': 20,
        'connect_args': {
            'sslmode': 'require',
            'connect_timeout': 10
        }
    }
    
    # Logs para Railway
    LOG_TO_STDOUT = True

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://juscash:juscash123@localhost:5432/juscash_test_db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'railway': RailwayConfig,
    'testing': TestConfig,
    'default': RailwayConfig if os.environ.get('RAILWAY_ENVIRONMENT') else DevelopmentConfig
} 