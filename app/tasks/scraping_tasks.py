from datetime import datetime
from celery import current_task
from app import create_app

def extract_publicacoes_task(data_inicio_str: str, data_fim_str: str):
    try:
        app = create_app()
        with app.app_context():
            from app.domain.use_cases.extract_publicacoes_use_case import ExtractPublicacoesUseCase
            from app.infrastructure.repositories.sqlalchemy_publicacao_repository import SQLAlchemyPublicacaoRepository
            from app.infrastructure.scraping.dje_scraper import DJEScraper
            
            data_inicio = datetime.fromisoformat(data_inicio_str)
            data_fim = datetime.fromisoformat(data_fim_str)
            
            repository = SQLAlchemyPublicacaoRepository()
            scraper = DJEScraper()
            use_case = ExtractPublicacoesUseCase(repository, scraper)
            
            if current_task:
                current_task.update_state(state='PROGRESS', meta={'current': 0, 'total': 100})
            
            publicacoes = use_case.execute(data_inicio, data_fim)
            
            scraper.close()
            
            return {
                'total_extraidas': len(publicacoes),
                'data_inicio': data_inicio_str,
                'data_fim': data_fim_str,
                'status': 'concluido'
            }
            
    except Exception as e:
        if current_task:
            current_task.update_state(
                state='FAILURE',
                meta={'error': str(e)}
            )
        raise e

def extract_daily_publicacoes():
    """Extrai publicações do dia anterior automaticamente"""
    app = create_app()
    with app.app_context():
        from datetime import date, timedelta
        import logging
        
        logger = logging.getLogger(__name__)
        
        if not app.config.get('SCRAPING_ENABLED', True):
            logger.info("Scraping desabilitado via configuração")
            return "Scraping desabilitado"
        
        try:
            from app.domain.use_cases.extract_publicacoes_use_case import ExtractPublicacoesUseCase
            from app.infrastructure.repositories.sqlalchemy_publicacao_repository import SQLAlchemyPublicacaoRepository
            from app.infrastructure.scraping.dje_scraper import DJEScraper
            
            ontem = date.today() - timedelta(days=1)
            data_inicio = datetime.combine(ontem, datetime.min.time())
            data_fim = datetime.combine(ontem, datetime.max.time())
            
            logger.info(f"Iniciando raspagem diária para {ontem}")
            
            repository = SQLAlchemyPublicacaoRepository()
            scraper = DJEScraper()
            use_case = ExtractPublicacoesUseCase(repository, scraper)
            
            publicacoes = use_case.execute(data_inicio, data_fim)
            scraper.close()
            
            resultado = f"Raspagem diária concluída: {len(publicacoes)} publicações extraídas do dia {ontem}"
            logger.info(resultado)
            return resultado
            
        except Exception as e:
            logger.error(f"Erro na raspagem diária: {str(e)}")
            raise e

def extract_full_period_publicacoes():
    """Extrai publicações do período completo (01/10/2024 a 29/11/2024) semanalmente"""
    app = create_app()
    with app.app_context():
        import logging
        
        logger = logging.getLogger(__name__)
        
        if not app.config.get('SCRAPING_ENABLED', True):
            logger.info("Scraping completo desabilitado via configuração")
            return "Scraping desabilitado"
        
        try:
            from app.domain.use_cases.extract_publicacoes_use_case import ExtractPublicacoesUseCase
            from app.infrastructure.repositories.sqlalchemy_publicacao_repository import SQLAlchemyPublicacaoRepository
            from app.infrastructure.scraping.dje_scraper import DJEScraper
            
            data_inicio = datetime(2024, 10, 1)
            data_fim = datetime(2024, 11, 29, 23, 59, 59)
            
            logger.info(f"Iniciando raspagem completa do período: {data_inicio} a {data_fim}")
            
            repository = SQLAlchemyPublicacaoRepository()
            scraper = DJEScraper()
            use_case = ExtractPublicacoesUseCase(repository, scraper)
            
            publicacoes = use_case.execute(data_inicio, data_fim)
            scraper.close()
            
            resultado = f"Raspagem completa concluída: {len(publicacoes)} publicações extraídas do período"
            logger.info(resultado)
            return resultado
            
        except Exception as e:
            logger.error(f"Erro na raspagem completa: {str(e)}")
            raise e

def extract_custom_period_publicacoes(data_inicio_str: str, data_fim_str: str):
    """Extrai publicações de um período customizado via cron"""
    app = create_app()
    with app.app_context():
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            from app.domain.use_cases.extract_publicacoes_use_case import ExtractPublicacoesUseCase
            from app.infrastructure.repositories.sqlalchemy_publicacao_repository import SQLAlchemyPublicacaoRepository
            from app.infrastructure.scraping.dje_scraper import DJEScraper
            
            data_inicio = datetime.fromisoformat(data_inicio_str)
            data_fim = datetime.fromisoformat(data_fim_str)
            
            logger.info(f"Iniciando raspagem customizada: {data_inicio} a {data_fim}")
            
            repository = SQLAlchemyPublicacaoRepository()
            scraper = DJEScraper()
            use_case = ExtractPublicacoesUseCase(repository, scraper)
            
            publicacoes = use_case.execute(data_inicio, data_fim)
            scraper.close()
            
            resultado = f"Raspagem customizada concluída: {len(publicacoes)} publicações extraídas"
            logger.info(resultado)
            return resultado
            
        except Exception as e:
            logger.error(f"Erro na raspagem customizada: {str(e)}")
            raise e 