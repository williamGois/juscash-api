# 🚀 Guia Completo: Deploy JusCash API na VPS Hostinger

## 📋 Informações da VPS
- **IP**: 77.37.68.178
- **SSH**: root@77.37.68.178
- **Senha**: Syberya1989@@
- **SO**: Ubuntu 20.04 LTS
- **Domínio**: cron.juscash.app

## 🔧 Passo a Passo Completo

### 1. 📤 Preparação e Upload (Execute no seu computador)

```bash
# No diretório do projeto juscash-api
chmod +x setup-vps.sh
chmod +x deploy-to-vps.sh
chmod +x generate-env-prod.sh

# Deploy automático
./deploy-to-vps.sh
```

### 2. 🖥️ Configuração Inicial do Servidor (Manual)

Conecte no servidor via SSH:
```bash
ssh root@77.37.68.178
# Senha: Syberya1989@@
```

Execute a configuração inicial:
```bash
cd /var/www/juscash
chmod +x setup-vps.sh
./setup-vps.sh
```

### 3. 🌐 Configuração DNS

**IMPORTANTE**: Configure o DNS do domínio `cron.juscash.app` antes de prosseguir:

1. Acesse o painel do seu provedor de domínio
2. Adicione/edite o registro A:
   - **Nome**: cron
   - **Tipo**: A
   - **Valor**: 77.37.68.178
   - **TTL**: 300 (ou padrão)

### 4. 🔒 Configuração SSL (Após DNS propagado)

```bash
# No servidor, após DNS estar funcionando
certbot --nginx -d cron.juscash.app

# Teste de renovação automática
certbot renew --dry-run
```

### 5. ✅ Verificação e Testes

```bash
# Verificar containers
docker-compose ps

# Ver logs
docker-compose logs web
docker-compose logs worker

# Testar API
curl https://cron.juscash.app/api/cron/health
curl https://cron.juscash.app/docs/
```

## 🌐 URLs da Aplicação

Após configuração completa:

- **API Principal**: https://cron.juscash.app
- **Documentação Swagger**: https://cron.juscash.app/docs/
- **Flower (Celery Monitor)**: https://cron.juscash.app/flower
- **Health Check**: https://cron.juscash.app/api/cron/health

## 🔧 Comandos de Manutenção

### Logs e Monitoramento
```bash
# Ver logs em tempo real
docker-compose logs -f web

# Status dos containers
docker-compose ps

# Uso de recursos
docker stats

# Logs do sistema
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Backup e Restore
```bash
# Backup do banco
docker-compose exec db pg_dump -U juscash juscash_db > backup_$(date +%Y%m%d).sql

# Backup dos dados Docker
docker-compose down
cp -r /var/lib/docker/volumes/ /backup/docker-volumes/
```

### Atualizações
```bash
# Atualizar código
git pull

# Rebuild containers
docker-compose build
docker-compose up -d

# Aplicar migrações
docker-compose exec web python create-tables.py
```

## 🚨 Solução de Problemas

### Container não inicia
```bash
# Ver logs detalhados
docker-compose logs container_name

# Verificar configuração
docker-compose config

# Restart forçado
docker-compose down
docker-compose up -d
```

### Banco de dados
```bash
# Conectar no PostgreSQL
docker-compose exec db psql -U juscash -d juscash_db

# Verificar tabelas
\dt

# Verificar dados
SELECT COUNT(*) FROM publicacoes;
```

### Nginx
```bash
# Testar configuração
nginx -t

# Restart Nginx
systemctl restart nginx

# Ver logs
tail -f /var/log/nginx/error.log
```

## 📊 Monitoramento Contínuo

### Flower (Celery)
- Acesse: https://cron.juscash.app/flower
- Monitore tasks, workers e filas

### Health Checks
```bash
# API Health
curl https://cron.juscash.app/api/cron/health

# Verificar scraping
curl -X POST https://cron.juscash.app/api/cron/scraping/daily
```

### Logs Importantes
```bash
# Aplicação
docker-compose logs web

# Worker Celery
docker-compose logs worker

# Nginx
tail -f /var/log/nginx/access.log

# Sistema
tail -f /var/log/syslog
```

## 🔐 Segurança

### Firewall (já configurado)
```bash
# Ver status
ufw status

# Portas abertas: 22 (SSH), 80 (HTTP), 443 (HTTPS)
```

### SSL/TLS
```bash
# Verificar certificado
certbot certificates

# Forçar renovação
certbot renew --force-renewal
```

### Backup Regular
```bash
# Criar script de backup automático
crontab -e

# Adicionar linha para backup diário às 2:00
0 2 * * * /var/www/juscash/backup.sh
```

## 📞 Suporte

Em caso de problemas:

1. **Verificar logs**: `docker-compose logs`
2. **Status dos serviços**: `docker-compose ps`
3. **Conectividade**: `curl https://cron.juscash.app/api/cron/health`
4. **Recursos**: `docker stats` e `df -h`

## 🎯 Checklist Final

- [ ] DNS configurado e propagado
- [ ] SSL certificado instalado
- [ ] Todos os containers rodando
- [ ] API respondendo em https://cron.juscash.app
- [ ] Swagger acessível em /docs/
- [ ] Flower monitorando em /flower
- [ ] Backup configurado
- [ ] Monitoramento ativo

---

**✅ Projeto pronto para produção!** 