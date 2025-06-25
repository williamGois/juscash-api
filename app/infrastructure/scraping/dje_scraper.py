import re
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests

class DJEScraper:
    
    def __init__(self, base_url: str = "https://dje.tjsp.jus.br/cdje"):
        self.base_url = base_url
        self.session = requests.Session()
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, 20)
        logging.basicConfig(level=logging.INFO)
    
    def _setup_driver(self):
        """Configura o driver do Selenium com opções otimizadas para Docker."""
        logging.info("Configurando o driver do Selenium...")
        chrome_options = Options()
        
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=4096")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--virtual-time-budget=300000")
        
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logging.info("Driver do Selenium configurado com sucesso via webdriver-manager.")
            return driver
        except Exception as e:
            logging.warning(f"Falha ao usar webdriver-manager: {e}")
            logging.info("Tentando usar o chromedriver padrão do sistema.")
            try:
                driver = webdriver.Chrome(options=chrome_options)
                logging.info("Driver do Selenium configurado com chromedriver do sistema.")
                return driver
            except Exception as e2:
                logging.error(f"Falha ao configurar driver: {e2}")
                logging.info("Tentando configuração alternativa...")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                return webdriver.Chrome(options=chrome_options)
    
    def extrair_publicacoes(self, data_inicio: datetime, data_fim: datetime) -> List[Dict[str, Any]]:
        publicacoes = []
        
        current_date = data_inicio
        while current_date <= data_fim:
            try:
                publicacoes_do_dia = self._extrair_publicacoes_do_dia(current_date)
                publicacoes.extend(publicacoes_do_dia)
                current_date += timedelta(days=1)
                time.sleep(2)
            except Exception as e:
                print(f"Erro ao extrair publicações do dia {current_date}: {str(e)}")
                current_date += timedelta(days=1)
                continue
        
        return publicacoes
    
    def _extrair_publicacoes_do_dia(self, data: datetime) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/consultaSimples.do"
        
        try:
            self.driver.get(url)
            
            data_field = self.wait.until(EC.presence_of_element_located((By.NAME, "dtDiario")))
            data_field.clear()
            data_field.send_keys(data.strftime("%d/%m/%Y"))
            
            caderno_select = self.driver.find_element(By.NAME, "cdCaderno")
            for option in caderno_select.find_elements(By.TAG_NAME, "option"):
                if "Judicial - 1ª Instância - Capital" in option.text:
                    option.click()
                    break
            
            buscar_btn = self.driver.find_element(By.XPATH, "//input[@type='submit' and @value='Buscar']")
            buscar_btn.click()
            
            time.sleep(3)
            
            publicacoes = []
            
            try:
                content_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "content")))
                soup = BeautifulSoup(content_element.get_attribute('innerHTML'), 'html.parser')
                
                publicacoes_elements = soup.find_all('div', class_='publicacao')
                
                for pub_element in publicacoes_elements:
                    publicacao_data = self._extrair_dados_publicacao(pub_element, data)
                    if publicacao_data and self._validar_criterios_busca(publicacao_data):
                        publicacoes.append(publicacao_data)
                        
            except Exception as e:
                print(f"Erro ao processar publicações: {str(e)}")
            
            return publicacoes
            
        except Exception as e:
            print(f"Erro ao acessar DJE: {str(e)}")
            return []
    
    def _extrair_dados_publicacao(self, element, data: datetime) -> Dict[str, Any]:
        try:
            conteudo_completo = element.get_text(strip=True)
            
            numero_processo = self._extrair_numero_processo(conteudo_completo)
            if not numero_processo:
                return None
            
            autores = self._extrair_autores(conteudo_completo)
            advogados = self._extrair_advogados(conteudo_completo)
            valor_principal_bruto = self._extrair_valor_principal_bruto(conteudo_completo)
            valor_principal_liquido = self._extrair_valor_principal_liquido(conteudo_completo)
            valor_juros_moratorios = self._extrair_valor_juros_moratorios(conteudo_completo)
            honorarios_advocaticios = self._extrair_honorarios_advocaticios(conteudo_completo)
            
            return {
                'numero_processo': numero_processo,
                'data_disponibilizacao': data,
                'autores': autores or '',
                'advogados': advogados or '',
                'conteudo_completo': conteudo_completo,
                'valor_principal_bruto': valor_principal_bruto,
                'valor_principal_liquido': valor_principal_liquido,
                'valor_juros_moratorios': valor_juros_moratorios,
                'honorarios_advocaticios': honorarios_advocaticios
            }
            
        except Exception as e:
            print(f"Erro ao extrair dados da publicação: {str(e)}")
            return None
    
    def _validar_criterios_busca(self, publicacao_data: Dict[str, Any]) -> bool:
        conteudo = publicacao_data['conteudo_completo'].lower()
        return 'inss' in conteudo and 'instituto nacional do seguro social' in conteudo
    
    def _extrair_numero_processo(self, texto: str) -> str:
        pattern = r'\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}'
        match = re.search(pattern, texto)
        return match.group(0) if match else None
    
    def _extrair_autores(self, texto: str) -> str:
        patterns = [
            r'Autor[es]*:?\s*([^,\n]+)',
            r'Requerente[s]*:?\s*([^,\n]+)',
            r'Exequente[s]*:?\s*([^,\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def _extrair_advogados(self, texto: str) -> str:
        patterns = [
            r'Advogado[s]*:?\s*([^,\n]+)',
            r'OAB[/\s]*\w+[/\s]*\d+[^,\n]*',
            r'Dr\.?\s*([^,\n]+)'
        ]
        
        advogados = []
        for pattern in patterns:
            matches = re.findall(pattern, texto, re.IGNORECASE)
            advogados.extend(matches)
        
        return ', '.join(set(advogados)) if advogados else None
    
    def _extrair_valor_principal_bruto(self, texto: str) -> float:
        patterns = [
            r'valor\s+principal\s+bruto[:\s]*R\$\s*([\d.,]+)',
            r'principal\s+bruto[:\s]*R\$\s*([\d.,]+)'
        ]
        return self._extrair_valor_monetario(texto, patterns)
    
    def _extrair_valor_principal_liquido(self, texto: str) -> float:
        patterns = [
            r'valor\s+principal\s+líquido[:\s]*R\$\s*([\d.,]+)',
            r'principal\s+líquido[:\s]*R\$\s*([\d.,]+)'
        ]
        return self._extrair_valor_monetario(texto, patterns)
    
    def _extrair_valor_juros_moratorios(self, texto: str) -> float:
        patterns = [
            r'juros\s+moratórios[:\s]*R\$\s*([\d.,]+)',
            r'juros[:\s]*R\$\s*([\d.,]+)'
        ]
        return self._extrair_valor_monetario(texto, patterns)
    
    def _extrair_honorarios_advocaticios(self, texto: str) -> float:
        patterns = [
            r'honorários\s+advocatícios[:\s]*R\$\s*([\d.,]+)',
            r'honorários[:\s]*R\$\s*([\d.,]+)'
        ]
        return self._extrair_valor_monetario(texto, patterns)
    
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
            self.driver.quit()
            logging.info("Driver do Selenium finalizado.") 