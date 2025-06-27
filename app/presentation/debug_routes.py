from flask import Blueprint, request, jsonify
from flask_restx import Namespace, Resource, fields
from datetime import datetime
import os
import tempfile
import base64

debug_ns = Namespace('debug', description='Endpoints de debug para visualizar scraping')

screenshot_model = debug_ns.model('Screenshot', {
    'success': fields.Boolean(description='Se o screenshot foi tirado com sucesso'),
    'filename': fields.String(description='Nome do arquivo'),
    'base64_data': fields.String(description='Dados da imagem em base64'),
    'timestamp': fields.String(description='Timestamp do screenshot')
})

scraping_debug_model = debug_ns.model('ScrapingDebug', {
    'data_inicio': fields.DateTime(required=True, description='Data de início'),
    'data_fim': fields.DateTime(required=True, description='Data fim'),
    'visual_mode': fields.Boolean(description='Se deve rodar em modo visual', default=False),
    'take_screenshots': fields.Boolean(description='Se deve tirar screenshots', default=True)
})

@debug_ns.route('/screenshot')
class DebugScreenshot(Resource):
    @debug_ns.doc('take_screenshot')
    @debug_ns.marshal_with(screenshot_model)
    def get(self):
        """Tira um screenshot da página inicial do DJE"""
        try:
            from app.infrastructure.scraping.dje_scraper_debug import DJEScraperDebug
            
            # Usar modo headless para screenshots via API
            scraper = DJEScraperDebug(visual_mode=False)
            
            try:
                # Acessar página inicial
                scraper.driver.get("https://dje.tjsp.jus.br/cdje/index.do")
                
                # Aguardar carregamento
                import time
                time.sleep(3)
                
                # Criar arquivo temporário
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    screenshot_path = tmp_file.name
                
                # Tirar screenshot
                scraper.driver.save_screenshot(screenshot_path)
                
                # Converter para base64
                with open(screenshot_path, 'rb') as img_file:
                    img_data = img_file.read()
                    base64_data = base64.b64encode(img_data).decode('utf-8')
                
                # Limpar arquivo temporário
                os.unlink(screenshot_path)
                
                return {
                    'success': True,
                    'filename': f'dje_screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png',
                    'base64_data': base64_data,
                    'timestamp': datetime.now().isoformat()
                }
                
            finally:
                scraper.close()
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, 500

@debug_ns.route('/scraping-visual')
class DebugScrapingVisual(Resource):
    @debug_ns.doc('debug_scraping_visual')
    @debug_ns.expect(scraping_debug_model)
    def post(self):
        """Executa scraping com opções de debug e screenshots"""
        data = request.get_json()
        
        try:
            data_inicio = datetime.fromisoformat(data['data_inicio'])
            data_fim = datetime.fromisoformat(data['data_fim'])
            visual_mode = data.get('visual_mode', False)
            take_screenshots = data.get('take_screenshots', True)
        except (KeyError, ValueError) as e:
            return {'error': f'Dados inválidos: {e}'}, 400
        
        try:
            from app.infrastructure.scraping.dje_scraper_debug import DJEScraperDebug
            
            # Forçar headless para API (visual_mode só funciona localmente)
            scraper = DJEScraperDebug(visual_mode=False)
            
            screenshots = []
            result = {
                'data_inicio': data_inicio.isoformat(),
                'data_fim': data_fim.isoformat(),
                'started_at': datetime.now().isoformat(),
                'steps': [],
                'screenshots': []
            }
            
            try:
                # Etapa 1: Acessar site
                result['steps'].append({
                    'step': 1,
                    'description': 'Acessando site do DJE',
                    'timestamp': datetime.now().isoformat()
                })
                
                scraper.driver.get("https://dje.tjsp.jus.br/cdje/index.do")
                
                if take_screenshots:
                    screenshot_data = take_screenshot_base64(scraper, "01_homepage")
                    if screenshot_data:
                        result['screenshots'].append(screenshot_data)
                
                # Etapa 2: Preencher formulário
                result['steps'].append({
                    'step': 2,
                    'description': 'Preenchendo formulário',
                    'timestamp': datetime.now().isoformat()
                })
                
                # Preencher formulário
                from selenium.webdriver.support.ui import WebDriverWait, Select
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.common.by import By
                import time
                
                wait = WebDriverWait(scraper.driver, 30)
                
                wait.until(EC.visibility_of_element_located((By.ID, "dtInicioString"))).send_keys(data_inicio.strftime("%d/%m/%Y"))
                scraper.driver.find_element(By.ID, "dtFimString").send_keys(data_fim.strftime("%d/%m/%Y"))
                
                select_caderno = Select(scraper.driver.find_element(By.NAME, "dadosConsulta.cdCaderno"))
                select_caderno.select_by_value("-11")
                
                search_box = scraper.driver.find_element(By.ID, "procura")
                search_box.clear()
                search_box.send_keys('"instituto nacional do seguro social" E inss')
                
                if take_screenshots:
                    screenshot_data = take_screenshot_base64(scraper, "02_form_filled")
                    if screenshot_data:
                        result['screenshots'].append(screenshot_data)
                
                # Etapa 3: Submeter
                result['steps'].append({
                    'step': 3,
                    'description': 'Submetendo formulário',
                    'timestamp': datetime.now().isoformat()
                })
                
                submit_button = scraper.driver.find_element(By.CSS_SELECTOR, "form[name='consultaAvancadaForm'] input[type='submit']")
                submit_button.click()
                
                time.sleep(5)  # Aguardar carregamento dos resultados
                
                if take_screenshots:
                    screenshot_data = take_screenshot_base64(scraper, "03_results")
                    if screenshot_data:
                        result['screenshots'].append(screenshot_data)
                
                # Etapa 4: Extrair dados
                result['steps'].append({
                    'step': 4,
                    'description': 'Extraindo dados',
                    'timestamp': datetime.now().isoformat()
                })
                
                publicacoes = scraper.extrair_publicacoes_debug(data_inicio, data_fim, pause_between_steps=False)
                
                result['completed_at'] = datetime.now().isoformat()
                result['total_publicacoes'] = len(publicacoes)
                result['publicacoes'] = publicacoes[:5] if publicacoes else []  # Primeiras 5
                result['success'] = True
                
                return result
                
            finally:
                scraper.close()
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, 500

def take_screenshot_base64(scraper, step_name: str) -> dict:
    """Tira screenshot e retorna dados em base64"""
    try:
        import tempfile
        import base64
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            screenshot_path = tmp_file.name
        
        scraper.driver.save_screenshot(screenshot_path)
        
        with open(screenshot_path, 'rb') as img_file:
            img_data = img_file.read()
            base64_data = base64.b64encode(img_data).decode('utf-8')
        
        os.unlink(screenshot_path)
        
        return {
            'step': step_name,
            'timestamp': datetime.now().isoformat(),
            'base64_data': base64_data,
            'filename': f'{step_name}_{datetime.now().strftime("%H%M%S")}.png'
        }
        
    except Exception as e:
        return {
            'step': step_name,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

@debug_ns.route('/browser-info')
class DebugBrowserInfo(Resource):
    @debug_ns.doc('get_browser_info')
    def get(self):
        """Obtém informações sobre o navegador disponível"""
        try:
            from app.infrastructure.scraping.dje_scraper_debug import DJEScraperDebug
            
            scraper = DJEScraperDebug(visual_mode=False)
            
            try:
                info = {
                    'chrome_available': True,
                    'current_url': scraper.driver.current_url,
                    'window_size': scraper.driver.get_window_size(),
                    'user_agent': scraper.driver.execute_script("return navigator.userAgent;"),
                    'selenium_version': 'Available',
                    'timestamp': datetime.now().isoformat()
                }
                
                return info
                
            finally:
                scraper.close()
                
        except Exception as e:
            return {
                'chrome_available': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Blueprint para registrar as rotas
debug_bp = Blueprint('debug', __name__)

def register_debug_routes(api):
    """Registra as rotas de debug na API"""
    api.add_namespace(debug_ns, path='/debug') 