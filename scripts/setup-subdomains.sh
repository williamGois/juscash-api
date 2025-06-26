#!/bin/bash

echo "🌐 Configurando subdomínios para JusCash Monitoring Tools"
echo "======================================================"

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root"
    echo "Use: sudo ./scripts/setup-subdomains.sh"
    exit 1
fi

# Verificar se nginx está instalado
if ! command -v nginx &> /dev/null; then
    echo "❌ Nginx não está instalado!"
    echo "Instale com: apt update && apt install nginx"
    exit 1
fi

# Verificar se certbot está instalado
if ! command -v certbot &> /dev/null; then
    echo "❌ Certbot não está instalado!"
    echo "Instale com: apt install certbot python3-certbot-nginx"
    exit 1
fi

echo "✅ Pré-requisitos verificados"
echo ""

# Criar diretório nginx se não existir
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled

# Copiar configurações nginx
echo "📁 Copiando configurações nginx..."

# Portainer
cp nginx/portainer.juscash.app.conf /etc/nginx/sites-available/
ln -sf /etc/nginx/sites-available/portainer.juscash.app.conf /etc/nginx/sites-enabled/
echo "✅ Portainer configurado"

# cAdvisor
cp nginx/cadvisor.juscash.app.conf /etc/nginx/sites-available/
ln -sf /etc/nginx/sites-available/cadvisor.juscash.app.conf /etc/nginx/sites-enabled/
echo "✅ cAdvisor configurado"

# Flower
cp nginx/flower.juscash.app.conf /etc/nginx/sites-available/
ln -sf /etc/nginx/sites-available/flower.juscash.app.conf /etc/nginx/sites-enabled/
echo "✅ Flower configurado"

# Testar configuração nginx
echo ""
echo "🔍 Testando configuração nginx..."
if nginx -t; then
    echo "✅ Configuração nginx válida"
else
    echo "❌ Erro na configuração nginx!"
    exit 1
fi

# Reload nginx
echo ""
echo "🔄 Recarregando nginx..."
systemctl reload nginx
echo "✅ Nginx recarregado"

# Obter certificados SSL
echo ""
echo "🔐 Configurando certificados SSL..."

# Lista de subdomínios
SUBDOMAINS=("portainer.juscash.app" "cadvisor.juscash.app" "flower.juscash.app")

for subdomain in "${SUBDOMAINS[@]}"; do
    echo "📜 Obtendo certificado para $subdomain..."
    
    # Verificar se certificado já existe
    if [ -f "/etc/letsencrypt/live/juscash.app/fullchain.pem" ]; then
        echo "ℹ️  Certificado base já existe, expandindo..."
        certbot --nginx -d $subdomain --non-interactive --agree-tos --email admin@juscash.app --expand || {
            echo "⚠️  Falha ao expandir certificado para $subdomain"
        }
    else
        echo "📜 Criando novo certificado para $subdomain..."
        certbot --nginx -d $subdomain --non-interactive --agree-tos --email admin@juscash.app || {
            echo "⚠️  Falha ao criar certificado para $subdomain"
        }
    fi
done

# Verificar status dos serviços
echo ""
echo "🔍 Verificando status dos serviços..."

# Verificar se containers estão rodando
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(portainer|cadvisor|flower)"

echo ""
echo "🌐 URLs configuradas:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎛️  Portainer:  https://portainer.juscash.app"
echo "📊 cAdvisor:   https://cadvisor.juscash.app" 
echo "🌸 Flower:     https://flower.juscash.app"
echo "🎨 Dashboard:  https://cron.juscash.app/api/simple/dashboard-ui"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "✅ Configuração de subdomínios concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Aguardar propagação DNS (pode levar até 24h)"
echo "2. Testar acesso aos subdomínios"
echo "3. Configurar autenticação adicional se necessário"

echo ""
echo "🛠️  Para verificar logs:"
echo "sudo tail -f /var/log/nginx/portainer.juscash.app.access.log"
echo "sudo tail -f /var/log/nginx/cadvisor.juscash.app.access.log"
echo "sudo tail -f /var/log/nginx/flower.juscash.app.access.log"