import json

def test_simple_ping(client):
    """Testa se o endpoint simples funciona"""
    response = client.get('/api/simple/ping')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert 'timestamp' in data
    assert 'version' in data

def test_docs_redirect(client):
    """Testa se a documentação redireciona corretamente"""
    response = client.get('/docs/')
    assert response.status_code == 200 