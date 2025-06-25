# 🚀 Deploy Simples - JusCash API

## ⚡ **Deploy em UM COMANDO**

### **Execute apenas isto:**

```bash
./deploy-completo.sh
```

**Pronto!** 🎉

---

## 📋 **O que o script faz automaticamente:**

1. ✅ **Conecta no servidor** (77.37.68.178)
2. ✅ **Instala Docker** e todas as dependências
3. ✅ **Configura Nginx** para proxy
4. ✅ **Configura Firewall** (portas 80, 443, SSH)
5. ✅ **Faz upload** de todos os arquivos
6. ✅ **Gera senhas seguras** automaticamente
7. ✅ **Executa a aplicação** com Docker
8. ✅ **Cria banco de dados** e tabelas

## 🌐 **URLs após deploy:**

- **API**: http://77.37.68.178
- **Swagger**: http://77.37.68.178/docs/
- **Flower**: http://77.37.68.178/flower

## 🔧 **Após o deploy:**

### **1. Configure DNS (opcional):**
- **Nome**: cron
- **Tipo**: A  
- **Valor**: 77.37.68.178

### **2. Configure SSL (opcional):**
```bash
ssh juscash-vps
certbot --nginx -d cron.juscash.app
```

## 📋 **Comandos úteis:**

```bash
# Conectar no servidor
ssh juscash-vps

# Ver logs da aplicação
ssh juscash-vps 'cd /var/www/juscash && docker-compose logs -f web'

# Restart da aplicação
ssh juscash-vps 'cd /var/www/juscash && docker-compose restart'

# Status dos containers
ssh juscash-vps 'cd /var/www/juscash && docker-compose ps'
```

## 🆘 **Se algo der errado:**

```bash
# Ver logs completos
ssh juscash-vps 'cd /var/www/juscash && docker-compose logs'

# Restart completo
ssh juscash-vps 'cd /var/www/juscash && docker-compose down && docker-compose up -d'
```

---

## 🎯 **Resumo:**

1. Execute: `./deploy-completo.sh`
2. Digite a senha quando pedir: `Syberya1989@@`
3. Aguarde ~10 minutos
4. Acesse: http://77.37.68.178/docs/

**✅ Pronto! Aplicação rodando!** 