#!/usr/bin/env python3
"""
Script para configurar cron jobs no sistema operacional
Usado como alternativa ao Celery Beat em ambientes que preferem crontab tradicional
"""

import os
import sys
from datetime import datetime
import subprocess

def create_crontab_entries():
    """Cria entradas no crontab para as tarefas de raspagem"""
    
    # Caminho para o diretório do projeto
    project_path = os.path.dirname(os.path.abspath(__file__))
    python_path = sys.executable
    
    cron_entries = [
        # Raspagem diária às 2:00 AM
        f"0 2 * * * cd {project_path} && {python_path} -c \"from app.tasks.scraping_tasks import extract_daily_publicacoes; extract_daily_publicacoes.delay()\" >> /var/log/juscash-daily.log 2>&1",
        
        # Raspagem completa aos domingos às 3:00 AM
        f"0 3 * * 0 cd {project_path} && {python_path} -c \"from app.tasks.scraping_tasks import extract_full_period_publicacoes; extract_full_period_publicacoes.delay()\" >> /var/log/juscash-weekly.log 2>&1",
        
        # Limpeza de logs todo dia às 4:00 AM
        f"0 4 * * * cd {project_path} && {python_path} -c \"from app.tasks.maintenance_tasks import cleanup_old_logs; cleanup_old_logs.delay()\" >> /var/log/juscash-cleanup.log 2>&1",
        
        # Health check a cada 6 horas
        f"0 */6 * * * cd {project_path} && {python_path} -c \"from app.tasks.maintenance_tasks import health_check; health_check.delay()\" >> /var/log/juscash-health.log 2>&1",
    ]
    
    return cron_entries

def install_crontab():
    """Instala os cron jobs no sistema"""
    try:
        # Obter crontab atual
        try:
            current_crontab = subprocess.check_output(['crontab', '-l'], stderr=subprocess.DEVNULL).decode('utf-8')
        except subprocess.CalledProcessError:
            current_crontab = ""
        
        # Adicionar entradas JusCash
        new_entries = create_crontab_entries()
        
        # Verificar se já existem entradas JusCash
        if 'juscash' not in current_crontab.lower():
            print("Adicionando entradas JusCash ao crontab...")
            
            # Criar novo crontab
            new_crontab = current_crontab + "\n# JusCash API Cron Jobs\n"
            for entry in new_entries:
                new_crontab += entry + "\n"
            
            # Escrever para arquivo temporário
            with open('/tmp/juscash_crontab', 'w') as f:
                f.write(new_crontab)
            
            # Instalar crontab
            subprocess.run(['crontab', '/tmp/juscash_crontab'], check=True)
            
            # Remover arquivo temporário
            os.remove('/tmp/juscash_crontab')
            
            print("✅ Cron jobs instalados com sucesso!")
            print("📋 Entradas adicionadas:")
            for entry in new_entries:
                print(f"   {entry}")
        else:
            print("⚠️ Entradas JusCash já existem no crontab")
            
    except Exception as e:
        print(f"❌ Erro ao instalar crontab: {str(e)}")
        return False
    
    return True

def remove_crontab():
    """Remove os cron jobs do sistema"""
    try:
        # Obter crontab atual
        try:
            current_crontab = subprocess.check_output(['crontab', '-l']).decode('utf-8')
        except subprocess.CalledProcessError:
            print("Nenhum crontab encontrado")
            return True
        
        # Filtrar linhas que não são do JusCash
        lines = current_crontab.split('\n')
        filtered_lines = []
        skip_next = False
        
        for line in lines:
            if '# JusCash API Cron Jobs' in line:
                skip_next = True
                continue
            if skip_next and ('juscash' in line.lower() or line.strip() == ''):
                continue
            else:
                skip_next = False
                filtered_lines.append(line)
        
        # Recriar crontab
        new_crontab = '\n'.join(filtered_lines)
        
        # Escrever para arquivo temporário
        with open('/tmp/juscash_crontab_clean', 'w') as f:
            f.write(new_crontab)
        
        # Instalar crontab limpo
        subprocess.run(['crontab', '/tmp/juscash_crontab_clean'], check=True)
        
        # Remover arquivo temporário
        os.remove('/tmp/juscash_crontab_clean')
        
        print("✅ Cron jobs JusCash removidos com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao remover crontab: {str(e)}")
        return False
    
    return True

def show_status():
    """Mostra o status atual do crontab"""
    try:
        current_crontab = subprocess.check_output(['crontab', '-l']).decode('utf-8')
        
        if 'juscash' in current_crontab.lower():
            print("✅ Cron jobs JusCash estão instalados")
            print("\n📋 Entradas atuais:")
            lines = current_crontab.split('\n')
            for line in lines:
                if 'juscash' in line.lower():
                    print(f"   {line}")
        else:
            print("❌ Nenhum cron job JusCash encontrado")
            
    except subprocess.CalledProcessError:
        print("❌ Nenhum crontab configurado")

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python cron_schedule.py [install|remove|status]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'install':
        install_crontab()
    elif command == 'remove':
        remove_crontab()
    elif command == 'status':
        show_status()
    else:
        print("Comando inválido. Use: install, remove ou status")
        sys.exit(1)

if __name__ == '__main__':
    main() 