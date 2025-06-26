# Build stage para dependências
FROM python:3.11-slim as builder

# Instalar apenas ferramentas de build necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python primeiro (melhor cache)
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Labels para rastreamento
LABEL maintainer="JusCash API"
LABEL version="1.0"
LABEL description="JusCash API com Selenium para scraping"

# Configurar variáveis de ambiente
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instalar dependências do sistema em uma única camada
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates \
    curl \
    unzip \
    xvfb \
    fonts-liberation \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Instalar ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    echo "Chrome version: $CHROME_VERSION" && \
    CHROME_MAJOR=$(echo $CHROME_VERSION | cut -d'.' -f1) && \
    if [ "$CHROME_MAJOR" -ge "115" ]; then \
        CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_MAJOR}") && \
        echo "ChromeDriver version for Chrome $CHROME_MAJOR: $CHROMEDRIVER_VERSION" && \
        wget -O /tmp/chromedriver.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" && \
        unzip /tmp/chromedriver.zip -d /tmp/ && \
        mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
        chmod +x /usr/local/bin/chromedriver && \
        rm -rf /tmp/chromedriver* ; \
    else \
        CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR}") && \
        echo "ChromeDriver version: $CHROMEDRIVER_VERSION" && \
        wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" && \
        unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
        chmod +x /usr/local/bin/chromedriver && \
        rm /tmp/chromedriver.zip ; \
    fi

# Criar usuário não-root
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copiar dependências Python do builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copiar arquivos da aplicação
COPY --chown=appuser:appuser . .

# Garantir permissões corretas
RUN chmod +x docker-entrypoint.sh && \
    mkdir -p logs && \
    chown -R appuser:appuser /app

# Mudar para usuário não-root
USER appuser

EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/simple/ping || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:create_app()"] 