import pytest
import os
from app import create_app, db
from app.infrastructure.database.models import PublicacaoModel
from datetime import datetime

@pytest.fixture(scope='session')
def app():
    """Cria uma instância da aplicação para testes"""
    # Configurar variáveis de ambiente para testes
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'True'
    
    # Se não há DATABASE_URL (testes locais), usar SQLite
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente de teste"""
    return app.test_client()

@pytest.fixture
def sample_publicacao_model():
    """Fixture para publicação de exemplo"""
    return PublicacaoModel(
        numero_processo="1234567-89.2024.1.01.0001",
        data_disponibilizacao=datetime(2024, 10, 1),
        autores="João da Silva",
        advogados="Dr. José Santos",
        conteudo_completo="Conteúdo da publicação teste",
        valor_principal_bruto=10000.00,
        valor_principal_liquido=9500.00,
        valor_juros_moratorios=500.00,
        honorarios_advocaticios=1000.00
    )

@pytest.fixture(autouse=True)
def clean_db(app):
    """Limpa o banco a cada teste"""
    with app.app_context():
        db.session.query(PublicacaoModel).delete()
        db.session.commit()
        yield
        db.session.rollback() 