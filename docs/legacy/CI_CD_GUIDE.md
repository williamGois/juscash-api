# 🚀 Guia Completo CI/CD - JusCash API

## 📖 Índice

1. [Visão Geral](#-visão-geral)
2. [Configuração Inicial](#-configuração-inicial)
3. [Workflows Disponíveis](#-workflows-disponíveis)
4. [Ambientes](#-ambientes)
5. [Secrets Necessários](#-secrets-necessários)
6. [Como Usar](#-como-usar)
7. [Troubleshooting](#-troubleshooting)
8. [Melhorias Futuras](#-melhorias-futuras)

---

## 🎯 Visão Geral

Sistema completo de CI/CD usando **GitHub Actions** para deploy automático da JusCash API na VPS Hostinger.

### ✨ **Funcionalidades:**
- ✅ **Testes automatizados** em cada push/PR
- ✅ **Deploy automático** para produção (branch `main/master`)
- ✅ **Deploy para staging** (branch `develop/staging`)
- ✅ **Rollback automático** em caso de falha
- ✅ **Notificações Discord** sobre status do deploy
- ✅ **Backup automático** do banco antes do deploy
- ✅ **Health checks** pós-deploy
- ✅ **Cache inteligente** para acelerar builds

---

## ⚙️ Configuração Inicial

### 🔧 **1. Configuração Automática (Recomendado)**

```bash
# Execute o script de configuração
chmod +x setup-cicd.sh
./setup-cicd.sh
```

**O script vai:**
- 🔐 Gerar chave SSH para CI/CD
- 🌐 Configurar Git no servidor
- 📋 Gerar todos os secrets necessários
- 💾 Salvar informações em `cicd-secrets.txt`

### 🔧 **2. Configuração Manual**

#### **2.1. Gerar Chave SSH:**
```bash
# Gerar chave específica para CI/CD
ssh-keygen -t ed25519 -f ~/.ssh/juscash_cicd -N "" -C "juscash-cicd@github-actions"

# Enviar chave pública para servidor
ssh-copy-id -i ~/.ssh/juscash_cicd.pub root@77.37.68.178
```

#### **2.2. Configurar Servidor:**
```bash
ssh root@77.37.68.178

# Configurar Git
cd /var/www/juscash
git config --global user.name "CI/CD Deploy"
git config --global user.email "cicd@juscash.app"

# Verificar repositório
git remote -v
```

#### **2.3. Adicionar Secrets no GitHub:**
1. Vá para: **Repositório → Settings → Secrets and variables → Actions**
2. Clique em **New repository secret**
3. Adicione os secrets listados abaixo

---

## 🔐 Secrets Necessários

### **Repository Secrets (obrigatórios):**

| Secret | Valor | Descrição |
|--------|-------|-----------|
| `SSH_PRIVATE_KEY` | Conteúdo de `~/.ssh/juscash_cicd` | Chave SSH para deploy |
| `VPS_HOST` | `77.37.68.178` | IP do servidor VPS |
| `VPS_USER` | `root` | Usuário SSH do servidor |

### **Repository Secrets (opcionais):**

| Secret | Valor | Descrição |
|--------|-------|-----------|
| `DISCORD_WEBHOOK` | URL do webhook Discord | Notificações sobre deploys |

---

## 🔄 Workflows Disponíveis

### **1. 🚀 Production Deploy (`.github/workflows/deploy.yml`)**

**Trigger:** Push para `main` ou `master`

**Etapas:**
1. **🧪 Testes Completos**
   - PostgreSQL + Redis como services
   - Testes unitários e integração
   - Lint com flake8
   - Coverage report

2. **🏗️ Build Docker**
   - Build da imagem Docker
   - Push para GitHub Container Registry
   - Cache inteligente

3. **🚀 Deploy Production**
   - Backup do banco de dados
   - Pull das mudanças do Git
   - Rebuild dos containers
   - Migrações do banco
   - Health check
   - Rollback em caso de falha

4. **📢 Notificações**
   - Status via Discord
   - Logs detalhados

### **2. 🧪 Staging Deploy (`.github/workflows/staging.yml`)**

**Trigger:** Push para `develop` ou `staging`

**Etapas:**
1. **🧪 Testes Rápidos**
   - Apenas testes unitários (mais rápido)

2. **🚀 Deploy Staging**
   - Deploy em porta diferente (5001)
   - Sem interferir com produção
   - Health check

3. **📢 Notificações**
   - Status do staging

---

## 🌍 Ambientes

### **📊 Produção**
- **URL**: https://cron.juscash.app
- **Branch**: `main` / `master`
- **Porta**: 5000
- **Diretório**: `/var/www/juscash`

### **🧪 Staging**
- **URL**: http://77.37.68.178:5001
- **Branch**: `develop` / `staging`
- **Porta**: 5001
- **Diretório**: `/var/www/juscash-staging`

---

## 📋 Como Usar

### **🚀 Deploy para Produção**

```bash
# 1. Fazer mudanças no código
git add .
git commit -m "feat: nova funcionalidade"

# 2. Push para main (trigger automático)
git push origin main

# 3. Acompanhar no GitHub Actions
# https://github.com/SEU_USUARIO/juscash-api/actions
```

### **🧪 Deploy para Staging**

```bash
# 1. Criar/usar branch develop
git checkout -b develop
git add .
git commit -m "test: nova funcionalidade"

# 2. Push para develop (trigger automático)
git push origin develop

# 3. Acessar staging
# http://77.37.68.178:5001/docs/
```

### **🔄 Deploy Manual**

```bash
# Via GitHub Web UI:
# 1. Actions → Workflows
# 2. Select "Staging Deploy"
# 3. Run workflow → escolher branch
# 4. Adicionar motivo (opcional)
```

---

## 🔍 Monitoramento

### **📊 URLs de Monitoramento:**

- **GitHub Actions**: `https://github.com/SEU_USUARIO/juscash-api/actions`
- **Produção**: https://cron.juscash.app/api/cron/health
- **Staging**: http://77.37.68.178:5001/api/cron/health
- **Flower (Prod)**: https://cron.juscash.app/flower
- **Flower (Staging)**: http://77.37.68.178:5556

### **📱 Notificações Discord:**

```javascript
// Configurar webhook Discord:
// 1. Servidor Discord → Settings → Integrations → Webhooks
// 2. Create Webhook
// 3. Copy URL
// 4. Adicionar como DISCORD_WEBHOOK secret
```

---

## 🐛 Troubleshooting

### **❌ Problemas Comuns:**

#### **1. SSH Permission Denied**
```bash
# Verificar chave SSH
ssh -i ~/.ssh/juscash_cicd root@77.37.68.178

# Regenerar chave se necessário
./setup-cicd.sh
```

#### **2. Build Falha**
```bash
# Verificar logs no GitHub Actions
# Actions → Failed workflow → View logs

# Testar localmente
docker-compose build
pytest tests/
```

#### **3. Deploy Falha**
```bash
# Conectar no servidor e verificar
ssh root@77.37.68.178
cd /var/www/juscash
docker-compose ps
docker-compose logs web
```

#### **4. Health Check Falha**
```bash
# Verificar saúde da aplicação
curl http://localhost:5000/api/cron/health

# Verificar containers
docker-compose ps
```

### **🔧 Comandos de Debug:**

```bash
# No servidor VPS
ssh root@77.37.68.178

# Status dos containers
cd /var/www/juscash
docker-compose ps

# Logs detalhados
docker-compose logs --tail=50 web
docker-compose logs --tail=50 db

# Restart manual
docker-compose restart

# Verificar espaço em disco
df -h

# Limpar imagens antigas
docker system prune -f
```

---

## 🛡️ Segurança

### **🔐 Boas Práticas:**

1. **Chaves SSH:**
   - ✅ Chave específica para CI/CD
   - ✅ Sem passphrase (para automação)
   - ✅ Rotação periódica

2. **Secrets:**
   - ✅ Nunca commitar secrets no código
   - ✅ Usar GitHub Secrets
   - ✅ Princípio do menor privilégio

3. **Servidor:**
   - ✅ Firewall configurado (UFW)
   - ✅ SSH keys apenas (sem senha)
   - ✅ Updates automáticos

---

## 📈 Melhorias Futuras

### **🚀 Próximas Implementações:**

- [ ] **Deploy Blue-Green** para zero downtime
- [ ] **Rollback automático** com versioning
- [ ] **Testes E2E** com Playwright
- [ ] **Monitoring** com Prometheus/Grafana
- [ ] **Slack/Teams** notifications
- [ ] **Ambiente de Review** para PRs
- [ ] **Security scanning** com Trivy
- [ ] **Performance testing** automático

### **📊 Métricas Avançadas:**

```yaml
# Exemplo de métricas futuras
jobs:
  metrics:
    name: 📊 Collect Metrics
    steps:
    - name: Deploy Time
    - name: Success Rate
    - name: Rollback Count
    - name: Test Coverage
```

---

## 📞 Suporte

### **🆘 Em caso de problemas:**

1. **Verificar GitHub Actions** primeiro
2. **Consultar logs** do servidor
3. **Executar health checks**
4. **Rollback manual** se necessário

### **📋 Comandos de Emergência:**

```bash
# Rollback rápido (produção)
ssh root@77.37.68.178
cd /var/www/juscash
git reset --hard HEAD~1
docker-compose restart

# Restaurar backup do banco
docker-compose exec -T db psql -U juscash juscash_db < backup_YYYYMMDD.sql

# Restart completo
docker-compose down
docker-compose up -d
```

---

## 📄 Conclusão

**✅ Sistema CI/CD totalmente funcional e automatizado!**

### **🎯 Benefícios Implementados:**
- **⚡ Deploy automático** em segundos
- **🛡️ Segurança** com SSH keys e secrets
- **📊 Monitoramento** completo via GitHub Actions
- **🔄 Rollback** automático em falhas
- **📱 Notificações** em tempo real
- **🧪 Ambiente de staging** para testes

### **🚀 Como Usar:**
1. **Configure** uma vez com `./setup-cicd.sh`
2. **Faça push** para `main` → Deploy automático para produção
3. **Faça push** para `develop` → Deploy automático para staging
4. **Monitore** via GitHub Actions e Discord

**🎉 Deploy automático configurado com sucesso!** 