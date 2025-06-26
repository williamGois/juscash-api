#!/bin/bash

echo "=== CORREÇÃO SSL ESPECÍFICA - PORTAINER ==="
echo "Data: $(date)"
echo

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root (sudo)"
    exit 1
fi

echo "🔍 Problema identificado: Portainer usando certificado do cron.juscash.app"
echo "🎯 Objetivo: Regenerar certificado específico para portainer.juscash.app"
echo

# Verificar DNS primeiro
echo "🌐 Verificando DNS do portainer.juscash.app..."
if nslookup portainer.juscash.app > /dev/null 2>&1; then
    ip=$(nslookup portainer.juscash.app | grep "Address:" | tail -1 | awk '{print $2}')
    echo "✅ DNS OK: $ip"
else
    echo "❌ Problema no DNS - verifique se portainer.juscash.app aponta para este servidor"
    exit 1
fi

# Parar nginx
echo "🔄 Parando nginx para regenerar certificado..."
systemctl stop nginx

# Fazer backup do certificado atual
echo "📦 Fazendo backup do certificado atual..."
mkdir -p /etc/letsencrypt/backup-portainer-$(date +%Y%m%d_%H%M%S)
if [ -d "/etc/letsencrypt/live/portainer.juscash.app" ]; then
    cp -r /etc/letsencrypt/live/portainer.juscash.app /etc/letsencrypt/backup-portainer-$(date +%Y%m%d_%H%M%S)/
    echo "✅ Backup criado"
else
    echo "⚠️  Nenhum certificado anterior encontrado"
fi

# Remover certificado antigo do portainer
echo "🗑️  Removendo certificado antigo do portainer..."
certbot delete --cert-name portainer.juscash.app --non-interactive 2>/dev/null || echo "⚠️  Nenhum certificado anterior para remover"

# Aguardar alguns segundos
echo "⏳ Aguardando 5 segundos..."
sleep 5

# Gerar novo certificado exclusivo para portainer
echo "🔐 Gerando novo certificado para portainer.juscash.app..."
if certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email admin@juscash.app \
    -d portainer.juscash.app \
    --force-renewal \
    --cert-name portainer.juscash.app; then
    echo "✅ Certificado gerado com sucesso!"
else
    echo "❌ Erro ao gerar certificado"
    echo "🔄 Tentando iniciar nginx..."
    systemctl start nginx
    exit 1
fi

# Verificar se o certificado foi criado corretamente
echo "🔍 Verificando certificado criado..."
if [ -f "/etc/letsencrypt/live/portainer.juscash.app/fullchain.pem" ]; then
    echo "✅ Arquivo fullchain.pem encontrado"
    
    # Verificar CN do certificado
    cn=$(openssl x509 -noout -subject -in /etc/letsencrypt/live/portainer.juscash.app/fullchain.pem | sed -n 's/.*CN=\([^,]*\).*/\1/p')
    echo "📋 CN do certificado: $cn"
    
    if [ "$cn" = "portainer.juscash.app" ]; then
        echo "✅ CN correto!"
    else
        echo "❌ CN incorreto: esperado 'portainer.juscash.app', encontrado '$cn'"
    fi
    
    # Verificar expiração
    expiry=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/portainer.juscash.app/fullchain.pem | cut -d= -f2)
    echo "📅 Expira em: $expiry"
else
    echo "❌ Arquivo de certificado não encontrado!"
    systemctl start nginx
    exit 1
fi

# Verificar se a chave privada existe
if [ -f "/etc/letsencrypt/live/portainer.juscash.app/privkey.pem" ]; then
    echo "✅ Chave privada encontrada"
else
    echo "❌ Chave privada não encontrada!"
    systemctl start nginx
    exit 1
fi

# Verificar configuração nginx antes de iniciar
echo "🔧 Verificando configuração nginx..."
if nginx -t; then
    echo "✅ Configuração nginx válida"
else
    echo "❌ Erro na configuração nginx:"
    nginx -t
    echo "🔄 Iniciando nginx mesmo assim..."
fi

# Iniciar nginx
echo "🚀 Iniciando nginx..."
systemctl start nginx

# Aguardar nginx inicializar
sleep 3

# Verificar se nginx está rodando
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx ativo"
else
    echo "❌ Nginx não está ativo"
    systemctl status nginx
fi

# Testar certificado SSL do portainer
echo "🔍 Testando certificado SSL do portainer..."
ssl_test=$(timeout 10 openssl s_client -connect portainer.juscash.app:443 -servername portainer.juscash.app </dev/null 2>/dev/null)

if echo "$ssl_test" | grep -q "CN = portainer.juscash.app"; then
    echo "✅ Certificado SSL correto para portainer.juscash.app"
elif echo "$ssl_test" | grep -q "CN = cron.juscash.app"; then
    echo "❌ AINDA está usando certificado do cron.juscash.app"
    echo "🔧 Pode ser necessário limpar cache do navegador ou aguardar propagação"
else
    echo "⚠️  Resultado do teste SSL inconcluso"
fi

# Extrair informações do certificado
echo
echo "📋 Informações do certificado em uso:"
echo "$ssl_test" | openssl x509 -noout -subject -dates 2>/dev/null || echo "❌ Não foi possível extrair informações"

echo
echo "=== VERIFICAÇÃO FINAL ==="
echo "1. Acesse: https://portainer.juscash.app"
echo "2. Verifique se o certificado mostra CN=portainer.juscash.app"
echo "3. Se ainda mostrar cron.juscash.app, limpe o cache do navegador"
echo "4. Em caso de problemas, execute: sudo ./scripts/diagnose-ssl.sh"
echo
echo "✅ Correção SSL do Portainer concluída!" 