#!/usr/bin/env python3
import os
import stat
import subprocess
from webdriver_manager.chrome import ChromeDriverManager

def setup_chromedriver():
    print("🔧 Configurando ChromeDriver...")
    
    try:
        # Baixar ChromeDriver
        print("📥 Baixando ChromeDriver via webdriver-manager...")
        driver_path = ChromeDriverManager().install()
        print(f"📍 ChromeDriver instalado em: {driver_path}")
        
        # Verificar se existe
        if not os.path.exists(driver_path):
            print("❌ ChromeDriver não foi encontrado!")
            return False
        
        # Dar permissões de execução
        current_perms = os.stat(driver_path)
        print(f"🔒 Permissões atuais: {oct(current_perms.st_mode)}")
        
        os.chmod(driver_path, current_perms.st_mode | stat.S_IEXEC)
        new_perms = os.stat(driver_path)
        print(f"✅ Permissões atualizadas: {oct(new_perms.st_mode)}")
        
        # Criar link simbólico
        symlink_path = "/usr/local/bin/chromedriver"
        if os.path.exists(symlink_path):
            os.remove(symlink_path)
        
        os.symlink(driver_path, symlink_path)
        print(f"🔗 Link simbólico criado: {symlink_path} -> {driver_path}")
        
        # Testar ChromeDriver
        print("🧪 Testando ChromeDriver...")
        result = subprocess.run([driver_path, "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ ChromeDriver funcionando: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Erro ao testar ChromeDriver: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao configurar ChromeDriver: {e}")
        return False

if __name__ == "__main__":
    success = setup_chromedriver()
    if success:
        print("🎉 ChromeDriver configurado com sucesso!")
    else:
        print("💥 Falha ao configurar ChromeDriver!")
        exit(1) 