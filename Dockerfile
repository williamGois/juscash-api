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

# Instalar ChromeDriver usando o novo método para Chrome 115+
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    echo "Chrome version: $CHROME_VERSION" && \
    CHROME_MAJOR=$(echo $CHROME_VERSION | cut -d'.' -f1) && \
    if [ "$CHROME_MAJOR" -ge "115" ]; then \
        # Novo método para Chrome 115+
        CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_MAJOR}") && \
        echo "ChromeDriver version for Chrome $CHROME_MAJOR: $CHROMEDRIVER_VERSION" && \
        wget -O /tmp/chromedriver.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" && \
        unzip /tmp/chromedriver.zip -d /tmp/ && \
        mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
        chmod +x /usr/local/bin/chromedriver && \
        rm -rf /tmp/chromedriver* ; \
    else \
        # Método antigo para Chrome < 115
        CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR}") && \
        echo "ChromeDriver version: $CHROMEDRIVER_VERSION" && \
        wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" && \
        unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
        chmod +x /usr/local/bin/chromedriver && \
        rm /tmp/chromedriver.zip ; \
    fi

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x docker-entrypoint.sh

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"] 