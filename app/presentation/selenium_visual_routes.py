from flask import Blueprint, request, jsonify, Response, render_template_string
from flask_restx import Namespace, Resource, fields
from datetime import datetime, timedelta
import os
import tempfile
import base64
import json
import time
import threading
from queue import Queue

selenium_visual_ns = Namespace('selenium-visual', description='Visualização do Selenium em tempo real')

# Queue para comunicação entre threads
screenshot_queue = Queue()
scraping_status = {'active': False, 'step': '', 'progress': 0}

@selenium_visual_ns.route('/live-scraping')
class LiveScraping(Resource):
    @selenium_visual_ns.doc('live_scraping')
    def get(self):
        """Interface web para ver o Selenium em tempo real"""
        
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>🕷️ Selenium Live Scraping - JusCash</title>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background: #f5f5f5; 
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            color: #333; 
        }
        .controls { 
            text-align: center; 
            margin-bottom: 20px; 
        }
        .btn { 
            padding: 10px 20px; 
            margin: 5px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px; 
        }
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn:hover { opacity: 0.8; }
        .status { 
            text-align: center; 
            margin: 20px 0; 
            padding: 10px; 
            border-radius: 5px; 
        }
        .status.active { background: #d4edda; color: #155724; }
        .status.inactive { background: #f8d7da; color: #721c24; }
        .progress-bar { 
            width: 100%; 
            height: 20px; 
            background: #e9ecef; 
            border-radius: 10px; 
            overflow: hidden; 
            margin: 10px 0; 
        }
        .progress-fill { 
            height: 100%; 
            background: #007bff; 
            transition: width 0.3s; 
        }
        .screenshot-container { 
            text-align: center; 
            margin: 20px 0; 
        }
        .screenshot { 
            max-width: 100%; 
            height: auto; 
            border: 2px solid #ddd; 
            border-radius: 5px; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
        }
        .logs { 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 5px; 
            height: 200px; 
            overflow-y: auto; 
            font-family: monospace; 
            font-size: 12px; 
            border: 1px solid #ddd; 
        }
        .date-inputs { 
            margin: 20px 0; 
            text-align: center; 
        }
        .date-inputs input { 
            padding: 8px; 
            margin: 5px; 
            border: 1px solid #ddd; 
            border-radius: 3px; 
        }
        .auto-refresh { 
            margin: 10px 0; 
            text-align: center; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕷️ Selenium Live Scraping</h1>
            <p>Visualize o web scraping do DJE em tempo real</p>
        </div>
        
        <div class="date-inputs">
            <label>Data Início: </label>
            <input type="date" id="dataInicio" />
            <label>Data Fim: </label>
            <input type="date" id="dataFim" />
        </div>
        
        <div class="controls">
            <button class="btn btn-success" onclick="startScraping()">🚀 Iniciar Scraping</button>
            <button class="btn btn-primary" onclick="takeScreenshot()">📸 Screenshot</button>
            <button class="btn btn-danger" onclick="stopScraping()">⏹️ Parar</button>
        </div>
        
        <div class="auto-refresh">
            <label>
                <input type="checkbox" id="autoRefresh" checked> 
                Atualizar automaticamente a cada 3 segundos
            </label>
        </div>
        
        <div class="status inactive" id="status">
            Status: Inativo
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" id="progressFill" style="width: 0%"></div>
        </div>
        
        <div class="screenshot-container">
            <div id="screenshotInfo">Nenhum screenshot disponível</div>
            <img id="screenshot" class="screenshot" style="display: none;" />
        </div>
        
        <div class="logs" id="logs">
            Logs aparecerão aqui...\n
        </div>
    </div>

    <script>
        let autoRefreshInterval;
        
        // Configurar datas padrão (ontem)
        window.onload = function() {
            const today = new Date();
            const yesterday = new Date(today);
            yesterday.setDate(yesterday.getDate() - 1);
            
            const formatDate = (date) => date.toISOString().split('T')[0];
            
            document.getElementById('dataInicio').value = formatDate(yesterday);
            document.getElementById('dataFim').value = formatDate(yesterday);
            
            // Iniciar auto-refresh
            startAutoRefresh();
        };
        
        function startAutoRefresh() {
            const checkbox = document.getElementById('autoRefresh');
            if (checkbox.checked) {
                autoRefreshInterval = setInterval(() => {
                    updateStatus();
                    if (document.getElementById('status').classList.contains('active')) {
                        takeScreenshot();
                    }
                }, 3000);
            }
        }
        
        function stopAutoRefresh() {
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
            }
        }
        
        document.getElementById('autoRefresh').onchange = function() {
            if (this.checked) {
                startAutoRefresh();
            } else {
                stopAutoRefresh();
            }
        };
        
        async function startScraping() {
            const dataInicio = document.getElementById('dataInicio').value + 'T00:00:00';
            const dataFim = document.getElementById('dataFim').value + 'T23:59:59';
            
            addLog('🚀 Iniciando scraping...');
            
            try {
                const response = await fetch('/api/selenium-visual/start-scraping', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        data_inicio: dataInicio,
                        data_fim: dataFim
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    addLog('✅ Scraping iniciado com sucesso!');
                    updateStatus();
                } else {
                    addLog('❌ Erro ao iniciar scraping: ' + data.error);
                }
            } catch (error) {
                addLog('❌ Erro: ' + error.message);
            }
        }
        
        async function takeScreenshot() {
            try {
                const response = await fetch('/api/selenium-visual/screenshot');
                const data = await response.json();
                
                if (data.success) {
                    const img = document.getElementById('screenshot');
                    const info = document.getElementById('screenshotInfo');
                    
                    img.src = 'data:image/png;base64,' + data.base64_data;
                    img.style.display = 'block';
                    info.textContent = 'Screenshot: ' + data.timestamp;
                    
                    addLog('📸 Screenshot atualizado');
                } else {
                    addLog('❌ Erro no screenshot: ' + data.error);
                }
            } catch (error) {
                addLog('❌ Erro: ' + error.message);
            }
        }
        
        async function stopScraping() {
            try {
                const response = await fetch('/api/selenium-visual/stop-scraping', {
                    method: 'POST'
                });
                
                const data = await response.json();
                addLog('⏹️ Scraping parado');
                updateStatus();
            } catch (error) {
                addLog('❌ Erro: ' + error.message);
            }
        }
        
        async function updateStatus() {
            try {
                const response = await fetch('/api/selenium-visual/status');
                const data = await response.json();
                
                const statusDiv = document.getElementById('status');
                const progressFill = document.getElementById('progressFill');
                
                if (data.active) {
                    statusDiv.className = 'status active';
                    statusDiv.textContent = 'Status: ' + data.step + ' (' + data.progress + '%)';
                    progressFill.style.width = data.progress + '%';
                } else {
                    statusDiv.className = 'status inactive';
                    statusDiv.textContent = 'Status: Inativo';
                    progressFill.style.width = '0%';
                }
            } catch (error) {
                console.error('Erro ao atualizar status:', error);
            }
        }
        
        function addLog(message) {
            const logs = document.getElementById('logs');
            const timestamp = new Date().toLocaleTimeString();
            logs.textContent += '[' + timestamp + '] ' + message + '\\n';
            logs.scrollTop = logs.scrollHeight;
        }
        
        // Atualizar status inicial
        updateStatus();
    </script>
</body>
</html>
        """
        
        return Response(html_template, mimetype='text/html')

@selenium_visual_ns.route('/start-scraping')
class StartScraping(Resource):
    @selenium_visual_ns.doc('start_scraping')
    def post(self):
        """Inicia o scraping com visualização em tempo real"""
        global scraping_status
        
        if scraping_status['active']:
            return {'success': False, 'error': 'Scraping já está ativo'}, 400
        
        data = request.get_json()
        
        try:
            data_inicio = datetime.fromisoformat(data['data_inicio'])
            data_fim = datetime.fromisoformat(data['data_fim'])
        except (KeyError, ValueError):
            return {'success': False, 'error': 'Datas inválidas'}, 400
        
        # Iniciar scraping em thread separada
        thread = threading.Thread(
            target=run_visual_scraping,
            args=(data_inicio, data_fim)
        )
        thread.daemon = True
        thread.start()
        
        return {
            'success': True,
            'message': 'Scraping iniciado',
            'data_inicio': data_inicio.isoformat(),
            'data_fim': data_fim.isoformat()
        }

@selenium_visual_ns.route('/screenshot')
class GetScreenshot(Resource):
    @selenium_visual_ns.doc('get_screenshot')
    def get(self):
        """Obtém o screenshot mais recente"""
        try:
            from app.infrastructure.scraping.dje_scraper_debug import DJEScraperDebug
            
            scraper = DJEScraperDebug(visual_mode=False)
            
            try:
                # Se não há URL atual, acessar DJE
                if scraper.driver.current_url == 'data:,':
                    scraper.driver.get("https://dje.tjsp.jus.br/cdje/index.do")
                    time.sleep(2)
                
                # Criar screenshot
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    screenshot_path = tmp_file.name
                
                scraper.driver.save_screenshot(screenshot_path)
                
                # Converter para base64
                with open(screenshot_path, 'rb') as img_file:
                    img_data = img_file.read()
                    base64_data = base64.b64encode(img_data).decode('utf-8')
                
                os.unlink(screenshot_path)
                
                return {
                    'success': True,
                    'base64_data': base64_data,
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'url': scraper.driver.current_url
                }
                
            finally:
                scraper.close()
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }

@selenium_visual_ns.route('/status')
class ScrapingStatus(Resource):
    @selenium_visual_ns.doc('scraping_status')
    def get(self):
        """Obtém o status atual do scraping"""
        global scraping_status
        return scraping_status

@selenium_visual_ns.route('/stop-scraping')
class StopScraping(Resource):
    @selenium_visual_ns.doc('stop_scraping')
    def post(self):
        """Para o scraping atual"""
        global scraping_status
        
        scraping_status['active'] = False
        scraping_status['step'] = 'Parado pelo usuário'
        scraping_status['progress'] = 0
        
        return {'success': True, 'message': 'Scraping parado'}

def run_visual_scraping(data_inicio: datetime, data_fim: datetime):
    """Executa o scraping com atualizações de status"""
    global scraping_status
    
    scraping_status['active'] = True
    scraping_status['step'] = 'Inicializando...'
    scraping_status['progress'] = 10
    
    try:
        from app.infrastructure.scraping.dje_scraper_debug import DJEScraperDebug
        from selenium.webdriver.support.ui import WebDriverWait, Select
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        scraper = DJEScraperDebug(visual_mode=False)
        
        try:
            # Etapa 1: Acessar site
            scraping_status['step'] = 'Acessando DJE...'
            scraping_status['progress'] = 20
            
            scraper.driver.get("https://dje.tjsp.jus.br/cdje/index.do")
            time.sleep(3)
            
            # Etapa 2: Preencher formulário
            scraping_status['step'] = 'Preenchendo formulário...'
            scraping_status['progress'] = 40
            
            wait = WebDriverWait(scraper.driver, 30)
            
            # Preencher datas
            data_inicio_field = wait.until(EC.visibility_of_element_located((By.ID, "dtInicioString")))
            data_inicio_field.clear()
            data_inicio_field.send_keys(data_inicio.strftime("%d/%m/%Y"))
            
            data_fim_field = scraper.driver.find_element(By.ID, "dtFimString")
            data_fim_field.clear()
            data_fim_field.send_keys(data_fim.strftime("%d/%m/%Y"))
            
            # Selecionar caderno
            select_caderno = Select(scraper.driver.find_element(By.NAME, "dadosConsulta.cdCaderno"))
            select_caderno.select_by_value("-11")
            
            # Termo de busca
            search_box = scraper.driver.find_element(By.ID, "procura")
            search_box.clear()
            search_box.send_keys('"instituto nacional do seguro social" E inss')
            
            # Etapa 3: Submeter
            scraping_status['step'] = 'Submetendo formulário...'
            scraping_status['progress'] = 60
            
            submit_button = scraper.driver.find_element(By.CSS_SELECTOR, "form[name='consultaAvancadaForm'] input[type='submit']")
            submit_button.click()
            
            time.sleep(5)
            
            # Etapa 4: Processar resultados
            scraping_status['step'] = 'Processando resultados...'
            scraping_status['progress'] = 80
            
            # Aguardar resultados
            wait.until(EC.presence_of_element_located((By.ID, "divResultadosInferior")))
            
            # Contar resultados
            result_elements = scraper.driver.find_elements(By.CSS_SELECTOR, "div#divResultadosInferior table tr.fundocinza1")
            
            scraping_status['step'] = f'Concluído! {len(result_elements)} resultados encontrados'
            scraping_status['progress'] = 100
            
            # Aguardar um pouco antes de finalizar
            time.sleep(5)
            
        finally:
            scraper.close()
            
    except Exception as e:
        scraping_status['step'] = f'Erro: {str(e)}'
        scraping_status['progress'] = 0
    
    finally:
        # Manter status por 30 segundos antes de resetar
        time.sleep(30)
        scraping_status['active'] = False
        scraping_status['step'] = 'Inativo'
        scraping_status['progress'] = 0

def register_selenium_visual_routes(api):
    """Registra as rotas de visualização do Selenium"""
    api.add_namespace(selenium_visual_ns, path='/selenium-visual') 