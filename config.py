import os
import logging
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.path.join(basedir, 'logs', 'app.log')
    
    @staticmethod
    def init_app(app):
        os.makedirs(os.path.join(basedir, 'logs'), exist_ok=True)
        
        logging.basicConfig(
            level=app.config['LOG_LEVEL'],
            format=app.config['LOG_FORMAT'],
            handlers=[
                logging.FileHandler(app.config['LOG_FILE']),
                logging.StreamHandler()
            ]
        )
        
        app.logger.setLevel(app.config['LOG_LEVEL'])

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://juscash:juscash123@localhost:5432/juscash_db'

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.INFO
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://juscash:juscash123@db:5432/juscash_db'

class TestingConfig(Config):
    TESTING = True
    LOG_LEVEL = logging.DEBUG
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://juscash:juscash123@localhost:5432/juscash_test'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig
} 