#!/bin/bash

echo "=== CORREÇÃO DE SSL PARA SUBDOMÍNIOS ==="
echo "Script para regenerar certificados SSL dos subdomínios"
echo

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root (sudo)"
    exit 1
fi

# Parar nginx temporariamente
echo "🔄 Parando nginx..."
systemctl stop nginx

# Backup dos certificados existentes
echo "📦 Fazendo backup dos certificados existentes..."
mkdir -p /etc/letsencrypt/backup-$(date +%Y%m%d)
cp -r /etc/letsencrypt/live /etc/letsencrypt/backup-$(date +%Y%m%d)/ 2>/dev/null || true

# Lista de subdomínios
SUBDOMAINS=("portainer.juscash.app" "flower.juscash.app" "cadvisor.juscash.app" "cron.juscash.app")

# Gerar certificados para cada subdomínio
for subdomain in "${SUBDOMAINS[@]}"; do
    echo
    echo "🔐 Gerando certificado SSL para $subdomain..."
    
    # Remover certificado antigo se existir
    certbot delete --cert-name $subdomain --non-interactive 2>/dev/null || true
    
    # Gerar novo certificado
    certbot certonly \
        --standalone \
        --non-interactive \
        --agree-tos \
        --email admin@juscash.app \
        -d $subdomain \
        --force-renewal
    
    if [ $? -eq 0 ]; then
        echo "✅ Certificado gerado com sucesso para $subdomain"
    else
        echo "❌ Erro ao gerar certificado para $subdomain"
    fi
done

# Gerar certificado wildcard (opcional, mais seguro)
echo
echo "🔐 Tentando gerar certificado wildcard para *.juscash.app..."
certbot certonly \
    --manual \
    --preferred-challenges dns \
    --non-interactive \
    --agree-tos \
    --email admin@juscash.app \
    -d "*.juscash.app" \
    -d "juscash.app" \
    --manual-auth-hook /dev/null \
    --manual-cleanup-hook /dev/null 2>/dev/null || echo "⚠️  Certificado wildcard não pôde ser gerado automaticamente"

# Verificar certificados gerados
echo
echo "📋 Verificando certificados gerados:"
for subdomain in "${SUBDOMAINS[@]}"; do
    if [ -f "/etc/letsencrypt/live/$subdomain/fullchain.pem" ]; then
        echo "✅ $subdomain: Certificado OK"
        # Verificar validade
        expiry=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/$subdomain/fullchain.pem | cut -d= -f2)
        echo "   Expira em: $expiry"
    else
        echo "❌ $subdomain: Certificado AUSENTE"
    fi
done

# Testar configuração nginx
echo
echo "🔧 Testando configuração nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuração nginx OK"
    echo "🚀 Iniciando nginx..."
    systemctl start nginx
    systemctl reload nginx
else
    echo "❌ Erro na configuração nginx"
    echo "🔄 Tentando iniciar nginx mesmo assim..."
    systemctl start nginx
fi

# Verificar status dos serviços
echo
echo "📊 Status dos serviços:"
systemctl is-active nginx && echo "✅ Nginx: Ativo" || echo "❌ Nginx: Inativo"

# Testar conectividade SSL
echo
echo "🔍 Testando conectividade SSL dos subdomínios:"
for subdomain in "${SUBDOMAINS[@]}"; do
    echo -n "Testing $subdomain: "
    timeout 10 openssl s_client -connect $subdomain:443 -servername $subdomain </dev/null 2>/dev/null | grep -q "Verify return code: 0" && echo "✅ SSL OK" || echo "❌ SSL ERRO"
done

# Instruções finais
echo
echo "=== INSTRUÇÕES FINAIS ==="
echo "1. Verifique se os subdomínios estão acessíveis:"
echo "   - https://portainer.juscash.app"
echo "   - https://flower.juscash.app" 
echo "   - https://cadvisor.juscash.app"
echo
echo "2. Se ainda houver erros, verifique:"
echo "   - DNS dos subdomínios apontando para o IP correto"
echo "   - Firewall liberando portas 80 e 443"
echo "   - Logs: tail -f /var/log/nginx/*.log"
echo
echo "3. Para renovação automática:"
echo "   systemctl enable certbot.timer"
echo "   systemctl start certbot.timer"
echo
echo "✅ Script de correção SSL concluído!"