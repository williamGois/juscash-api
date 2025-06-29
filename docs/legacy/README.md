# JusCash API - Web Scraping DJE

API em Python Flask para automação de web scraping do Diário da Justiça Eletrônico (DJE) de São Paulo, desenvolvida seguindo Clean Architecture e princípios SOLID.

## 🌐 **PRODUÇÃO ONLINE** 

### ✅ **APLICAÇÃO EM FUNCIONAMENTO:**
- **🌍 URL Principal**: https://cron.juscash.app
- **📖 Documentação**: https://cron.juscash.app/docs/
- **🔍 API Health**: https://cron.juscash.app/api/cron/health
- **🌸 Monitoramento**: https://cron.juscash.app/flower

### 🛠️ **Status da Infraestrutura:**
- **✅ Servidor**: VPS Hostinger Ubuntu 24.04 (77.37.68.178)
- **✅ SSL/HTTPS**: Certificado Let's Encrypt válido
- **✅ PostgreSQL**: 15.13 - Banco funcionando com índices otimizados
- **✅ Redis**: 7-alpine - Cache e message broker ativos
- **✅ Docker**: 5 containers em execução (web, db, redis, worker, flower)
- **✅ Nginx**: Proxy reverso configurado
- **✅ Celery**: Worker processando tarefas assíncronas
- **✅ DNS**: Configurado com CNAMEs para domínio personalizado

### 📊 **Containers em Produção:**
```bash
NAME               IMAGE                STATUS
juscash-web-1      juscash-web          Up (healthy) - Flask API
juscash-db-1       postgres:15-alpine   Up (healthy) - PostgreSQL
juscash-redis-1    redis:7-alpine       Up (healthy) - Redis
juscash-worker-1   juscash-worker       Up - Celery Worker
juscash-flower-1   juscash-flower       Up - Task Monitor
```

### 🚀 **Deploy Automático:**
```bash
# Deploy completo em um comando
./deploy-completo.sh

# Acesso SSH configurado
ssh juscash-vps
```

---

## 🏗️ Arquitetura

O projeto segue os princípios da Clean Architecture:

- **Domain Layer**: Entidades de negócio e regras fundamentais
- **Use Cases Layer**: Lógica de aplicação e casos de uso
- **Infrastructure Layer**: Adaptadores externos (banco de dados, web scraping)
- **Presentation Layer**: Controllers e rotas da API

## 🚀 Funcionalidades

- ✅ Web scraping automatizado do DJE-SP
- ✅ Extração de dados de publicações do Caderno 3 - Judicial 1ª Instância Capital
- ✅ **Banco PostgreSQL** com índices otimizados e busca textual
- ✅ API REST completa com documentação Swagger
- ✅ Interface interativa para testes de API (`/docs/`)
- ✅ **Busca avançada** por conteúdo, autores e advogados
- ✅ **Paginação e filtros** eficientes
- ✅ **Estatísticas** de publicações por status
- ✅ Processamento assíncrono com Celery
- ✅ Containerização com Docker
- ✅ Testes automatizados com pytest

### Dados Extraídos

- Número do processo
- Data de disponibilização
- Autor(es)
- Advogado(s)
- Conteúdo completo da publicação
- Valor principal bruto/líquido
- Valor dos juros moratórios
- Honorários advocatícios

### 📖 Documentação API (Swagger)

A documentação interativa da API está disponível em:
- **🌐 Produção**: https://cron.juscash.app/docs/
- **💻 Desenvolvimento**: `http://localhost:5000/docs/`

**Interface Swagger completa com:**
- 📝 Especificação detalhada de todos os endpoints
- 🔍 Modelos de dados com validação automática
- 💡 Exemplos de requisições e respostas
- 🧪 Teste interativo de endpoints no browser
- 📊 Organização por namespaces (Publicações / Scraping)
- ⚡ Validação de dados em tempo real
- 🔐 Documentação de códigos de erro

## 🗄️ Banco de Dados PostgreSQL

### Estrutura Otimizada

O projeto utiliza **PostgreSQL** como banco de dados principal, com as seguintes otimizações:

#### ✅ **Armazenamento Eficiente**
- Tipos de dados otimizados (`NUMERIC` para valores monetários, `UUID` para identificadores únicos)
- Campos com timezone (`TIMESTAMP WITH TIME ZONE`)
- Constraints de validação para integridade dos dados

#### ✅ **Índices de Performance**
- **Índices simples**: `numero_processo`, `status`, `data_disponibilizacao`
- **Índices compostos**: `(status, data_disponibilizacao)` para consultas filtradas
- **Índices GIN**: Busca textual otimizada em `conteudo_completo`, `autores`, `advogados`
- **Índice UUID**: Para identificação única e distribuída

#### ✅ **Funcionalidades Avançadas**
- **Sistema de migrações**: Flask-Migrate para versionamento do schema
- **Busca textual**: Extensão `pg_trgm` para busca aproximada
- **Triggers automáticos**: Atualização de `updated_at` 
- **Validação de status**: Constraint para valores válidos
- **Comentários**: Documentação no próprio banco

#### ✅ **Facilidade de Consulta e Atualização**
```sql
-- Busca textual otimizada
SELECT * FROM publicacoes WHERE conteudo_completo ILIKE '%termo%';

-- Consultas por status com paginação
SELECT * FROM publicacoes WHERE status = 'nova' 
ORDER BY created_at DESC LIMIT 10 OFFSET 20;

-- Estatísticas agregadas
SELECT status, COUNT(*) FROM publicacoes GROUP BY status;
```

## 📦 Tecnologias

- **Python 3.11**
- **Flask** - Framework web
- **Flask-RESTX** - Documentação Swagger automática
- **PostgreSQL** - Banco de dados relacional robusto
- **SQLAlchemy** - ORM com otimizações para PostgreSQL
- **Selenium** - Web scraping
- **BeautifulSoup** - Parser HTML
- **Celery** - Processamento assíncrono
- **Redis** - Message broker
- **pytest** - Testes automatizados
- **Docker** - Containerização

## 🛠️ Instalação e Configuração

### Pré-requisitos

- Python 3.11+
- Docker e Docker Compose (desenvolvimento local)
- PostgreSQL 15+ (desenvolvimento local)
- Redis (desenvolvimento local)

### 1. Usando Docker (Produção - Recomendado)

```bash
# Executar com Docker Compose
docker-compose up --build

# A API estará disponível em http://localhost:5000
# Documentação Swagger em http://localhost:5000/docs/
```

### 2. Desenvolvimento Local

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Aplicar migrações
flask upgrade-db

# Executar aplicação
python run.py

# API disponível em: http://localhost:5000
# Swagger docs em: http://localhost:5000/docs/

# Em outro terminal, executar worker Celery
celery -A celery_worker.celery worker --loglevel=info
```

### 3. Executar Aplicação

```bash
# Aplicar migrações
flask upgrade-db

# Verificar status do banco
flask db-status

# Executar aplicação
python run.py
```

## 🔧 Configuração

### **Método 1: Automático (Recomendado)**
```bash
# Docker gera SECRET_KEY automaticamente
docker-compose up --build
```

### **Método 2: Manual**
Crie um arquivo `.env` com as seguintes variáveis:

```env
DATABASE_URL=postgresql://juscash:juscash123@localhost:5432/juscash_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=sua-chave-secreta-aqui
DJE_BASE_URL=https://dje.tjsp.jus.br/cdje
FLASK_ENV=development
```

### **Gerar SECRET_KEY automaticamente:**
```bash
# Opção 1: Script automático
python generate_secret_key.py

# Opção 2: Python direto
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Opção 3: Setup completo (Linux/Mac)
./setup-env.sh
```

**📚 Guia completo**: [`DOCKER_SECRET_SETUP.md`](DOCKER_SECRET_SETUP.md)

## 📚 API Endpoints

A API possui endpoints organizados em dois namespaces:

### 🌐 **URLs Base:**
- **Produção**: https://cron.juscash.app
- **Desenvolvimento**: http://localhost:5000

### 📋 Publicações (`/api/publicacoes/`)
- `GET /api/publicacoes/` - Listar todas as publicações
- `GET /api/publicacoes/?status=nova` - Filtrar por status
- `GET /api/publicacoes/?search=termo` - Buscar por termo
- `GET /api/publicacoes/?limit=10&offset=20` - Paginação
- `GET /api/publicacoes/stats` - **Estatísticas por status**
- `GET /api/publicacoes/{id}` - Obter publicação específica
- `PUT /api/publicacoes/{id}/status` - Atualizar status

### 🕷️ Web Scraping (`/api/scraping/`)
- `POST /api/scraping/extract` - Iniciar extração
- `GET /api/scraping/status/{task_id}` - Verificar status da tarefa

### 🕐 Cron Jobs (`/api/cron/`)
- `POST /api/cron/scraping/daily` - Executar raspagem diária
- `POST /api/cron/scraping/full-period` - Executar raspagem completa
- `POST /api/cron/scraping/custom-period` - Raspagem período customizado
- `GET /api/cron/health` - Verificar saúde do sistema
- `GET /api/cron/tasks/{task_id}` - Status de tarefa específica

### 💡 Exemplos Práticos

Para exemplos detalhados de uso com curl e Python, consulte:
- [`examples/api_examples.md`](examples/api_examples.md) - Exemplos gerais da API
- [`examples/cron_examples.md`](examples/cron_examples.md) - Exemplos específicos de cron jobs

## 🕐 Cron Jobs Automáticos

O agendamento automático é feito com **Celery Beat**, que roda junto com o serviço `worker` para maior eficiência e controle.

### 🚀 **Configuração Integrada**
- **Agendador**: Celery Beat integrado ao worker (`-B` flag)
- **Serviços**: Apenas `web`, `worker`, `flower` (sem `beat` separado)
- **Flexibilidade**: Horários configurados em `celery_worker.py`
- **Monitoramento**: Flower exibe tasks agendadas

### 📋 **Tarefas Agendadas (em `celery_worker.py`)**

| Tarefa | Agendamento (Crontab) | Descrição |
|---|---|---|
| **Raspagem Diária** | `crontab(minute=0)` | A cada hora, no minuto 0 |
| **Raspagem Completa** | `crontab(hour=3, day_of_week='sun')` | Domingo, 3h |
| **Limpeza de Logs** | `crontab(hour=4, minute=0)` | Todo dia, 4h |

### 🎛️ **Gerenciamento Manual via API**
Mesmo com automação, você pode executar tarefas manualmente:
```bash
# Executar raspagem diária
curl -X POST http://localhost:5000/api/cron/scraping/daily

# Verificar saúde do sistema
curl http://localhost:5000/api/cron/health
```

**📚 Guia completo**: [`CRON_JOBS_GUIDE.md`](CRON_JOBS_GUIDE.md)

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=app

# Executar testes específicos
pytest tests/test_publicacao_repository.py

# Testes específicos do PostgreSQL
pytest tests/test_postgresql_repository.py
```

## 📁 Estrutura do Projeto

```
juscash-api/
├── app/
│   ├── domain/
│   │   ├── entities/
│   │   │   └── publicacao.py
│   │   ├── repositories/  
│   │   │   └── publicacao_repository.py
│   │   └── use_cases/
│   │       └── extract_publicacoes_use_case.py
│   ├── infrastructure/
│   │   ├── database/
│   │   │   └── models.py
│   │   ├── repositories/
│   │   │   └── sqlalchemy_publicacao_repository.py
│   │   └── scraping/
│   │       └── dje_scraper.py
│   ├── presentation/
│   │   ├── routes.py
│   │   └── cron_routes.py
│   └── tasks/
│       ├── scraping_tasks.py
│       └── maintenance_tasks.py
├── tests/
│   ├── test_publicacao_repository.py
│   ├── test_extract_publicacoes_use_case.py
│   ├── test_api_routes.py
│   ├── test_swagger.py
│   └── test_postgresql_repository.py
├── migrations/
│   ├── versions/
│   │   └── 001_initial_migration.py
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── README
├── examples/
│   └── api_examples.md
├── config.py
├── run.py
├── celery_worker.py
├── cron_schedule.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
├── logs/
├── CRON_JOBS_GUIDE.md
├── FLASK_MIGRATE_COMMANDS.md
├── Procfile
└── README.md
```

## 🔄 Fluxo de Funcionamento

1. **Agendamento Automático**: Celery Beat executa tarefas periodicamente
2. **Scraping**: Selenium acessa o DJE e extrai dados das publicações
3. **Filtragem**: Aplicação de critérios de busca (INSS, Instituto Nacional do Seguro Social)
4. **Processamento**: Extração de dados específicos usando regex
5. **Armazenamento**: Salvamento no PostgreSQL com índices otimizados
6. **API**: Disponibilização dos dados via endpoints REST com busca avançada
7. **Monitoramento**: Interface Flower para acompanhar tarefas em tempo real

## 🐛 Logs e Monitoramento

### Logs Automáticos
Os logs são gerados automaticamente e incluem:
- Logs de scraping (`/logs/scraping.log`)
- Logs de migrações (`/logs/migrations.log`)
- Logs de cron jobs (`/logs/cron.log`)
- Logs de manutenção (`/logs/maintenance.log`)

### Monitoramento com Flower
Interface web para monitoramento de tarefas Celery:
```bash
# Acessar interface
http://localhost:5555

# Funcionalidades:
- ✅ Tasks ativas e concluídas
- ✅ Estatísticas de performance
- ✅ Controle de workers
- ✅ Logs em tempo real
```

### Health Checks
```bash
# Via API
curl http://localhost:5000/api/cron/health

# Via Flower
http://localhost:5555/monitor

# Via logs
tail -f logs/cron.log
```

## 🛠️ Comandos de Manutenção da Produção

### 📊 **Monitoramento:**
```bash
# Status geral dos containers
ssh juscash-vps 'cd /var/www/juscash && docker-compose ps'

# Verificar saúde da aplicação
curl https://cron.juscash.app/api/cron/health

# Logs da aplicação em tempo real
ssh juscash-vps 'cd /var/www/juscash && docker-compose logs -f web'

# Logs do worker Celery
ssh juscash-vps 'cd /var/www/juscash && docker-compose logs -f worker'
```

### 🔄 **Operações de Deploy:**
```bash
# Deploy completo (local)
./deploy-completo.sh

# Restart da aplicação (servidor)
ssh juscash-vps 'cd /var/www/juscash && docker-compose restart'

# Rebuild da aplicação (servidor)
ssh juscash-vps 'cd /var/www/juscash && docker-compose build && docker-compose up -d'

# Aplicar migrações do banco
ssh juscash-vps 'cd /var/www/juscash && docker-compose exec -T web python create-tables.py'
```

### 🔧 **Manutenção do Sistema:**
```bash
# Verificar espaço em disco
ssh juscash-vps 'df -h'

# Limpar containers não utilizados
ssh juscash-vps 'docker system prune -f'

# Backup do banco de dados
ssh juscash-vps 'cd /var/www/juscash && docker-compose exec -T db pg_dump -U juscash juscash_db > backup_$(date +%Y%m%d).sql'

# Verificar certificado SSL
curl -I https://cron.juscash.app | grep -i ssl
```

### 🌐 **URLs de Monitoramento:**
- **Status da API**: https://cron.juscash.app/api/cron/health
- **Documentação**: https://cron.juscash.app/docs/
- **Monitor Celery**: https://cron.juscash.app/flower

## 🚀 CI/CD Automático

### ✅ **Sistema de Deploy Automático Implementado!**

- **🔄 Deploy automático** via GitHub Actions
- **🧪 Ambiente de staging** para testes
- **📱 Notificações** via Discord
- **🔐 Backup automático** antes do deploy
- **🛡️ Rollback** automático em falhas
- **🏥 Health checks** pós-deploy

### 📋 **Como Configurar:**

```bash
# Configuração automática em um comando
chmod +x setup-cicd.sh
./setup-cicd.sh
```

### 🌍 **Ambientes Disponíveis:**

| Ambiente | Branch | URL | Porta |
|----------|--------|-----|-------|
| **Produção** | `main/master` | https://cron.juscash.app | 5000 |
| **Staging** | `develop/staging` | http://77.37.68.178:5001 | 5001 |

### 🔄 **Workflows:**

- **📤 Push para `main`** → Deploy automático para produção
- **📤 Push para `develop`** → Deploy automático para staging
- **🧪 Pull Requests** → Testes automatizados

**📚 Guia completo**: [`CI_CD_GUIDE.md`](CI_CD_GUIDE.md)

---

## 🚧 Melhorias Futuras

- [ ] Implementação de autenticação JWT
- [ ] Notificações por email/Slack para falhas
- [ ] Cache inteligente com Redis
- [ ] Métricas e monitoring com Prometheus
- [ ] ~~Deploy automático CI/CD~~ ✅ **Implementado!**
- [ ] Rate limiting na API
- [ ] Logs estruturados com ELK Stack
- [ ] Backup automático do banco
- [ ] Alertas para falhas de scraping

## ✅ Projeto Validado

O projeto foi desenvolvido seguindo todas as melhores práticas e passa em 100% dos testes de validação:

```bash
# Execute a validação do projeto
python validate_project.py
```

**Características validadas:**
- ✅ Clean Architecture implementada
- ✅ Princípios SOLID aplicados  
- ✅ Documentação Swagger configurada
- ✅ Testes automatizados (unitários e integração)
- ✅ **PostgreSQL** configurado com índices otimizados
- ✅ Docker configurado corretamente
- ✅ Estrutura de pastas organizada

## 🎉 Conclusão

**A JusCash API está oficialmente em produção e totalmente funcional!**

### ✅ **Status do Projeto:**
- **🚀 Deploy realizado com sucesso** na VPS Hostinger
- **🌐 Aplicação online** e acessível via HTTPS
- **📊 Todos os serviços operacionais** (PostgreSQL, Redis, Celery, Flower)
- **🔒 SSL configurado** com Let's Encrypt
- **📖 Documentação ativa** via Swagger UI
- **🛡️ Infraestrutura robusta** com Docker e Nginx

### 🌍 **Acesse agora:**
- **API Principal**: https://cron.juscash.app
- **Documentação**: https://cron.juscash.app/docs/

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
⌊吠獥整䌠⽉䑃ⴠ圠摥䨠湵㈠‵㜱㔺㨲㠵ⴠ㌰㈠㈰ਵ‣敔瑳⁥楦慮⁬䥃䌯⁄‭档癡⁥卓⁈潣牲杩摩⁡‭敗⁤畊⁮㔲ㄠ㨷㜵㈺‴〭″〲㔲⌊䨠獵慃桳䄠䥐ⴠ吠獥整䐠灥潬⁹畁潴썭璡捩⁯敗⁤畊⁮㔲ㄠ㨸㐴ㄺ‵〭″〲㔲�