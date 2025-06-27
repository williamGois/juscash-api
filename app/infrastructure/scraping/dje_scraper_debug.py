import re
import time
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import tempfile
import uuid
import threading
import subprocess
import pdfplumber
from selenium.webdriver.common.action_chains import ActionChains

class DJEScraperDebug:
    """
    Versão de debug do DJEScraper que permite visualizar o Chrome em execução
    e implementa o padrão Singleton para garantir uma única instância.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(DJEScraperDebug, cls).__new__(cls)
        return cls._instance

    def __init__(self, base_url: str = "https://dje.tjsp.jus.br/cdje/index.do", visual_mode: bool = False):
        if not hasattr(self, 'initialized'):
            with self._lock:
                if not hasattr(self, 'initialized'):
                    self.base_url = base_url
                    self.session = requests.Session()
                    self.driver = None
                    self.wait = None
                    self.max_retries = 3
                    self.visual_mode = visual_mode
                    self.log_buffer = []  # Buffer para logs
                    logging.basicConfig(level=logging.INFO)
                    self.initialized = True

    def log(self, message: str, level: str = 'info'):
        """Registra log no buffer e imprime"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.log_buffer.append(log_entry)
        print(log_entry)
        
        # Manter apenas últimos 1000 logs
        if len(self.log_buffer) > 1000:
            self.log_buffer = self.log_buffer[-1000:]
    
    def get_logs(self) -> List[str]:
        """Retorna logs armazenados"""
        return self.log_buffer

    def get_driver(self):
        """Obtém o driver, inicializando-o se necessário."""
        if not self.driver:
            self.log("🔧 Criando nova instância do scraper...")
            
            # Verificar display
            self.log("🔍 Verificando prerequisitos...")
            if not os.environ.get('DISPLAY'):
                os.environ['DISPLAY'] = ':99'
                self.log(f"🖥️ Display configurado: {os.environ['DISPLAY']}")
            else:
                self.log(f"🖥️ Display já configurado: {os.environ['DISPLAY']}")
            
            # Verificar Xvfb
            try:
                xvfb_pid = subprocess.check_output(['pgrep', 'Xvfb']).decode().strip()
                self.log(f"✅ Xvfb está rodando (PID: {xvfb_pid})")
            except:
                self.log("⚠️ Xvfb não está rodando, tentando iniciar...")
                try:
                    subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1920x1080x24'])
                    time.sleep(3)
                    xvfb_pid = subprocess.check_output(['pgrep', 'Xvfb']).decode().strip()
                    self.log(f"✅ Xvfb iniciado (PID: {xvfb_pid})")
                except Exception as e:
                    self.log(f"❌ Erro ao iniciar Xvfb: {e}")
                    return None
            
            # Inicializar Chrome driver
            for attempt in range(3):
                try:
                    self.log(f"🚀 Tentativa {attempt + 1}/3 de inicializar Chrome driver...")
                    
                    # Configurar Chrome
                    chrome_options = self._get_chrome_options()
                    
                    # Verificar ChromeDriver
                    chromedriver_path = "/usr/local/bin/chromedriver"
                    if not os.path.exists(chromedriver_path):
                        self.log("⚠️ ChromeDriver não encontrado, baixando...")
                        from webdriver_manager.chrome import ChromeDriverManager
                        chromedriver_path = ChromeDriverManager().install()
                    
                    # Verificar versão
                    try:
                        version = subprocess.check_output([chromedriver_path, '--version']).decode()
                        self.log(f"✅ ChromeDriver encontrado em {chromedriver_path}: {version.strip()}")
                    except:
                        self.log("⚠️ Erro ao verificar versão do ChromeDriver")
                    
                    # Inicializar driver
                    self.log(f"🔧 Tentando com ChromeDriver em {chromedriver_path}")
                    service = Service(executable_path=chromedriver_path)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    self.wait = WebDriverWait(self.driver, 30)
                    
                    # Testar driver
                    self.driver.get("data:text/html,<html><body><h1>Chrome Test</h1></body></html>")
                    if "Chrome Test" in self.driver.page_source:
                        self.log("✅ Chrome inicializado com sucesso!")
                        self.log(f"✅ Nova instância do scraper criada com sucesso")
                        return self.driver
                    else:
                        self.log("⚠️ Chrome inicializado mas teste falhou")
                        self.close()
                        
                except Exception as e:
                    self.log(f"❌ Erro na tentativa {attempt + 1}: {e}")
                    if self.driver:
                        self.close()
                    time.sleep(5)
            
            self.log("❌ Todas as tentativas de inicializar Chrome falharam")
            return None
        
        return self.driver

    def _get_chrome_options(self):
        """Configura opções do Chrome"""
        chrome_options = Options()
        
        # Modo headless
        if not self.visual_mode:
            self.log("🎯 Modo: HEADLESS (Chrome oculto)")
            chrome_options.add_argument('--headless=new')
        else:
            self.log("🎯 Modo: VISUAL (Chrome visível)")
        
        # Configurações básicas
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        
        # Configurações de performance
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--memory-pressure-off')
        chrome_options.add_argument('--max_old_space_size=4096')
        chrome_options.add_argument('--single-process')
        chrome_options.add_argument('--no-zygote')
        chrome_options.add_argument('--aggressive-cache-discard')
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--remote-debugging-port=0')
        chrome_options.add_argument('--disable-crash-reporter')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--disable-in-process-stack-traces')
        chrome_options.add_argument('--disable-background-mode')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-infobars')
        
        # Configurações de proxy (se necessário)
        # chrome_options.add_argument('--proxy-server=socks5://localhost:9050')
        
        # Configurações experimentais
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Preferências
        prefs = {
            'profile.default_content_settings.popups': 0,
            'download.default_directory': '/tmp',
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': True,
            'plugins.always_open_pdf_externally': True
        }
        chrome_options.add_experimental_option('prefs', prefs)
        
        return chrome_options

    def _ensure_chromedriver(self):
        """Garante que o ChromeDriver esteja disponível"""
        import os
        import shutil
        
        # Verificar se ChromeDriver já está no local correto
        if os.path.exists('/usr/local/bin/chromedriver') and os.access('/usr/local/bin/chromedriver', os.X_OK):
            return True
        
        # Verificar se existe no local do webdriver-manager
        wdm_path = '/app/.wdm/drivers/chromedriver/linux64/138.0.7204.49/chromedriver-linux64/chromedriver'
        if os.path.exists(wdm_path):
            print("🔧 Aplicando fix ChromeDriver: copiando do webdriver-manager...")
            try:
                shutil.copy2(wdm_path, '/usr/local/bin/chromedriver')
                os.chmod('/usr/local/bin/chromedriver', 0o755)
                print("✅ ChromeDriver copiado e configurado com sucesso!")
                return True
            except Exception as e:
                print(f"❌ Erro ao copiar ChromeDriver: {e}")
        
        return False

    def _initialize_driver(self):
        """Inicializa o driver com configurações de debug"""
        # Aplicar fix do ChromeDriver primeiro
        self._ensure_chromedriver()
        
        chrome_options = self._get_chrome_options()
        
        # Verificar prerequisitos
        print("🔍 Verificando prerequisitos...")
        
        # Verificar display virtual
        if 'DISPLAY' not in os.environ:
            os.environ['DISPLAY'] = ':99'
            print("🖥️ Display configurado para :99")
        else:
            print(f"🖥️ Display já configurado: {os.environ['DISPLAY']}")
        
        # Verificar se Xvfb está rodando
        try:
            result = subprocess.run(['pgrep', '-f', 'Xvfb'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Xvfb está rodando (PID: {result.stdout.strip()})")
            else:
                print("⚠️ Xvfb não está rodando, tentando iniciar...")
                subprocess.run(['Xvfb', ':99', '-screen', '0', '1920x1080x24'], check=False)
        except Exception as e:
            print(f"⚠️ Erro ao verificar Xvfb: {e}")
        
        for attempt in range(self.max_retries):
            try:
                print(f"🚀 Tentativa {attempt + 1}/{self.max_retries} de inicializar Chrome driver...")
                
                if self.visual_mode:
                    print(f"🎯 Modo: VISUAL (Chrome será visível no display {os.environ.get('DISPLAY', 'padrão')})")
                else:
                    print(f"🎯 Modo: HEADLESS (Chrome oculto)")
                
                # Verificar se ChromeDriver existe
                chromedriver_paths = ['/usr/local/bin/chromedriver', '/usr/bin/chromedriver']
                chromedriver_path = None
                
                for path in chromedriver_paths:
                    try:
                        result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            chromedriver_path = path
                            print(f"✅ ChromeDriver encontrado em {path}: {result.stdout.strip()}")
                            break
                    except Exception as e:
                        print(f"⚠️ ChromeDriver não encontrado em {path}: {e}")
                
                if not chromedriver_path:
                    print("❌ ChromeDriver não encontrado em nenhum local padrão")
                    # Tentar instalar via webdriver-manager
                    print("🔄 Tentando instalar ChromeDriver via webdriver-manager...")
                
                # Estratégia 1: Usar chromedriver encontrado
                if chromedriver_path:
                    try:
                        print(f"🔧 Tentando com ChromeDriver em {chromedriver_path}")
                        self.driver = webdriver.Chrome(
                            service=Service(chromedriver_path),
                            options=chrome_options
                        )
                        print("✅ Driver inicializado com ChromeDriver local")
                        break
                    except Exception as e:
                        print(f"❌ ChromeDriver local falhou: {e}")
                        
                # Estratégia 2: Fallback para webdriver-manager
                try:
                    print("🔧 Tentando com webdriver-manager...")
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    print("✅ Driver inicializado com webdriver-manager")
                    break
                except Exception as e:
                    print(f"❌ Webdriver-manager falhou: {e}")
                    
                # Estratégia 3: Chrome sem service específico
                try:
                    print("🔧 Tentando Chrome sem service específico...")
                    self.driver = webdriver.Chrome(options=chrome_options)
                    print("✅ Driver inicializado com Chrome padrão")
                    break
                except Exception as e:
                    print(f"❌ Chrome padrão falhou: {e}")
                    
                    # Log detalhado do erro
                    print(f"❌ Erro detalhado: {str(e)}")
                    if "chrome not reachable" in str(e).lower():
                        print("💡 Sugestão: Problema com display virtual ou Chrome não instalado")
                    elif "chromedriver" in str(e).lower():
                        print("💡 Sugestão: Problema com ChromeDriver - versão incompatível")
                    elif "permission" in str(e).lower():
                        print("💡 Sugestão: Problema de permissões")
            
            except Exception as e:
                print(f"❌ Erro crítico na tentativa {attempt + 1}: {e}")
                if self.driver:
                    try:
                        self.driver.quit()
                    except: 
                        pass
                    self.driver = None
                
                if attempt == self.max_retries - 1:
                    print("❌ ERRO CRÍTICO: Todas as tentativas falharam")
                    print("🔍 Dicas de debug:")
                    print("  - Verificar se o Xvfb está rodando: ps aux | grep Xvfb")
                    print("  - Verificar se o Chrome está instalado: google-chrome --version")
                    print("  - Verificar se o ChromeDriver está instalado: chromedriver --version")
                    print("  - Verificar permissões dos arquivos")
                    raise Exception(f"Falha crítica ao inicializar Chrome após {self.max_retries} tentativas. Último erro: {e}")
                
                time.sleep(3)
        
        if self.driver:
            try:
                self.driver.set_page_load_timeout(45)
                self.driver.implicitly_wait(15)
                self.wait = WebDriverWait(self.driver, 30)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                # Testar se o driver está funcionando
                self.driver.get("data:text/html,<html><body><h1>Chrome Test</h1></body></html>")
                print(f"✅ Chrome inicializado com sucesso! URL de teste: {self.driver.current_url}")
                
                if self.visual_mode:
                    print(f"🌐 Chrome visível no display {os.environ.get('DISPLAY')}")
                    
            except Exception as e:
                print(f"❌ Erro no teste pós-inicialização: {e}")
                raise

    def _preencher_formulario(self, data_inicio: datetime, data_fim: datetime):
        """Preenche o formulário de busca"""
        try:
            # Aguardar campo data início
            self.log("  📅 Preenchendo data de início...")
            data_inicio_field = self._wait_for_element_ready(By.ID, "dataInicio")
            if not self._safe_send_keys(data_inicio_field, data_inicio.strftime("%d/%m/%Y")):
                self.log("  ❌ Falha ao preencher data início")
                return False
            
            # Aguardar campo data fim
            self.log("  📅 Preenchendo data de fim...")
            data_fim_field = self._wait_for_element_ready(By.ID, "dataFim")
            if not self._safe_send_keys(data_fim_field, data_fim.strftime("%d/%m/%Y")):
                self.log("  ❌ Falha ao preencher data fim")
                return False
            
            # Selecionar caderno
            self.log("  📂 Selecionando caderno...")
            try:
                select_caderno = Select(self._wait_for_element_ready(By.NAME, "dadosConsulta.cdCaderno"))
                select_caderno.select_by_value("-11")  # Judicial - 1ª instância
                self.log("  ✅ Caderno selecionado: Judicial - 1ª instância")
            except Exception as e:
                self.log(f"  ❌ Erro ao selecionar caderno: {e}")
                return False
            
            # Preencher termos de busca
            self.log("  🔍 Preenchendo termos de busca...")
            search_field = self._wait_for_element_ready(By.ID, "procura")
            search_terms = '"instituto nacional do seguro social" E inss E rpv'
            if not self._safe_send_keys(search_field, search_terms):
                self.log("  ❌ Falha ao preencher termos de busca")
                return False
            
            # Submeter formulário
            self.log("  🔘 Submetendo formulário...")
            try:
                # Procurar por botão "Pesquisar"
                submit_button = self._wait_for_element_ready(By.XPATH, "//input[@type='button' and @value='Pesquisar']")
                if not self._safe_click(submit_button):
                    self.log("  ❌ Falha ao clicar no botão Pesquisar")
                    return False
                
                # Aguardar resultados
                self.log("  ⏳ Aguardando resultados...")
                time.sleep(5)
                
                # Verificar se há erro na página
                if "erro" in self.driver.page_source.lower():
                    self.log("  ❌ Erro detectado na página após submissão")
                    return False
                
                # Verificar se há resultados
                try:
                    self.wait.until(EC.presence_of_element_located((By.ID, "divResultadosInferior")))
                    self.log("  ✅ Resultados carregados")
                    return True
                except:
                    self.log("  ❌ Resultados não carregaram")
                    return False
                
            except Exception as e:
                self.log(f"  ❌ Erro ao submeter formulário: {e}")
                return False
            
        except Exception as e:
            self.log(f"❌ Erro ao preencher formulário: {e}")
            return False

    def extrair_publicacoes_debug(self, data_inicio: datetime, data_fim: datetime, pause_between_steps: bool = True) -> List[Dict[str, Any]]:
        """Versão debug com navegação completa em cada resultado e paginação"""
        driver = self.get_driver()
        if not driver:
            self.log("❌ Driver não está operacional. Abortando extração.")
            return []

        self.log(f"🕷️ Iniciando extração COMPLETA de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
        
        try:
            # Etapa 1: Acessar o site
            self.log("📍 Etapa 1: Acessando o site do DJE...")
            driver.get(self.base_url)
            
            # Aguardar carregamento completo
            self.log("  ⏳ Aguardando carregamento completo da página...")
            self._wait_for_page_load()
            
            if pause_between_steps and self.visual_mode:
                input("⏸️ Pressione Enter para continuar para o preenchimento do formulário...")

            # Etapa 2: Preencher formulário
            self.log("📍 Etapa 2: Preenchendo formulário...")
            if not self._preencher_formulario(data_inicio, data_fim):
                self.log("❌ Falha ao preencher formulário. Abortando.")
                return []
            
            if pause_between_steps and self.visual_mode:
                input("⏸️ Pressione Enter para processar os resultados...")

            # Etapa 3: Processar TODAS as páginas de resultados
            self.log("📍 Etapa 3: Processando TODAS as páginas de resultados...")
            all_publicacoes = []
            page_num = 1
            
            while True:
                self.log(f"  📄 Processando página {page_num}...")
                
                try:
                    # Aguardar div de resultados
                    self.log(f"    ⏳ Aguardando div de resultados da página {page_num}...")
                    self.wait.until(EC.presence_of_element_located((By.ID, "divResultadosInferior")))
                    time.sleep(3)
                    
                    # Verificar se há erro na página
                    page_source = driver.page_source.lower()
                    if "erro" in page_source or "error" in page_source:
                        self.log(f"    ⚠️ Possível erro detectado na página {page_num}")
                    
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    # DEBUG: Verificar conteúdo da página
                    self.log(f"    🔍 URL atual: {driver.current_url}")
                    self.log(f"    🔍 Título da página: {driver.title}")
                    
                    # Verificar se há div de resultados
                    div_resultados = soup.find('div', id='divResultadosInferior')
                    if div_resultados:
                        self.log(f"    📋 Div divResultadosInferior encontrado com {len(div_resultados.get_text())} caracteres")
                        
                        # Verificar se há texto "nenhum resultado"  
                        texto_resultados = div_resultados.get_text().lower()
                        if "nenhum" in texto_resultados or "não foram encontrados" in texto_resultados or "sem resultados" in texto_resultados:
                            self.log(f"    ℹ️ Mensagem de nenhum resultado detectada na página {page_num}")
                            if page_num == 1:
                                self.log("    ℹ️ Nenhuma publicação encontrada para os critérios definidos.")
                                break
                        
                        # Verificar quantidade de resultados
                        total_text = driver.page_source
                        if "Resultados 1 a" in total_text:
                            import re
                            match = re.search(r'Resultados \d+ a \d+ de (\d+)', total_text)
                            if match:
                                total = int(match.group(1))
                                self.log(f"    📊 Total de resultados encontrados: {total}")
                    else:
                        self.log(f"    ⚠️ Div divResultadosInferior não encontrado na página {page_num}")
                    
                    # Buscar por elementos de publicação usando a estrutura correta
                    self.log(f"    🔍 Procurando links com onclick que contém consultaSimples.do...")
                    
                    # NOVA ABORDAGEM: Primeiro buscar TODOS os links onclick na página
                    all_onclick_links = driver.find_elements(By.XPATH, "//a[@onclick]")
                    self.log(f"    📋 Total de links com onclick na página: {len(all_onclick_links)}")
                    
                    # Filtrar apenas os que contém consultaSimples.do
                    publicacao_elements = []
                    for link in all_onclick_links:
                        onclick_attr = link.get_attribute('onclick')
                        if onclick_attr and 'consultaSimples.do' in onclick_attr:
                            publicacao_elements.append(link)
                            self.log(f"      🔗 Link encontrado: {onclick_attr[:100]}...")
                    
                    # Se ainda não encontrou, tentar com seletor mais amplo
                    if not publicacao_elements:
                        # Buscar qualquer link que mencione consultaSimples
                        broader_links = driver.find_elements(By.XPATH, "//*[contains(@onclick, 'consultaSimples')]")
                        self.log(f"    📋 Busca mais ampla encontrou {len(broader_links)} elementos")
                        
                        for link in broader_links:
                            onclick_attr = link.get_attribute('onclick')
                            self.log(f"      🔗 Elemento broader: {onclick_attr[:100]}...")
                            if 'consultaSimples.do' in onclick_attr:
                                publicacao_elements.append(link)
                    
                    if not publicacao_elements and page_num == 1:
                        self.log("    ℹ️ Nenhuma publicação encontrada para os critérios definidos.")
                        break
                    elif not publicacao_elements:
                        self.log(f"    ℹ️ Fim dos resultados na página {page_num}")
                        break
                    else:
                        self.log(f"    📋 Processando {len(publicacao_elements)} publicações na página {page_num}")
                        
                        # Processar cada elemento de publicação
                        for i, element in enumerate(publicacao_elements, 1):
                            self.log(f"      🔍 Processando publicação {i}/{len(publicacao_elements)} da página {page_num}...")
                            
                            try:
                                # Clicar no link "Visualizar" para abrir o PDF
                                self.log(f"        🖱️ Clicando em 'Visualizar' do item {i}...")
                                
                                # Salvar a janela atual
                                janela_principal = driver.current_window_handle
                                
                                # Clicar no elemento (que vai abrir nova janela/aba)
                                if not self._safe_click(element):
                                    self.log(f"        ❌ Falha ao clicar no link. Tentando próximo...")
                                    continue
                                
                                time.sleep(3)
                                
                                # Verificar se nova janela foi aberta
                                todas_janelas = driver.window_handles
                                if len(todas_janelas) > 1:
                                    # Mudar para a nova janela
                                    for janela in todas_janelas:
                                        if janela != janela_principal:
                                            driver.switch_to.window(janela)
                                            break
                                    
                                    self.log(f"        📋 Nova janela aberta: {driver.current_url}")
                                    time.sleep(5)  # Aguardar carregamento completo
                                    
                                    # Procurar pelo frame que contém o PDF
                                    try:
                                        # Verificar se há frames na página
                                        frames = driver.find_elements(By.TAG_NAME, "frame")
                                        iframe_elements = driver.find_elements(By.TAG_NAME, "iframe")
                                        
                                        pdf_url = None
                                        
                                        # Tentar encontrar URL do PDF no HTML
                                        page_source = driver.page_source
                                        
                                        # Procurar por URLs de PDF no código fonte
                                        import re
                                        pdf_patterns = [
                                            r'src="([^"]*\.pdf[^"]*)"',
                                            r"src='([^']*\.pdf[^']*)'",
                                            r'href="([^"]*\.pdf[^"]*)"',
                                            r"href='([^']*\.pdf[^']*)'",
                                            r'(https?://[^"\s]*\.pdf[^"\s]*)',
                                            r'/cdje/getPaginaDoDiario\.do[^"]*'
                                        ]
                                        
                                        for pattern in pdf_patterns:
                                            matches = re.findall(pattern, page_source, re.IGNORECASE)
                                            if matches:
                                                for match in matches:
                                                    if 'getPaginaDoDiario.do' in match or '.pdf' in match.lower():
                                                        if not match.startswith('http'):
                                                            if match.startswith('/'):
                                                                pdf_url = f"https://dje.tjsp.jus.br{match}"
                                                            else:
                                                                pdf_url = f"https://dje.tjsp.jus.br/{match}"
                                                        else:
                                                            pdf_url = match
                                                        self.log(f"        📄 PDF URL encontrada: {pdf_url}")
                                                        break
                                            if pdf_url:
                                                break
                                    except Exception as e:
                                        self.log(f"        ⚠️ Erro ao buscar PDF no HTML: {e}")
                                        pdf_url = None
                                    
                                    # Se não encontrou URL direta, tentar navegar pelos frames
                                    if not pdf_url and frames:
                                        self.log(f"        🔍 Verificando {len(frames)} frames...")
                                        for frame_idx, frame in enumerate(frames):
                                            try:
                                                driver.switch_to.frame(frame)
                                                frame_source = driver.page_source
                                                
                                                # Procurar PDF no frame
                                                for pattern in pdf_patterns:
                                                    matches = re.findall(pattern, frame_source, re.IGNORECASE)
                                                    if matches:
                                                        for match in matches:
                                                            if 'getPaginaDoDiario.do' in match or '.pdf' in match.lower():
                                                                if not match.startswith('http'):
                                                                    pdf_url = f"https://dje.tjsp.jus.br{match}"
                                                                else:
                                                                    pdf_url = match
                                                                self.log(f"        📄 PDF encontrado no frame {frame_idx}: {pdf_url}")
                                                                break
                                                    if pdf_url:
                                                        break
                                                
                                                driver.switch_to.default_content()
                                                if pdf_url:
                                                    break
                                            except Exception as e:
                                                self.log(f"        ⚠️ Erro ao acessar frame {frame_idx}: {e}")
                                                driver.switch_to.default_content()
                                    
                                    # Extrair dados usando PDF ou HTML
                                    if pdf_url:
                                        self.log(f"        📥 Baixando e processando PDF: {pdf_url}")
                                        texto_pdf = self._download_pdf_text(pdf_url)
                                        if texto_pdf:
                                            publicacao_data = self._extrair_dados_do_texto(texto_pdf, pdf_url)
                                            self.log(f"        ✅ Dados extraídos do PDF")
                                        else:
                                            self.log(f"        ⚠️ Não foi possível extrair texto do PDF, usando HTML")
                                            publicacao_data = self._extrair_dados_do_texto(page_source, driver.current_url)
                                    else:
                                        self.log(f"        ⚠️ PDF não encontrado, usando HTML da página")
                                        publicacao_data = self._extrair_dados_do_texto(page_source, driver.current_url)
                                    
                                    if publicacao_data:
                                        all_publicacoes.append(publicacao_data)
                                        self.log(f"        ✅ Publicação processada: {publicacao_data.get('numero_processo', 'N/A')}")
                                        self.log(f"        📋 JSON: {publicacao_data}")
                                    else:
                                        self.log(f"        ⚠️ Não foi possível extrair dados desta publicação")
                                        
                            except Exception as e:
                                self.log(f"        ❌ Erro ao processar publicação {i}: {e}")
                                # Garantir que estamos na janela correta
                                try:
                                    todas_janelas = driver.window_handles
                                    if len(todas_janelas) > 1:
                                        for janela in todas_janelas[1:]:
                                            driver.switch_to.window(janela)
                                            driver.close()
                                        driver.switch_to.window(todas_janelas[0])
                                except Exception as cleanup_error:
                                    self.log(f"        ⚠️ Erro na limpeza: {cleanup_error}")
                                continue
                
                    # Tentar ir para a próxima página
                    self.log(f"    🔄 Procurando link para próxima página...")
                    try:
                        # Procurar por botão "Próximo" ou link de próxima página
                        next_page_found = False
                        
                        # Tentar encontrar link "Próximo" primeiro
                        try:
                            next_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Próximo') or contains(text(), '>')]")
                            onclick_attr = next_button.get_attribute('onclick')
                            self.log(f"    📄 Botão próximo encontrado: {onclick_attr}")
                            
                            # Clicar no botão próximo
                            if self._safe_click(next_button):
                                time.sleep(4)
                                page_num += 1
                                next_page_found = True
                                self.log(f"    📄 Navegou para página {page_num}")
                            else:
                                self.log("    ❌ Falha ao clicar no botão próximo")
                            
                        except Exception as e:
                            self.log(f"    ⚠️ Botão 'Próximo' não encontrado: {e}")
                        
                        # Se não encontrou botão próximo, tentar pelos números das páginas
                        if not next_page_found:
                            try:
                                # Procurar por link da próxima página (número)
                                next_page_num = page_num + 1
                                page_link = driver.find_element(By.XPATH, f"//a[contains(@onclick, 'trocaDePg({next_page_num})')]")
                                
                                self.log(f"    📄 Link da página {next_page_num} encontrado")
                                if self._safe_click(page_link):
                                    time.sleep(4)
                                    page_num = next_page_num
                                    next_page_found = True
                                    self.log(f"    📄 Navegou para página {page_num}")
                                else:
                                    self.log(f"    ❌ Falha ao clicar no link da página {next_page_num}")
                                
                            except Exception as e:
                                self.log(f"    ⚠️ Link da página {next_page_num} não encontrado: {e}")
                        
                        if not next_page_found:
                            self.log(f"    🏁 Não há mais páginas. Finalizada na página {page_num}")
                            break
                        
                    except Exception as e:
                        self.log(f"    ❌ Erro ao navegar para próxima página: {e}")
                        break
                
                except Exception as e:
                    self.log(f"    ❌ Erro ao processar página {page_num}: {e}")
                    break
            
            self.log(f"🎉 Extração concluída! Total de publicações extraídas: {len(all_publicacoes)}")
            
            # Log resumo final
            if all_publicacoes:
                self.log("📊 Resumo das publicações:")
                for i, pub in enumerate(all_publicacoes[:5], 1):  # Mostrar 5 primeiras
                    self.log(f"  {i}. {pub.get('numero_processo', 'N/A')} - {pub.get('autores', 'N/A')[:30]}...")
            
            return all_publicacoes

        except Exception as e:
            self.log(f"❌ Erro fatal durante a extração: {e}")
            return []

    def _extrair_dados_do_texto(self, texto: str, url_origem: str) -> Dict[str, Any]:
        """Extrai dados estruturados do texto (PDF ou HTML)"""
        try:
            # Extrair número do processo com padrões mais específicos
            numero_processo = self._extrair_numero_processo(texto)
            if not numero_processo:
                self.log("⚠️ Número do processo não encontrado no texto")
                return None
            
            # Extrair data de disponibilização
            data_disponibilizacao = self._extrair_data_disponibilizacao(texto)
            if not data_disponibilizacao:
                self.log("⚠️ Data de disponibilização não encontrada, usando data atual")
                data_disponibilizacao = datetime.now()
            
            # Extrair informações de RPV específicas
            autor_info = self._extrair_autor_rpv(texto)
            if not autor_info:
                self.log("⚠️ Autor não encontrado no texto")
                autor_info = "Autor não identificado"
            
            advogado_info = self._extrair_advogado_rpv(texto)
            if not advogado_info:
                self.log("⚠️ Advogado não encontrado no texto")
                advogado_info = "Advogado não identificado"
            
            # Extrair valores monetários específicos para RPV
            valores = self._extrair_valores_rpv(texto)
            
            # Log dos valores encontrados
            if any(valores.values()):
                self.log(f"💰 Valores encontrados: {valores}")
            else:
                self.log("⚠️ Nenhum valor monetário encontrado")
            
            # Verificar se é realmente uma RPV
            if not self._verificar_se_rpv(texto):
                self.log("⚠️ Texto não parece ser uma RPV")
                return None
            
            dados = {
                'numero_processo': numero_processo,
                'data_disponibilizacao': data_disponibilizacao,
                'autores': autor_info,
                'advogados': advogado_info,
                'conteudo_completo': texto[:2000] + '...' if len(texto) > 2000 else texto,
                'valor_principal_bruto': valores.get('bruto'),
                'valor_principal_liquido': valores.get('liquido'),
                'valor_juros_moratorios': valores.get('juros'),
                'honorarios_advocaticios': valores.get('honorarios'),
                'reu': 'Instituto Nacional do Seguro Social - INSS',
                'url_origem': url_origem
            }
            
            self.log(f"✅ Dados extraídos com sucesso do processo {numero_processo}")
            return dados
            
        except Exception as e:
            self.log(f"❌ Erro ao extrair dados do texto: {e}")
            return None

    def _verificar_se_rpv(self, texto: str) -> bool:
        """Verifica se o texto é realmente uma RPV"""
        texto_lower = texto.lower()
        
        # Termos que indicam RPV
        termos_rpv = [
            'rpv',
            'requisição de pequeno valor',
            'requisitório de pequeno valor',
            'requisição de pagamento',
            'ofício requisitório'
        ]
        
        # Termos que devem estar presentes
        termos_obrigatorios = [
            'inss',
            'instituto nacional',
            'seguro social'
        ]
        
        # Termos que indicam pagamento
        termos_pagamento = [
            'valor',
            'pagamento',
            'crédito',
            'depósito',
            'requisitado'
        ]
        
        # Verificar termos RPV (pelo menos 1)
        tem_rpv = any(termo in texto_lower for termo in termos_rpv)
        
        # Verificar termos obrigatórios (pelo menos 2)
        tem_obrigatorios = sum(1 for termo in termos_obrigatorios if termo in texto_lower) >= 2
        
        # Verificar termos de pagamento (pelo menos 1)
        tem_pagamento = any(termo in texto_lower for termo in termos_pagamento)
        
        # Verificar se tem número de processo
        tem_processo = bool(self._extrair_numero_processo(texto))
        
        # Verificar se tem algum valor monetário
        tem_valor = any(self._extrair_valores_rpv(texto).values())
        
        # Verificar se tem data
        tem_data = bool(self._extrair_data_disponibilizacao(texto))
        
        # Calcular pontuação
        pontos = 0
        if tem_rpv: pontos += 3
        if tem_obrigatorios: pontos += 2
        if tem_pagamento: pontos += 1
        if tem_processo: pontos += 2
        if tem_valor: pontos += 2
        if tem_data: pontos += 1
        
        # Logar resultado
        self.log(f"🔍 Análise do texto:")
        self.log(f"  - Termos RPV: {'✅' if tem_rpv else '❌'}")
        self.log(f"  - Termos obrigatórios: {'✅' if tem_obrigatorios else '❌'}")
        self.log(f"  - Termos pagamento: {'✅' if tem_pagamento else '❌'}")
        self.log(f"  - Número processo: {'✅' if tem_processo else '❌'}")
        self.log(f"  - Valor monetário: {'✅' if tem_valor else '❌'}")
        self.log(f"  - Data: {'✅' if tem_data else '❌'}")
        self.log(f"  📊 Pontuação total: {pontos}/11")
        
        # Retornar true se tiver pontuação mínima
        return pontos >= 7

    def _extrair_numero_processo(self, texto: str) -> str:
        """Extrai número do processo com padrões específicos"""
        # Padrão padrão: 0000000-00.0000.0.00.0000
        patterns = [
            r'\b\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}\b',
            r'\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b',
            r'Processo\s+n[ºo°\.]*\s*(\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4})',
            r'Proc\.*\s*(\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4})',
            r'Autos\s+n[ºo°\.]*\s*(\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto, re.IGNORECASE)
            if match:
                numero = match.group(1) if len(match.groups()) > 0 else match.group(0)
                # Validar formato
                if re.match(r'^\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}$', numero):
                    return numero
        return None

    def _extrair_data_disponibilizacao(self, texto: str) -> datetime:
        """Extrai data de disponibilização"""
        patterns = [
            r'(\d{2}/\d{2}/\d{4})',
            r'data[:\s]+(\d{2}/\d{2}/\d{4})',
            r'disponibiliza[^:]*:?\s*(\d{2}/\d{2}/\d{4})',
            r'publicad[oa]\s+em[:\s]*(\d{2}/\d{2}/\d{4})',
            r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto, re.IGNORECASE)
            if match:
                try:
                    if len(match.groups()) == 3:  # Formato "1 de janeiro de 2025"
                        dia, mes_nome, ano = match.groups()
                        meses = {'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
                               'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12}
                        mes = meses.get(mes_nome.lower())
                        if mes:
                            return datetime(int(ano), mes, int(dia))
                    else:
                        data_str = match.group(1).strip() if len(match.groups()) > 0 else match.group(0)
                        return datetime.strptime(data_str, "%d/%m/%Y")
                except:
                    continue
        return None

    def _extrair_autor_rpv(self, texto: str) -> str:
        """Extrai informações do autor em casos de RPV"""
        patterns = [
            r'(?:Requerente|Autor|Exequente|Beneficiário)[:\s]*([^,\n\r]+?)(?:\s+(?:CPF|RG|contra)|,|\n|\r|$)',
            r'RPV\s+em\s+favor\s+de[:\s]*([^,\n\r]+?)(?:\s+(?:CPF|RG|contra)|,|\n|\r|$)',
            r'beneficiário[:\s]*([^,\n\r]+?)(?:\s+(?:CPF|RG|contra)|,|\n|\r|$)',
            r'em\s+face\s+de[:\s]*([^,\n\r]+?)(?:\s+(?:CPF|RG|contra)|,|\n|\r|$)',
            r'(?:Requerente|Autor|Exequente|Beneficiário)[:\s]*([^,\n\r]+?)(?=\s+(?:CPF|RG|contra|x|versus|vs\.?|,|\n|\r|$))',
            r'(?<=\bde\s)([A-ZÇÁÉÍÓÚÂÊÎÔÛÃÕ][a-zçáéíóúâêîôûãõ]+(?:\s+[A-ZÇÁÉÍÓÚÂÊÎÔÛÃÕ][a-zçáéíóúâêîôûãõ]+)*)',
            r'(?<=\ba\s)([A-ZÇÁÉÍÓÚÂÊÎÔÛÃÕ][a-zçáéíóúâêîôûãõ]+(?:\s+[A-ZÇÁÉÍÓÚÂÊÎÔÛÃÕ][a-zçáéíóúâêîôûãõ]+)*)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, texto, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                autor = match.group(1).strip()
                # Limpar texto desnecessário
                autor = re.sub(r'\s+', ' ', autor)
                autor = re.sub(r'[,\.\:]$', '', autor)
                # Validar nome próprio
                if (len(autor.split()) >= 2 and  # Pelo menos nome e sobrenome
                    all(word.istitle() for word in autor.split()) and  # Todas palavras capitalizadas
                    not re.search(r'\d', autor) and  # Sem números
                    len(autor) > 5):  # Tamanho mínimo
                    return autor
        return None

    def _extrair_advogado_rpv(self, texto: str) -> str:
        """Extrai informações do advogado em casos de RPV"""
        patterns = [
            r'Advogad[oa][:\s]*([^(\n\r]+?)\s*\(OAB[:\s]*(\d+/[A-Z]{2})\)',
            r'Dr[aª]?\.\s*([^(\n\r]+?)\s*\(OAB[:\s]*(\d+/[A-Z]{2})\)',
            r'([A-ZÁÊÇ][a-záêçõã]+(?:\s+[A-ZÁÊÇ][a-záêçõã]+)*)\s*\(OAB[:\s]*(\d+/[A-Z]{2})\)',
            r'representad[oa]\s+por[:\s]*([^(\n\r]+?)\s*\(OAB[:\s]*(\d+/[A-Z]{2})\)',
            r'Advogad[oa][:\s]*([^(\n\r]+?)\s*OAB[:\s]*(\d+/[A-Z]{2})',
            r'Dr[aª]?\.\s*([^(\n\r]+?)\s*OAB[:\s]*(\d+/[A-Z]{2})',
            r'([A-ZÁÊÇ][a-záêçõã]+(?:\s+[A-ZÁÊÇ][a-záêçõã]+)*)\s*OAB[:\s]*(\d+/[A-Z]{2})'
        ]
        
        advogados = []
        for pattern in patterns:
            matches = re.finditer(pattern, texto, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                nome = match.group(1).strip()
                oab = match.group(2).strip() if len(match.groups()) > 1 else ''
                # Limpar nome
                nome = re.sub(r'\s+', ' ', nome)
                nome = re.sub(r'[,\.\:]$', '', nome)
                # Validar nome próprio
                if (len(nome.split()) >= 2 and  # Pelo menos nome e sobrenome
                    all(word.istitle() for word in nome.split()) and  # Todas palavras capitalizadas
                    not re.search(r'\d', nome) and  # Sem números
                    len(nome) > 5):  # Tamanho mínimo
                    advogado_info = f"{nome} (OAB: {oab})" if oab else nome
                    if advogado_info not in advogados:
                        advogados.append(advogado_info)
        
        return ', '.join(advogados) if advogados else None

    def _extrair_valores_rpv(self, texto: str) -> Dict[str, float]:
        """Extrai valores monetários específicos para RPV"""
        valores = {'bruto': None, 'liquido': None, 'juros': None, 'honorarios': None}
        
        # Padrões para valores monetários
        patterns = {
            'bruto': [
                r'valor\s+principal\s+bruto[:\s]*R?\$?\s*([\d.,]+)',
                r'principal\s+bruto[:\s]*R?\$?\s*([\d.,]+)',
                r'valor\s+bruto[:\s]*R?\$?\s*([\d.,]+)',
                r'montante\s+bruto[:\s]*R?\$?\s*([\d.,]+)',
                r'valor\s+total\s+bruto[:\s]*R?\$?\s*([\d.,]+)',
                r'total\s+bruto[:\s]*R?\$?\s*([\d.,]+)',
                r'valor\s+da\s+execução[:\s]*R?\$?\s*([\d.,]+)',
                r'valor\s+executado[:\s]*R?\$?\s*([\d.,]+)'
            ],
            'liquido': [
                r'valor\s+principal\s+líquido[:\s]*R?\$?\s*([\d.,]+)',
                r'principal\s+líquido[:\s]*R?\$?\s*([\d.,]+)',
                r'valor\s+líquido[:\s]*R?\$?\s*([\d.,]+)',
                r'montante\s+líquido[:\s]*R?\$?\s*([\d.,]+)',
                r'valor\s+total\s+líquido[:\s]*R?\$?\s*([\d.,]+)',
                r'total\s+líquido[:\s]*R?\$?\s*([\d.,]+)',
                r'valor\s+final[:\s]*R?\$?\s*([\d.,]+)',
                r'valor\s+devido[:\s]*R?\$?\s*([\d.,]+)'
            ],
            'juros': [
                r'juros\s+moratórios[:\s]*R?\$?\s*([\d.,]+)',
                r'juros[:\s]*R?\$?\s*([\d.,]+)',
                r'moratórios[:\s]*R?\$?\s*([\d.,]+)',
                r'correção\s+monetária[:\s]*R?\$?\s*([\d.,]+)',
                r'juros\s+de\s+mora[:\s]*R?\$?\s*([\d.,]+)',
                r'juros\s+legais[:\s]*R?\$?\s*([\d.,]+)',
                r'atualização\s+monetária[:\s]*R?\$?\s*([\d.,]+)',
                r'valor\s+dos\s+juros[:\s]*R?\$?\s*([\d.,]+)'
            ],
            'honorarios': [
                r'honorários\s+advocatícios[:\s]*R?\$?\s*([\d.,]+)',
                r'honorários[:\s]*R?\$?\s*([\d.,]+)',
                r'advocatícios[:\s]*R?\$?\s*([\d.,]+)',
                r'sucumbência[:\s]*R?\$?\s*([\d.,]+)',
                r'honorários\s+sucumbenciais[:\s]*R?\$?\s*([\d.,]+)',
                r'verba\s+honorária[:\s]*R?\$?\s*([\d.,]+)',
                r'honorários\s+contratuais[:\s]*R?\$?\s*([\d.,]+)',
                r'honorários\s+de\s+sucumbência[:\s]*R?\$?\s*([\d.,]+)'
            ]
        }
        
        for tipo, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, texto, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    try:
                        valor_str = match.group(1).replace('.', '').replace(',', '.')
                        valor = float(valor_str)
                        # Validar valor
                        if 0 < valor < 1000000:  # Entre R$ 0,01 e R$ 1.000.000,00
                            valores[tipo] = valor
                            break  # Parar no primeiro valor válido para cada tipo
                    except ValueError:
                        continue
        
        return valores

    def take_screenshot(self, filename: str = None):
        """Tira screenshot da página atual"""
        driver = self.get_driver()
        if not driver:
            print("❌ Driver não inicializado")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraping_screenshot_{timestamp}.png"
        
        try:
            driver.save_screenshot(filename)
            print(f"📸 Screenshot salva: {filename}")
        except Exception as e:
            print(f"❌ Erro ao salvar screenshot: {e}")

    def get_page_info(self):
        """Mostra informações da página atual"""
        driver = self.get_driver()
        if not driver:
            print("❌ Driver não inicializado")
            return
        
        print(f"🌐 URL atual: {driver.current_url}")
        print(f"📄 Título: {driver.title}")
        print(f"🖥️ Tamanho da janela: {driver.get_window_size()}")

    def close(self):
        """Fecha o driver e limpa recursos"""
        if self.driver:
            try:
                # Fechar todas as janelas
                for handle in self.driver.window_handles:
                    self.driver.switch_to.window(handle)
                    self.driver.close()
            except:
                pass
            
            try:
                # Encerrar driver
                self.driver.quit()
            except:
                pass
            
            # Limpar referência
            self.driver = None
            self.wait = None
            
            self.log("✅ Driver fechado e recursos limpos")

    @classmethod
    def reset_instance(cls):
        """Reseta a instância singleton (útil em caso de erro)"""
        with cls._lock:
            if cls._instance:
                try:
                    if hasattr(cls._instance, 'driver') and cls._instance.driver:
                        cls._instance.driver.quit()
                except:
                    pass
            cls._instance = None
            print("🔄 Instância singleton resetada")

    def _wait_for_page_load(self, timeout=30):
        """Aguarda o carregamento completo da página"""
        try:
            # Aguardar documento estar pronto
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Aguardar jQuery terminar (se existir)
            try:
                WebDriverWait(self.driver, 5).until(
                    lambda driver: driver.execute_script("return typeof jQuery === 'undefined' || jQuery.active == 0")
                )
            except:
                pass  # jQuery pode não existir
            
            # Aguardar elementos dinâmicos
            try:
                # Aguardar div de resultados
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "divResultadosInferior"))
                )
                
                # Aguardar links de publicação
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@onclick, 'consultaSimples.do')]"))
                )
                
                # Aguardar botões de navegação
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Próximo') or contains(text(), '>')]"))
                )
            except:
                pass  # Elementos podem não existir
            
            # Aguardar um pouco mais
            time.sleep(3)
            self.log("    ✅ Página carregada completamente")
            
        except Exception as e:
            self.log(f"    ⚠️ Timeout aguardando carregamento da página: {e}")

    def _wait_for_element_ready(self, by, value, timeout=30):
        """Aguarda elemento estar visível, habilitado e pronto para interação"""
        try:
            # Aguardar elemento estar presente
            element = self.wait.until(EC.presence_of_element_located((by, value)))
            
            # Aguardar estar visível
            self.wait.until(EC.visibility_of_element_located((by, value)))
            
            # Aguardar estar clicável
            element = self.wait.until(EC.element_to_be_clickable((by, value)))
            
            # Verificação adicional de estado usando JavaScript
            for attempt in range(10):  # Aumentei para 10 tentativas
                try:
                    # Usar JavaScript para verificar se o elemento está realmente pronto
                    is_ready = self.driver.execute_script("""
                        var element = arguments[0];
                        return element && 
                               element.offsetWidth > 0 && 
                               element.offsetHeight > 0 && 
                               !element.disabled && 
                               element.style.display !== 'none' &&
                               element.style.visibility !== 'hidden';
                    """, element)
                    
                    if is_ready:
                        # Scroll para o elemento usando JavaScript
                        self.driver.execute_script("""
                            arguments[0].scrollIntoView({
                                behavior: 'smooth', 
                                block: 'center',
                                inline: 'center'
                            });
                        """, element)
                        time.sleep(1)  # Aguardar scroll completar
                        
                        # Verificar novamente após scroll
                        element = self.driver.find_element(by, value)
                        return element
                        
                except Exception as e:
                    self.log(f"    ⚠️ Tentativa {attempt + 1}: Elemento não pronto: {e}")
                    time.sleep(1)
                    # Re-localizar elemento
                    try:
                        element = self.driver.find_element(by, value)
                    except:
                        element = self.wait.until(EC.presence_of_element_located((by, value)))
            
            self.log(f"    ✅ Elemento {value} pronto para interação")
            return element
            
        except Exception as e:
            self.log(f"    ❌ Erro ao aguardar elemento {value}: {e}")
            raise

    def _safe_click(self, element, retries=3):
        """Tenta clicar em um elemento de forma segura"""
        for i in range(retries):
            try:
                # Scroll para o elemento
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(1)
                
                # Tentar click normal
                try:
                    element.click()
                    return True
                except:
                    pass
                
                # Tentar click via JavaScript
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                except:
                    pass
                
                # Tentar simular click via Actions
                try:
                    actions = ActionChains(self.driver)
                    actions.move_to_element(element).click().perform()
                    return True
                except:
                    pass
                
                if i < retries - 1:
                    time.sleep(2)  # Aguardar antes da próxima tentativa
                    
            except Exception as e:
                if i == retries - 1:
                    self.log(f"    ❌ Falha ao clicar no elemento após {retries} tentativas: {e}")
                    return False
                time.sleep(2)
        
        return False

    def _safe_send_keys(self, element, text, clear_first=True):
        """Envia texto de forma segura"""
        try:
            # Scroll para o elemento
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(1)
            
            # Limpar campo
            if clear_first:
                try:
                    element.clear()
                except:
                    try:
                        self.driver.execute_script("arguments[0].value = '';", element)
                    except:
                        pass
            
            # Tentar enviar texto normalmente
            try:
                element.send_keys(text)
                return True
            except:
                pass
            
            # Tentar via JavaScript
            try:
                self.driver.execute_script(f"arguments[0].value = '{text}';", element)
                return True
            except:
                pass
            
            # Tentar via Actions
            try:
                actions = ActionChains(self.driver)
                actions.move_to_element(element)
                actions.click()
                actions.send_keys(text)
                actions.perform()
                return True
            except:
                pass
            
            return False
            
        except Exception as e:
            self.log(f"    ❌ Falha ao enviar texto para o elemento: {e}")
            return False

    def _download_pdf_text(self, pdf_url: str) -> str:
        """Baixa e extrai texto do PDF"""
        try:
            # Tentar até 3 vezes
            for attempt in range(3):
                try:
                    r = requests.get(pdf_url, timeout=30)
                    if r.status_code == 200:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            tmp.write(r.content)
                            tmp_path = tmp.name
                        
                        text = ""
                        with pdfplumber.open(tmp_path) as pdf:
                            pages = [p.extract_text() or "" for p in pdf.pages]
                            text = "\n".join(pages)
                        
                        os.unlink(tmp_path)
                        
                        if text.strip():
                            return text
                        else:
                            self.log(f"    ⚠️ PDF baixado mas texto vazio (tentativa {attempt + 1})")
                    else:
                        self.log(f"    ⚠️ Erro ao baixar PDF: Status {r.status_code} (tentativa {attempt + 1})")
                    
                    if attempt < 2:
                        time.sleep(5)  # Aguardar antes da próxima tentativa
                        
                except Exception as e:
                    self.log(f"    ⚠️ Erro ao processar PDF: {e} (tentativa {attempt + 1})")
                    if attempt < 2:
                        time.sleep(5)
            
            return ""
            
        except Exception as e:
            self.log(f"    ❌ Erro fatal ao baixar PDF: {e}")
            return ""

    def _extrair_dados_pagina_individual(self, driver) -> Dict[str, Any]:
        """Extrai dados detalhados de uma página individual de publicação"""
        try:
            # Aguardar a página carregar
            time.sleep(3)
            
            html = driver.page_source
            pdf_url = self._find_pdf_url(html)
            
            # Se encontrou PDF, baixar e extrair texto
            if pdf_url:
                print(f"        📥 Baixando PDF: {pdf_url}")
                texto_pdf = self._download_pdf_text(pdf_url)
                if texto_pdf:
                    return self._extrair_dados_do_texto(texto_pdf, driver.current_url)
                else:
                    print(f"        ⚠️ Falha ao extrair texto do PDF, usando HTML")
            
            # Se não há PDF ou falhou, usar HTML
            print(f"        📄 Extraindo dados do HTML")
            return self._extrair_dados_do_texto(html, driver.current_url)
            
        except Exception as e:
            print(f"        ❌ Erro ao extrair dados da página individual: {e}")
            return None 