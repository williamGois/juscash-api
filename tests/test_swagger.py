import json

def test_swagger_docs_available(client):
    """Testa se a documentação Swagger está acessível"""
    response = client.get('/docs/')
    assert response.status_code == 200

def test_swagger_json_available(client):
    """Testa se o JSON da especificação Swagger está disponível"""
    response = client.get('/api/swagger.json')
    assert response.status_code == 200
    
    swagger_spec = json.loads(response.data)
    assert 'swagger' in swagger_spec or 'openapi' in swagger_spec
    assert 'info' in swagger_spec
    assert swagger_spec['info']['title'] == 'JusCash API'

def test_swagger_contains_publicacoes_endpoints(client):
    """Testa se os endpoints de publicações estão na documentação"""
    response = client.get('/api/swagger.json')
    swagger_spec = json.loads(response.data)
    
    paths = swagger_spec.get('paths', {})
    # Verificar se pelo menos um endpoint de publicações existe
    publicacoes_endpoints = [path for path in paths.keys() if 'publicacoes' in path]
    assert len(publicacoes_endpoints) > 0, f"Nenhum endpoint de publicações encontrado. Caminhos disponíveis: {list(paths.keys())[:5]}"

def test_swagger_contains_scraping_endpoints(client):
    """Testa se os endpoints de scraping estão na documentação"""
    response = client.get('/api/swagger.json')
    swagger_spec = json.loads(response.data)
    
    paths = swagger_spec.get('paths', {})
    # Verificar se pelo menos um endpoint de scraping existe
    scraping_endpoints = [path for path in paths.keys() if 'scraping' in path or 'extract' in path]
    assert len(scraping_endpoints) > 0, f"Nenhum endpoint de scraping encontrado. Caminhos disponíveis: {list(paths.keys())[:5]}"

def test_swagger_contains_models(client):
    """Testa se os modelos estão definidos na documentação"""
    response = client.get('/api/swagger.json')
    swagger_spec = json.loads(response.data)
    
    definitions = swagger_spec.get('definitions', {}) or swagger_spec.get('components', {}).get('schemas', {})
    assert 'Publicacao' in definitions
    assert 'PublicacaoStatusUpdate' in definitions
    assert 'ScrapingRequest' in definitions
    assert 'TaskResponse' in definitions
    assert 'TaskStatus' in definitions 