# Guia de Configuração SSH para CI/CD

## 🔧 Configurando SSH para GitHub Actions

### Passo 1: Gerar Chave SSH na VPS

Acesse sua VPS e execute:

```bash
# 1. Gerar nova chave SSH (sem senha)
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions -N ""

# 2. Adicionar chave pública ao authorized_keys
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 3. Mostrar a chave privada
cat ~/.ssh/github_actions
```

### Passo 2: Configurar Secrets no GitHub

1. Vá para seu repositório no GitHub
2. Clique em **Settings** → **Secrets and variables** → **Actions**
3. Clique em **New repository secret**
4. Adicione os seguintes secrets:

#### VPS_HOST
- **Name**: `VPS_HOST`
- **Value**: IP do seu servidor (ex: `123.456.789.0`)

#### VPS_USER
- **Name**: `VPS_USER`
- **Value**: `root` (ou seu usuário SSH)

#### VPS_SSH_KEY
- **Name**: `VPS_SSH_KEY`
- **Value**: Cole TODO o conteúdo da chave privada, incluindo:
```
-----BEGIN OPENSSH PRIVATE KEY-----
[conteúdo da chave]
-----END OPENSSH PRIVATE KEY-----
```

### Passo 3: Testar Conexão

Para testar se está funcionando, faça um push ou execute manualmente:

1. Vá em **Actions** no GitHub
2. Clique no workflow **Deploy to VPS**
3. Clique em **Run workflow**

## 🔍 Troubleshooting

### Erro: "can't connect without a private SSH key"
- Verifique se o secret `VPS_SSH_KEY` está configurado
- Certifique-se de copiar TODA a chave, incluindo BEGIN e END

### Erro: "Permission denied"
- Verifique se a chave pública está em `~/.ssh/authorized_keys` na VPS
- Verifique permissões: `chmod 600 ~/.ssh/authorized_keys`

### Erro: "Host key verification failed"
- Adicione o host ao known_hosts:
```bash
ssh-keyscan -H seu-ip >> ~/.ssh/known_hosts
``` 