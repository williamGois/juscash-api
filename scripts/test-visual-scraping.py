#!/usr/bin/env python3

"""
Script para testar o web scraping com visualização do Chrome em execução
"""

import sys
import os
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.scraping.dje_scraper_debug import DJEScraperDebug

def test_visual_scraping():
    """Testa o scraping com Chrome visível"""
    
    print("🕷️ TESTE DE WEB SCRAPING VISUAL")
    print("=" * 50)
    
    # Configurar datas (ontem para ter mais chance de ter dados)
    data_fim = datetime.now() - timedelta(days=1)
    data_inicio = data_fim
    
    print(f"📅 Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
    print()
    
    # Criar scraper em modo visual
    print("🚀 Inicializando scraper em modo VISUAL...")
    scraper = DJEScraperDebug(visual_mode=True)
    
    try:
        print("🎯 Iniciando extração com pausas interativas...")
        print("   (Você poderá ver o Chrome funcionando!)")
        print()
        
        # Executar scraping com pausas
        publicacoes = scraper.extrair_publicacoes_debug(
            data_inicio, 
            data_fim, 
            pause_between_steps=True
        )
        
        # Mostrar resultados
        print("\n" + "=" * 50)
        print("📊 RESULTADOS")
        print("=" * 50)
        print(f"Total de publicações extraídas: {len(publicacoes)}")
        
        if publicacoes:
            print("\n📋 Primeiras 3 publicações:")
            for i, pub in enumerate(publicacoes[:3], 1):
                print(f"\n{i}. Processo: {pub.get('numero_processo', 'N/A')}")
                print(f"   Data: {pub.get('data_disponibilizacao', 'N/A')}")
                print(f"   Autores: {pub.get('autores', 'N/A')[:50]}...")
        else:
            print("\n⚠️ Nenhuma publicação encontrada para o período")
        
        # Tirar screenshot final
        print("\n📸 Tirando screenshot final...")
        scraper.take_screenshot("final_scraping_result.png")
        
    except Exception as e:
        print(f"\n❌ Erro durante o scraping: {e}")
    
    finally:
        print("\n🔚 Finalizando...")
        scraper.close()

def test_headless_scraping():
    """Testa o scraping sem interface visual (modo normal)"""
    
    print("🕷️ TESTE DE WEB SCRAPING HEADLESS")
    print("=" * 50)
    
    # Configurar datas
    data_fim = datetime.now() - timedelta(days=1)
    data_inicio = data_fim
    
    print(f"📅 Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
    
    # Criar scraper em modo headless
    print("🚀 Inicializando scraper em modo HEADLESS...")
    scraper = DJEScraperDebug(visual_mode=False)
    
    try:
        # Executar scraping sem pausas
        publicacoes = scraper.extrair_publicacoes_debug(
            data_inicio, 
            data_fim, 
            pause_between_steps=False
        )
        
        print(f"\n📊 Total extraídas: {len(publicacoes)}")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    print("🎯 ESCOLHA O MODO DE TESTE:")
    print("1. 🖥️  Visual (Chrome visível)")
    print("2. 👻 Headless (Chrome oculto)")
    print("3. 📸 Apenas screenshot")
    
    choice = input("\nDigite sua escolha (1/2/3): ").strip()
    
    if choice == "1":
        test_visual_scraping()
    elif choice == "2":
        test_headless_scraping()
    elif choice == "3":
        # Teste rápido apenas para screenshot
        print("📸 Teste rápido para screenshot...")
        scraper = DJEScraperDebug(visual_mode=True)
        try:
            scraper.driver.get("https://dje.tjsp.jus.br/cdje/index.do")
            input("⏸️ Pressione Enter para tirar screenshot...")
            scraper.take_screenshot("dje_homepage.png")
            scraper.get_page_info()
        finally:
            scraper.close()
    else:
        print("❌ Opção inválida!") 