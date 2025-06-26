# Guia CI/CD - JusCash API

## 📋 Visão Geral

O CI/CD está configurado com GitHub Actions para deploy automático na VPS.

## 🔧 Configuração

### 1. Secrets do GitHub

No repositório, vá em Settings > Secrets e adicione:

- `VPS_HOST`: IP do servidor
- `VPS_USER`: Usuário SSH (geralmente `root`)
- `VPS_SSH_KEY`: Chave privada SSH

### 2. Fluxo do Pipeline

```mermaid
graph LR
    A[Push Master] --> B[Run Tests]
    B --> C[Deploy to VPS]
    C --> D[Verify Health]
```

### 3. Etapas do Deploy

1. **Test**: Executa testes automatizados
2. **Deploy**: 
   - Faz backup do banco
   - Atualiza código via Git
   - Reconstrói containers Docker
   - Aplica migrações
3. **Verify**: Verifica se API está respondendo

## 🚀 Deploy Manual

Se precisar fazer deploy manual:

```bash
ssh root@seu-servidor
cd /var/www/juscash
./scripts/deploy/simple-deploy.sh
```

## 🔍 Monitoramento

Para verificar o status:

```bash
# Ver logs do último deploy
tail -f /var/www/juscash/deploy_*.log

# Ver status dos containers
docker-compose ps

# Ver logs da aplicação
docker-compose logs -f web
```

## ❗ Troubleshooting

### Problema: Deploy falha no Git pull

**Solução**: Limpar arquivos locais
```bash
git stash --include-untracked
git clean -fd
git pull origin master
```

### Problema: Containers não iniciam

**Solução**: Verificar logs
```bash
docker-compose logs
docker ps -a
```

### Problema: Migrações falhando

**Solução**: Executar manualmente
```bash
docker-compose exec web flask db upgrade
``` 