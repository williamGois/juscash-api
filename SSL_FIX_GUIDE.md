# Guia de Correção SSL - JusCash API

## Problema Identificado

Os subdomínios estão apresentando erro SSL: `net::ERR_CERT_COMMON_NAME_INVALID`

## Subdomínios Afetados

- `portainer.juscash.app` - Interface do Portainer (Docker)
- `flower.juscash.app` - Interface do Flower (Celery)
- `cadvisor.juscash.app` - Interface do cAdvisor (Monitoramento)
- `cron.juscash.app` - API de Cron Jobs
- `www.juscash.app` - Site principal

## Configuração DNS Atual

Todos os subdomínios estão configurados como CNAME apontando para `juscash.app`:
```
CNAME	www	0	juscash.app	300
CNAME	cadvisor	0	juscash.app	14400
CNAME	flower	0	juscash.app	14400
CNAME	portainer	0	juscash.app	14400
CNAME	cron	0	juscash.app	14400
```

## Solução Rápida

### 1. Executar Diagnóstico

```bash
sudo ./scripts/diagnose-ssl.sh
```

### 2. Corrigir Certificados SSL

```bash
sudo ./scripts/fix-ssl-subdomains.sh
```

### 3. Verificar Resultado

Após a execução, teste os subdomínios:
- https://portainer.juscash.app
- https://flower.juscash.app
- https://cadvisor.juscash.app
- https://cron.juscash.app

## Como o Script Funciona

### 1. Backup dos Certificados Existentes
- Cria backup em `/etc/letsencrypt/backup-YYYYMMDD/`

### 2. Para o Nginx Temporariamente
- Necessário para usar método `--standalone` do certbot

### 3. Remove Certificados Antigos
- Limpa certificados corrompidos ou inválidos

### 4. Gera Novos Certificados
- Usa Let's Encrypt para cada subdomínio individualmente
- Método `--standalone` (mais confiável)

### 5. Verifica e Reinicia Nginx
- Testa configuração antes de ativar
- Reinicia serviços

## Configuração Nginx

### Arquivos de Configuração
```
nginx/
├── portainer.juscash.app.conf  # Portainer (porta 9000)
├── flower.juscash.app.conf     # Flower (porta 5555)
├── cadvisor.juscash.app.conf   # cAdvisor (porta 8080)
└── cron.juscash.app.conf       # API Cron (porta 5000/api/cron)
```

### Estrutura Padrão de Cada Configuração
```nginx
server {
    listen 80;
    server_name subdomain.juscash.app;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name subdomain.juscash.app;
    
    ssl_certificate /etc/letsencrypt/live/subdomain.juscash.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/subdomain.juscash.app/privkey.pem;
    
    # Headers de segurança e proxy para serviço local
}
```

## Problema: Certificado Cruzado (Portainer usando certificado do cron)

### Sintoma
- Portainer mostra certificado com CN=cron.juscash.app
- Browser exibe erro de certificado inválido

### Solução Rápida
```bash
sudo ./scripts/fix-portainer-ssl.sh
```

### Causa Provável
- Certificados wildcard ou compartilhados
- Cache do nginx ou browser
- Ordem de geração dos certificados

## Troubleshooting

### Se o Script Falhar

1. **Verifique DNS**:
```bash
nslookup portainer.juscash.app
nslookup flower.juscash.app
nslookup cadvisor.juscash.app
nslookup cron.juscash.app
```

2. **Verifique Firewall**:
```bash
sudo ufw status
sudo iptables -L
```

3. **Verifique Logs**:
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

### Certificado Wildcard (Alternativo)

Para um certificado wildcard `*.juscash.app`:
```bash
sudo certbot certonly --manual --preferred-challenges dns -d "*.juscash.app" -d "juscash.app"
```

**Nota**: Requer configuração manual de registro TXT no DNS.

## Renovação Automática

### Habilitar Timer do Certbot
```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
sudo systemctl status certbot.timer
```

### Testar Renovação
```bash
sudo certbot renew --dry-run
```

## Comandos Úteis

### Verificar Certificados
```bash
sudo certbot certificates
```

### Testar SSL de um Subdomínio
```bash
openssl s_client -connect portainer.juscash.app:443 -servername portainer.juscash.app
```

### Verificar Expiração
```bash
openssl x509 -enddate -noout -in /etc/letsencrypt/live/portainer.juscash.app/fullchain.pem
```

### Recarregar Nginx
```bash
sudo nginx -t && sudo systemctl reload nginx
```

## Monitoramento

### Status dos Serviços
```bash
sudo systemctl status nginx
sudo systemctl status certbot.timer
```

### Logs em Tempo Real
```bash
sudo tail -f /var/log/nginx/portainer.juscash.app.access.log
sudo tail -f /var/log/nginx/flower.juscash.app.error.log
```

## Conclusão

Com essa configuração:
- ✅ Cada subdomínio terá seu próprio certificado SSL válido
- ✅ Renovação automática configurada
- ✅ Redirecionamento HTTP → HTTPS
- ✅ Headers de segurança aplicados
- ✅ Logs separados por subdomínio

O erro `net::ERR_CERT_COMMON_NAME_INVALID` será resolvido após a execução do script de correção.