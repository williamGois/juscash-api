# 🔐 Sistema Automatizado de SECRET_KEY no Docker

Implementamos um sistema completo para gerar e gerenciar automaticamente a SECRET_KEY no Docker, eliminando a necessidade de configuração manual.

## 🚀 Como Funciona

### **1. Geração Automática no Docker**
O `docker-entrypoint.sh` verifica se a SECRET_KEY existe e gera automaticamente se necessário:

```bash
# Se SECRET_KEY não existir, gera automaticamente
if [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
    echo "✅ SECRET_KEY gerada automaticamente"
fi
```

### **2. Configuração Automática do .env**
O `docker-compose.yml` lê automaticamente as variáveis do arquivo `.env`:

```yaml
environment:
  - SECRET_KEY=${SECRET_KEY}  # Lê do .env ou gera automaticamente
  - DATABASE_URL=${DATABASE_URL:-postgresql://juscash:juscash123@db:5432/juscash_db}
```

## 🛠️ Métodos de Configuração

### **Método 1: Automático (Recomendado)**
```bash
# Docker gera SECRET_KEY automaticamente
docker-compose up --build

# ✅ SECRET_KEY é gerada na primeira execução
# ✅ Funciona sem configuração manual
```

### **Método 2: Pré-configurado**
```bash
# 1. Gerar .env automaticamente (Linux/Mac)
./setup-env.sh

# 2. Ou gerar .env manualmente (Windows)
python generate_secret_key.py
# Copiar uma das chaves para .env

# 3. Executar Docker
docker-compose up --build
```

### **Método 3: Railway/Produção**
```bash
# 1. Gerar chave
python generate_secret_key.py

# 2. Configurar no Railway
# Variables → SECRET_KEY = [chave-gerada]

# 3. Deploy automático
```

## 📋 Scripts Disponíveis

### **generate_secret_key.py**
```bash
python generate_secret_key.py
```
**Saída:**
```
🔐 SECRET_KEY geradas com segurança:
============================================================
Opção 1 (URL-safe): zETCNBuqEI6c5L3Mu-jQTt...
Opção 2 (Hex):      827dca5dbbb970dd128e3d91...
Opção 3 (Token):    80dff3b5f73271ebed76355...
```

### **setup-env.sh** (Linux/Mac)
```bash
./setup-env.sh
```
- ✅ Cria `.env` automaticamente
- ✅ Gera SECRET_KEY segura
- ✅ Configura todas as variáveis

### **setup-env.ps1** (Windows)
```powershell
powershell -ExecutionPolicy Bypass -File setup-env.ps1
```
- ✅ Versão PowerShell
- ✅ Mesma funcionalidade

## 🔧 Estrutura do docker-compose.yml

```yaml
services:
  web:
    build: .
    environment:
      - SECRET_KEY=${SECRET_KEY}                    # ← Automático
      - DATABASE_URL=${DATABASE_URL:-postgresql://...}
      - REDIS_URL=${REDIS_URL:-redis://redis:6379/0}
      - FLASK_ENV=${FLASK_ENV:-development}

  celery:
    build: .
    environment:
      - SECRET_KEY=${SECRET_KEY}                    # ← Automático
```

## ⚡ Fluxo de Execução

### **Primeira Execução (Sem .env)**
1. `docker-compose up --build`
2. Container inicia → `docker-entrypoint.sh`
3. **Verifica**: `SECRET_KEY` não existe
4. **Gera**: `SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")`
5. **Exporta**: `export SECRET_KEY=...`
6. **Inicia**: Aplicação com SECRET_KEY gerada

### **Próximas Execuções (Com .env)**
1. `docker-compose up`
2. **Lê**: SECRET_KEY do arquivo `.env`
3. **Confirma**: `✅ SECRET_KEY encontrada: zETCNBuqE...`
4. **Inicia**: Aplicação com SECRET_KEY do .env

## 🔍 Verificação e Debug

### **Verificar SECRET_KEY no Container**
```bash
# Entrar no container
docker-compose exec web bash

# Verificar variável
echo $SECRET_KEY

# Verificar logs
docker-compose logs web | grep SECRET_KEY
```

### **Logs Esperados**
```
web_1  | 🚀 Iniciando JusCash API...
web_1  | 🔐 SECRET_KEY não encontrada, gerando automaticamente...
web_1  | ✅ SECRET_KEY gerada: zETCNBuqEI6c5L3Mu...
web_1  | ⏳ Aguardando PostgreSQL...
```

## 📁 Arquivos Criados/Modificados

```
juscash-api/
├── setup-env.sh           ← Script Linux/Mac
├── setup-env.ps1          ← Script Windows  
├── docker-entrypoint.sh   ← Modificado (geração automática)
├── docker-compose.yml     ← Modificado (variáveis .env)
├── .env.example           ← Template configuração
└── generate_secret_key.py ← Script geração manual
```

## 🎯 Vantagens do Sistema

- ✅ **Zero configuração manual** no Docker
- ✅ **Compatível** com desenvolvimento local e produção
- ✅ **Seguro** - chaves únicas e seguras
- ✅ **Flexível** - múltiplos métodos de configuração
- ✅ **Logs** informativos para debug
- ✅ **Cross-platform** - Linux, Mac, Windows

## ⚠️ Segurança

- **NUNCA** comite `.env` no git
- **SEMPRE** use chaves diferentes para produção
- **SECRET_KEY** é gerada com `secrets.token_urlsafe(64)` (seguro)
- **Logs** mostram apenas os primeiros 20 caracteres

## 🚀 Comandos Finais

```bash
# Setup completo automático
docker-compose up --build

# Ou com pré-configuração
./setup-env.sh && docker-compose up --build

# Para produção (Railway)
python generate_secret_key.py
# [Configurar no Railway Dashboard]
```

**🎉 Resultado:** API funcionando com SECRET_KEY gerada automaticamente!
