# 📦 Guia de Comandos Flask-Migrate

Este documento contém todos os comandos necessários para gerenciar as migrações do banco de dados PostgreSQL da JusCash API.

## 🚀 Comandos Básicos

### Inicializar Migrações (Primeira vez)
```bash
flask init-migrations
```
Cria o diretório `migrations/` e arquivos de configuração.

### Aplicar Migrações
```bash
flask upgrade-db
# ou
flask db upgrade
```
Aplica todas as migrações pendentes ao banco de dados.

### Criar Nova Migração
```bash
flask db migrate -m "Descrição da mudança"
```
Gera automaticamente uma migração baseada nas mudanças nos modelos.

### Verificar Status
```bash
flask db current          # Migração atual
flask db history          # Histórico de migrações
flask db-status           # Status da conexão e tabelas
```

## 🔄 Comandos Avançados

### Reverter Migração
```bash
flask db downgrade        # Reverter última migração
flask db downgrade -1     # Reverter 1 migração
flask db downgrade <revision_id>  # Reverter para revisão específica
```

### Criar Migração Vazia (Para scripts customizados)
```bash
flask db revision -m "Script customizado"
```

### Marcar como Aplicada (Sem executar)
```bash
flask db stamp head       # Marcar como última versão
flask db stamp <revision> # Marcar revisão específica
```

### Ver SQL da Migração
```bash
flask db upgrade --sql    # Ver SQL sem executar
flask db downgrade --sql  # Ver SQL de downgrade
```

## 🐳 Docker Commands

### Com Docker Compose
```bash
# Migrações são aplicadas automaticamente
docker-compose up --build

# Executar migração manualmente no container
docker-compose exec web flask upgrade-db

# Ver status no container
docker-compose exec web flask db-status
```

### Container Individual
```bash
# Executar bash no container
docker-compose exec web bash

# Dentro do container
flask db current
flask db history
```

## 📝 Exemplos Práticos

### Workflow Completo de Desenvolvimento

1. **Modificar modelo** (ex: adicionar campo)
```python
# app/infrastructure/database/models.py
class PublicacaoModel(db.Model):
    # ... campos existentes ...
    novo_campo = db.Column(db.String(100), nullable=True)
```

2. **Gerar migração**
```bash
flask db migrate -m "Adicionar campo novo_campo"
```

3. **Revisar migração gerada**
```bash
# Verificar arquivo em migrations/versions/
cat migrations/versions/XXX_adicionar_campo_novo_campo.py
```

4. **Aplicar migração**
```bash
flask upgrade-db
```

5. **Verificar resultado**
```bash
flask db-status
```

### Resolver Conflitos de Migração

```bash
# Verificar estado atual
flask db current

# Ver todas as migrações
flask db history

# Reverter para ponto comum
flask db downgrade <revision_comum>

# Aplicar migração correta
flask upgrade-db
```

## 🔧 Configurações Importantes

### Configuração no `app/__init__.py`
```python
from flask_migrate import Migrate

migrate = Migrate()

def create_app():
    # ...
    migrate.init_app(app, db)
    # Importar modelos para detecção automática
    from app.infrastructure.database.models import PublicacaoModel
```

### Variáveis de Ambiente
```env
FLASK_APP=run.py
FLASK_ENV=development
DATABASE_URL=postgresql://user:pass@host:port/db
```

## ⚠️ Boas Práticas

### ✅ Fazer Sempre
- Revisar migrações geradas antes de aplicar
- Fazer backup do banco antes de migrações importantes
- Testar migrações em ambiente de desenvolvimento primeiro
- Usar mensagens descritivas nas migrações

### ❌ Evitar
- Editar migrações já aplicadas em produção
- Aplicar migrações diretamente em produção sem teste
- Ignorar warnings do Flask-Migrate
- Misturar alterações de schema com dados

## 🚨 Troubleshooting

### Erro: "Target database is not up to date"
```bash
flask db stamp head
flask upgrade-db
```

### Erro: "Can't locate revision identified by..."
```bash
flask db history
flask db stamp <revision_válida>
```

### Migração não detecta mudanças
```bash
# Verificar se modelo foi importado
# Verificar se está no mesmo contexto da aplicação
flask shell
>>> from app.infrastructure.database.models import *
```

### Resetar migrações (CUIDADO!)
```bash
# APENAS EM DESENVOLVIMENTO
rm -rf migrations/
flask init-migrations
flask db migrate -m "Initial migration"
flask upgrade-db
```

**💡 Dica**: Sempre use `flask db-status` para verificar o estado atual antes de executar migrações! 