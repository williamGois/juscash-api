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
- ✅ Removido `set -e` e adicionado tratamento granular de erros
- ✅ Verificação de dependências (Python3, Docker, Docker Compose)
- ✅ Logs detalhados para debug em caso de falha
- ✅ **MONITORAMENTO AVANÇADO:** Verificação HTTP da aplicação a cada 10s
- ✅ **DEBUG COMPLETO:** Logs de web, DB e Redis em caso de crash
- ✅ **TIMEOUT INTELIGENTE:** 6 verificações de 10s com status HTTP

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
- ✅ **AJUSTADO PARA VPS 1 CPU:** Todos os limites de CPU reduzidos para serem compatíveis
- ✅ Reduzido workers Gunicorn de 4 para 2, concorrência Celery de 2 para 1

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

## ⚠️ Última Atualização - 04:17:00 - DEBUG AVANÇADO IMPLEMENTADO
As mudanças neste commit resolvem:
1. ❌ **Problema atual:** Container inicia mas aplicação pode estar crashando silenciosamente
2. ✅ **MONITORAMENTO IMPLEMENTADO:** Script agora verifica status HTTP da aplicação
3. ✅ **DEBUG AVANÇADO:** 
   - Verificação HTTP a cada 10 segundos (6x)
   - Logs completos de web, DB e Redis em caso de crash
   - Detecção precisa se container crasha ou aplicação falha
   - Timeout inteligente com feedback contínuo
4. ✅ **RECURSOS OTIMIZADOS:** VPS 1 CPU compatível (~0.9 CPU total)
5. ✅ **DIAGNÓSTICO COMPLETO:** Identificará exatamente onde está o problema

🔍 **AGORA COM MONITORAMENTO AVANÇADO - PROBLEMAS SERÃO DETECTADOS E LOGADOS!**

## 📊 Resumo das Otimizações de Recursos

### Antes (❌ Incompatível com VPS 1 CPU):
- **Total CPU:** 3.8 CPUs (DB:1 + Redis:0.5 + Web:2 + Worker:1 + Flower:0.5)
- **Total RAM:** ~5GB  
- **Workers:** Gunicorn 4 workers + Celery 2 concorrência

### Depois (✅ Otimizado para VPS 1 CPU):
- **Total CPU:** ~0.9 CPUs (DB:0.2 + Redis:0.1 + Web:0.5 + Worker:0.2 + Flower:0.1)
- **Total RAM:** ~2.4GB
- **Workers:** Gunicorn 2 workers + Celery 1 concorrência

### Resultado:
- ✅ Compatível com VPS básico de 1 CPU
- ✅ Uso eficiente de recursos  
- ✅ Performance adequada para aplicação de produção 