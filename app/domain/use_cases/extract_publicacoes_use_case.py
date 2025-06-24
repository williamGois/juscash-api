from typing import List
from datetime import datetime
from app.domain.entities.publicacao import Publicacao
from app.domain.repositories.publicacao_repository import PublicacaoRepository
from app.infrastructure.scraping.dje_scraper import DJEScraper

class ExtractPublicacoesUseCase:
    
    def __init__(self, publicacao_repository: PublicacaoRepository, dje_scraper: DJEScraper):
        self.publicacao_repository = publicacao_repository
        self.dje_scraper = dje_scraper
    
    def execute(self, data_inicio: datetime, data_fim: datetime) -> List[Publicacao]:
        publicacoes_extraidas = self.dje_scraper.extrair_publicacoes(data_inicio, data_fim)
        publicacoes_salvas = []
        
        for publicacao_data in publicacoes_extraidas:
            publicacao_existente = self.publicacao_repository.find_by_numero_processo(
                publicacao_data['numero_processo']
            )
            
            if not publicacao_existente:
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
                
                publicacao_salva = self.publicacao_repository.create(publicacao)
                publicacoes_salvas.append(publicacao_salva)
        
        return publicacoes_salvas 