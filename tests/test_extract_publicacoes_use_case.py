import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from app.domain.entities.publicacao import Publicacao
from app.domain.use_cases.extract_publicacoes_use_case import ExtractPublicacoesUseCase

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def mock_scraper():
    return Mock()

@pytest.fixture
def use_case(mock_repository, mock_scraper):
    return ExtractPublicacoesUseCase(mock_repository, mock_scraper)

@pytest.fixture
def sample_publicacao_data():
    return {
        'numero_processo': '1234567-89.2024.1.01.0001',
        'data_disponibilizacao': datetime(2024, 10, 1),
        'autores': 'João da Silva',
        'advogados': 'Dr. José Santos',
        'conteudo_completo': 'Conteúdo da publicação teste',
        'valor_principal_bruto': 10000.00,
        'valor_principal_liquido': 9500.00,
        'valor_juros_moratorios': 500.00,
        'honorarios_advocaticios': 1000.00
    }

def test_execute_with_new_publicacao(use_case, mock_repository, mock_scraper, sample_publicacao_data):
    data_inicio = datetime(2024, 10, 1)
    data_fim = datetime(2024, 10, 31)
    
    mock_scraper.extrair_publicacoes.return_value = [sample_publicacao_data]
    mock_repository.find_by_numero_processo.return_value = None
    
    created_publicacao = Publicacao(**sample_publicacao_data)
    created_publicacao.id = 1
    mock_repository.create.return_value = created_publicacao
    
    result = use_case.execute(data_inicio, data_fim)
    
    assert len(result) == 1
    mock_scraper.extrair_publicacoes.assert_called_once_with(data_inicio, data_fim)
    mock_repository.find_by_numero_processo.assert_called_once_with('1234567-89.2024.1.01.0001')
    mock_repository.create.assert_called_once()

def test_execute_with_existing_publicacao(use_case, mock_repository, mock_scraper, sample_publicacao_data):
    data_inicio = datetime(2024, 10, 1)
    data_fim = datetime(2024, 10, 31)
    
    mock_scraper.extrair_publicacoes.return_value = [sample_publicacao_data]
    
    existing_publicacao = Publicacao(**sample_publicacao_data)
    existing_publicacao.id = 1
    mock_repository.find_by_numero_processo.return_value = existing_publicacao
    
    result = use_case.execute(data_inicio, data_fim)
    
    assert len(result) == 0
    mock_repository.create.assert_not_called()

def test_execute_with_empty_results(use_case, mock_repository, mock_scraper):
    data_inicio = datetime(2024, 10, 1)
    data_fim = datetime(2024, 10, 31)
    
    mock_scraper.extrair_publicacoes.return_value = []
    
    result = use_case.execute(data_inicio, data_fim)
    
    assert len(result) == 0
    mock_repository.find_by_numero_processo.assert_not_called()
    mock_repository.create.assert_not_called() 