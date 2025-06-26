# 🔐 Configuração Segura da VPS - JusCash API

## ⚠️ IMPORTANTE: Segurança de Credenciais

Este projeto agora implementa práticas de segurança adequadas:
- **Senhas NÃO estão mais no Git**
- **Credenciais devem ser geradas localmente na VPS**
- **Arquivo .env é ignorado pelo Git**

## 🚀 Setup na VPS

### 🚨 **CORREÇÃO IMEDIATA DO ERRO ATUAL**

Se você está vendo erro de autenticação, execute estes passos:

```bash
# 1. Ir para o diretório do projeto
cd /caminho/para/juscash-api

# 2. Fazer pull do código atualizado
git pull origin master

# 3. Parar containers atuais
docker-compose -f docker-compose.prod.yml down

# 4. Limpar volumes do PostgreSQL (REMOVE DADOS!)
docker volume rm $(docker volume ls -q | grep postgres)

# 5. Restart com valores padrão (temporário)
docker-compose -f docker-compose.prod.yml up --build -d
```

### 📋 **Setup Completo e Seguro:**

### 1. Fazer pull do código atualizado
```bash
cd /caminho/para/juscash-api
git pull origin master
```

### 2. Gerar credenciais seguras
```bash
# Executar script que gera senhas aleatórias
./generate-env-prod.sh
```

### 3. Verificar arquivo .env gerado
```bash
# Verificar se o arquivo foi criado (SEM exibir as senhas)
ls -la .env
head -5 .env
```

### 4. Parar serviços atuais
```bash
docker-compose -f docker-compose.prod.yml down
```

### 5. Limpar volumes antigos (CUIDADO: remove dados!)
```bash
# ATENÇÃO: Isso apagará dados do banco existente
docker volume rm juscash-api_postgres_data
docker volume rm juscash-api_redis_data
```

### 6. Rebuild e restart com novas credenciais
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

### 7. Verificar logs
```bash
# Verificar se todos os serviços iniciaram
docker-compose -f docker-compose.prod.yml ps

# Ver logs da aplicação
docker-compose -f docker-compose.prod.yml logs web

# Ver logs do banco
docker-compose -f docker-compose.prod.yml logs db
```

### 8. Verificar variáveis de ambiente
```bash
# NOVO: Endpoint de diagnóstico (não mostra senhas)
curl https://cron.juscash.app/api/simple/env-check
```

### 9. Criar tabela do banco
```bash
# Acessar endpoint para criar tabela
curl https://cron.juscash.app/api/publicacoes/setup-database
```

## 🔍 Verificação de Funcionamento

```bash
# Health check geral
curl https://cron.juscash.app/api/simple/ping

# Diagnóstico de variáveis (sem mostrar senhas)
curl https://cron.juscash.app/api/simple/env-check

# Health check específico das publicações
curl https://cron.juscash.app/api/publicacoes/health

# Listar publicações (deve retornar array vazio inicialmente)
curl https://cron.juscash.app/api/publicacoes/
```

## 🛡️ Segurança Implementada

### ✅ O que foi corrigido:
- Removidas senhas hardcoded do docker-compose.prod.yml
- Atualizado .gitignore para ignorar arquivos .env
- Criado script para gerar credenciais seguras
- Documentado processo seguro de deploy

### ✅ Arquivo .env agora contém:
- SECRET_KEY aleatória de 64 caracteres
- POSTGRES_PASSWORD aleatória de 32 caracteres  
- FLOWER_PASSWORD aleatória de 16 caracteres
- URLs de conexão geradas automaticamente

### ❌ O que NÃO está mais no Git:
- Senhas do PostgreSQL
- Chaves secretas
- Credenciais de serviços

## 🚨 Em caso de erro

### Se der erro de autenticação:
1. Verificar se .env existe: `ls -la .env`
2. Verificar variáveis: `docker-compose -f docker-compose.prod.yml config`
3. Regenerar credenciais: `./generate-env-prod.sh`
4. Restart completo: `docker-compose -f docker-compose.prod.yml up --build -d`

### Se container não iniciar:
```bash
# Logs detalhados
docker-compose -f docker-compose.prod.yml logs --tail=50

# Verificar containers em execução
docker ps -a

# Restart específico de um serviço
docker-compose -f docker-compose.prod.yml restart web
```

## 📝 Backup de Credenciais

**IMPORTANTE**: Após gerar as credenciais, faça backup seguro:

1. Copie o arquivo .env para local seguro
2. Anote as senhas em gerenciador de senhas
3. NÃO envie por email ou chat

O arquivo .env é fundamental para o funcionamento da aplicação!