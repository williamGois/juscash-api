# Correção do Deploy - Problema de Autenticação PostgreSQL

## Problema Identificado
O deploy estava falhando com erro de autenticação PostgreSQL:
```
psql: error: connection to server at "db" (172.20.0.3), port 5432 failed: FATAL: password authentication failed for user "juscash"
```

## Causa Raiz
1. O workflow do GitHub Actions estava usando `docker-compose.yml` (desenvolvimento) ao invés de `docker-compose.prod.yml` (produção)
2. As variáveis de ambiente não estavam sendo carregadas corretamente
3. Senhas hard-coded diferentes entre os ambientes

## Correções Aplicadas

### 1. Workflow de Deploy (`.github/workflows/deploy.yml`)
- ✅ Alterado para usar `docker-compose.prod.yml` em todos os comandos
- ✅ Adicionada geração automática de arquivo `.env` com senhas seguras
- ✅ Configuração correta das variáveis de ambiente do PostgreSQL
- ✅ Removido comando `create-tables.py` inexistente (tabelas são criadas pelo `run.py`)
- ✅ Melhorada a sequência de inicialização dos containers

### 2. Configurações de Ambiente
O script agora cria automaticamente um arquivo `.env` com:
- `POSTGRES_USER=juscash`
- `POSTGRES_PASSWORD` (gerada aleatoriamente com 32 caracteres seguros)
- `DATABASE_URL` configurada corretamente com a senha gerada
- `REDIS_URL` sem senha (rede privada Docker)
- `SECRET_KEY` (gerada aleatoriamente com 64 caracteres seguros)
- Outras variáveis essenciais para produção

### 3. Sequência de Deploy Corrigida
1. Para containers web existentes
2. Remove imagens antigas
3. Cria/valida arquivo `.env` com senhas seguras
4. Inicia banco e Redis com configuração de produção
5. Aguarda banco ficar pronto
6. Constrói nova imagem web
7. Inicia aplicação web
8. Inicia worker Celery
9. Inicia Flower para monitoramento

## Próximo Deploy
O próximo push para `master` deve resolver o problema de autenticação automaticamente.

## Verificação Pós-Deploy
Após o deploy, verificar:
- Containers rodando: `docker-compose -f docker-compose.prod.yml ps`
- Logs da aplicação: `docker-compose -f docker-compose.prod.yml logs web`
- Endpoint da API: `curl http://localhost:5000/api/simple/ping`

## Status das Correções
✅ **Correções aplicadas em:** $(date +'%Y-%m-%d %H:%M:%S')  
✅ **Workflow de deploy corrigido**  
✅ **Configuração de ambiente ajustada**  
✅ **Pronto para novo deploy**  

As mudanças neste commit devem resolver automaticamente o problema de autenticação do PostgreSQL no próximo deploy. 