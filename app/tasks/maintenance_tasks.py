import os
import logging
from datetime import datetime, timedelta
from app import create_app
from app.infrastructure.repositories.sqlalchemy_publicacao_repository import SQLAlchemyPublicacaoRepository

logger = logging.getLogger(__name__)

def cleanup_old_logs():
    """Remove logs antigos para liberar espaço em disco"""
    try:
        app = create_app()
        with app.app_context():
            log_dir = 'logs'
            if not os.path.exists(log_dir):
                return "Diretório de logs não existe"
            
            cutoff_date = datetime.now() - timedelta(days=30)
            removed_files = 0
            
            for filename in os.listdir(log_dir):
                filepath = os.path.join(log_dir, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_time < cutoff_date:
                        os.remove(filepath)
                        removed_files += 1
            
            logger.info(f"Limpeza de logs concluída: {removed_files} arquivos removidos")
            return f"Removidos {removed_files} arquivos de log antigos"
            
    except Exception as e:
        logger.error(f"Erro na limpeza de logs: {str(e)}")
        raise e

def generate_daily_stats():
    """Gera estatísticas diárias das publicações"""
    try:
        app = create_app()
        with app.app_context():
            repository = SQLAlchemyPublicacaoRepository()
            
            stats = {}
            for status in ['nova', 'lida', 'processada']:
                count = len(repository.find_by_status(status))
                stats[status] = count
            
            ontem = datetime.now() - timedelta(days=1)
            publicacoes_ontem = repository.find_by_date_range(ontem, datetime.now())
            stats['novas_ultimas_24h'] = len(publicacoes_ontem)
            
            logger.info(f"Estatísticas diárias: {stats}")
            return stats
            
    except Exception as e:
        logger.error(f"Erro ao gerar estatísticas: {str(e)}")
        raise e

def health_check():
    """Verifica saúde do sistema de scraping"""
    try:
        app = create_app()
        with app.app_context():
            repository = SQLAlchemyPublicacaoRepository()
            
            all_publicacoes = repository.find_all()
            total_publicacoes = len(all_publicacoes)
            
            semana_passada = datetime.now() - timedelta(days=7)
            publicacoes_recentes = repository.find_by_date_range(semana_passada, datetime.now())
            
            status = {
                'database_connection': 'ok',
                'total_publicacoes': total_publicacoes,
                'publicacoes_ultima_semana': len(publicacoes_recentes),
                'timestamp': datetime.now().isoformat(),
                'status': 'healthy' if len(publicacoes_recentes) > 0 else 'warning'
            }
            
            logger.info(f"Health check: {status}")
            return status
            
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        } 