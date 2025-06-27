import re
import time
import logging
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

class DJEScraper:
    
    def __init__(self, base_url: str = "https://dje.tjsp.jus.br/cdje/index.do"):
        self.base_url = base_url
        self.session = requests.Session()
        self.driver = None
        self.wait = None
        self.max_retries = 3
        logging.basicConfig(level=logging.INFO)
        self._initialize_driver()
    
    def _get_chrome_options(self):
        """Configurações otimizadas do Chrome para Docker/Railway"""
        chrome_options = Options()
        
        chrome_options.add_argument("--headless")
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
        
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option('detach', True)
        
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        return chrome_options
    
    def _initialize_driver(self):
        """Inicializa o driver com retry e múltiplas estratégias"""
        chrome_options = self._get_chrome_options()
        
        for attempt in range(self.max_retries):
            try:
                logging.info(f"Tentativa {attempt + 1} de inicializar Chrome driver...")
                
                try:
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    logging.info("✅ Driver inicializado com webdriver-manager")
                    break
                except Exception as e:
                    logging.warning(f"Webdriver-manager falhou, tentando com o Chrome do sistema: {e}")
                    self.driver = webdriver.Chrome(options=chrome_options)
                    logging.info("✅ Driver inicializado com Chrome do sistema")
                    break
            
            except Exception as e:
                logging.error(f"Erro na tentativa {attempt + 1}: {e}")
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                
                if attempt == self.max_retries - 1:
                    raise Exception(f"Falha crítica ao inicializar Chrome após {self.max_retries} tentativas: {e}")
                
                time.sleep(2)
        
        if self.driver:
            self.driver.set_page_load_timeout(45)
            self.driver.implicitly_wait(15)
            self.wait = WebDriverWait(self.driver, 30)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def _restart_driver_if_needed(self):
        """Reinicia o driver se não estiver respondendo."""
        try:
            self.driver.current_url
            return True
        except Exception:
            logging.warning("Driver não responsivo. Reiniciando...")
            try:
                if self.driver:
                    self.driver.quit()
            except:
                pass
            self._initialize_driver()
            return self.driver is not None

    def extrair_publicacoes(self, data_inicio: datetime, data_fim: datetime) -> List[Dict[str, Any]]:
        if not self._restart_driver_if_needed():
            logging.error("Driver não está operacional. Abortando extração.")
            return []

        logging.info(f"Iniciando extração de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
        self.driver.get(self.base_url)

        try:
            self.wait.until(EC.visibility_of_element_located((By.ID, "dtInicioString"))).send_keys(data_inicio.strftime("%d/%m/%Y"))
            self.driver.find_element(By.ID, "dtFimString").send_keys(data_fim.strftime("%d/%m/%Y"))
            
            select_caderno = Select(self.driver.find_element(By.NAME, "dadosConsulta.cdCaderno"))
            select_caderno.select_by_value("-11")

            self.driver.find_element(By.ID, "procura").send_keys('"instituto nacional do seguro social" E inss')
            
            self.driver.find_element(By.CSS_SELECTOR, "form[name='consultaAvancadaForm'] input[type='submit']").click()

            all_publicacoes = []
            page_num = 1
            while True:
                logging.info(f"Processando página de resultados {page_num}...")
                try:
                    self.wait.until(EC.presence_of_element_located((By.ID, "divResultadosInferior")))
                    time.sleep(2)
                    
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    publicacoes_elements = soup.select('div#divResultadosInferior table tr.fundocinza1')
                    
                    if not publicacoes_elements and page_num == 1:
                        logging.info("Nenhuma publicação encontrada para os critérios definidos.")
                        break
                
                    for element in publicacoes_elements:
                        publicacao_data = self._extrair_dados_publicacao(element)
                        if publicacao_data:
                            all_publicacoes.append(publicacao_data)
                    
                    try:
                        next_page_link = self.driver.find_element(By.LINK_TEXT, 'Próximo>')
                        logging.info("Encontrado link 'Próximo>'. Navegando para a próxima página.")
                        self.driver.execute_script("arguments[0].click();", next_page_link)
                        page_num += 1
                    except Exception:
                        logging.info("Fim da paginação. Não há mais link 'Próximo>'.")
                        break
                        
                except Exception as e:
                    logging.error(f"Erro ao processar página {page_num}: {e}")
                    break
            
            return all_publicacoes
            
        except Exception as e:
            logging.error(f"Erro fatal durante a extração: {e}")
            return []
    
    def _extrair_dados_publicacao(self, element) -> Dict[str, Any]:
        try:
            texto_completo_element = element.select_one('tr.ementaClass2 td')
            if not texto_completo_element:
                return None
            conteudo_completo = texto_completo_element.get_text(strip=True)
            
            numero_processo = self._extrair_numero_processo(conteudo_completo)
            if not numero_processo:
                return None
            
            data_str = "N/A"
            date_element = element.select_one('tr.ementaClass a')
            if date_element:
                match = re.search(r'(\d{2}/\d{2}/\d{4})', date_element.get_text())
                if match:
                    data_str = match.group(1)
            
            data_disponibilizacao = datetime.strptime(data_str, "%d/%m/%Y") if data_str != "N/A" else None
            
            return {
                'numero_processo': numero_processo,
                'data_disponibilizacao': data_disponibilizacao,
                'autores': self._extrair_autores(conteudo_completo) or '',
                'advogados': self._extrair_advogados(conteudo_completo) or '',
                'conteudo_completo': conteudo_completo,
                'valor_principal_bruto': self._extrair_valor_monetario(conteudo_completo, [r'valor\s+principal\s+bruto[:\s]*R\$\s*([\d.,]+)']),
                'valor_principal_liquido': self._extrair_valor_monetario(conteudo_completo, [r'valor\s+principal\s+líquido[:\s]*R\$\s*([\d.,]+)']),
                'valor_juros_moratorios': self._extrair_valor_monetario(conteudo_completo, [r'juros\s+moratórios[:\s]*R\$\s*([\d.,]+)']),
                'honorarios_advocaticios': self._extrair_valor_monetario(conteudo_completo, [r'honorários\s+advocatícios[:\s]*R\$\s*([\d.,]+)'])
            }
        except Exception as e:
            logging.error(f"Erro ao parsear dados da publicação: {e}")
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
    
    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                logging.info("✅ Driver do Selenium finalizado com sucesso")
            except Exception as e:
                logging.warning(f"Erro ao fechar driver: {e}")
            finally:
                self.driver = None 