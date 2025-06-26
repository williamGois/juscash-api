#!/usr/bin/env python3

"""
Script simples para testar Selenium visual - funciona localmente
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

def test_selenium_visual():
    """Testa Selenium com Chrome visível"""
    
    print("🕷️ TESTE VISUAL DO SELENIUM")
    print("=" * 40)
    
    # Configurar Chrome para modo visual
    chrome_options = Options()
    
    # COMENTAR a linha abaixo para ver o Chrome
    # chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-web-security")
    
    print("🚀 Abrindo Chrome...")
    
    try:
        # Inicializar driver
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Chrome aberto! Você deve ver a janela do navegador.")
        
        # Etapa 1: Acessar DJE
        print("\n📍 Etapa 1: Acessando DJE...")
        driver.get("https://dje.tjsp.jus.br/cdje/index.do")
        
        input("⏸️ Pressione Enter para continuar para o preenchimento...")
        
        # Etapa 2: Preencher formulário
        print("\n📍 Etapa 2: Preenchendo formulário...")
        
        # Aguardar elemento aparecer
        wait = WebDriverWait(driver, 30)
        
        # Data de ontem
        ontem = datetime.now() - timedelta(days=1)
        data_str = ontem.strftime("%d/%m/%Y")
        
        print(f"  📅 Preenchendo data: {data_str}")
        
        # Preencher datas
        data_inicio_field = wait.until(EC.visibility_of_element_located((By.ID, "dtInicioString")))
        data_inicio_field.clear()
        data_inicio_field.send_keys(data_str)
        
        data_fim_field = driver.find_element(By.ID, "dtFimString")
        data_fim_field.clear()
        data_fim_field.send_keys(data_str)
        
        print("  📂 Selecionando caderno...")
        # Selecionar caderno
        select_caderno = Select(driver.find_element(By.NAME, "dadosConsulta.cdCaderno"))
        select_caderno.select_by_value("-11")
        
        print("  🔍 Preenchendo termo de busca...")
        # Termo de busca
        search_box = driver.find_element(By.ID, "procura")
        search_box.clear()
        search_box.send_keys('"instituto nacional do seguro social" E inss')
        
        input("⏸️ Pressione Enter para submeter o formulário...")
        
        # Etapa 3: Submeter
        print("\n📍 Etapa 3: Submetendo formulário...")
        submit_button = driver.find_element(By.CSS_SELECTOR, "form[name='consultaAvancadaForm'] input[type='submit']")
        submit_button.click()
        
        print("⏳ Aguardando resultados...")
        time.sleep(5)
        
        input("⏸️ Pressione Enter para verificar resultados...")
        
        # Etapa 4: Verificar resultados
        print("\n📍 Etapa 4: Verificando resultados...")
        
        try:
            # Procurar por resultados
            results_div = wait.until(EC.presence_of_element_located((By.ID, "divResultadosInferior")))
            
            # Contar elementos de resultado
            result_elements = driver.find_elements(By.CSS_SELECTOR, "div#divResultadosInferior table tr.fundocinza1")
            
            print(f"📊 Encontrados {len(result_elements)} resultados na página")
            
            if result_elements:
                print("✅ Scraping funcionando! Resultados encontrados.")
                
                # Mostrar primeiro resultado
                first_result = result_elements[0]
                texto = first_result.text[:200] + "..." if len(first_result.text) > 200 else first_result.text
                print(f"📋 Primeiro resultado: {texto}")
            else:
                print("ℹ️ Nenhum resultado encontrado para a data selecionada")
                
        except Exception as e:
            print(f"⚠️ Erro ao verificar resultados: {e}")
        
        input("⏸️ Pressione Enter para fechar o Chrome...")
        
        print("\n🎉 Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
    
    finally:
        try:
            driver.quit()
            print("✅ Chrome fechado")
        except:
            pass

def test_selenium_screenshot():
    """Testa Selenium tirando screenshots"""
    
    print("📸 TESTE COM SCREENSHOTS")
    print("=" * 40)
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Modo oculto para screenshots
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        print("🌐 Acessando DJE...")
        driver.get("https://dje.tjsp.jus.br/cdje/index.do")
        
        print("📸 Tirando screenshot da homepage...")
        driver.save_screenshot("dje_homepage.png")
        print("✅ Screenshot salva: dje_homepage.png")
        
        # Preencher formulário rapidamente
        wait = WebDriverWait(driver, 30)
        
        ontem = datetime.now() - timedelta(days=1)
        data_str = ontem.strftime("%d/%m/%Y")
        
        data_inicio_field = wait.until(EC.visibility_of_element_located((By.ID, "dtInicioString")))
        data_inicio_field.send_keys(data_str)
        
        data_fim_field = driver.find_element(By.ID, "dtFimString")
        data_fim_field.send_keys(data_str)
        
        select_caderno = Select(driver.find_element(By.NAME, "dadosConsulta.cdCaderno"))
        select_caderno.select_by_value("-11")
        
        search_box = driver.find_element(By.ID, "procura")
        search_box.send_keys('"instituto nacional do seguro social" E inss')
        
        print("📸 Tirando screenshot do formulário preenchido...")
        driver.save_screenshot("dje_form_filled.png")
        print("✅ Screenshot salva: dje_form_filled.png")
        
        # Submeter
        submit_button = driver.find_element(By.CSS_SELECTOR, "form[name='consultaAvancadaForm'] input[type='submit']")
        submit_button.click()
        
        time.sleep(5)
        
        print("📸 Tirando screenshot dos resultados...")
        driver.save_screenshot("dje_results.png")
        print("✅ Screenshot salva: dje_results.png")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    print("🎯 ESCOLHA O TIPO DE TESTE:")
    print("1. 🖥️  Visual (Chrome visível)")
    print("2. 📸 Screenshots (Chrome oculto)")
    
    choice = input("\nDigite sua escolha (1/2): ").strip()
    
    if choice == "1":
        print("\n⚠️ IMPORTANTE: Você verá o Chrome abrir e navegar automaticamente!")
        print("   Observe cada etapa do processo de scraping.")
        input("\nPressione Enter para começar...")
        test_selenium_visual()
    elif choice == "2":
        test_selenium_screenshot()
    else:
        print("❌ Opção inválida!") 