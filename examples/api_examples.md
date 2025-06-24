# Exemplos de Uso da JusCash API

Este arquivo contém exemplos práticos de como usar a API JusCash para gerenciar publicações do DJE.

## 🚀 Executando a API

```bash
# Usando Docker (recomendado)
docker-compose up --build

# Ou localmente
flask upgrade-db  # Aplicar migrações primeiro
python run.py
```

A API estará disponível em: `http://localhost:5000`
Documentação Swagger em: `http://localhost:5000/docs/`

## 📋 Exemplos de Requisições

### 1. Listar Todas as Publicações

```bash
curl -X GET "http://localhost:5000/api/publicacoes/" \
  -H "Content-Type: application/json"
```

### 2. Filtrar Publicações por Status

```bash
# Listar apenas publicações novas
curl -X GET "http://localhost:5000/api/publicacoes/?status=nova" \
  -H "Content-Type: application/json"

# Listar publicações processadas
curl -X GET "http://localhost:5000/api/publicacoes/?status=processada" \
  -H "Content-Type: application/json"

# Buscar por termo específico
curl -X GET "http://localhost:5000/api/publicacoes/?search=aposentadoria" \
  -H "Content-Type: application/json"

# Paginação - 10 registros, pular os primeiros 20
curl -X GET "http://localhost:5000/api/publicacoes/?limit=10&offset=20" \
  -H "Content-Type: application/json"
```

### 3. Obter Publicação Específica

```bash
curl -X GET "http://localhost:5000/api/publicacoes/1" \
  -H "Content-Type: application/json"
```

### 4. Obter Estatísticas das Publicações

```bash
curl -X GET "http://localhost:5000/api/publicacoes/stats" \
  -H "Content-Type: application/json"
```

Resposta:
```json
{
  "nova": 15,
  "lida": 8,
  "processada": 12,
  "total": 35
}
```

### 5. Atualizar Status de uma Publicação

```bash
curl -X PUT "http://localhost:5000/api/publicacoes/1/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "processada"
  }'
```

### 6. Iniciar Extração de Publicações

```bash
curl -X POST "http://localhost:5000/api/scraping/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "data_inicio": "2024-10-01T00:00:00",
    "data_fim": "2024-10-31T23:59:59"
  }'
```

Resposta:
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "Em processamento",
  "message": "Extração de publicações iniciada em background"
}
```

### 7. Verificar Status da Extração

```bash
curl -X GET "http://localhost:5000/api/scraping/status/abc123-def456-ghi789" \
  -H "Content-Type: application/json"
```

Possíveis respostas:

**Em processamento:**
```json
{
  "state": "PROGRESS",
  "status": "Em progresso",
  "current": 50,
  "total": 100
}
```

**Concluído:**
```json
{
  "state": "SUCCESS",
  "status": "Concluído",
  "result": {
    "total_extraidas": 25,
    "data_inicio": "2024-10-01T00:00:00",
    "data_fim": "2024-10-31T23:59:59",
    "status": "concluido"
  }
}
```

## 🧪 Exemplos com Python

### Usando requests

```python
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

# 1. Listar publicações
response = requests.get(f"{BASE_URL}/publicacoes/")
publicacoes = response.json()
print(f"Total de publicações: {len(publicacoes)}")

# 1.1. Obter estatísticas
response = requests.get(f"{BASE_URL}/publicacoes/stats")
stats = response.json()
print(f"Estatísticas: {stats}")

# 1.2. Buscar por termo
response = requests.get(f"{BASE_URL}/publicacoes/?search=INSS")
resultados = response.json()
print(f"Publicações encontradas com 'INSS': {len(resultados)}")

# 1.3. Paginação
response = requests.get(f"{BASE_URL}/publicacoes/?limit=5&offset=0")
primeira_pagina = response.json()
print(f"Primeira página: {len(primeira_pagina)} registros")

# 2. Iniciar extração
data = {
    "data_inicio": "2024-10-01T00:00:00",
    "data_fim": "2024-10-31T23:59:59"
}
response = requests.post(f"{BASE_URL}/scraping/extract", json=data)
task_info = response.json()
task_id = task_info["task_id"]

# 3. Verificar status da tarefa
import time
while True:
    response = requests.get(f"{BASE_URL}/scraping/status/{task_id}")
    status = response.json()
    
    if status["state"] == "SUCCESS":
        print("Extração concluída!")
        print(f"Resultado: {status['result']}")
        break
    elif status["state"] == "FAILURE":
        print(f"Erro na extração: {status['error']}")
        break
    else:
        print(f"Status: {status['status']}")
        time.sleep(5)

# 4. Atualizar status de uma publicação
if publicacoes:
    pub_id = publicacoes[0]["id"]
    data = {"status": "lida"}
    response = requests.put(f"{BASE_URL}/publicacoes/{pub_id}/status", json=data)
    print(f"Status atualizado: {response.json()}")
```

## 🔍 Estrutura da Resposta de Publicação

```json
{
  "id": 1,
  "numero_processo": "1234567-89.2024.1.01.0001",
  "data_disponibilizacao": "2024-10-01T00:00:00",
  "autores": "João da Silva",
  "advogados": "Dr. José Santos - OAB/SP 123456",
  "conteudo_completo": "Conteúdo completo da publicação...",
  "valor_principal_bruto": 10000.50,
  "valor_principal_liquido": 9500.00,
  "valor_juros_moratorios": 500.25,
  "honorarios_advocaticios": 1000.00,
  "reu": "Instituto Nacional do Seguro Social - INSS",
  "status": "nova",
  "created_at": "2024-10-01T10:30:00",
  "updated_at": "2024-10-01T10:30:00"
}
```

## 📊 Status Possíveis

- **nova**: Publicação recém-extraída
- **lida**: Publicação visualizada
- **processada**: Publicação processada/finalizada

## 🚨 Códigos de Resposta HTTP

- **200**: Sucesso
- **201**: Criado com sucesso
- **400**: Dados inválidos
- **404**: Recurso não encontrado
- **500**: Erro interno do servidor

## 📖 Swagger UI

Para uma interface interativa e documentação completa, acesse:
`http://localhost:5000/docs/`

Na interface Swagger você pode:
- Ver todos os endpoints disponíveis
- Testar requisições diretamente no browser
- Ver exemplos de requisições e respostas
- Verificar validações de dados 