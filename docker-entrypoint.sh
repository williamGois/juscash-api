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

# Inicializar Xvfb para Selenium (se não estiver rodando)
echo "🖥️ Configurando display virtual para Selenium..."
if ! pgrep -x "Xvfb" > /dev/null; then
    echo "🖥️ Iniciando Xvfb..."
    Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
    sleep 2
    echo "✅ Xvfb iniciado com sucesso"
else
    echo "✅ Xvfb já está rodando"
fi

# Função para manter Xvfb rodando em produção
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🔄 Configurando monitoramento do Xvfb..."
    (
        while true; do
            sleep 30
            if ! pgrep -x "Xvfb" > /dev/null; then
                echo "⚠️ Xvfb parou, reiniciando..."
                Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
                sleep 2
                echo "✅ Xvfb reiniciado"
            fi
        done
    ) &
    echo "✅ Monitor do Xvfb iniciado"
fi

# Verificar ChromeDriver
echo "🔍 Verificando ChromeDriver..."
if command -v chromedriver >/dev/null 2>&1; then
    echo "✅ ChromeDriver encontrado: $(chromedriver --version 2>/dev/null | head -1 || echo 'Versão não disponível')"
else
    echo "❌ ChromeDriver não encontrado"
fi

# Verificar Google Chrome
if command -v google-chrome >/dev/null 2>&1; then
    echo "✅ Google Chrome encontrado: $(google-chrome --version 2>/dev/null || echo 'Versão não disponível')"
elif command -v chromium >/dev/null 2>&1; then
    echo "✅ Chromium encontrado: $(chromium --version 2>/dev/null || echo 'Versão não disponível')"
else
    echo "❌ Chrome/Chromium não encontrado"
fi

# Aguardar banco de dados se especificado
if [ -n "$DATABASE_URL" ]; then
    echo "⏳ Aguardando banco de dados..."
    ./wait-for-it.sh ${DB_HOST:-localhost}:${DB_PORT:-5432} --timeout=30 --strict -- echo "✅ Banco de dados disponível"
fi

# Executar migrações se necessário
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "🔄 Executando migrações do banco de dados..."
    python -c "
from app import create_app
from app.infrastructure.database.models import db
app = create_app()
with app.app_context():
    try:
        db.create_all()
        print('✅ Tabelas criadas/atualizadas com sucesso')
    except Exception as e:
        print(f'⚠️ Erro nas migrações: {e}')
"
fi

# Configurar variáveis de ambiente para Selenium
export DISPLAY=:99
export CHROME_BIN=/usr/bin/google-chrome
export CHROMEDRIVER_PATH=/usr/bin/chromedriver

echo "🌟 Iniciando aplicação..."

# Executar o comando passado
exec "$@" 