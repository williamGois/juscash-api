#!/bin/bash

echo "🔐 Corrigindo SSL para subdomínios JusCash"
echo "=========================================="

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root"
    echo "Use: sudo ./scripts/fix-ssl-subdomains.sh"
    exit 1
fi

# Lista de subdomínios e suas portas
declare -A SUBDOMAINS=(
    ["portainer.juscash.app"]="9000"
    ["cadvisor.juscash.app"]="8080"
    ["flower.juscash.app"]="5555"
)

echo "🔧 Passo 1: Configurando HTTP temporário para validação..."

# Remover configurações existentes
rm -f /etc/nginx/sites-enabled/*juscash.app*.conf

for subdomain in "${!SUBDOMAINS[@]}"; do
    port=${SUBDOMAINS[$subdomain]}
    
    echo "📁 Configurando HTTP para $subdomain (porta $port)..."
    
    cat > /etc/nginx/sites-available/${subdomain}-http.conf << EOF
server {
    listen 80;
    server_name ${subdomain};
    
    # Location para Let's Encrypt validation
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        proxy_pass http://127.0.0.1:${port};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Headers específicos por serviço
EOF

    if [[ $subdomain == "portainer.juscash.app" ]]; then
        cat >> /etc/nginx/sites-available/${subdomain}-http.conf << EOF
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
EOF
    elif [[ $subdomain == "flower.juscash.app" ]]; then
        cat >> /etc/nginx/sites-available/${subdomain}-http.conf << EOF
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass \$http_upgrade;
        proxy_buffering off;
EOF
    fi
    
    cat >> /etc/nginx/sites-available/${subdomain}-http.conf << EOF
    }
}
EOF

    ln -sf /etc/nginx/sites-available/${subdomain}-http.conf /etc/nginx/sites-enabled/
    echo "✅ HTTP configurado para $subdomain"
done

# Criar diretório para validação
mkdir -p /var/www/html/.well-known/acme-challenge

# Testar configuração nginx
echo ""
echo "🔍 Testando configuração nginx..."
if nginx -t; then
    echo "✅ Configuração nginx válida"
    systemctl reload nginx
    echo "✅ Nginx recarregado"
else
    echo "❌ Erro na configuração nginx!"
    exit 1
fi

echo ""
echo "⏳ Aguardando 10 segundos para estabilizar..."
sleep 10

echo ""
echo "🔐 Passo 2: Obtendo certificados SSL..."

for subdomain in "${!SUBDOMAINS[@]}"; do
    echo "📜 Obtendo certificado para $subdomain..."
    
    # Tentar obter certificado usando webroot
    if certbot certonly --webroot -w /var/www/html -d $subdomain --non-interactive --agree-tos --email admin@juscash.app --force-renewal; then
        echo "✅ Certificado obtido para $subdomain via webroot"
    else
        echo "⚠️  Webroot falhou, tentando método standalone..."
        # Parar nginx temporariamente
        systemctl stop nginx
        
        if certbot certonly --standalone -d $subdomain --non-interactive --agree-tos --email admin@juscash.app --force-renewal; then
            echo "✅ Certificado obtido para $subdomain via standalone"
        else
            echo "❌ Falha ao obter certificado para $subdomain"
            systemctl start nginx
            continue
        fi
        
        # Reiniciar nginx
        systemctl start nginx
    fi
done

echo ""
echo "🔧 Passo 3: Configurando HTTPS..."

# Remover configurações HTTP temporárias
rm -f /etc/nginx/sites-enabled/*-http.conf

# Ativar configurações HTTPS
for subdomain in "${!SUBDOMAINS[@]}"; do
    if [[ -f "/etc/letsencrypt/live/$subdomain/fullchain.pem" ]]; then
        echo "🔒 Ativando HTTPS para $subdomain..."
        
        config_file=""
        case $subdomain in
            "portainer.juscash.app")
                config_file="portainer.juscash.app.conf"
                ;;
            "cadvisor.juscash.app")
                config_file="cadvisor.juscash.app.conf"
                ;;
            "flower.juscash.app")
                config_file="flower.juscash.app.conf"
                ;;
        esac
        
        if [[ -f "/etc/nginx/sites-available/$config_file" ]]; then
            ln -sf /etc/nginx/sites-available/$config_file /etc/nginx/sites-enabled/
            echo "✅ HTTPS ativado para $subdomain"
        else
            echo "⚠️  Arquivo de configuração não encontrado para $subdomain"
        fi
    else
        echo "⚠️  Certificado não encontrado para $subdomain"
    fi
done

# Testar configuração final
echo ""
echo "🔍 Testando configuração final..."
if nginx -t; then
    echo "✅ Configuração final válida"
    systemctl reload nginx
    echo "✅ Nginx recarregado com HTTPS"
else
    echo "❌ Erro na configuração final!"
    echo "🔄 Restaurando configurações HTTP..."
    rm -f /etc/nginx/sites-enabled/*.conf
    for subdomain in "${!SUBDOMAINS[@]}"; do
        ln -sf /etc/nginx/sites-available/${subdomain}-http.conf /etc/nginx/sites-enabled/
    done
    nginx -t && systemctl reload nginx
    exit 1
fi

echo ""
echo "🎉 Configuração SSL concluída!"
echo ""
echo "🌐 URLs HTTPS configuradas:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for subdomain in "${!SUBDOMAINS[@]}"; do
    if [[ -f "/etc/letsencrypt/live/$subdomain/fullchain.pem" ]]; then
        echo "✅ https://$subdomain"
    else
        echo "❌ $subdomain (certificado não encontrado)"
    fi
done
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "🔍 Para verificar certificados:"
echo "sudo certbot certificates"
echo ""
echo "📊 Para ver logs:"
echo "sudo tail -f /var/log/nginx/error.log"