#!/bin/bash

echo "=== DIAGNÓSTICO SSL SUBDOMÍNIOS ==="
echo "Data: $(date)"
echo

# Lista de subdomínios
SUBDOMAINS=("www.juscash.app" "portainer.juscash.app" "flower.juscash.app" "cadvisor.juscash.app" "cron.juscash.app")

echo "🔍 Verificando certificados locais..."
echo "─────────────────────────────────────────"

for subdomain in "${SUBDOMAINS[@]}"; do
    echo -n "$subdomain: "
    if [ -f "/etc/letsencrypt/live/$subdomain/fullchain.pem" ]; then
        expiry=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/$subdomain/fullchain.pem 2>/dev/null | cut -d= -f2)
        if [ $? -eq 0 ]; then
            echo "✅ Válido até $expiry"
        else
            echo "❌ Erro ao ler certificado"
        fi
    else
        echo "❌ Certificado não encontrado"
    fi
done

echo
echo "🌐 Testando conectividade HTTPS..."
echo "─────────────────────────────────────────"

for subdomain in "${SUBDOMAINS[@]}"; do
    echo -n "Testing $subdomain: "
    
    # Testar conectividade SSL
    ssl_test=$(timeout 10 openssl s_client -connect $subdomain:443 -servername $subdomain </dev/null 2>/dev/null)
    
    if echo "$ssl_test" | grep -q "Verify return code: 0"; then
        echo "✅ SSL válido"
    elif echo "$ssl_test" | grep -q "certificate verify failed"; then
        echo "❌ Certificado inválido"
    elif echo "$ssl_test" | grep -q "connect: Connection refused"; then
        echo "❌ Conexão recusada"
    else
        echo "❌ Erro de conectividade"
    fi
done

echo
echo "📋 Status dos serviços relacionados..."
echo "─────────────────────────────────────────"

# Verificar nginx
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx: Ativo"
else
    echo "❌ Nginx: Inativo"
fi

# Verificar certbot timer
if systemctl is-enabled --quiet certbot.timer; then
    echo "✅ Certbot timer: Habilitado"
else
    echo "❌ Certbot timer: Desabilitado"
fi

# Verificar portas
echo
echo "🔌 Verificando portas..."
echo "─────────────────────────────────────────"

if netstat -ln | grep -q ":80 "; then
    echo "✅ Porta 80: Aberta"
else
    echo "❌ Porta 80: Fechada"
fi

if netstat -ln | grep -q ":443 "; then
    echo "✅ Porta 443: Aberta"
else
    echo "❌ Porta 443: Fechada"
fi

echo
echo "📁 Configurações nginx dos subdomínios..."
echo "─────────────────────────────────────────"

for subdomain in "${SUBDOMAINS[@]}"; do
    config_file=""
    case $subdomain in
        "www.juscash.app") config_file="juscash.app.conf" ;;
        "portainer.juscash.app") config_file="portainer.juscash.app.conf" ;;
        "flower.juscash.app") config_file="flower.juscash.app.conf" ;;
        "cadvisor.juscash.app") config_file="cadvisor.juscash.app.conf" ;;
        "cron.juscash.app") config_file="cron.juscash.app.conf" ;;
    esac
    
    echo -n "$subdomain: "
    if [ -f "/etc/nginx/sites-available/$config_file" ]; then
        if [ -L "/etc/nginx/sites-enabled/$config_file" ]; then
            echo "✅ Configurado e ativo"
        else
            echo "⚠️  Configurado mas inativo"
        fi
    else
        echo "❌ Configuração não encontrada"
    fi
done

echo
echo "🔧 Testando configuração nginx..."
echo "─────────────────────────────────────────"

if nginx -t 2>/dev/null; then
    echo "✅ Configuração nginx válida"
    else
    echo "❌ Erro na configuração nginx:"
    nginx -t
fi

echo
echo "📊 Últimos logs de erro nginx..."
echo "─────────────────────────────────────────"
if [ -f "/var/log/nginx/error.log" ]; then
    tail -5 /var/log/nginx/error.log | grep -E "(ssl|certificate|https)" || echo "Nenhum erro SSL recente encontrado"
else
    echo "Log de erro não encontrado"
fi

echo
echo "=== SOLUÇÕES RECOMENDADAS ==="
echo
echo "Se encontrou problemas, execute:"
echo "1. Para recriar certificados: sudo ./scripts/fix-ssl-subdomains.sh"
echo "2. Para verificar logs detalhados: sudo tail -f /var/log/nginx/error.log"
echo "3. Para verificar certbot: sudo certbot certificates"
echo "4. Para testar nginx: sudo nginx -t"
echo
echo "✅ Diagnóstico concluído!"