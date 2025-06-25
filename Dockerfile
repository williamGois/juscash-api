FROM python:3.11-slim

# Instalar dependências do sistema e Google Chrome
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget gnupg ca-certificates curl \
    libnss3 libgconf-2-4 libxi6 libxrandr2 libasound2 libpangocairo-1.0-0 \
    libatk1.0-0 libcairo-gobject2 libgtk-3-0 libgdk-pixbuf2.0-0 \
    libxss1 libappindicator1 libindicator7 xvfb unzip \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libatspi2.0-0 libdrm2 libgtk-3-0 libnspr4 libnss3 libxcomposite1 \
    libxdamage1 libxfixes3 libxkbcommon0 libxrandr2 xdg-utils \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

ENV DISPLAY=:99

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Tornar o script de inicialização executável
RUN chmod +x docker-entrypoint.sh

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"] 