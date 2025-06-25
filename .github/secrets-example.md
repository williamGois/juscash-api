# 🔐 GitHub Secrets - Configuração

## 📋 Repository Secrets Necessários

Vá para: **Repositório → Settings → Secrets and variables → Actions → New repository secret**

### **Obrigatórios:**

| Nome | Valor | Descrição |
|------|-------|-----------|
| `SSH_PRIVATE_KEY` | `-----BEGIN OPENSSH PRIVATE KEY-----`<br/>`[CONTEÚDO DA CHAVE]`<br/>`-----END OPENSSH PRIVATE KEY-----` | Chave SSH privada para acesso ao servidor |
| `VPS_HOST` | `77.37.68.178` | IP do servidor VPS |
| `VPS_USER` | `root` | Usuário SSH do servidor |

### **Opcionais:**

| Nome | Valor | Descrição |
|------|-------|-----------|
| `DISCORD_WEBHOOK` | `https://discord.com/api/webhooks/...` | URL do webhook Discord para notificações |

---

## 🔧 Como Obter os Valores

### 1. **SSH_PRIVATE_KEY**

```bash
# Execute o script de configuração
./setup-cicd.sh

# OU gere manualmente
ssh-keygen -t ed25519 -f ~/.ssh/juscash_cicd -N "" -C "juscash-cicd@github-actions"

# Copie o conteúdo da chave privada
cat ~/.ssh/juscash_cicd
```

**⚠️ IMPORTANTE:** Copie **toda** a chave, incluindo as linhas `-----BEGIN` e `-----END`

### 2. **VPS_HOST e VPS_USER**

Estes valores são fixos para nossa VPS:
- **VPS_HOST**: `77.37.68.178`
- **VPS_USER**: `root`

### 3. **DISCORD_WEBHOOK (Opcional)**

1. Acesse seu servidor Discord
2. **Settings → Integrations → Webhooks**
3. **Create Webhook**
4. **Copy Webhook URL**

---

## ✅ Verificação

Após configurar os secrets, você pode testar fazendo um push:

```bash
git add .
git commit -m "test: CI/CD configuration"
git push origin main
```

Monitore em: **GitHub → Actions**

---

## 🔍 Troubleshooting

### **❌ "SSH Permission Denied"**
- Verifique se a chave SSH foi adicionada corretamente
- Execute `./setup-cicd.sh` novamente

### **❌ "Host key verification failed"**
- O workflow adiciona automaticamente o host conhecido
- Verifique se o `VPS_HOST` está correto

### **❌ "Discord webhook failed"**
- Verifique se a URL do webhook está correta
- Este secret é opcional - pode funcionar sem ele

---

## 🔐 Segurança

- ✅ **Nunca** commite secrets no código
- ✅ Use apenas GitHub Secrets
- ✅ Chave SSH específica para CI/CD
- ✅ Rotacione chaves periodicamente 