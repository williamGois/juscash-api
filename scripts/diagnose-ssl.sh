#!/bin/bash

echo "🔍 Diagnóstico SSL - JusCash Subdomínios"
echo "========================================"

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root"
    echo "Use: sudo ./scripts/diagnose-ssl.sh"
    exit 1
fi

echo ""
echo "1️⃣ VERIFICANDO DNS E CONECTIVIDADE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

SUBDOMAINS=("portainer.juscash.app" "cadvisor.juscash.app" "flower.juscash.app")

for subdomain in "${SUBDOMAINS[@]}"; do
    echo "🌐 Testando $subdomain..."
    
    # DNS Resolution
    if nslookup $subdomain > /dev/null 2>&1; then
        ip=$(nslookup $subdomain | grep "Address:" | tail -1 | awk '{print $2}')
        echo "  ✅ DNS: $ip"
    else
        echo "  ❌ DNS: Falha na resolução"
        continue
    fi
    
    # HTTP Test
    if curl -s -I --connect-timeout 5 http://$subdomain > /dev/null 2>&1; then
        echo "  ✅ HTTP: Conectando"
    else
        echo "  ❌ HTTP: Não conecta"
    fi
    
    # HTTPS Test
    if curl -s -I --connect-timeout 5 https://$subdomain > /dev/null 2>&1; then
        echo "  ✅ HTTPS: Conectando"
    else
        echo "  ❌ HTTPS: Falha SSL/Conexão"
    fi
    
    echo ""
done

echo ""
echo "2️⃣ VERIFICANDO CERTIFICADOS SSL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Listar certificados existentes
echo "📜 Certificados Let's Encrypt instalados:"
certbot certificates 2>/dev/null | grep -E "(Certificate Name|Domains|Expiry Date)" || echo "  ❌ Nenhum certificado encontrado"

echo ""
echo "📁 Verificando arquivos de certificados:"
for subdomain in "${SUBDOMAINS[@]}"; do
    cert_path="/etc/letsencrypt/live/$subdomain"
    if [ -d "$cert_path" ]; then
        echo "  ✅ $subdomain: Diretório existe"
        if [ -f "$cert_path/fullchain.pem" ]; then
            echo "    ✅ fullchain.pem existe"
        else
            echo "    ❌ fullchain.pem não encontrado"
        fi
        if [ -f "$cert_path/privkey.pem" ]; then
            echo "    ✅ privkey.pem existe"
        else
            echo "    ❌ privkey.pem não encontrado"
        fi
    else
        echo "  ❌ $subdomain: Diretório não existe"
    fi
done

echo ""
echo "3️⃣ VERIFICANDO CONFIGURAÇÃO NGINX"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar sintaxe nginx
echo "🔧 Testando sintaxe nginx:"
if nginx -t 2>&1; then
    echo "  ✅ Sintaxe nginx válida"
else
    echo "  ❌ Erro na sintaxe nginx"
fi

echo ""
echo "📁 Arquivos de configuração ativos:"
ls -la /etc/nginx/sites-enabled/ | grep juscash || echo "  ❌ Nenhuma configuração juscash encontrada"

echo ""
echo "🔍 Verificando configurações por subdomínio:"
for subdomain in "${SUBDOMAINS[@]}"; do
    config_file="/etc/nginx/sites-enabled/${subdomain}.conf"
    if [ -f "$config_file" ]; then
        echo "  ✅ $subdomain: Configuração existe"
        
        # Verificar se tem SSL configurado
        if grep -q "ssl_certificate" "$config_file"; then
            echo "    ✅ SSL configurado"
            
            # Verificar se os arquivos SSL existem
            cert_path=$(grep "ssl_certificate " "$config_file" | head -1 | awk '{print $2}' | sed 's/;//')
            key_path=$(grep "ssl_certificate_key" "$config_file" | head -1 | awk '{print $2}' | sed 's/;//')
            
            if [ -f "$cert_path" ]; then
                echo "    ✅ Certificado encontrado: $cert_path"
            else
                echo "    ❌ Certificado não encontrado: $cert_path"
            fi
            
            if [ -f "$key_path" ]; then
                echo "    ✅ Chave privada encontrada: $key_path"
            else
                echo "    ❌ Chave privada não encontrada: $key_path"
            fi
        else
            echo "    ⚠️  SSL não configurado (apenas HTTP)"
        fi
    else
        echo "  ❌ $subdomain: Configuração não encontrada"
    fi
done

echo ""
echo "4️⃣ VERIFICANDO CONTAINERS DOCKER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "🐳 Status dos containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(portainer|cadvisor|flower)" || echo "  ❌ Containers não encontrados"

echo ""
echo "🔌 Verificando portas locais:"
declare -A PORTS=(
    ["portainer"]="9000"
    ["cadvisor"]="8080"
    ["flower"]="5555"
)

for service in "${!PORTS[@]}"; do
    port=${PORTS[$service]}
    if netstat -tlnp | grep ":$port " > /dev/null 2>&1; then
        echo "  ✅ Porta $port ($service): Ativa"
    else
        echo "  ❌ Porta $port ($service): Não encontrada"
    fi
done

echo ""
echo "5️⃣ TESTE DE CONECTIVIDADE DETALHADO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for subdomain in "${SUBDOMAINS[@]}"; do
    echo "🔍 Testando $subdomain detalhadamente:"
    
    # Teste HTTP detalhado
    echo "  📡 HTTP Response:"
    curl -s -I --connect-timeout 5 http://$subdomain 2>&1 | head -3 | sed 's/^/    /'
    
    # Teste HTTPS detalhado
    echo "  🔒 HTTPS Response:"
    curl -s -I --connect-timeout 5 https://$subdomain 2>&1 | head -3 | sed 's/^/    /'
    
    # Teste SSL Certificate
    echo "  📜 SSL Certificate Info:"
    echo | openssl s_client -servername $subdomain -connect $subdomain:443 2>/dev/null | openssl x509 -noout -subject -dates 2>/dev/null | sed 's/^/    /' || echo "    ❌ Falha ao obter informações do certificado"
    
    echo ""
done

echo ""
echo "6️⃣ LOGS RECENTES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "📋 Últimos erros nginx:"
tail -20 /var/log/nginx/error.log | tail -10 | sed 's/^/  /'

echo ""
echo "📋 Últimos logs certbot:"
if [ -f "/var/log/letsencrypt/letsencrypt.log" ]; then
    tail -20 /var/log/letsencrypt/letsencrypt.log | tail -10 | sed 's/^/  /'
else
    echo "  ⚠️  Log do certbot não encontrado"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 DIAGNÓSTICO CONCLUÍDO"
echo ""
echo "📊 Para corrigir problemas identificados, use:"
echo "   sudo ./scripts/fix-ssl-subdomains.sh"
echo ""
echo "🔧 Para reconfigurar nginx:"
echo "   sudo systemctl reload nginx"
echo ""
echo "📜 Para renovar certificados:"
echo "   sudo certbot renew"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"