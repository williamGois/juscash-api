# JusCash API

## Descrição
API para extração e análise de publicações do Diário da Justiça Eletrônico (DJE).

## Funcionalidades
- Extração automatizada de publicações do DJE
- API RESTful para consulta de dados
- Sistema de scraping com agendamento
- Interface de monitoramento com Flower

## Tecnologias
- Python 3.11
- Flask
- PostgreSQL
- Redis
- Celery
- Docker

## Deploy
O sistema é automaticamente deployado via GitHub Actions quando há push na branch master.

<!-- Deploy timestamp: 2025-01-26 05:15:00 -->

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.11+
- Docker e Docker Compose
- PostgreSQL 13+

### Instalação Local

```bash
# Clonar repositório
git clone https://github.com/williamGois/juscash-api.git
cd juscash-api

# Configurar ambiente
cp .env.example .env
pip install -r requirements.txt

# Iniciar com Docker
docker-compose up -d
```

### Endpoints Principais

- `GET /api/simple/ping` - Health check
- `GET /api/publicacoes` - Listar publicações
- `POST /api/publicacoes/extract` - Extrair novas publicações
- `GET /api/docs` - Documentação Swagger

## 📦 Deploy

O deploy é automatizado via GitHub Actions quando há push na branch `master`.

### Deploy Manual

```bash
ssh user@servidor
cd /var/www/juscash
git pull origin master
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🔧 Desenvolvimento

### Estrutura do Projeto

```
juscash-api/
├── app/                 # Código da aplicação
│   ├── domain/         # Entidades e regras de negócio
│   ├── infrastructure/ # Banco de dados e scraping
│   └── presentation/   # Rotas e API
├── scripts/            # Scripts auxiliares
├── tests/              # Testes automatizados
└── docker-compose.yml  # Configuração Docker
```

### Executar Testes

```bash
pytest tests/ -v
```

## 📝 Variáveis de Ambiente

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
SECRET_KEY=your-secret-key
FLASK_ENV=development
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add: nova funcionalidade'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. 