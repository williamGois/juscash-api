from typing import List
import logging
from datetime import datetime
from app.domain.entities.publicacao import Publicacao
from app.domain.repositories.publicacao_repository import PublicacaoRepository
from app.infrastructure.scraping.dje_scraper import DJEScraper

class ExtractPublicacoesUseCase:
    
    def __init__(self, publicacao_repository: PublicacaoRepository, dje_scraper: DJEScraper):
        self.publicacao_repository = publicacao_repository
        self.dje_scraper = dje_scraper
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    def execute(self, data_inicio: datetime, data_fim: datetime) -> List[Publicacao]:
        logging.info(f"Iniciando extração de publicações de {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}")
        
        publicacoes_extraidas = self.dje_scraper.extrair_publicacoes(data_inicio, data_fim)
        logging.info(f"Total de publicações extraídas: {len(publicacoes_extraidas)}")
        
        publicacoes_salvas = []
        publicacoes_existentes = 0
        erros_salvamento = 0
        
        for idx, publicacao_data in enumerate(publicacoes_extraidas, 1):
            try:
                logging.info(f"Processando publicação {idx}/{len(publicacoes_extraidas)}")
                
                if not publicacao_data.get('numero_processo'):
                    logging.warning(f"Publicação {idx} ignorada: número do processo não encontrado")
                    continue
                
                publicacao_existente = self.publicacao_repository.find_by_numero_processo(
                    publicacao_data['numero_processo']
                )
                
                if publicacao_existente:
                    logging.info(f"Publicação já existe no banco: {publicacao_data['numero_processo']}")
                    publicacoes_existentes += 1
                    continue
                
                logging.info(f"Criando nova publicação: {publicacao_data['numero_processo']}")
                
                publicacao = Publicacao(
                    numero_processo=publicacao_data['numero_processo'],
                    data_disponibilizacao=publicacao_data['data_disponibilizacao'],
                    autores=publicacao_data['autores'],
                    advogados=publicacao_data['advogados'],
                    conteudo_completo=publicacao_data['conteudo_completo'],
                    valor_principal_bruto=publicacao_data.get('valor_principal_bruto'),
                    valor_principal_liquido=publicacao_data.get('valor_principal_liquido'),
                    valor_juros_moratorios=publicacao_data.get('valor_juros_moratorios'),
                    honorarios_advocaticios=publicacao_data.get('honorarios_advocaticios')
                )
                
                try:
                    publicacao_salva = self.publicacao_repository.create(publicacao)
                    publicacoes_salvas.append(publicacao_salva)
                    logging.info(f"✅ Publicação salva com sucesso: {publicacao_data['numero_processo']}")
                except Exception as e:
                    erros_salvamento += 1
                    logging.error(f"❌ Erro ao salvar publicação {publicacao_data['numero_processo']}: {str(e)}")
                
            except Exception as e:
                erros_salvamento += 1
                logging.error(f"❌ Erro ao processar publicação {idx}: {str(e)}")
        
        logging.info(f"""
Resumo da extração:
- Total extraído: {len(publicacoes_extraidas)}
- Novas publicações salvas: {len(publicacoes_salvas)}
- Publicações já existentes: {publicacoes_existentes}
- Erros de salvamento: {erros_salvamento}
""")
        
        return publicacoes_salvas 