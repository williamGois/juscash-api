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

# Primeiro configurar HTTP apenas
echo ""
echo "🔧 Configurando versões HTTP temporárias..."

# Criar configurações HTTP temporárias
for subdomain in portainer.juscash.app cadvisor.juscash.app flower.juscash.app; do
    case $subdomain in
        "portainer.juscash.app")
            port=9000
            ;;
        "cadvisor.juscash.app")
            port=8080
            ;;
        "flower.juscash.app")
            port=5555
            ;;
    esac
    
    cat > /etc/nginx/sites-available/${subdomain}-temp.conf << EOF
server {
    listen 80;
    server_name ${subdomain};
    
    location / {
        proxy_pass http://127.0.0.1:${port};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    
    ln -sf /etc/nginx/sites-available/${subdomain}-temp.conf /etc/nginx/sites-enabled/
    echo "✅ HTTP temporário configurado para $subdomain"
done

# Remover configurações HTTPS temporariamente
rm -f /etc/nginx/sites-enabled/portainer.juscash.app.conf
rm -f /etc/nginx/sites-enabled/cadvisor.juscash.app.conf  
rm -f /etc/nginx/sites-enabled/flower.juscash.app.conf

# Testar e recarregar nginx
nginx -t && systemctl reload nginx

echo ""
echo "🔐 Obtendo certificados SSL..."

# Obter certificados individuais
for subdomain in portainer.juscash.app cadvisor.juscash.app flower.juscash.app; do
    echo "📜 Obtendo certificado para $subdomain..."
    
    certbot certonly --webroot -w /var/www/html -d $subdomain --non-interactive --agree-tos --email admin@juscash.app --force-renewal || {
        echo "⚠️  Tentando método nginx para $subdomain..."
        certbot --nginx -d $subdomain --non-interactive --agree-tos --email admin@juscash.app || {
            echo "❌ Falha ao obter certificado para $subdomain"
            continue
        }
    }
    
    echo "✅ Certificado obtido para $subdomain"
done

echo ""
echo "🔧 Ativando configurações HTTPS..."

# Remover configurações temporárias HTTP
rm -f /etc/nginx/sites-enabled/*-temp.conf

# Ativar configurações HTTPS completas
ln -sf /etc/nginx/sites-available/portainer.juscash.app.conf /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/cadvisor.juscash.app.conf /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/flower.juscash.app.conf /etc/nginx/sites-enabled/

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