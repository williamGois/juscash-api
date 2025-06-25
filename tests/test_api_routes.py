import json
from app import db

def test_get_publicacoes_empty(client):
    response = client.get('/api/publicacoes/')
    assert response.status_code == 200
    assert json.loads(response.data) == []

def test_get_publicacoes_with_data(client, sample_publicacao_model):
    db.session.add(sample_publicacao_model)
    db.session.commit()
    
    response = client.get('/api/publicacoes/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['numero_processo'] == "1234567-89.2024.1.01.0001"

def test_get_publicacao_by_id(client, sample_publicacao_model):
    db.session.add(sample_publicacao_model)
    db.session.commit()
    
    response = client.get(f'/api/publicacoes/{sample_publicacao_model.id}')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['numero_processo'] == "1234567-89.2024.1.01.0001"

def test_get_publicacao_not_found(client):
    response = client.get('/api/publicacoes/999')
    assert response.status_code == 404

def test_update_status(client, sample_publicacao_model):
    db.session.add(sample_publicacao_model)
    db.session.commit()
    
    response = client.put(
        f'/api/publicacoes/{sample_publicacao_model.id}/status',
        data=json.dumps({'status': 'processada'}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'processada'

def test_update_status_not_found(client):
    response = client.put(
        '/api/publicacoes/999/status',
        data=json.dumps({'status': 'processada'}),
        content_type='application/json'
    )
    
    assert response.status_code == 404

def test_update_status_without_status(client, sample_publicacao_model):
    db.session.add(sample_publicacao_model)
    db.session.commit()
    
    response = client.put(
        f'/api/publicacoes/{sample_publicacao_model.id}/status',
        data=json.dumps({}),
        content_type='application/json'
    )
    
    assert response.status_code == 400

def test_extract_publicacoes_without_dates(client):
    response = client.post(
        '/api/scraping/extract',
        data=json.dumps({}),
        content_type='application/json'
    )
    
    assert response.status_code == 400 