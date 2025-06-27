#!/bin/bash

# Script de inicialização para o container da API JusCash

set -e

echo "🚀 Iniciando JusCash API..."

# Verificar se estamos em produção
if [ "$ENVIRONMENT" = "production" ]; then
    echo "📦 Ambiente: PRODUÇÃO"
else
    echo "📦 Ambiente: DESENVOLVIMENTO"
fi

# Aguardar serviços ficarem prontos
echo "🔄 Aguardando serviços..."
./wait-for-it.sh db_prod:5432 --timeout=60 --strict -- echo "✅ PostgreSQL pronto"
./wait-for-it.sh redis_prod:6379 --timeout=60 --strict -- echo "✅ Redis pronto"

# Configurar display para Selenium
export DISPLAY=:99

# Verificar e instalar Xvfb se necessário
if ! pgrep -x "Xvfb" > /dev/null; then
    echo "🖥️ Iniciando Xvfb..."
    Xvfb :99 -screen 0 1920x1080x24 &
    sleep 3
    echo "✅ Xvfb iniciado"
else
    echo "✅ Xvfb já está rodando"
fi

# Verificar e instalar ChromeDriver se necessário
if [ ! -f "/usr/local/bin/chromedriver" ]; then
    echo "🔧 ChromeDriver não encontrado, instalando..."
    cd /tmp
    wget -q -O chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/138.0.7204.0/linux64/chromedriver-linux64.zip"
    unzip -o chromedriver.zip
    chmod +x chromedriver-linux64/chromedriver
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
    echo "✅ ChromeDriver instalado: $(chromedriver --version)"
    rm -rf chromedriver* /tmp/chromedriver*
else
    echo "✅ ChromeDriver já instalado: $(chromedriver --version)"
fi

# Verificar Google Chrome
if command -v google-chrome &> /dev/null; then
    echo "✅ Google Chrome: $(google-chrome --version)"
else
    echo "❌ Google Chrome não encontrado"
fi

# Limpar cache de webdriver-manager antigo
rm -rf /home/.wdm /app/.wdm 2>/dev/null || true

# Configurar permissões
chmod 755 /usr/local/bin/chromedriver 2>/dev/null || true

echo "🚀 Iniciando aplicação..."

# Executar migrações
echo "📊 Executando migrações do banco..."
flask db upgrade

# Executar comando
exec "$@" 