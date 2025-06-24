import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.domain.entities.publicacao import Publicacao
from app.infrastructure.repositories.sqlalchemy_publicacao_repository import SQLAlchemyPublicacaoRepository
from app.infrastructure.database.models import PublicacaoModel

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
def sample_publicacoes():
    return [
        Publicacao(
            numero_processo="1234567-89.2024.1.01.0001",
            data_disponibilizacao=datetime(2024, 10, 1),
            autores="João da Silva",
            advogados="Dr. José Santos",
            conteudo_completo="Processo contra o INSS sobre aposentadoria",
            valor_principal_bruto=10000.00,
            status="nova"
        ),
        Publicacao(
            numero_processo="1234567-89.2024.1.01.0002",
            data_disponibilizacao=datetime(2024, 10, 2),
            autores="Maria Santos",
            advogados="Dr. Pedro Silva",
            conteudo_completo="Processo contra o Instituto Nacional sobre auxílio doença",
            valor_principal_liquido=5000.00,
            status="lida"
        ),
        Publicacao(
            numero_processo="1234567-89.2024.1.01.0003",
            data_disponibilizacao=datetime(2024, 10, 3),
            autores="Carlos Oliveira",
            advogados="Dr. Ana Costa",
            conteudo_completo="Ação judicial sobre benefício previdenciário",
            honorarios_advocaticios=2000.00,
            status="processada"
        )
    ]

def test_search_by_content(repository, sample_publicacoes):
    """Testa busca textual no PostgreSQL"""
    # Criar publicações de teste
    for pub in sample_publicacoes:
        repository.create(pub)
    
    # Buscar por INSS
    results = repository.search_by_content("INSS")
    assert len(results) == 1
    assert "João da Silva" in results[0].autores
    
    # Buscar por Instituto
    results = repository.search_by_content("Instituto")
    assert len(results) == 2
    
    # Buscar por advogado
    results = repository.search_by_content("Dr. Pedro")
    assert len(results) == 1
    assert results[0].numero_processo == "1234567-89.2024.1.01.0002"

def test_find_by_date_range(repository, sample_publicacoes):
    """Testa busca por intervalo de datas"""
    for pub in sample_publicacoes:
        repository.create(pub)
    
    # Buscar por intervalo específico
    data_inicio = datetime(2024, 10, 1)
    data_fim = datetime(2024, 10, 2)
    
    results = repository.find_by_date_range(data_inicio, data_fim)
    assert len(results) == 2
    
    # Buscar com filtro de status
    results = repository.find_by_date_range(data_inicio, data_fim, status="nova")
    assert len(results) == 1
    assert results[0].status == "nova"

def test_count_by_status(repository, sample_publicacoes):
    """Testa contagem por status"""
    for pub in sample_publicacoes:
        repository.create(pub)
    
    stats = repository.count_by_status()
    
    assert stats.get('nova', 0) == 1
    assert stats.get('lida', 0) == 1
    assert stats.get('processada', 0) == 1

def test_pagination(repository, sample_publicacoes):
    """Testa paginação"""
    # Criar mais publicações para testar paginação
    for i, pub in enumerate(sample_publicacoes * 5):  # 15 publicações
        pub.numero_processo = f"proc-{i:03d}"
        repository.create(pub)
    
    # Testar limite
    results = repository.find_all(limit=5)
    assert len(results) == 5
    
    # Testar offset
    results = repository.find_all(limit=5, offset=5)
    assert len(results) == 5
    
    # Testar paginação por status
    results = repository.find_by_status('nova', limit=3)
    assert len(results) == 3

def test_numeric_precision(repository):
    """Testa precisão dos valores monetários no PostgreSQL"""
    publicacao = Publicacao(
        numero_processo="1234567-89.2024.1.01.9999",
        data_disponibilizacao=datetime(2024, 10, 1),
        autores="Teste Precisão",
        advogados="Dr. Teste",
        conteudo_completo="Teste de precisão numérica",
        valor_principal_bruto=12345.67,
        valor_principal_liquido=9876.54,
        valor_juros_moratorios=123.45,
        honorarios_advocaticios=500.99
    )
    
    created = repository.create(publicacao)
    found = repository.find_by_id(created.id)
    
    # Verificar precisão de 2 casas decimais
    assert found.valor_principal_bruto == 12345.67
    assert found.valor_principal_liquido == 9876.54
    assert found.valor_juros_moratorios == 123.45
    assert found.honorarios_advocaticios == 500.99

def test_uuid_field(repository, app):
    """Testa se o campo UUID está sendo gerado automaticamente"""
    publicacao = Publicacao(
        numero_processo="uuid-test-001",
        data_disponibilizacao=datetime(2024, 10, 1),
        autores="Teste UUID",
        advogados="Dr. UUID",
        conteudo_completo="Teste do campo UUID"
    )
    
    created = repository.create(publicacao)
    
    # Verificar diretamente no modelo
    with app.app_context():
        model = PublicacaoModel.query.get(created.id)
        assert model.uuid is not None
        assert len(str(model.uuid)) == 36  # Formato UUID padrão

def test_timestamp_with_timezone(repository, app):
    """Testa se os timestamps estão usando timezone"""
    publicacao = Publicacao(
        numero_processo="tz-test-001",
        data_disponibilizacao=datetime(2024, 10, 1),
        autores="Teste Timezone",
        advogados="Dr. Timezone",
        conteudo_completo="Teste de timezone"
    )
    
    created = repository.create(publicacao)
    
    with app.app_context():
        model = PublicacaoModel.query.get(created.id)
        # Verificar se os campos de data têm timezone
        assert model.created_at.tzinfo is not None
        assert model.updated_at.tzinfo is not None 