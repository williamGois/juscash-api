# 🚀 Guia Completo: Deploy JusCash API no VPS Hostinger

## 📋 Informações do Servidor

**VPS Hostinger - São Paulo, Brasil**
- **Host**: srv525028.hstgr.cloud
- **IP**: 77.37.68.178
- **SO**: Ubuntu 20.04 LTS
- **User**: root
- **Password**: Syberya1989@@

## 🔧 Passo 1: Conectar no VPS

```bash
# Via SSH
ssh root@77.37.68.178
# Ou
ssh root@srv525028.hstgr.cloud

# Password: Syberya1989@@
```

## 🛠️ Passo 2: Setup Inicial do Servidor

```bash
# Executar script de setup automático
curl -fsSL https://raw.githubusercontent.com/seu-usuario/juscash-api/main/deploy-vps.sh | bash

# Ou manualmente:
chmod +x deploy-vps.sh
./deploy-vps.sh
```

### Setup Manual (se preferir):

```bash
# 1. Atualizar sistema
apt update && apt upgrade -y

# 2. Instalar Docker
curl -fsSL https://get.docker.com | sh
systemctl start docker
systemctl enable docker

# 3. Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 4. Instalar Git e dependências
apt install -y git nginx ufw htop vim

# 5. Configurar firewall
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# 6. Criar estrutura de diretórios
mkdir -p /opt/juscash/{logs,backups,ssl}
```

## 📥 Passo 3: Clonar e Configurar Aplicação

```bash
# Ir para diretório de trabalho
cd /opt/juscash

# Clonar repositório
git clone https://github.com/seu-usuario/juscash-api.git app
cd app

# Copiar arquivos de configuração para VPS
cp docker-compose.vps.yml docker-compose.yml
cp Dockerfile.vps Dockerfile
cp env.vps .env
```

## ⚙️ Passo 4: Configurar Variáveis de Ambiente

```bash
# Editar arquivo .env
nano .env

# Configurações necessárias:
```

```env
# Gerar chaves seguras
SECRET_KEY=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)

# Database
DATABASE_URL=postgresql://juscash_user:SUA_DB_PASSWORD@postgres:5432/juscash_db
DB_PASSWORD=SUA_DB_PASSWORD

# Redis
REDIS_URL=redis://:SUA_REDIS_PASSWORD@redis:6379/0
REDIS_PASSWORD=SUA_REDIS_PASSWORD

# Celery
CELERY_BROKER_URL=redis://:SUA_REDIS_PASSWORD@redis:6379/0
CELERY_RESULT_BACKEND=redis://:SUA_REDIS_PASSWORD@redis:6379/0

# Domain (altere conforme necessário)
DOMAIN=srv525028.hstgr.cloud
```

## 🐳 Passo 5: Deploy com Docker

```bash
# Build e iniciar containers
docker-compose up -d --build

# Verificar status
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f
```

## 🔄 Passo 6: Executar Migrações

```bash
# Criar tabelas do banco
docker-compose exec web python -c "
from app.infrastructure.database.models import db
from app import create_app
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Tabelas criadas com sucesso!')
"

# Ou via Flask-Migrate (se configurado)
docker-compose exec web flask db upgrade
```

## 🌐 Passo 7: Configurar Nginx

```bash
# Copiar configuração do Nginx
cp nginx.conf /etc/nginx/sites-available/juscash
ln -s /etc/nginx/sites-available/juscash /etc/nginx/sites-enabled/

# Remover site padrão
rm -f /etc/nginx/sites-enabled/default

# Testar configuração
nginx -t

# Reiniciar Nginx
systemctl restart nginx
systemctl enable nginx
```

## 🔒 Passo 8: Configurar SSL (Let's Encrypt)

```bash
# Instalar Certbot
snap install --classic certbot

# Obter certificado SSL
certbot --nginx -d srv525028.hstgr.cloud

# Ou se tiver domínio personalizado:
# certbot --nginx -d api.juscash.com.br

# Configurar renovação automática
crontab -e
# Adicionar linha:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🧪 Passo 9: Testes e Verificação

### 1. Health Check
```bash
curl http://srv525028.hstgr.cloud/health
# Deve retornar: {"status": "healthy", ...}
```

### 2. API Documentation
```bash
# Acessar no browser:
http://srv525028.hstgr.cloud/docs/
```

### 3. Flower (Monitoramento Celery)
```bash
# Acessar no browser:
http://srv525028.hstgr.cloud/flower
```

### 4. Teste de Scraping
```bash
curl -X POST "http://srv525028.hstgr.cloud/api/scraping/extract" \
  -H "Content-Type: application/json" \
  -d '{"data_inicio": "2024-10-01T00:00:00", "data_fim": "2024-10-01T23:59:59"}'
```

## 📊 Passo 10: Monitoramento

### Ver Logs dos Containers
```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f web
docker-compose logs -f worker
docker-compose logs -f postgres
```

### Status dos Serviços
```bash
# Docker containers
docker-compose ps

# Nginx
systemctl status nginx

# Disk space
df -h

# Memory usage
free -h
```

## 🔄 Passo 11: Backup e Manutenção

### Backup do Banco de Dados
```bash
# Script de backup
docker-compose exec postgres pg_dump -U juscash_user juscash_db > /opt/juscash/backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Cron job para backup diário (adicionar no crontab)
# 0 2 * * * cd /opt/juscash && docker-compose exec postgres pg_dump -U juscash_user juscash_db > /opt/juscash/backups/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql
```

### Atualizações
```bash
# Atualizar código
cd /opt/juscash/app
git pull origin main

# Rebuildar e reiniciar
docker-compose down
docker-compose up -d --build
```

## 🎯 URLs Finais

Após o deploy completo, você terá:

- **API Principal**: https://srv525028.hstgr.cloud/api/
- **Documentação**: https://srv525028.hstgr.cloud/docs/
- **Health Check**: https://srv525028.hstgr.cloud/health
- **Flower (Celery)**: https://srv525028.hstgr.cloud/flower

## 🆘 Troubleshooting

### Container não inicia
```bash
# Ver logs detalhados
docker-compose logs web

# Verificar portas em uso
netstat -tulpn | grep :5000
```

### Erro de conexão com banco
```bash
# Verificar se PostgreSQL está rodando
docker-compose ps postgres

# Testar conexão
docker-compose exec postgres psql -U juscash_user -d juscash_db -c "SELECT 1;"
```

### SSL não funciona
```bash
# Verificar configuração do Nginx
nginx -t

# Ver logs do Nginx
tail -f /var/log/nginx/error.log
```

## 🎉 Deploy Concluído!

Sua JusCash API está rodando no VPS Hostinger com:
- ✅ Flask API em produção
- ✅ PostgreSQL database
- ✅ Redis cache/broker
- ✅ Celery workers
- ✅ Nginx reverse proxy
- ✅ SSL/HTTPS configurado
- ✅ Monitoramento com Flower
- ✅ Backups automáticos 