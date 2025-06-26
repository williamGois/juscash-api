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
- ✅ Corrigido erro de sintaxe no heredoc (agora usa echo linha por linha)

### 2. Configurações de Ambiente
O script agora cria automaticamente um arquivo `.env` com:
- `POSTGRES_USER=juscash`
- `POSTGRES_PASSWORD` (gerada aleatoriamente com 32 caracteres seguros)
- `DATABASE_URL` configurada corretamente com a senha gerada
- `REDIS_URL` sem senha (rede privada Docker)
- `SECRET_KEY` (gerada aleatoriamente com 64 caracteres seguros)
- Outras variáveis essenciais para produção

### 3. Docker Compose de Produção (`docker-compose.prod.yml`)
- ✅ Removida linha `version: '3.8'` obsoleta
- ✅ Corrigido conflito de volumes `/app/logs` (removido volume externo, mantido apenas tmpfs)
- ✅ Eliminados warnings do Docker Compose

### 4. Sequência de Deploy Corrigida
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
✅ **Correções aplicadas em:** 2025-06-26 04:05:00  
✅ **Workflow de deploy corrigido** - Erro de sintaxe do script resolvido  
✅ **Configuração de ambiente ajustada** - Arquivo .env criado linha por linha  
✅ **Docker Compose otimizado** - Warnings eliminados  
✅ **Pronto para novo deploy**  

## ⚠️ Última Atualização
As mudanças neste commit resolvem:
1. ❌ **Erro anterior:** Script quebrado por formatação heredoc incorreta
2. ✅ **Correção aplicada:** Geração de .env linha por linha com echo
3. ✅ **Bonus:** Warnings do Docker Compose eliminados

O próximo deploy deve funcionar perfeitamente! 