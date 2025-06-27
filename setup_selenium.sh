#!/bin/bash

echo "🚀 Configurando Selenium no container..."

# Instalar dependências se não estiverem instaladas
if ! command -v chromium-driver &> /dev/null; then
    echo "📦 Instalando ChromeDriver..."
    apt-get update -q
    apt-get install -y chromium-driver xvfb
fi

# Configurar display virtual
echo "🖥️ Configurando display virtual..."
export DISPLAY=:99
echo "DISPLAY=:99" >> /etc/environment

# Iniciar Xvfb se não estiver rodando
if ! pgrep -f "Xvfb :99" > /dev/null; then
    echo "🚀 Iniciando Xvfb..."
    Xvfb :99 -screen 0 1920x1080x24 &
    sleep 2
fi

# Verificar ChromeDriver
echo "🔍 Verificando ChromeDriver..."
if [ -f "/usr/bin/chromedriver" ]; then
    echo "✅ ChromeDriver encontrado em /usr/bin/chromedriver"
    /usr/bin/chromedriver --version
else
    echo "❌ ChromeDriver não encontrado!"
    exit 1
fi

# Limpar diretórios temporários antigos
echo "🧹 Limpando diretórios temporários antigos..."
find /tmp -name "chrome_data_*" -type d -mtime +1 -exec rm -rf {} + 2>/dev/null || true

echo "🎉 Selenium configurado com sucesso!" 