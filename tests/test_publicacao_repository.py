import pytest
from datetime import datetime
from app import create_app, db
from app.domain.entities.publicacao import Publicacao
from app.infrastructure.repositories.sqlalchemy_publicacao_repository import SQLAlchemyPublicacaoRepository

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def repository(app):
    return SQLAlchemyPublicacaoRepository()

@pytest.fixture
def sample_publicacao():
    return Publicacao(
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

def test_create_publicacao(repository, sample_publicacao):
    created = repository.create(sample_publicacao)
    
    assert created.id is not None
    assert created.numero_processo == sample_publicacao.numero_processo
    assert created.autores == sample_publicacao.autores
    assert created.status == "nova"

def test_find_by_id(repository, sample_publicacao):
    created = repository.create(sample_publicacao)
    found = repository.find_by_id(created.id)
    
    assert found is not None
    assert found.numero_processo == sample_publicacao.numero_processo

def test_find_by_numero_processo(repository, sample_publicacao):
    created = repository.create(sample_publicacao)
    found = repository.find_by_numero_processo(sample_publicacao.numero_processo)
    
    assert found is not None
    assert found.id == created.id

def test_find_by_status(repository, sample_publicacao):
    repository.create(sample_publicacao)
    found = repository.find_by_status("nova")
    
    assert len(found) == 1
    assert found[0].numero_processo == sample_publicacao.numero_processo

def test_update_publicacao(repository, sample_publicacao):
    created = repository.create(sample_publicacao)
    created.status = "processada"
    
    updated = repository.update(created)
    
    assert updated.status == "processada"
    assert updated.id == created.id

def test_delete_publicacao(repository, sample_publicacao):
    created = repository.create(sample_publicacao)
    result = repository.delete(created.id)
    
    assert result is True
    
    found = repository.find_by_id(created.id)
    assert found is None 