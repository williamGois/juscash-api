#!/usr/bin/env python3
"""
Script para aplicar automaticamente o fix do ChromeDriver
Pode ser executado via API ou diretamente no container
"""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

def log(message):
    """Log com timestamp"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_chromedriver():
    """Verifica se o ChromeDriver está funcionando"""
    try:
        result = subprocess.run(['/usr/local/bin/chromedriver', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            log(f"✅ ChromeDriver OK: {result.stdout.strip()}")
            return True
    except Exception as e:
        log(f"❌ ChromeDriver não funciona: {e}")
    return False

def apply_chromedriver_fix():
    """Aplica o fix do ChromeDriver"""
    log("🔧 Iniciando fix do ChromeDriver...")
    
    # Verificar se o ChromeDriver já está funcionando
    if check_chromedriver():
        log("✅ ChromeDriver já está funcionando, fix não necessário")
        return True
    
    # Procurar ChromeDriver do webdriver-manager
    wdm_paths = [
        '/app/.wdm/drivers/chromedriver/linux64/138.0.7204.49/chromedriver-linux64/chromedriver',
        '/home/.wdm/drivers/chromedriver/linux64/138.0.7204.49/chromedriver-linux64/chromedriver',
        '/root/.wdm/drivers/chromedriver/linux64/138.0.7204.49/chromedriver-linux64/chromedriver'
    ]
    
    chromedriver_source = None
    for path in wdm_paths:
        if os.path.exists(path):
            chromedriver_source = path
            log(f"🔍 ChromeDriver encontrado em: {path}")
            break
    
    if not chromedriver_source:
        log("❌ ChromeDriver não encontrado no webdriver-manager")
        return False
    
    try:
        # Copiar ChromeDriver para local correto
        log(f"📋 Copiando {chromedriver_source} para /usr/local/bin/chromedriver")
        shutil.copy2(chromedriver_source, '/usr/local/bin/chromedriver')
        
        # Dar permissão de execução
        os.chmod('/usr/local/bin/chromedriver', 0o755)
        log("✅ Permissões aplicadas")
        
        # Verificar se está funcionando
        if check_chromedriver():
            log("🎉 Fix aplicado com sucesso!")
            return True
        else:
            log("❌ Fix aplicado mas ChromeDriver ainda não funciona")
            return False
            
    except Exception as e:
        log(f"❌ Erro ao aplicar fix: {e}")
        return False

def download_chromedriver():
    """Baixa ChromeDriver como último recurso"""
    log("🌐 Tentando baixar ChromeDriver diretamente...")
    
    try:
        import requests
        
        # URL do ChromeDriver compatível
        url = "https://storage.googleapis.com/chrome-for-testing-public/138.0.7204.0/linux64/chromedriver-linux64.zip"
        
        log(f"📥 Baixando de: {url}")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            # Salvar arquivo zip
            zip_path = "/tmp/chromedriver.zip"
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            # Extrair
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("/tmp/")
            
            # Copiar executável
            extracted_path = "/tmp/chromedriver-linux64/chromedriver"
            if os.path.exists(extracted_path):
                shutil.copy2(extracted_path, '/usr/local/bin/chromedriver')
                os.chmod('/usr/local/bin/chromedriver', 0o755)
                
                # Limpar arquivos temporários
                os.remove(zip_path)
                shutil.rmtree("/tmp/chromedriver-linux64")
                
                if check_chromedriver():
                    log("🎉 ChromeDriver baixado e instalado com sucesso!")
                    return True
                    
        log("❌ Falha no download do ChromeDriver")
        return False
        
    except Exception as e:
        log(f"❌ Erro no download: {e}")
        return False

def ensure_xvfb():
    """Garante que o Xvfb está rodando"""
    try:
        # Verificar se Xvfb está rodando
        result = subprocess.run(['pgrep', '-f', 'Xvfb'], capture_output=True, text=True)
        if result.returncode == 0:
            log(f"✅ Xvfb já está rodando (PID: {result.stdout.strip()})")
            return True
        
        # Iniciar Xvfb
        log("🖥️ Iniciando Xvfb...")
        subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1920x1080x24'])
        time.sleep(3)
        
        # Verificar novamente
        result = subprocess.run(['pgrep', '-f', 'Xvfb'], capture_output=True, text=True)
        if result.returncode == 0:
            log("✅ Xvfb iniciado com sucesso")
            return True
        else:
            log("❌ Falha ao iniciar Xvfb")
            return False
            
    except Exception as e:
        log(f"❌ Erro com Xvfb: {e}")
        return False

def main():
    """Função principal"""
    log("🚀 Iniciando fix automático do ChromeDriver")
    
    # Configurar DISPLAY
    os.environ['DISPLAY'] = ':99'
    log("🖥️ DISPLAY configurado para :99")
    
    # Tentar fix do ChromeDriver
    if apply_chromedriver_fix():
        log("✅ ChromeDriver configurado com sucesso!")
        return True
    
    log("❌ Fix falhou")
    return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 