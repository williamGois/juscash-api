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
        
        # Configurar display virtual
        if 'DISPLAY' not in os.environ:
            os.environ['DISPLAY'] = ':99'
            print("🖥️ Display configurado para :99")
        
        for attempt in range(self.max_retries):
            try:
                logging.info(f"🚀 Tentativa {attempt + 1} de inicializar Chrome driver...")
                
                if self.visual_mode:
                    print(f"🎯 Modo: VISUAL (Chrome será visível no display {os.environ.get('DISPLAY', 'padrão')})")
                else:
                    print(f"🎯 Modo: HEADLESS (Chrome oculto)")
                
                # Estratégia 1: Usar chromedriver do sistema (instalado no Dockerfile)
                try:
                    self.driver = webdriver.Chrome(
                        service=Service('/usr/bin/chromedriver'),
                        options=chrome_options
                    )
                    logging.info("✅ Driver inicializado com chromedriver do sistema")
                    break
                except Exception as e:
                    logging.warning(f"ChromeDriver do sistema falhou: {e}")
                    
                # Estratégia 2: Usar link simbólico
                try:
                    self.driver = webdriver.Chrome(
                        service=Service('/usr/local/bin/chromedriver'),
                        options=chrome_options
                    )
                    logging.info("✅ Driver inicializado com link simbólico")
                    break
                except Exception as e:
                    logging.warning(f"Link simbólico falhou: {e}")
                    
                # Estratégia 3: Fallback para webdriver-manager
                try:
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    logging.info("✅ Driver inicializado com webdriver-manager")
                    break
                except Exception as e:
                    logging.warning(f"Webdriver-manager falhou: {e}")
                    
                # Estratégia 4: Chrome sem service específico
                try:
                    self.driver = webdriver.Chrome(options=chrome_options)
                    logging.info("✅ Driver inicializado com Chrome padrão")
                    break
                except Exception as e:
                    logging.warning(f"Chrome padrão falhou: {e}")
            
            except Exception as e:
                logging.error(f"❌ Erro na tentativa {attempt + 1}: {e}")
                if self.driver:
                    try:
                        self.driver.quit()
                    except: pass
                    self.driver = None
                
                if attempt == self.max_retries - 1:
                    raise Exception(f"Falha crítica ao inicializar Chrome após {self.max_retries} tentativas: {e}")
                
                time.sleep(2)
        
        if self.driver:
            self.driver.set_page_load_timeout(45)
            self.driver.implicitly_wait(15)
            self.wait = WebDriverWait(self.driver, 30)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            if self.visual_mode:
                print(f"🌐 Chrome aberto! URL atual: {self.driver.current_url}")

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

            # Etapa 2: Preencher formulário
            print("📍 Etapa 2: Preenchendo formulário de pesquisa...")
            
            # Aguardar campo data início estar disponível e interagível
            print(f"  📅 Aguardando campo data início...")
            data_inicio_field = self._wait_for_element_ready(By.ID, "dtInicioString")
            self._safe_send_keys(data_inicio_field, data_inicio.strftime("%d/%m/%Y"))
            
            # Aguardar campo data fim estar disponível
            print(f"  📅 Aguardando campo data fim...")
            data_fim_field = self._wait_for_element_ready(By.ID, "dtFimString")
            self._safe_send_keys(data_fim_field, data_fim.strftime("%d/%m/%Y"))
            
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
            self._safe_send_keys(search_box, '"instituto nacional do seguro social" E inss')
            
            if pause_between_steps and self.visual_mode:
                input("⏸️ Pressione Enter para submeter o formulário...")
            
            # Etapa 3: Submeter formulário
            print("📍 Etapa 3: Submetendo formulário...")
            
            # Aguardar botão submit estar disponível
            print("  🔘 Aguardando botão submit...")
            submit_button = self._wait_for_element_ready(By.CSS_SELECTOR, "form[name='consultaAvancadaForm'] input[type='submit']")
            self._safe_click(submit_button)

            print("⏳ Aguardando resultados...")
            time.sleep(8)
            
            if pause_between_steps and self.visual_mode:
                input("⏸️ Pressione Enter para processar os resultados...")

            # Etapa 4: Processar TODAS as páginas de resultados
            print("📍 Etapa 4: Processando TODAS as páginas de resultados...")
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
                    
                    # Buscar por elementos de publicação (links clicáveis)
                    publicacao_links = soup.select('div#divResultadosInferior a[href*="consultaSimples.do"]')
                    
                    if not publicacao_links and page_num == 1:
                        print("    ℹ️ Nenhuma publicação encontrada para os critérios definidos.")
                        break
                    elif not publicacao_links:
                        print(f"    ℹ️ Fim dos resultados na página {page_num}")
                        break
                    else:
                        print(f"    📋 Encontrados {len(publicacao_links)} links de publicações na página {page_num}")
                        
                        # Processar cada link de publicação
                        for i, link in enumerate(publicacao_links, 1):
                            print(f"      🔍 Processando publicação {i}/{len(publicacao_links)} da página {page_num}...")
                            
                            try:
                                # Obter URL do link
                                href = link.get('href')
                                if href:
                                    # Construir URL completa
                                    if href.startswith('/'):
                                        full_url = f"https://dje.tjsp.jus.br{href}"
                                    elif href.startswith('consultaSimples.do'):
                                        full_url = f"https://dje.tjsp.jus.br/cdje/{href}"
                                    else:
                                        full_url = href
                                    
                                    print(f"        🌐 Navegando para: {full_url}")
                                    
                                    # Navegar para a página específica da publicação
                                    driver.get(full_url)
                                    time.sleep(2)
                                    
                                    # Extrair dados detalhados desta página
                                    publicacao_data = self._extrair_dados_pagina_individual(driver)
                                    
                                    if publicacao_data:
                                        all_publicacoes.append(publicacao_data)
                                        print(f"        ✅ Dados extraídos: {publicacao_data.get('numero_processo', 'N/A')}")
                                        
                                        # Log do JSON extraído (para debug)
                                        print(f"        📋 JSON: {publicacao_data}")
                                    else:
                                        print(f"        ⚠️ Não foi possível extrair dados desta publicação")
                                    
                                    # Voltar para a página de resultados
                                    driver.back()
                                    time.sleep(2)
                                    
                            except Exception as e:
                                print(f"        ❌ Erro ao processar publicação {i}: {e}")
                                # Tentar voltar para a página de resultados em caso de erro
                                try:
                                    driver.back()
                                    time.sleep(1)
                                except:
                                    # Se back() falhar, navegar novamente para os resultados
                                    # (seria necessário resubmeter o formulário)
                                    pass
                                continue
                    
                    # Tentar ir para a próxima página
                    print(f"    🔄 Procurando link para próxima página...")
                    try:
                        # Atualizar o soup com a página atual
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        
                        # Procurar por links de paginação
                        next_links = soup.select('a[href*="nuSeqpagina"]')
                        next_page_link = None
                        
                        for link in next_links:
                            if 'próximo' in link.get_text().lower() or '>' in link.get_text():
                                next_page_link = link
                                break
                        
                        if next_page_link:
                            href = next_page_link.get('href')
                            if href:
                                print(f"    📄 Navegando para próxima página...")
                                
                                # Construir URL da próxima página
                                if href.startswith('/'):
                                    next_url = f"https://dje.tjsp.jus.br{href}"
                                else:
                                    next_url = f"https://dje.tjsp.jus.br/cdje/{href}"
                                
                                driver.get(next_url)
                                time.sleep(3)
                                page_num += 1
                                continue
                        
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

    def _extrair_dados_pagina_individual(self, driver) -> Dict[str, Any]:
        """Extrai dados detalhados de uma página individual de publicação"""
        try:
            # Aguardar a página carregar
            time.sleep(2)
            
            # Obter HTML da página
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extrair conteúdo completo da publicação
            conteudo_completo = ""
            
            # Tentar diferentes seletores para encontrar o conteúdo
            content_selectors = [
                'div.ementaClass2',
                'div.ementaClass',
                'td.ementaClass2',
                'td.ementaClass',
                '.fundocinza1',
                'tbody tr td'
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    conteudo_completo = ' '.join([el.get_text(strip=True) for el in elements])
                    if conteudo_completo:
                        break
            
            # Se não encontrou com seletores específicos, pegar todo o texto da página
            if not conteudo_completo:
                body = soup.find('body')
                if body:
                    conteudo_completo = body.get_text(strip=True)
            
            if not conteudo_completo:
                print(f"        ⚠️ Não foi possível extrair conteúdo da página")
                return None
            
            # Extrair número do processo
            numero_processo = self._extrair_numero_processo(conteudo_completo)
            if not numero_processo:
                print(f"        ⚠️ Não foi possível extrair número do processo")
                return None
            
            # Extrair data de disponibilização
            data_disponibilizacao = None
            data_patterns = [
                r'(\d{2}/\d{2}/\d{4})',
                r'data[:\s]+(\d{2}/\d{2}/\d{4})',
                r'disponibiliza[^:]*:?\s*(\d{2}/\d{2}/\d{4})'
            ]
            
            for pattern in data_patterns:
                match = re.search(pattern, conteudo_completo, re.IGNORECASE)
                if match:
                    try:
                        data_disponibilizacao = datetime.strptime(match.group(1), "%d/%m/%Y")
                        break
                    except:
                        continue
            
            # Extrair informações financeiras com padrões mais abrangentes
            valor_principal_bruto = self._extrair_valor_monetario(conteudo_completo, [
                r'valor\s+principal\s+bruto[:\s]*R?\$?\s*([\d.,]+)',
                r'principal\s+bruto[:\s]*R?\$?\s*([\d.,]+)',
                r'bruto[:\s]*R?\$?\s*([\d.,]+)',
                r'valor\s+bruto[:\s]*R?\$?\s*([\d.,]+)'
            ])
            
            valor_principal_liquido = self._extrair_valor_monetario(conteudo_completo, [
                r'valor\s+principal\s+líquido[:\s]*R?\$?\s*([\d.,]+)',
                r'principal\s+líquido[:\s]*R?\$?\s*([\d.,]+)',
                r'líquido[:\s]*R?\$?\s*([\d.,]+)',
                r'valor\s+líquido[:\s]*R?\$?\s*([\d.,]+)'
            ])
            
            valor_juros_moratorios = self._extrair_valor_monetario(conteudo_completo, [
                r'juros\s+moratórios[:\s]*R?\$?\s*([\d.,]+)',
                r'juros[:\s]*R?\$?\s*([\d.,]+)',
                r'moratórios[:\s]*R?\$?\s*([\d.,]+)'
            ])
            
            honorarios_advocaticios = self._extrair_valor_monetario(conteudo_completo, [
                r'honorários\s+advocatícios[:\s]*R?\$?\s*([\d.,]+)',
                r'honorários[:\s]*R?\$?\s*([\d.,]+)',
                r'advocatícios[:\s]*R?\$?\s*([\d.,]+)'
            ])
            
            return {
                'numero_processo': numero_processo,
                'data_disponibilizacao': data_disponibilizacao,
                'autores': self._extrair_autores(conteudo_completo) or 'Não identificado',
                'advogados': self._extrair_advogados(conteudo_completo) or 'Não identificado',
                'conteudo_completo': conteudo_completo,
                'valor_principal_bruto': valor_principal_bruto,
                'valor_principal_liquido': valor_principal_liquido,
                'valor_juros_moratorios': valor_juros_moratorios,
                'honorarios_advocaticios': honorarios_advocaticios,
                'url_origem': driver.current_url
            }
            
        except Exception as e:
            print(f"        ❌ Erro ao extrair dados da página individual: {e}")
            return None

    def _extrair_numero_processo(self, texto: str) -> str:
        match = re.search(r'\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}', texto)
        return match.group(0) if match else None

    def _extrair_autores(self, texto: str) -> str:
        patterns = [
            r'(?:Apelante|Requerente|Exequente)s?:?\s*([^,(\n]+)',
            r'Autor[es]*:?\s*([^,(\n]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, texto, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extrair_advogados(self, texto: str) -> str:
        matches = re.findall(r'Advogad[oa]:\s*([^(\n]+?)\s*\(OAB:\s*\d+/[A-Z]{2}\)', texto, re.IGNORECASE)
        return ', '.join(set([adv.strip() for adv in matches])) if matches else None

    def _extrair_valor_monetario(self, texto: str, patterns: List[str]) -> float:
        for pattern in patterns:
            match = re.search(pattern, texto, re.IGNORECASE)
            if match:
                valor_str = match.group(1).replace('.', '').replace(',', '.')
                try:
                    return float(valor_str)
                except ValueError:
                    continue
        return None

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