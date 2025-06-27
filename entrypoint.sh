#!/bin/bash

set -e

echo "🚀 Iniciando JusCash API..."

if [ "$ENVIRONMENT" = "production" ]; then
    echo "📦 Ambiente: PRODUÇÃO"
else
    echo "📦 Ambiente: DESENVOLVIMENTO"
fi

echo "🔄 Aguardando serviços..."

max_retries=30
count=0
until curl -s db:5432 > /dev/null 2>&1; do
    count=$((count+1))
    if [ $count -eq $max_retries ]; then
        echo "❌ Postgres não disponível após $max_retries tentativas. Abortando."
        exit 1
    fi
    echo "⏳ Aguardando Postgres... ($count/$max_retries)"
    sleep 2
done
echo "✅ PostgreSQL pronto"

count=0
until curl -s redis:6379 > /dev/null 2>&1; do
    count=$((count+1))
    if [ $count -eq $max_retries ]; then
        echo "❌ Redis não disponível após $max_retries tentativas. Abortando."
        exit 1
    fi
    echo "⏳ Aguardando Redis... ($count/$max_retries)"
    sleep 2
done
echo "✅ Redis pronto"

check_xvfb() {
    pgrep Xvfb > /dev/null
    return $?
}

start_xvfb() {
    echo "🖥️ Iniciando Xvfb..."
    Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
    sleep 3
    
    if check_xvfb; then
        echo "✅ Xvfb iniciado com sucesso"
        return 0
    else
        echo "❌ Falha ao iniciar Xvfb"
        return 1
    fi
}

setup_chromedriver() {
    echo "🔧 Aplicando fix ChromeDriver..."
    
    CHROME_DRIVER=$(find /root/.wdm/drivers/chromedriver -type f -name "chromedriver" | sort -r | head -1)
    
    if [ -n "$CHROME_DRIVER" ]; then
        cp "$CHROME_DRIVER" /usr/local/bin/chromedriver
        chmod +x /usr/local/bin/chromedriver
        echo "✅ ChromeDriver copiado e configurado com sucesso!"
    else
        echo "⚠️ ChromeDriver não encontrado, tentando download..."
        python3 -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
        
        CHROME_DRIVER=$(find /root/.wdm/drivers/chromedriver -type f -name "chromedriver" | sort -r | head -1)
        if [ -n "$CHROME_DRIVER" ]; then
            cp "$CHROME_DRIVER" /usr/local/bin/chromedriver
            chmod +x /usr/local/bin/chromedriver
            echo "✅ ChromeDriver baixado e configurado com sucesso!"
        else
            echo "❌ Falha ao configurar ChromeDriver"
            exit 1
        fi
    fi
}

echo "🔍 Verificando prerequisitos..."

if [ -z "$DISPLAY" ]; then
    export DISPLAY=:99
    echo "🖥️ Display configurado: $DISPLAY"
else
    echo "🖥️ Display já configurado: $DISPLAY"
fi

if ! check_xvfb; then
    echo "⚠️ Xvfb não está rodando, tentando iniciar..."
    if ! start_xvfb; then
        echo "❌ Falha ao iniciar Xvfb. Tentando matar processos existentes..."
        pkill Xvfb || true
        sleep 2
        if ! start_xvfb; then
            echo "❌ Falha definitiva ao iniciar Xvfb"
            exit 1
        fi
    fi
else
    echo "✅ Xvfb já está rodando"
fi

setup_chromedriver

if command -v google-chrome &> /dev/null; then
    echo "✅ Google Chrome: $(google-chrome --version)"
else
    echo "❌ Google Chrome não encontrado"
    exit 1
fi

rm -rf /home/.wdm /app/.wdm 2>/dev/null || true
chmod 755 /usr/local/bin/chromedriver 2>/dev/null || true

echo "🚀 Iniciando aplicação..."

echo "📊 Executando migrações do banco..."
flask db upgrade

echo "✅ Tudo pronto! Executando comando: $@"
exec "$@" 