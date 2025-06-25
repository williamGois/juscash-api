FROM python:3.11-slim

# Configurar variáveis de ambiente
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99

# Instalar dependências básicas
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Adicionar repositório do Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list

# Instalar Chrome e dependências mínimas essenciais
RUN apt-get update && apt-get install -y --no-install-recommends \
    google-chrome-stable \
    xvfb \
    fonts-liberation \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    && rm -rf /var/lib/apt/lists/*

# Baixar ChromeDriver compatível com a versão instalada do Chrome
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1) && \
    echo "Chrome major version: $CHROME_VERSION" && \
    DRIVER_VERSION=$(curl -sS "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}") && \
    echo "ChromeDriver version: $DRIVER_VERSION" && \
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x docker-entrypoint.sh

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"] 