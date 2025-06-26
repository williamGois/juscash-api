# Acesso ao VPS JusCash

## Informações de Conexão

- **IP**: 77.37.68.178
- **Usuário**: root
- **Senha**: Syberya1989@@
- **Diretório do Projeto**: /var/www/juscash

## Scripts de Acesso

### 1. Conexão Rápida
```bash
./scripts/connect-vps.sh
```
Conecta diretamente ao VPS via SSH.

### 2. Setup Completo
```bash
./scripts/setup-vps-project.sh
```
Configura o projeto completo no VPS:
- Clona/atualiza repositório
- Verifica Docker
- Configura ambiente
- Oferece opção para iniciar containers

## Comandos Manuais

### Conectar via SSH
```bash
ssh root@77.37.68.178
# Senha: Syberya1989@@
```

### Comandos Úteis no VPS

#### Navegação
```bash
cd /var/www/juscash
```

#### Git
```bash
git pull origin master
git status
```

#### Docker
```bash
# Ver containers
docker ps

# Logs em tempo real
docker-compose -f docker-compose.prod.yml logs -f

# Iniciar containers
docker-compose -f docker-compose.prod.yml up -d

# Reconstruir containers
docker-compose -f docker-compose.prod.yml up -d --build

# Parar containers
docker-compose -f docker-compose.prod.yml down

# Restart específico
docker-compose -f docker-compose.prod.yml restart web
```

#### SSL e Nginx
```bash
# Verificar certificados
sudo certbot certificates

# Status nginx
sudo systemctl status nginx

# Logs nginx
sudo tail -f /var/log/nginx/error.log

# Corrigir SSL
sudo ./scripts/fix-ssl-subdomains.sh
```

#### Monitoramento
```bash
# Status dos serviços
sudo systemctl status nginx docker

# Uso de recursos
htop
df -h
free -h
```

## URLs de Acesso

### APIs
- **API Principal**: http://77.37.68.178:5000
- **Health Check**: http://77.37.68.178:5000/api/simple/ping

### Interfaces (com SSL)
- **Portainer**: https://portainer.juscash.app
- **Flower**: https://flower.juscash.app  
- **cAdvisor**: https://cadvisor.juscash.app
- **Cron**: https://cron.juscash.app

## Estrutura do Projeto no VPS

```
/var/www/juscash/
├── app/                    # Código da aplicação
├── scripts/               # Scripts de automação
├── nginx/                 # Configurações nginx
├── docker-compose.prod.yml # Configuração Docker
├── .env                   # Variáveis de ambiente
└── logs/                  # Logs da aplicação
```

## Troubleshooting

### Problema de Conexão SSH
```bash
# Se der erro de "Host key verification failed"
ssh-keygen -R 77.37.68.178
```

### Problema com Docker
```bash
# Verificar se Docker está rodando
sudo systemctl start docker

# Verificar logs de um container específico
docker logs juscash_web_prod
```

### Problema com SSL
```bash
# Executar diagnóstico
sudo ./scripts/diagnose-ssl.sh

# Corrigir SSL específico do Portainer
sudo ./scripts/fix-portainer-ssl.sh
```

### Problema com Banco de Dados
```bash
# Verificar container do banco
docker ps | grep db

# Conectar no banco
docker exec -it juscash_db_prod psql -U juscash -d juscash_db

# Ver logs do banco
docker logs juscash_db_prod
```

## Backup e Manutenção

### Fazer Backup
```bash
# Backup do banco
docker exec juscash_db_prod pg_dump -U juscash juscash_db > backup_$(date +%Y%m%d).sql

# Backup dos certificados SSL
sudo cp -r /etc/letsencrypt/live /backup/ssl_$(date +%Y%m%d)
```

### Limpeza
```bash
# Limpar containers antigos
docker system prune

# Limpar logs nginx
sudo truncate -s 0 /var/log/nginx/*.log
```

## Segurança

- ✅ SSH configurado com senha forte
- ✅ Certificados SSL válidos
- ✅ Containers com recursos limitados
- ✅ Logs monitorados
- ✅ Firewall configurado para portas necessárias (80, 443, 22)

## Contatos de Emergência

Em caso de problemas graves:
1. Verificar logs: `docker-compose logs -f`
2. Reiniciar serviços: `docker-compose restart`
3. Contatar suporte do provedor VPS se necessário 