# 🔐 Configurar SSH no Cursor para VPS Hostinger

## 📋 **Informações do Servidor**
- **Host**: srv525028.hstgr.cloud
- **IP**: 77.37.68.178
- **User**: root
- **Password**: Syberya1989@@

## 🔧 **Passo 1: Gerar Chave SSH (Recomendado)**

### No seu computador local (Windows):

```powershell
# Abrir PowerShell como administrador
# Gerar chave SSH
ssh-keygen -t rsa -b 4096 -C "seu-email@exemplo.com"

# Pressionar Enter para usar local padrão: C:\Users\SeuUsuario\.ssh\id_rsa
# Pressionar Enter duas vezes para não usar senha (ou criar uma senha)
```

### Localização das chaves:
- **Chave privada**: `C:\Users\SeuUsuario\.ssh\id_rsa`
- **Chave pública**: `C:\Users\SeuUsuario\.ssh\id_rsa.pub`

## 🔑 **Passo 2: Copiar Chave Pública para VPS**

```powershell
# Visualizar chave pública
Get-Content C:\Users\SeuUsuario\.ssh\id_rsa.pub

# Copiar o conteúdo (começando com ssh-rsa...)
```

### No VPS (conectar via password primeiro):
```bash
# Conectar no VPS
ssh root@77.37.68.178
# Password: Syberya1989@@

# Criar diretório .ssh se não existir
mkdir -p ~/.ssh

# Adicionar sua chave pública
nano ~/.ssh/authorized_keys
# Colar a chave pública aqui e salvar (Ctrl+X, Y, Enter)

# Definir permissões corretas
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# Reiniciar SSH (opcional)
systemctl restart ssh
```

## ⚙️ **Passo 3: Configurar SSH Config**

Criar arquivo de configuração SSH no Windows:

```powershell
# Criar/editar arquivo config
notepad C:\Users\SeuUsuario\.ssh\config
```

**Conteúdo do arquivo config:**
```
# JusCash VPS Hostinger
Host juscash-vps
    HostName 77.37.68.178
    User root
    Port 22
    IdentityFile C:\Users\SeuUsuario\.ssh\id_rsa
    ServerAliveInterval 60
    ServerAliveCountMax 3

# Alternativo com hostname
Host juscash-host
    HostName srv525028.hstgr.cloud
    User root
    Port 22
    IdentityFile C:\Users\SeuUsuario\.ssh\id_rsa
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

## 🖥️ **Passo 4: Configurar no Cursor**

### Opção A: Extensão Remote-SSH

1. **Instalar extensão**:
   - Abrir Cursor
   - Ir em Extensions (Ctrl+Shift+X)
   - Buscar "Remote - SSH"
   - Instalar

2. **Conectar**:
   - Pressionar `Ctrl+Shift+P`
   - Digitar: "Remote-SSH: Connect to Host"
   - Selecionar: `juscash-vps` ou `juscash-host`

### Opção B: Terminal Integrado

1. **Abrir terminal no Cursor**:
   - Pressionar `Ctrl+`` (backtick)

2. **Conectar via SSH**:
   ```bash
   # Com chave SSH configurada
   ssh juscash-vps
   
   # Ou direto
   ssh root@77.37.68.178
   ```

## 🧪 **Passo 5: Testar Conexão**

```powershell
# Testar conexão SSH
ssh juscash-vps

# Deve conectar sem pedir senha se a chave estiver configurada
# Se pedir senha, algo está errado na configuração
```

## 🔐 **Configuração Alternativa (Senha)**

Se preferir usar senha ao invés de chave SSH:

**Arquivo config simples:**
```
Host juscash-vps
    HostName 77.37.68.178
    User root
    Port 22
    PreferredAuthentications password
```

## 🛡️ **Melhorar Segurança SSH (Recomendado)**

### No VPS, editar configuração SSH:
```bash
# Editar config SSH
nano /etc/ssh/sshd_config

# Adicionar/modificar estas linhas:
PermitRootLogin yes
PasswordAuthentication no  # Desabilitar senha após configurar chave
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
Port 22  # Ou mudar para porta customizada (ex: 2222)

# Reiniciar SSH
systemctl restart ssh
```

## 📝 **Comandos Úteis SSH**

```powershell
# Testar conexão
ssh -T juscash-vps

# Conectar com verbose (debug)
ssh -v juscash-vps

# Conectar executando comando direto
ssh juscash-vps "docker-compose ps"

# Copiar arquivo local para VPS
scp arquivo.txt juscash-vps:/opt/juscash/

# Copiar arquivo do VPS para local
scp juscash-vps:/opt/juscash/logs/app.log ./
```

## 🖼️ **Interface Visual no Cursor**

Depois de configurar, no Cursor você terá:

1. **Sidebar Remote**: Lista de conexões SSH
2. **Terminal direto**: Acesso ao VPS
3. **File Explorer**: Navegar arquivos do VPS
4. **Editor remoto**: Editar arquivos diretamente no servidor

## 🔄 **Troubleshooting**

### Erro: "Permission denied (publickey)"
```bash
# Verificar se chave está carregada
ssh-add -l

# Adicionar chave manualmente
ssh-add C:\Users\SeuUsuario\.ssh\id_rsa
```

### Erro: "Host key verification failed"
```bash
# Limpar host key antigo
ssh-keygen -R 77.37.68.178
ssh-keygen -R srv525028.hstgr.cloud
```

### Erro: "Connection refused"
```bash
# Verificar se SSH está rodando no VPS
ssh root@77.37.68.178 "systemctl status ssh"
```

## 🎯 **Resultado Final**

Após configuração completa, você poderá:

✅ **Conectar instantaneamente**: `ssh juscash-vps`  
✅ **Editar arquivos remotos** direto no Cursor  
✅ **Terminal integrado** no VPS  
✅ **Transferir arquivos** facilmente  
✅ **Deploy direto** do Cursor para VPS

---

**🚀 SSH configurado = Deploy mais rápido e desenvolvimento mais eficiente!** 