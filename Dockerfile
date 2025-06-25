FROM python:3.11-slim

# Configurar variáveis de ambiente
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99

# Instalar dependências básicas
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget gnupg ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Adicionar repositório e instalar Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get install -y --no-install-recommends xvfb fonts-liberation && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x docker-entrypoint.sh

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"] 