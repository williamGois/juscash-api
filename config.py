import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
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
        } if os.environ.get('PRODUCTION') else {}
    }
    
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    DJE_BASE_URL = 'https://dje.tjsp.jus.br/cdje'
    
    PORT = int(os.environ.get('PORT', 5000))
    
    DAILY_SCRAPING_SCHEDULE = float(os.environ.get('DAILY_SCRAPING_SCHEDULE', 3600))
    WEEKLY_SCRAPING_SCHEDULE = float(os.environ.get('WEEKLY_SCRAPING_SCHEDULE', 604800))
    CLEANUP_SCHEDULE = float(os.environ.get('CLEANUP_SCHEDULE', 86400))
    
    SCRAPING_ENABLED = os.environ.get('SCRAPING_ENABLED', 'true').lower() == 'true'
    
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
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 3)),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 300)),
        'pool_pre_ping': True,
        'connect_args': {
            'sslmode': 'require'
        }
    }

class TestConfig(Config):
    TESTING = True
    
    # Usar DATABASE_URL do ambiente de teste (GitHub Actions) se disponível
    TEST_DATABASE_URL = os.environ.get('DATABASE_URL')
    if TEST_DATABASE_URL and TEST_DATABASE_URL.startswith("postgres://"):
        TEST_DATABASE_URL = TEST_DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Usar SQLite em memória para testes locais, PostgreSQL para CI
    if TEST_DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = TEST_DATABASE_URL
        # Configuração para PostgreSQL em CI
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 1,
            'pool_recycle': -1,
            'pool_pre_ping': False,
            'connect_args': {
                'sslmode': 'disable'
            }
        }
    else:
        # SQLite em memória para testes locais
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': False
        }

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig,
    'default': ProductionConfig if os.environ.get('PRODUCTION') else DevelopmentConfig
} 