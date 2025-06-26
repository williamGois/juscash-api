#!/bin/bash

echo "🔧 Correção Rápida - Ativando HTTPS para Subdomínios"
echo "===================================================="

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root"
    echo "Use: sudo ./scripts/quick-fix-nginx.sh"
    exit 1
fi

echo "🔍 Verificando certificados existentes..."
for subdomain in flower.juscash.app portainer.juscash.app cadvisor.juscash.app; do
    if [ -f "/etc/letsencrypt/live/$subdomain/fullchain.pem" ]; then
        echo "✅ Certificado encontrado para $subdomain"
    else
        echo "❌ Certificado NÃO encontrado para $subdomain"
        exit 1
    fi
done

echo ""
echo "📁 Copiando arquivos de configuração HTTPS..."

# Verificar se os arquivos de configuração existem no projeto
PROJECT_DIR="/root/juscash-api"
if [ ! -d "$PROJECT_DIR/nginx" ]; then
    echo "❌ Diretório nginx não encontrado em $PROJECT_DIR"
    exit 1
fi

# Copiar configurações para nginx
cp "$PROJECT_DIR/nginx/portainer.juscash.app.conf" /etc/nginx/sites-available/
cp "$PROJECT_DIR/nginx/cadvisor.juscash.app.conf" /etc/nginx/sites-available/
cp "$PROJECT_DIR/nginx/flower.juscash.app.conf" /etc/nginx/sites-available/

echo "✅ Arquivos de configuração copiados"

echo ""
echo "🔧 Removendo configurações HTTP temporárias..."
rm -f /etc/nginx/sites-enabled/*juscash.app*-temp.conf
rm -f /etc/nginx/sites-enabled/*juscash.app*-http.conf

echo ""
echo "🔒 Ativando configurações HTTPS..."
ln -sf /etc/nginx/sites-available/portainer.juscash.app.conf /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/cadvisor.juscash.app.conf /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/flower.juscash.app.conf /etc/nginx/sites-enabled/

echo "✅ Configurações HTTPS ativadas"

echo ""
echo "🔍 Testando configuração nginx..."
if nginx -t; then
    echo "✅ Configuração nginx válida"
    
    echo "🔄 Recarregando nginx..."
    systemctl reload nginx
    echo "✅ Nginx recarregado"
    
    echo ""
    echo "🎉 HTTPS configurado com sucesso!"
    echo ""
    echo "🌐 Testando URLs:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    for subdomain in portainer.juscash.app cadvisor.juscash.app flower.juscash.app; do
        echo -n "🔒 https://$subdomain: "
        if curl -s -I --connect-timeout 5 https://$subdomain > /dev/null 2>&1; then
            echo "✅ OK"
        else
            echo "❌ Falha"
        fi
    done
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
else
    echo "❌ Erro na configuração nginx!"
    echo ""
    echo "🔄 Restaurando HTTP temporário..."
    
    # Voltar para HTTP se der erro
    rm -f /etc/nginx/sites-enabled/*juscash.app*.conf
    
    # Recriar configurações HTTP básicas
    for subdomain in portainer.juscash.app cadvisor.juscash.app flower.juscash.app; do
        case $subdomain in
            "portainer.juscash.app") port=9000 ;;
            "cadvisor.juscash.app") port=8080 ;;
            "flower.juscash.app") port=5555 ;;
        esac
        
        cat > /etc/nginx/sites-enabled/${subdomain}-http.conf << EOF
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
    done
    
    nginx -t && systemctl reload nginx
    echo "⚠️  Voltou para HTTP. Verifique os logs de erro."
    exit 1
fi

echo ""
echo "📋 Comandos úteis:"
echo "🔍 Verificar certificados: sudo certbot certificates"
echo "📊 Ver logs nginx: sudo tail -f /var/log/nginx/error.log"
echo "🔧 Diagnóstico completo: sudo ./scripts/diagnose-ssl.sh"