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
                    logging.basicConfig(level=logging.INFO)
                    # NÃO inicializar o driver aqui
                    self.initialized = True

    def get_driver(self):
        """Obtém o driver, inicializando-o se necessário."""
        with self._lock:
            if self.driver is None:
                self._initialize_driver()
            
            # Verificar se o driver está vivo
            try:
                # Uma operação simples como pegar a URL atual pode verificar a conexão
                _ = self.driver.current_url
            except Exception as e:
                print(f"⚠️ Driver não responsivo ({e}), tentando reiniciar...")
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
                self._initialize_driver()

            return self.driver

    def _get_chrome_options(self):
        """Configurações do Chrome - com opção visual para debug"""
        chrome_options = Options()
        
        # Configurar display virtual se disponível
        if 'DISPLAY' not in os.environ:
            os.environ['DISPLAY'] = ':99'
        
        # Criar diretório de dados único para esta sessão
        user_data_dir = f"/tmp/chrome_data_{uuid.uuid4().hex[:8]}"
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # MODO VISUAL: Comentar --headless para ver o Chrome
        if not self.visual_mode:
            chrome_options.add_argument("--headless")
        else:
            print("🖥️ MODO VISUAL ATIVADO - Chrome será visível!")
            # Para modo visual, usar configurações mais simples
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--display=:99")
            return chrome_options
        
        # Configurações essenciais para container
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=4096")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--aggressive-cache-discard")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--display=:99")
        chrome_options.add_argument("--remote-debugging-port=0")  # Porta aleatória
        chrome_options.add_argument("--disable-crash-reporter")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-in-process-stack-traces")
        chrome_options.add_argument("--disable-background-mode")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-sync")
        
        # NOVO: Configurações para melhor estabilidade
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-save-password-bubble")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor,VizHitTestSurfaceLayer")
        chrome_options.add_argument("--force-device-scale-factor=1")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-component-update")
        chrome_options.add_argument("--disable-domain-reliability")
        chrome_options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
        chrome_options.add_argument("--disable-hang-monitor")
        chrome_options.add_argument("--disable-prompt-on-repost")
        chrome_options.add_argument("--disable-web-resources")
        chrome_options.add_argument("--enable-automation")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--password-store=basic")
        chrome_options.add_argument("--use-mock-keychain")
        
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option('detach', False)  # Não destacar
        
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        return chrome_options

    def _initialize_driver(self):
        """Inicializa o driver com configurações de debug"""
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

    def extrair_publicacoes_debug(self, data_inicio: datetime, data_fim: datetime, pause_between_steps: bool = True) -> List[Dict[str, Any]]:
        """Versão debug com navegação completa em cada resultado e paginação"""
        driver = self.get_driver()
        if not driver:
            logging.error("❌ Driver não está operacional. Abortando extração.")
            return []

        print(f"🕷️ Iniciando extração COMPLETA de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
        
        try:
            # Etapa 1: Acessar o site
            print("📍 Etapa 1: Acessando o site do DJE...")
            driver.get(self.base_url)
            
            # Aguardar carregamento completo
            print("  ⏳ Aguardando carregamento completo da página...")
            self._wait_for_page_load()
            
            if pause_between_steps and self.visual_mode:
                input("⏸️ Pressione Enter para continuar para o preenchimento do formulário...")

            # Etapa 2: Preencher período de datas (OPCIONAL - comentar para teste)
            print("📍 Etapa 2: Preenchendo período de datas...")
            
            # TESTE: Comentar esta seção para fazer busca sem filtro de data
            # try:
            #     # Aguardar campo data início
            #     print("  📅 Preenchendo data de início...")
            #     data_inicio_field = self._wait_for_element_ready(By.ID, "dataInicio")
            #     data_inicio_str = data_inicio.strftime("%d%m%Y")
            #     self._safe_send_keys(data_inicio_field, data_inicio_str)
            #
            #     # Aguardar campo data fim
            #     print("  📅 Preenchendo data de fim...")
            #     data_fim_field = self._wait_for_element_ready(By.ID, "dataFim")
            #     data_fim_str = data_fim.strftime("%d%m%Y")
            #     self._safe_send_keys(data_fim_field, data_fim_str)
            #
            #     print(f"  ✅ Período configurado: {data_inicio_str} a {data_fim_str}")
            # except Exception as e:
            #     print(f"  ⚠️ Erro ao configurar datas: {e}")
            
            # TESTE TEMPORÁRIO: Pular configuração de data para ver se encontra resultados gerais
            print("  🚧 TESTE: Pulando configuração de data para busca geral...")
            time.sleep(2)

            # Etapa 3: Preencher formulário
            print("📍 Etapa 3: Preenchendo formulário de pesquisa...")
            
            # Aguardar campo data início estar disponível e interagível
            print("  📅 Aguardando campo de data início...")
            try:
                data_inicio_field = self._wait_for_element_ready(By.ID, "dataInicio")
                data_inicio_str = data_inicio.strftime("%d%m%Y")
                self._safe_send_keys(data_inicio_field, data_inicio_str)
                print(f"  ✅ Data início preenchida: {data_inicio_str}")
            except Exception as e:
                print(f"  ⚠️ Erro ao preencher data início: {e}")

            # Aguardar campo data fim estar disponível e interagível  
            print("  📅 Aguardando campo de data fim...")
            try:
                data_fim_field = self._wait_for_element_ready(By.ID, "dataFim")
                data_fim_str = data_fim.strftime("%d%m%Y")
                self._safe_send_keys(data_fim_field, data_fim_str)
                print(f"  ✅ Data fim preenchida: {data_fim_str}")
            except Exception as e:
                print(f"  ⚠️ Erro ao preencher data fim: {e}")

            # Aguardar select caderno estar disponível
            print("  📂 Aguardando select caderno...")
            select_caderno_element = self._wait_for_element_ready(By.NAME, "dadosConsulta.cdCaderno")
            
            # Usar JavaScript para selecionar o valor do select
            try:
                select_caderno = Select(select_caderno_element)
                select_caderno.select_by_value("-11")
                print("  ✅ Caderno selecionado via Selenium")
            except:
                print("  ⚠️ Selenium falhou, usando JavaScript para select")
                driver.execute_script("""
                    var select = arguments[0];
                    select.value = '-11';
                    select.dispatchEvent(new Event('change', {bubbles: true}));
                """, select_caderno_element)
                print("  ✅ Caderno selecionado via JavaScript")

            # Aguardar campo de busca estar disponível
            print("  🔍 Aguardando campo de busca...")
            search_box = self._wait_for_element_ready(By.ID, "procura")
            self._safe_send_keys(search_box, '"RPV" e "pagamento pelo INSS"')
            
            if pause_between_steps and self.visual_mode:
                input("⏸️ Pressione Enter para submeter o formulário...")
            
            # Etapa 4: Submeter formulário
            print("📍 Etapa 4: Submetendo formulário...")
            
            # Aguardar botão submit estar disponível
            print("  🔘 Aguardando botão submit...")
            submit_button = self._wait_for_element_ready(By.CSS_SELECTOR, "form[name='consultaAvancadaForm'] input[type='submit']")
            self._safe_click(submit_button)

            print("⏳ Aguardando resultados...")
            time.sleep(8)
            
            if pause_between_steps and self.visual_mode:
                input("⏸️ Pressione Enter para processar os resultados...")

            # Etapa 5: Processar TODAS as páginas de resultados
            print("📍 Etapa 5: Processando TODAS as páginas de resultados...")
            all_publicacoes = []
            page_num = 1
            
            while True:
                print(f"  📄 Processando página {page_num}...")
                
                try:
                    # Aguardar div de resultados
                    print(f"    ⏳ Aguardando div de resultados da página {page_num}...")
                    self.wait.until(EC.presence_of_element_located((By.ID, "divResultadosInferior")))
                    time.sleep(3)
                    
                    # Verificar se há erro na página
                    page_source = driver.page_source.lower()
                    if "erro" in page_source or "error" in page_source:
                        print(f"    ⚠️ Possível erro detectado na página {page_num}")
                    
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    # DEBUG: Verificar conteúdo da página
                    print(f"    🔍 URL atual: {driver.current_url}")
                    print(f"    🔍 Título da página: {driver.title}")
                    
                    # Verificar se há div de resultados
                    div_resultados = soup.find('div', id='divResultadosInferior')
                    if div_resultados:
                        print(f"    📋 Div divResultadosInferior encontrado com {len(div_resultados.get_text())} caracteres")
                        
                        # Verificar se há texto "nenhum resultado"  
                        texto_resultados = div_resultados.get_text().lower()
                        if "nenhum" in texto_resultados or "não foram encontrados" in texto_resultados or "sem resultados" in texto_resultados:
                            print(f"    ℹ️ Mensagem de nenhum resultado detectada na página {page_num}")
                            if page_num == 1:
                                print("    ℹ️ Nenhuma publicação encontrada para os critérios definidos.")
                                break
                        
                        # Verificar quantidade de resultados
                        total_text = driver.page_source
                        if "Resultados 1 a" in total_text:
                            import re
                            match = re.search(r'Resultados \d+ a \d+ de (\d+)', total_text)
                            if match:
                                total = int(match.group(1))
                                print(f"    📊 Total de resultados encontrados: {total}")
                    else:
                        print(f"    ⚠️ Div divResultadosInferior não encontrado na página {page_num}")
                    
                    # Buscar por elementos de publicação usando a estrutura correta
                    print(f"    🔍 Procurando links com onclick que contém consultaSimples.do...")
                    
                    # NOVA ABORDAGEM: Primeiro buscar TODOS os links onclick na página
                    all_onclick_links = driver.find_elements(By.XPATH, "//a[@onclick]")
                    print(f"    📋 Total de links com onclick na página: {len(all_onclick_links)}")
                    
                    # Filtrar apenas os que contém consultaSimples.do
                    publicacao_elements = []
                    for link in all_onclick_links:
                        onclick_attr = link.get_attribute('onclick')
                        if onclick_attr and 'consultaSimples.do' in onclick_attr:
                            publicacao_elements.append(link)
                            print(f"      🔗 Link encontrado: {onclick_attr[:100]}...")
                    
                    # Se ainda não encontrou, tentar com seletor mais amplo
                    if not publicacao_elements:
                        # Buscar qualquer link que mencione consultaSimples
                        broader_links = driver.find_elements(By.XPATH, "//*[contains(@onclick, 'consultaSimples')]")
                        print(f"    📋 Busca mais ampla encontrou {len(broader_links)} elementos")
                        
                        for link in broader_links:
                            onclick_attr = link.get_attribute('onclick')
                            print(f"      🔗 Elemento broader: {onclick_attr[:100]}...")
                            if 'consultaSimples.do' in onclick_attr:
                                publicacao_elements.append(link)
                    
                    if not publicacao_elements and page_num == 1:
                        print("    ℹ️ Nenhuma publicação encontrada para os critérios definidos.")
                        break
                    elif not publicacao_elements:
                        print(f"    ℹ️ Fim dos resultados na página {page_num}")
                        break
                    else:
                        print(f"    📋 Processando {len(publicacao_elements)} publicações na página {page_num}")
                        
                        # Processar cada elemento de publicação
                        for i, element in enumerate(publicacao_elements, 1):
                            print(f"      🔍 Processando publicação {i}/{len(publicacao_elements)} da página {page_num}...")
                            
                            try:
                                # Clicar no link "Visualizar" para abrir o PDF
                                print(f"        🖱️ Clicando em 'Visualizar' do item {i}...")
                                
                                # Salvar a janela atual
                                janela_principal = driver.current_window_handle
                                
                                # Clicar no elemento (que vai abrir nova janela/aba)
                                driver.execute_script("arguments[0].click();", element)
                                time.sleep(3)
                                
                                # Verificar se nova janela foi aberta
                                todas_janelas = driver.window_handles
                                if len(todas_janelas) > 1:
                                    # Mudar para a nova janela
                                    for janela in todas_janelas:
                                        if janela != janela_principal:
                                            driver.switch_to.window(janela)
                                            break
                                    
                                    print(f"        📋 Nova janela aberta: {driver.current_url}")
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
                                                        print(f"        📄 PDF URL encontrada: {pdf_url}")
                                                        break
                                            if pdf_url:
                                                break
                                        
                                        # Se não encontrou URL direta, tentar navegar pelos frames
                                        if not pdf_url and frames:
                                            print(f"        🔍 Verificando {len(frames)} frames...")
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
                                                                    print(f"        📄 PDF encontrado no frame {frame_idx}: {pdf_url}")
                                                                    break
                                                        if pdf_url:
                                                            break
                                                    
                                                    driver.switch_to.default_content()
                                                    if pdf_url:
                                                        break
                                                except Exception as e:
                                                    print(f"        ⚠️ Erro ao acessar frame {frame_idx}: {e}")
                                                    driver.switch_to.default_content()
                                        
                                        # Extrair dados usando PDF ou HTML
                                        if pdf_url:
                                            print(f"        📥 Baixando e processando PDF: {pdf_url}")
                                            texto_pdf = self._download_pdf_text(pdf_url)
                                            if texto_pdf:
                                                publicacao_data = self._extrair_dados_do_texto(texto_pdf, pdf_url)
                                                print(f"        ✅ Dados extraídos do PDF")
                                            else:
                                                print(f"        ⚠️ Não foi possível extrair texto do PDF, usando HTML")
                                                publicacao_data = self._extrair_dados_do_texto(page_source, driver.current_url)
                                        else:
                                            print(f"        ⚠️ PDF não encontrado, usando HTML da página")
                                            publicacao_data = self._extrair_dados_do_texto(page_source, driver.current_url)
                                        
                                        if publicacao_data:
                                            all_publicacoes.append(publicacao_data)
                                            print(f"        ✅ Publicação processada: {publicacao_data.get('numero_processo', 'N/A')}")
                                            print(f"        📋 JSON: {publicacao_data}")
                                        else:
                                            print(f"        ⚠️ Não foi possível extrair dados desta publicação")
                                            
                                    except Exception as e:
                                        print(f"        ❌ Erro ao processar PDF/conteúdo: {e}")
                                    
                                    # Fechar a janela atual e voltar para a principal
                                    driver.close()
                                    driver.switch_to.window(janela_principal)
                                    time.sleep(2)
                                    
                                else:
                                    print(f"        ⚠️ Nova janela não foi aberta para item {i}")
                                    
                            except Exception as e:
                                print(f"        ❌ Erro ao processar publicação {i}: {e}")
                                # Garantir que estamos na janela correta
                                try:
                                    todas_janelas = driver.window_handles
                                    if len(todas_janelas) > 1:
                                        for janela in todas_janelas[1:]:
                                            driver.switch_to.window(janela)
                                            driver.close()
                                        driver.switch_to.window(todas_janelas[0])
                                except Exception as cleanup_error:
                                    print(f"        ⚠️ Erro na limpeza: {cleanup_error}")
                                continue
                    
                    # Tentar ir para a próxima página
                    print(f"    🔄 Procurando link para próxima página...")
                    try:
                        # Procurar por botão "Próximo" ou link de próxima página
                        next_page_found = False
                        
                        # Tentar encontrar link "Próximo" primeiro
                        try:
                            next_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Próximo') or contains(text(), '>')]")
                            onclick_attr = next_button.get_attribute('onclick')
                            print(f"    📄 Botão próximo encontrado: {onclick_attr}")
                            
                            # Clicar no botão próximo
                            driver.execute_script("arguments[0].click();", next_button)
                            time.sleep(4)
                            page_num += 1
                            next_page_found = True
                            print(f"    📄 Navegou para página {page_num}")
                            
                        except Exception as e:
                            print(f"    ⚠️ Botão 'Próximo' não encontrado: {e}")
                        
                        # Se não encontrou botão próximo, tentar pelos números das páginas
                        if not next_page_found:
                            try:
                                # Procurar por link da próxima página (número)
                                next_page_num = page_num + 1
                                page_link = driver.find_element(By.XPATH, f"//a[contains(@onclick, 'trocaDePg({next_page_num})')]")
                                
                                print(f"    📄 Link da página {next_page_num} encontrado")
                                driver.execute_script("arguments[0].click();", page_link)
                                time.sleep(4)
                                page_num = next_page_num
                                next_page_found = True
                                print(f"    📄 Navegou para página {page_num}")
                                
                            except Exception as e:
                                print(f"    ⚠️ Link da página {next_page_num} não encontrado: {e}")
                        
                        if not next_page_found:
                            print(f"    🏁 Não há mais páginas. Finalizada na página {page_num}")
                            break
                        
                    except Exception as e:
                        print(f"    ❌ Erro ao navegar para próxima página: {e}")
                        break
                
                except Exception as e:
                    print(f"    ❌ Erro ao processar página {page_num}: {e}")
                    break
            
            print(f"🎉 Extração concluída! Total de publicações extraídas: {len(all_publicacoes)}")
            
            # Log resumo final
            if all_publicacoes:
                print("📊 Resumo das publicações:")
                for i, pub in enumerate(all_publicacoes[:5], 1):  # Mostrar 5 primeiras
                    print(f"  {i}. {pub.get('numero_processo', 'N/A')} - {pub.get('autores', 'N/A')[:30]}...")
            
            return all_publicacoes

        except Exception as e:
            print(f"❌ Erro fatal durante a extração: {e}")
            return []

    def _extrair_dados_do_texto(self, texto: str, url_origem: str) -> Dict[str, Any]:
        """Extrai dados estruturados do texto (PDF ou HTML)"""
        try:
            # Extrair número do processo com padrões mais específicos
            numero_processo = self._extrair_numero_processo(texto)
            
            # Extrair data de disponibilização
            data_disponibilizacao = self._extrair_data_disponibilizacao(texto)
            
            # Extrair informações de RPV específicas
            autor_info = self._extrair_autor_rpv(texto)
            advogado_info = self._extrair_advogado_rpv(texto) 
            
            # Extrair valores monetários específicos para RPV
            valores = self._extrair_valores_rpv(texto)
            
            return {
                'numero_processo': numero_processo or 'Não identificado',
                'data_disponibilizacao': data_disponibilizacao,
                'autores': autor_info or 'Não identificado', 
                'advogados': advogado_info or 'Não identificado',
                'conteudo_completo': texto[:2000] + '...' if len(texto) > 2000 else texto,  # Limitar tamanho
                'valor_principal_bruto': valores.get('bruto'),
                'valor_principal_liquido': valores.get('liquido'),
                'valor_juros_moratorios': valores.get('juros'),
                'honorarios_advocaticios': valores.get('honorarios'),
                'reu': 'Instituto Nacional do Seguro Social - INSS',  # Sempre INSS conforme solicitado
                'url_origem': url_origem
            }
            
        except Exception as e:
            print(f"❌ Erro ao extrair dados do texto: {e}")
            return None

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
                return match.group(1) if len(match.groups()) > 0 else match.group(0)
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
                        data_str = match.group(1) if len(match.groups()) > 0 else match.group(0)
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
            r'em\s+face\s+de[:\s]*([^,\n\r]+?)(?:\s+(?:CPF|RG|contra)|,|\n|\r|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto, re.IGNORECASE)
            if match:
                autor = match.group(1).strip()
                # Limpar texto desnecessário
                autor = re.sub(r'\s+', ' ', autor)
                autor = re.sub(r'[,\.\:]$', '', autor)
                if len(autor) > 3 and not re.match(r'^\d+$', autor):  # Evitar números puros
                    return autor
        return None

    def _extrair_advogado_rpv(self, texto: str) -> str:
        """Extrai informações do advogado em casos de RPV"""
        patterns = [
            r'Advogad[oa][:\s]*([^(\n\r]+?)\s*\(OAB[:\s]*(\d+/[A-Z]{2})\)',
            r'Dr[aª]?\.\s*([^(\n\r]+?)\s*\(OAB[:\s]*(\d+/[A-Z]{2})\)',
            r'([A-ZÁÊÇ][a-záêçõã]+(?:\s+[A-ZÁÊÇ][a-záêçõã]+)*)\s*\(OAB[:\s]*(\d+/[A-Z]{2})\)',
            r'representad[oa]\s+por[:\s]*([^(\n\r]+?)\s*\(OAB[:\s]*(\d+/[A-Z]{2})\)'
        ]
        
        advogados = []
        for pattern in patterns:
            matches = re.finditer(pattern, texto, re.IGNORECASE)
            for match in matches:
                nome = match.group(1).strip()
                oab = match.group(2).strip() if len(match.groups()) > 1 else ''
                # Limpar nome
                nome = re.sub(r'\s+', ' ', nome)
                nome = re.sub(r'[,\.\:]$', '', nome)
                if len(nome) > 3:
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
                r'montante\s+bruto[:\s]*R?\$?\s*([\d.,]+)'
            ],
            'liquido': [
                r'valor\s+principal\s+líquido[:\s]*R?\$?\s*([\d.,]+)',
                r'principal\s+líquido[:\s]*R?\$?\s*([\d.,]+)',
                r'valor\s+líquido[:\s]*R?\$?\s*([\d.,]+)',
                r'montante\s+líquido[:\s]*R?\$?\s*([\d.,]+)'
            ],
            'juros': [
                r'juros\s+moratórios[:\s]*R?\$?\s*([\d.,]+)',
                r'juros[:\s]*R?\$?\s*([\d.,]+)',
                r'moratórios[:\s]*R?\$?\s*([\d.,]+)',
                r'correção\s+monetária[:\s]*R?\$?\s*([\d.,]+)'
            ],
            'honorarios': [
                r'honorários\s+advocatícios[:\s]*R?\$?\s*([\d.,]+)',
                r'honorários[:\s]*R?\$?\s*([\d.,]+)',
                r'advocatícios[:\s]*R?\$?\s*([\d.,]+)',
                r'sucumbência[:\s]*R?\$?\s*([\d.,]+)'
            ]
        }
        
        for tipo, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, texto, re.IGNORECASE)
                if match:
                    try:
                        valor_str = match.group(1).replace('.', '').replace(',', '.')
                        valores[tipo] = float(valor_str)
                        break  # Parar no primeiro valor encontrado para cada tipo
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
        """Fecha o driver e reseta a instância para permitir recriação."""
        with self._lock:
            if self.driver:
                try:
                    self.driver.quit()
                    print("✅ Chrome fechado com sucesso")
                except Exception as e:
                    print(f"⚠️ Erro ao fechar driver: {e}")
                finally:
                    self.driver = None
                    self.wait = None
                    
            if self.__class__._instance:
                self.__class__._instance = None
            
            if hasattr(self, 'initialized'):
                del self.initialized

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
            
            # Aguardar um pouco mais para elementos dinâmicos
            time.sleep(2)
            print("    ✅ Página carregada completamente")
            
        except Exception as e:
            print(f"    ⚠️ Timeout aguardando carregamento da página: {e}")

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
                    print(f"    ⚠️ Tentativa {attempt + 1}: Elemento não pronto: {e}")
                    time.sleep(1)
                    # Re-localizar elemento
                    try:
                        element = self.driver.find_element(by, value)
                    except:
                        element = self.wait.until(EC.presence_of_element_located((by, value)))
            
            print(f"    ✅ Elemento {value} pronto para interação")
            return element
            
        except Exception as e:
            print(f"    ❌ Erro ao aguardar elemento {value}: {e}")
            raise

    def _safe_send_keys(self, element, text, clear_first=True):
        """Envia texto de forma segura com JavaScript como fallback"""
        try:
            # Primeira tentativa: Selenium normal
            if clear_first:
                try:
                    element.clear()
                    time.sleep(0.5)
                except:
                    # Fallback: limpar via JavaScript
                    self.driver.execute_script("arguments[0].value = '';", element)
                    time.sleep(0.5)
            
            # Verificar se o elemento ainda está ativo
            is_interactive = self.driver.execute_script("""
                var element = arguments[0];
                return element && !element.disabled && element.style.display !== 'none';
            """, element)
            
            if not is_interactive:
                raise Exception("Elemento não está mais disponível")
            
            # Tentar enviar texto via Selenium
            try:
                element.send_keys(text)
                time.sleep(0.5)
            except:
                # Fallback: usar JavaScript
                print(f"    ⚠️ Selenium falhou, usando JavaScript para inserir texto")
                self.driver.execute_script("arguments[0].value = arguments[1];", element, text)
                # Disparar eventos de mudança
                self.driver.execute_script("""
                    var element = arguments[0];
                    element.dispatchEvent(new Event('input', {bubbles: true}));
                    element.dispatchEvent(new Event('change', {bubbles: true}));
                """, element)
                time.sleep(0.5)
            
            # Verificar se o texto foi inserido
            current_value = element.get_attribute('value')
            if current_value != text:
                print(f"    ⚠️ Valor esperado: {text}, valor atual: {current_value}")
                # Tentar novamente via JavaScript
                self.driver.execute_script("arguments[0].value = arguments[1];", element, text)
                self.driver.execute_script("""
                    var element = arguments[0];
                    element.dispatchEvent(new Event('input', {bubbles: true}));
                    element.dispatchEvent(new Event('change', {bubbles: true}));
                """, element)
                
            print(f"    ✅ Texto inserido: {text}")
            return True
            
        except Exception as e:
            print(f"    ❌ Erro ao inserir texto: {e}")
            raise

    def _safe_click(self, element):
        """Clica de forma segura com múltiplos fallbacks"""
        try:
            # Verificar se elemento está disponível via JavaScript
            is_clickable = self.driver.execute_script("""
                var element = arguments[0];
                return element && 
                       !element.disabled && 
                       element.style.display !== 'none' &&
                       element.style.visibility !== 'hidden';
            """, element)
            
            if not is_clickable:
                raise Exception("Elemento não está disponível para click")
            
            # Primeira tentativa: click normal do Selenium
            try:
                element.click()
                print(f"    ✅ Click normal realizado")
                return True
            except:
                print(f"    ⚠️ Click normal falhou, tentando JavaScript")
                
            # Segunda tentativa: JavaScript click
            try:
                self.driver.execute_script("arguments[0].click();", element)
                print(f"    ✅ Click via JavaScript realizado")
                return True
            except:
                print(f"    ⚠️ JavaScript click falhou, tentando dispatchEvent")
                
            # Terceira tentativa: Simular evento de click
            try:
                self.driver.execute_script("""
                    var element = arguments[0];
                    var event = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    });
                    element.dispatchEvent(event);
                """, element)
                print(f"    ✅ Click via dispatchEvent realizado")
                return True
            except Exception as e3:
                print(f"    ❌ Todos os métodos de click falharam: {e3}")
                raise
                
        except Exception as e:
            print(f"    ❌ Erro geral no click: {e}")
            raise

    def _find_pdf_url(self, html: str) -> str:
        import re
        match = re.search(r"https?://[^"]+\.pdf", html, re.IGNORECASE)
        if match:
            return match.group(0)
        return None

    def _download_pdf_text(self, pdf_url: str) -> str:
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
                return text
        except Exception as e:
            print(f"Erro ao baixar PDF {e}")
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