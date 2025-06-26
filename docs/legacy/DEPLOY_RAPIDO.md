# 🚀 Deploy Rápido - JusCash API

## ⚡ **Método Git (Recomendado)**

### **1. Configurar GitHub:**
```bash
# 1. Crie um repositório em: https://github.com/new
# 2. Nome: juscash-api (público ou privado)

# 3. Configure no seu computador:
git remote add origin https://github.com/SEU_USUARIO/juscash-api.git
git branch -M main
git push -u origin main
```

### **2. Deploy Automático:**
```bash
# Execute no seu computador:
./deploy-git.sh
```

### **3. Configurar no Servidor:**
```bash
# 1. Conectar no servidor:
ssh juscash-vps

# 2. Clonar e configurar:
cd /var/www
git clone https://github.com/SEU_USUARIO/juscash-api.git juscash
cd juscash
chmod +x setup-projeto.sh
./setup-projeto.sh
```

### **4. Configurar DNS:**
- **Nome**: cron
- **Tipo**: A
- **Valor**: 77.37.68.178

### **5. Configurar SSL:**
```bash
# No servidor, após DNS propagado:
certbot --nginx -d cron.juscash.app
```

## 🌐 **URLs Finais:**
- **API**: https://cron.juscash.app
- **Swagger**: https://cron.juscash.app/docs/
- **Flower**: https://cron.juscash.app/flower

## 🔧 **Comandos Úteis:**

### SSH Simplificado:
```bash
ssh juscash-vps  # Conecta direto na VPS
```

### Monitoramento:
```bash
# Ver logs
docker-compose logs -f web

# Status containers
docker-compose ps

# Restart aplicação
docker-compose restart
```

### Atualizações:
```bash
# No servidor
cd /var/www/juscash
git pull origin main
docker-compose build
docker-compose up -d
```

## 🆘 **Solução de Problemas:**

1. **Container não inicia**: `docker-compose logs web`
2. **Erro de conexão**: `docker-compose ps`
3. **SSL não funciona**: Verificar DNS primeiro
4. **API não responde**: `curl http://localhost:5000/api/cron/health`

---
**✅ Deploy em menos de 10 minutos!** 