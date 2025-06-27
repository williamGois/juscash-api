#!/usr/bin/env python3

import requests
import json
import sys
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any
import time

class ScrapingAnalyzer:
    def __init__(self):
        self.api_base = "https://cron.juscash.app/api"
        self.flower_url = "https://flower.juscash.app"
        self.ssh_cmd = "sshpass -p 'Syberya1989@@' ssh -o StrictHostKeyChecking=no root@77.37.68.178"
        
    def print_header(self, title: str):
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
    
    def print_section(self, title: str):
        print(f"\n📋 {title}")
        print("-" * 40)
    
    def test_api_connectivity(self) -> bool:
        """Testa conectividade com a API"""
        self.print_section("Testando Conectividade da API")
        
        try:
            response = requests.get(f"{self.api_base}/simple/ping", timeout=10)
            if response.status_code == 200:
                print("✅ API está respondendo")
                return True
            else:
                print(f"❌ API retornou status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao conectar com a API: {e}")
            return False
    
    def check_containers_status(self):
        """Verifica status dos containers"""
        self.print_section("Status dos Containers Docker")
        
        try:
            cmd = f"{self.ssh_cmd} 'cd /var/www/juscash && docker ps --format \"table {{{{.Names}}}}\\t{{{{.Status}}}}\\t{{{{.Ports}}}}\"'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("🐳 Containers ativos:")
                print(result.stdout)
            else:
                print(f"❌ Erro ao verificar containers: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Erro ao executar comando SSH: {e}")
    
    def check_selenium_dependencies(self):
        """Verifica se Selenium e Chrome estão funcionando"""
        self.print_section("Verificando Dependências do Selenium")
        
        # Testar Selenium
        try:
            cmd = f"{self.ssh_cmd} 'cd /var/www/juscash && docker exec juscash_worker_prod python -c \"from selenium import webdriver; print(\\\"Selenium OK\\\")\"'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Selenium está funcionando")
            else:
                print(f"❌ Erro no Selenium: {result.stderr}")
        except Exception as e:
            print(f"❌ Erro ao testar Selenium: {e}")
        
        # Testar Chrome/Chromium
        print("\n🔍 Verificando Chrome/Chromium:")
        chrome_commands = [
            "google-chrome --version",
            "chromium-browser --version", 
            "chromium --version",
            "ls -la /usr/bin/ | grep -E '(chrome|chromium)'"
        ]
        
        for cmd in chrome_commands:
            try:
                full_cmd = f"{self.ssh_cmd} 'cd /var/www/juscash && docker exec juscash_worker_prod {cmd}'"
                result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0 and result.stdout.strip():
                    print(f"✅ {cmd}: {result.stdout.strip()}")
                    break
                else:
                    print(f"❌ {cmd}: Não encontrado")
            except Exception as e:
                print(f"❌ {cmd}: Erro - {e}")
        else:
            print("🚨 PROBLEMA CRÍTICO: Chrome/Chromium não encontrado no container!")
            print("💡 Solução: Usar Dockerfile.alternative que inclui Chrome")
    
    def test_dje_connectivity(self):
        """Testa conectividade com o site do DJE"""
        self.print_section("Testando Conectividade com DJE")
        
        try:
            cmd = f"{self.ssh_cmd} 'cd /var/www/juscash && docker exec juscash_worker_prod curl -I -s -m 10 https://dje.tjsp.jus.br/cdje/index.do'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if "200 OK" in result.stdout:
                print("✅ Site do DJE está acessível")
            elif "HTTP" in result.stdout:
                print(f"⚠️ Site do DJE respondeu: {result.stdout.split()[1] if len(result.stdout.split()) > 1 else 'Status desconhecido'}")
            else:
                print(f"❌ Erro ao acessar DJE: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Erro ao testar conectividade com DJE: {e}")
    
    def check_database_data(self) -> Dict[str, Any]:
        """Verifica dados no banco de dados"""
        self.print_section("Análise do Banco de Dados")
        
        try:
            response = requests.get(f"{self.api_base}/publicacoes/?limit=100", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar se retornou erro
                if isinstance(data, dict) and data.get('status') == 'error':
                    print("❌ Erro no banco de dados:")
                    print(f"   {data.get('message', 'Erro desconhecido')}")
                    return {'total': 0, 'status': 'error'}
                
                # Analisar dados
                if isinstance(data, list):
                    total = len(data)
                    print(f"📊 Total de publicações: {total}")
                    
                    if total > 0:
                        # Análise de qualidade
                        campos_vazios = {'numero_processo': 0, 'autores': 0, 'advogados': 0, 'conteudo_completo': 0}
                        publicacoes_com_valores = 0
                        datas_extraidas = set()
                        
                        for pub in data:
                            # Verificar campos vazios
                            for campo in campos_vazios:
                                if not pub.get(campo) or str(pub[campo]).strip() == '':
                                    campos_vazios[campo] += 1
                            
                            # Contar publicações com valores monetários
                            if any([pub.get('valor_principal_bruto'), pub.get('valor_principal_liquido'),
                                   pub.get('valor_juros_moratorios'), pub.get('honorarios_advocaticios')]):
                                publicacoes_com_valores += 1
                            
                            # Coletar datas
                            if pub.get('data_disponibilizacao'):
                                data_str = pub['data_disponibilizacao'][:10]
                                datas_extraidas.add(data_str)
                        
                        print(f"💰 Publicações com valores: {publicacoes_com_valores} ({publicacoes_com_valores/total*100:.1f}%)")
                        print(f"📅 Datas diferentes: {len(datas_extraidas)}")
                        
                        if datas_extraidas:
                            print(f"📆 Período: {min(datas_extraidas)} a {max(datas_extraidas)}")
                            
                            # Mostrar últimas extrações
                            print("\n📅 Últimas extrações:")
                            for data_str in sorted(datas_extraidas, reverse=True)[:5]:
                                count = sum(1 for pub in data if pub.get('data_disponibilizacao', '').startswith(data_str))
                                print(f"   - {data_str}: {count} publicações")
                        
                        print(f"\n🔍 Qualidade dos campos:")
                        for campo, count in campos_vazios.items():
                            porcentagem = count/total*100
                            status = "✅" if porcentagem < 10 else "⚠️" if porcentagem < 50 else "❌"
                            print(f"   {status} {campo}: {count} vazios ({porcentagem:.1f}%)")
                        
                        return {
                            'total': total,
                            'status': 'success',
                            'quality': sum(1 for v in campos_vazios.values() if v/total < 0.1) / len(campos_vazios),
                            'datas_count': len(datas_extraidas)
                        }
                    else:
                        print("❌ Nenhuma publicação encontrada no banco")
                        return {'total': 0, 'status': 'empty'}
                else:
                    print(f"❌ Resposta inesperada da API: {type(data)}")
                    return {'total': 0, 'status': 'unexpected_response'}
                    
            else:
                print(f"❌ Erro na API: Status {response.status_code}")
                return {'total': 0, 'status': 'api_error'}
                
        except Exception as e:
            print(f"❌ Erro ao verificar banco de dados: {e}")
            return {'total': 0, 'status': 'exception'}
    
    def test_scraping_execution(self) -> Dict[str, Any]:
        """Executa um teste de scraping"""
        self.print_section("Teste de Execução do Scraping")
        
        try:
            # Usar data de ontem para teste
            ontem = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            print(f"🚀 Iniciando teste de scraping para {ontem}...")
            
            response = requests.post(f"{self.api_base}/scraping/extract", 
                                   json={
                                       'data_inicio': f'{ontem}T00:00:00',
                                       'data_fim': f'{ontem}T23:59:59'
                                   }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get('task_id')
                
                print(f"✅ Tarefa iniciada: {task_id}")
                print(f"📋 Status: {data.get('status')}")
                
                # Aguardar um pouco e verificar status
                print("⏳ Aguardando 30 segundos...")
                time.sleep(30)
                
                status_response = requests.get(f"{self.api_base}/cron/tasks/{task_id}", timeout=15)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    state = status_data.get('state')
                    
                    print(f"📊 Estado atual: {state}")
                    
                    if state == 'SUCCESS':
                        result = status_data.get('result', {})
                        total = result.get('total_extraidas', 0)
                        print(f"🎉 Sucesso! {total} publicações extraídas")
                        return {'status': 'success', 'total_extraidas': total}
                    elif state == 'FAILURE':
                        print("❌ Falha na execução do scraping")
                        print(f"Erro: {status_data.get('result', 'Erro desconhecido')}")
                        return {'status': 'failure', 'error': status_data.get('result')}
                    elif state in ['PENDING', 'PROGRESS']:
                        print(f"⏳ Ainda em execução (estado: {state})")
                        return {'status': 'running', 'state': state}
                    else:
                        print(f"❓ Estado desconhecido: {state}")
                        return {'status': 'unknown', 'state': state}
                else:
                    print(f"❌ Erro ao verificar status: {status_response.status_code}")
                    return {'status': 'status_error'}
            else:
                print(f"❌ Erro ao iniciar scraping: {response.status_code}")
                print(f"Resposta: {response.text}")
                return {'status': 'start_error', 'code': response.status_code}
                
        except Exception as e:
            print(f"❌ Erro no teste de scraping: {e}")
            return {'status': 'exception', 'error': str(e)}
    
    def check_worker_logs(self):
        """Verifica logs do worker"""
        self.print_section("Logs Recentes do Worker")
        
        try:
            cmd = f"{self.ssh_cmd} 'cd /var/www/juscash && docker logs juscash_worker_prod --tail 20'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logs = result.stdout
                print("📋 Últimos logs do worker:")
                print(logs)
                
                # Procurar por indicadores específicos
                if "extract" in logs.lower():
                    print("✅ Encontradas referências a 'extract' nos logs")
                if "selenium" in logs.lower():
                    print("✅ Encontradas referências ao Selenium nos logs")
                if "error" in logs.lower() or "failed" in logs.lower():
                    print("⚠️ Encontrados erros nos logs")
                if "success" in logs.lower() or "concluída" in logs.lower():
                    print("✅ Encontrados sucessos nos logs")
            else:
                print(f"❌ Erro ao obter logs: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Erro ao verificar logs: {e}")
    
    def generate_report(self):
        """Gera relatório completo"""
        self.print_header("ANÁLISE COMPLETA DO WEB SCRAPING - JUSCASH")
        
        # 1. Conectividade
        api_ok = self.test_api_connectivity()
        
        # 2. Containers
        self.check_containers_status()
        
        # 3. Dependências
        self.check_selenium_dependencies()
        
        # 4. Conectividade DJE
        self.test_dje_connectivity()
        
        # 5. Dados do banco
        db_status = self.check_database_data()
        
        # 6. Logs
        self.check_worker_logs()
        
        # 7. Teste de execução
        test_result = self.test_scraping_execution()
        
        # Resumo final
        self.print_header("RESUMO EXECUTIVO")
        
        print("📊 STATUS GERAL:")
        print(f"   API: {'✅ OK' if api_ok else '❌ FALHA'}")
        print(f"   Banco de dados: {'✅ OK' if db_status['status'] == 'success' else '❌ PROBLEMA'}")
        print(f"   Total de publicações: {db_status.get('total', 0)}")
        
        if test_result['status'] == 'success':
            print(f"   Teste de scraping: ✅ SUCESSO ({test_result.get('total_extraidas', 0)} extraídas)")
        elif test_result['status'] == 'running':
            print(f"   Teste de scraping: ⏳ EM EXECUÇÃO")
        else:
            print(f"   Teste de scraping: ❌ FALHA")
        
        print("\n🎯 RECOMENDAÇÕES:")
        
        if db_status['total'] == 0:
            print("❗ CRÍTICO: Nenhuma publicação no banco - scraping nunca funcionou")
            print("   💡 Verificar logs de erro e dependências")
        
        if test_result['status'] == 'failure':
            print("❗ CRÍTICO: Teste de scraping falhou")
            print("   💡 Verificar Chrome/Selenium e conectividade")
        
        if not api_ok:
            print("❗ CRÍTICO: API não está respondendo")
            print("   💡 Verificar containers e nginx")
        
        print("\n🔧 PRÓXIMOS PASSOS:")
        print("1. Acessar Flower: https://flower.juscash.app (admin:juscash2024)")
        print("2. Verificar logs detalhados: docker logs juscash_worker_prod")
        print("3. Se Chrome não estiver instalado, usar Dockerfile.alternative")
        print("4. Testar scraping manual via API")

if __name__ == "__main__":
    analyzer = ScrapingAnalyzer()
    analyzer.generate_report() 