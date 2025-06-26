# 🎥 Guia Completo - Como Visualizar o Selenium em Execução

## 🎯 **Formas de Ver o Chrome Raspando os Dados**

### **1. 🖥️ Modo Visual Local (Recomendado para Debug)**

#### **Opção A: Script Python Local**
```bash
# 1. Instalar dependências localmente
pip install selenium webdriver-manager beautifulsoup4

# 2. Executar script visual
python scripts/test-visual-scraping.py

# Escolher opção 1 (Visual)
# O Chrome abrirá e você verá cada etapa!
```

#### **Opção B: Jupyter Notebook**
```python
from app.infrastructure.scraping.dje_scraper_debug import DJEScraperDebug
from datetime import datetime, timedelta

# Criar scraper visual
scraper = DJEScraperDebug(visual_mode=True)

# Definir período
data_fim = datetime.now() - timedelta(days=1)
data_inicio = data_fim

# Executar com pausas interativas
publicacoes = scraper.extrair_publicacoes_debug(
    data_inicio, 
    data_fim, 
    pause_between_steps=True
)

# Fechar
scraper.close()
```

### **2. 📸 Screenshots Automáticos**

#### **Via API (Funciona no Servidor)**
```bash
# Tirar screenshot da página inicial
curl -X GET 'https://cron.juscash.app/api/debug/screenshot'

# Executar scraping com screenshots
curl -X POST 'https://cron.juscash.app/api/debug/scraping-visual' \
  -H 'Content-Type: application/json' \
  -d '{
    "data_inicio": "2024-12-25T00:00:00",
    "data_fim": "2024-12-25T23:59:59",
    "take_screenshots": true
  }'
```

#### **Via Script Local**
```python
from app.infrastructure.scraping.dje_scraper_debug import DJEScraperDebug

scraper = DJEScraperDebug(visual_mode=False)
try:
    # Acessar site
    scraper.driver.get("https://dje.tjsp.jus.br/cdje/index.do")
    
    # Tirar screenshots em cada etapa
    scraper.take_screenshot("01_homepage.png")
    
    # ... preencher formulário ...
    scraper.take_screenshot("02_form_filled.png")
    
    # ... submeter ...
    scraper.take_screenshot("03_results.png")
    
finally:
    scraper.close()
```

### **3. 🎬 Gravação de Vídeo (Avançado)**

#### **Com OBS Studio (Windows/Mac/Linux)**
1. Instalar OBS Studio
2. Executar script visual: `python scripts/test-visual-scraping.py`
3. No OBS: Adicionar fonte "Captura de Janela" → Selecionar Chrome
4. Iniciar gravação
5. Executar scraping visual

#### **Com SimpleScreenRecorder (Linux)**
```bash
# Instalar
sudo apt install simplescreenrecorder

# Executar scraping visual em background
python scripts/test-visual-scraping.py &

# Gravar a tela
simplescreenrecorder
```

### **4. 🐳 Docker com VNC (Para Servidor)**

#### **Criar Dockerfile com VNC**
```dockerfile
FROM selenium/standalone-chrome-debug:latest

# Instalar Python e dependências
USER root
RUN apt-get update && apt-get install -y python3 python3-pip
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copiar código
COPY . /app
WORKDIR /app

# Expor porta VNC
EXPOSE 5900

CMD ["python3", "scripts/test-visual-scraping.py"]
```

#### **Executar com VNC**
```bash
# Build e run
docker build -t juscash-visual .
docker run -p 5900:5900 -p 4444:4444 juscash-visual

# Conectar via VNC Viewer em localhost:5900
# Senha padrão: secret
```

### **5. 🌐 Browser Remoto (Selenium Grid)**

#### **Docker Compose com Selenium Grid**
```yaml
version: '3'
services:
  selenium-hub:
    image: selenium/hub:latest
    ports:
      - "4444:4444"
  
  chrome-debug:
    image: selenium/node-chrome-debug:latest
    ports:
      - "5900:5900"  # VNC
    environment:
      - HUB_HOST=selenium-hub
    depends_on:
      - selenium-hub
  
  scraper:
    build: .
    depends_on:
      - chrome-debug
    environment:
      - SELENIUM_REMOTE_URL=http://selenium-hub:4444/wd/hub
```

### **6. 🎯 Configurações Específicas para Visualização**

#### **Modificar DJEScraper para Modo Visual**
```python
def _get_chrome_options_visual(self):
    """Configurações otimizadas para visualização"""
    chrome_options = Options()
    
    # REMOVER --headless para ver o navegador
    # chrome_options.add_argument("--headless")  # Comentar esta linha
    
    # Configurações para melhor visualização
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    # Desabilitar automação detectável
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    return chrome_options
```

#### **Adicionar Pausas para Observação**
```python
def extrair_com_pausas(self, data_inicio, data_fim):
    """Versão com pausas para observar cada etapa"""
    
    print("🌐 Acessando DJE...")
    self.driver.get(self.base_url)
    input("⏸️ Pressione Enter para continuar...")
    
    print("📝 Preenchendo formulário...")
    # ... código de preenchimento ...
    input("⏸️ Pressione Enter para submeter...")
    
    print("🔍 Submetendo pesquisa...")
    # ... código de submissão ...
    input("⏸️ Pressione Enter para processar resultados...")
    
    print("📊 Processando resultados...")
    # ... código de processamento ...
```

### **7. 🛠️ Ferramentas de Debug Avançadas**

#### **Chrome DevTools via Selenium**
```python
# Habilitar DevTools
chrome_options.add_argument("--auto-open-devtools-for-tabs")

# Executar JavaScript para debug
result = driver.execute_script("""
    console.log('Estado atual da página:');
    console.log('URL:', window.location.href);
    console.log('Título:', document.title);
    console.log('Formulários:', document.forms.length);
    return {
        url: window.location.href,
        title: document.title,
        forms: document.forms.length
    };
""")
print("Debug info:", result)
```

#### **Logs Detalhados**
```python
import logging

# Configurar logs detalhados
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Logs específicos do Selenium
selenium_logger = logging.getLogger('selenium')
selenium_logger.setLevel(logging.DEBUG)
```

### **8. 📱 Monitoramento em Tempo Real**

#### **Via Flower + Screenshots**
```python
from celery import current_task

def scraping_task_with_screenshots():
    """Tarefa Celery que tira screenshots durante execução"""
    
    scraper = DJEScraperDebug(visual_mode=False)
    
    try:
        # Atualizar progresso no Flower
        current_task.update_state(
            state='PROGRESS',
            meta={'step': 'Acessando DJE', 'progress': 10}
        )
        
        scraper.driver.get("https://dje.tjsp.jus.br/cdje/index.do")
        scraper.take_screenshot("step1_homepage.png")
        
        current_task.update_state(
            state='PROGRESS',
            meta={'step': 'Preenchendo formulário', 'progress': 30}
        )
        
        # ... continuar com screenshots em cada etapa ...
        
    finally:
        scraper.close()
```

### **9. 🎮 Interface Web para Controle**

#### **Dashboard HTML Simples**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Controle Visual do Scraping</title>
</head>
<body>
    <h1>🕷️ Controle Visual do Web Scraping</h1>
    
    <button onclick="takeScreenshot()">📸 Screenshot</button>
    <button onclick="startScraping()">🚀 Iniciar Scraping</button>
    <button onclick="stopScraping()">⏹️ Parar</button>
    
    <div id="screenshots"></div>
    
    <script>
        async function takeScreenshot() {
            const response = await fetch('/api/debug/screenshot');
            const data = await response.json();
            
            if (data.success) {
                const img = document.createElement('img');
                img.src = 'data:image/png;base64,' + data.base64_data;
                img.style.maxWidth = '500px';
                document.getElementById('screenshots').appendChild(img);
            }
        }
    </script>
</body>
</html>
```

## 🎯 **Resumo - Melhores Opções por Cenário**

### **🏠 Desenvolvimento Local**
- ✅ **Script Python Visual**: `python scripts/test-visual-scraping.py`
- ✅ **Jupyter Notebook**: Controle interativo passo a passo

### **🖥️ Servidor VPS**
- ✅ **Screenshots via API**: `/api/debug/screenshot`
- ✅ **Docker + VNC**: Visualização remota
- ✅ **Selenium Grid**: Ambiente profissional

### **🎬 Demonstração/Apresentação**
- ✅ **OBS Studio**: Gravação de vídeo profissional
- ✅ **Script com pausas**: Controle manual de timing

### **🐛 Debug/Troubleshooting**
- ✅ **Chrome DevTools**: Inspeção detalhada
- ✅ **Logs detalhados**: Rastreamento de problemas
- ✅ **Screenshots automáticos**: Histórico visual

## 🚀 **Como Começar Agora**

1. **Teste Local Rápido**:
   ```bash
   python scripts/test-visual-scraping.py
   # Escolha opção 1 (Visual)
   ```

2. **Screenshot do Servidor**:
   ```bash
   curl -X GET 'https://cron.juscash.app/api/debug/screenshot'
   ```

3. **Scraping Visual Completo**:
   ```bash
   curl -X POST 'https://cron.juscash.app/api/debug/scraping-visual' \
     -H 'Content-Type: application/json' \
     -d '{"data_inicio": "2024-12-25T00:00:00", "data_fim": "2024-12-25T23:59:59"}'
   ```

**Agora você pode ver exatamente como o Selenium navega e extrai os dados do DJE! 🎉** 