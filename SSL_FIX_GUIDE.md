# 🔐 Guia de Correção SSL para Subdomínios

## ❌ **Problema Identificado**

O erro `net::ERR_CERT_COMMON_NAME_INVALID` ocorre porque:
1. Os certificados SSL não foram gerados para os subdomínios específicos
2. As configurações nginx estão tentando usar certificados que não existem
3. É necessário gerar certificados individuais para cada subdomínio

## 🚀 **Solução Rápida**

### Na VPS, execute os seguintes comandos:

```bash
# 1. Conectar na VPS
ssh root@77.37.68.178

# 2. Ir para o diretório do projeto
cd /root/juscash-api

# 3. Fazer pull das correções
git pull origin master

# 4. Executar script de correção SSL
sudo ./scripts/fix-ssl-subdomains.sh
```

## 🔧 **O que o script faz:**

### Passo 1: HTTP Temporário
- ✅ Remove configurações SSL problemáticas
- ✅ Configura HTTP simples para cada subdomínio
- ✅ Prepara validação Let's Encrypt

### Passo 2: Certificados SSL
- 📜 Gera certificado individual para `portainer.juscash.app`
- 📜 Gera certificado individual para `cadvisor.juscash.app`  
- 📜 Gera certificado individual para `flower.juscash.app`

### Passo 3: HTTPS Final
- 🔒 Ativa configurações HTTPS com certificados corretos
- ✅ Testa e valida configuração final

## 📋 **Configurações DNS Necessárias**

**IMPORTANTE**: Antes de executar, verifique se estes registros DNS estão configurados:

```
portainer.juscash.app    A    77.37.68.178
cadvisor.juscash.app     A    77.37.68.178  
flower.juscash.app       A    77.37.68.178
```

## 🔍 **Verificação Manual**

### Teste se os subdomínios resolvem:
```bash
# Testar resolução DNS
nslookup portainer.juscash.app
nslookup cadvisor.juscash.app
nslookup flower.juscash.app

# Testar conectividade HTTP (temporário)
curl -I http://portainer.juscash.app
curl -I http://cadvisor.juscash.app
curl -I http://flower.juscash.app
```

### Após executar o script, testar HTTPS:
```bash
# Testar HTTPS
curl -I https://portainer.juscash.app
curl -I https://cadvisor.juscash.app
curl -I https://flower.juscash.app

# Verificar certificados
sudo certbot certificates
```

## 🚨 **Se der erro durante execução:**

### Erro de DNS:
```bash
# Verificar se DNS está propagado
dig portainer.juscash.app
dig cadvisor.juscash.app
dig flower.juscash.app
```

### Erro de nginx:
```bash
# Verificar configuração
sudo nginx -t

# Ver logs de erro
sudo tail -f /var/log/nginx/error.log
```

### Erro de certificado:
```bash
# Verificar logs do certbot
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Listar certificados existentes
sudo certbot certificates

# Remover certificados problemáticos se necessário
sudo certbot delete --cert-name portainer.juscash.app
```

## ⏰ **Timeline Esperado**

1. **0-5 min**: Configuração HTTP e validação DNS
2. **5-10 min**: Geração de certificados SSL
3. **10-15 min**: Ativação HTTPS
4. **Total**: ~15 minutos

## ✅ **Resultado Esperado**

Após a execução bem-sucedida:

- ✅ `https://portainer.juscash.app` - Interface Docker
- ✅ `https://cadvisor.juscash.app` - Métricas de containers  
- ✅ `https://flower.juscash.app` - Monitor Celery
- ✅ Certificados SSL válidos para todos
- ✅ Redirecionamento HTTP → HTTPS automático

## 🛠️ **Troubleshooting Comum**

### Se um subdomínio específico falhar:

```bash
# Verificar se o container está rodando
docker ps | grep portainer
docker ps | grep cadvisor
docker ps | grep flower

# Verificar se as portas estão abertas
netstat -tlnp | grep :9000   # Portainer
netstat -tlnp | grep :8080   # cAdvisor  
netstat -tlnp | grep :5555   # Flower

# Restart containers se necessário
docker-compose -f docker-compose.prod.yml restart portainer
docker-compose -f docker-compose.prod.yml restart cadvisor
docker-compose -f docker-compose.prod.yml restart flower
```

### Se certificados expirarem:

```bash
# Renovar todos os certificados
sudo certbot renew

# Testar renovação
sudo certbot renew --dry-run
```

## 📞 **Suporte**

Se ainda houver problemas após seguir este guia, execute:

```bash
# Gerar relatório de diagnóstico
sudo nginx -t
sudo certbot certificates  
curl -I https://portainer.juscash.app
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

E me envie a saída destes comandos para análise!