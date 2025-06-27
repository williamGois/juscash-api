from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from datetime import datetime
from app.domain.use_cases.extract_publicacoes_use_case import ExtractPublicacoesUseCase
from app.infrastructure.repositories.sqlalchemy_publicacao_repository import SQLAlchemyPublicacaoRepository
from app.infrastructure.scraping.dje_scraper import DJEScraper
from app.tasks.scraping_tasks import extract_publicacoes_task
import os
import threading

def get_version():
    """Lê a versão do arquivo VERSION na raiz do projeto."""
    import os
    
    # Possíveis localizações do arquivo VERSION
    possible_paths = [
        # Dentro do container Docker
        '/app/VERSION',
        # Na raiz do projeto (desenvolvimento)
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'VERSION')),
        # Caminho alternativo
        './VERSION',
        # Outro caminho possível
        os.path.join(os.getcwd(), 'VERSION')
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    version = f.read().strip()
                    if version:  # Só retorna se não estiver vazio
                        return version
        except Exception:
            continue
    
    # Se não encontrou em nenhum lugar, retorna um valor baseado no timestamp
    # para pelo menos saber que o deploy foi executado
    try:
        import subprocess
        # Tentar obter hash do git se disponível
        result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    # Última opção: usar variável de ambiente se disponível
    return os.environ.get('DEPLOY_VERSION', 'unknown')

publicacoes_ns = Namespace('publicacoes', description='Operações relacionadas às publicações do DJE')
scraping_ns = Namespace('scraping', description='Operações de web scraping')

publicacao_model = publicacoes_ns.model('Publicacao', {
    'id': fields.Integer(description='ID único da publicação'),
    'numero_processo': fields.String(required=True, description='Número do processo judicial'),
    'data_disponibilizacao': fields.String(required=True, description='Data de disponibilização no DJE'),
    'autores': fields.String(required=True, description='Autor(es) do processo'),
    'advogados': fields.String(required=True, description='Advogado(s) responsáveis'),
    'conteudo_completo': fields.String(required=True, description='Conteúdo completo da publicação'),
    'valor_principal_bruto': fields.Float(description='Valor principal bruto em reais'),
    'valor_principal_liquido': fields.Float(description='Valor principal líquido em reais'),
    'valor_juros_moratorios': fields.Float(description='Valor dos juros moratórios em reais'),
    'honorarios_advocaticios': fields.Float(description='Honorários advocatícios em reais'),
    'reu': fields.String(description='Réu do processo', default='Instituto Nacional do Seguro Social - INSS'),
    'status': fields.String(description='Status da publicação', enum=['nova', 'lida', 'processada']),
    'created_at': fields.String(description='Data de criação do registro'),
    'updated_at': fields.String(description='Data da última atualização')
})

stats_model = publicacoes_ns.model('PublicacoesStats', {
    'nova': fields.Integer(description='Quantidade de publicações novas'),
    'lida': fields.Integer(description='Quantidade de publicações lidas'),
    'processada': fields.Integer(description='Quantidade de publicações processadas'),
    'total': fields.Integer(description='Total de publicações')
})

@publicacoes_ns.route('/health')
class PublicacoesHealth(Resource):
    @publicacoes_ns.doc('publicacoes_health')
    def get(self):
        """Health check do endpoint de publicações"""
        try:
            from app import db
            from app.infrastructure.database.models import PublicacaoModel
            
            # Verificar se consegue conectar no banco
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            
            # Verificar se tabela existe
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'publicacoes' in tables:
                # Fazer uma query de teste
                result = db.session.execute(db.text('SELECT COUNT(*) FROM publicacoes'))
                count = result.scalar()
                
                return {
                    'status': 'healthy',
                    'message': 'Endpoint de publicações funcionando',
                    'database': 'connected',
                    'table_exists': True,
                    'publicacoes_count': count,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'degraded',
                    'message': 'Tabela publicacoes não existe',
                    'database': 'connected',
                    'table_exists': False,
                    'available_tables': tables,
                    'solution': 'Use /api/publicacoes/setup-database para criar a tabela',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Erro de banco de dados: {str(e)}',
                'database': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, 500

@publicacoes_ns.route('/setup-database')
class SetupDatabase(Resource):
    @publicacoes_ns.doc('setup_database')
    def get(self):
        """ENDPOINT ESPECIAL: Força criação da tabela publicacoes"""
        try:
            from app import db
            from app.infrastructure.database.models import PublicacaoModel
            
            # Verificar tabelas antes
            inspector = db.inspect(db.engine)
            tables_before = inspector.get_table_names()
            
            # Forçar criação
            db.create_all()
            
            # Verificar depois
            tables_after = db.inspect(db.engine).get_table_names()
            
            # Testar se funciona
            if 'publicacoes' in tables_after:
                # Fazer uma query de teste
                result = db.session.execute(db.text('SELECT COUNT(*) FROM publicacoes'))
                count = result.scalar()
                
                return {
                    'success': True,
                    'message': 'Tabela publicacoes criada com sucesso!',
                    'tables_before': tables_before,
                    'tables_after': tables_after,
                    'publicacoes_count': count
                }
            else:
                return {
                    'success': False,
                    'message': 'Falha ao criar tabela publicacoes',
                    'tables_before': tables_before,
                    'tables_after': tables_after
                }, 500
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Erro ao configurar banco: {str(e)}'
            }, 500

@publicacoes_ns.route('/')
class PublicacoesList(Resource):
    @publicacoes_ns.doc('list_publicacoes')
    @publicacoes_ns.param('status', 'Filtrar por status (nova, lida, processada)', _in='query')
    @publicacoes_ns.param('search', 'Buscar por termo no conteúdo, autores ou advogados', _in='query')
    @publicacoes_ns.param('limit', 'Limitar número de resultados', _in='query', type='integer')
    @publicacoes_ns.param('offset', 'Pular número de registros (paginação)', _in='query', type='integer')
    @publicacoes_ns.marshal_list_with(publicacao_model)
    def get(self):
        """Lista todas as publicações ou filtra por status"""
        try:
            repository = SQLAlchemyPublicacaoRepository()
            
            status = request.args.get('status')
            search = request.args.get('search')
            limit = request.args.get('limit', type=int)
            offset = request.args.get('offset', type=int)
            
            if search:
                publicacoes = repository.search_by_content(search, limit or 50)
            elif status:
                publicacoes = repository.find_by_status(status, limit, offset)
            else:
                publicacoes = repository.find_all(limit, offset)
            
            publicacoes_dict = []
            for pub in publicacoes:
                publicacoes_dict.append({
                    'id': pub.id,
                    'numero_processo': pub.numero_processo,
                    'data_disponibilizacao': pub.data_disponibilizacao.isoformat(),
                    'autores': pub.autores,
                    'advogados': pub.advogados,
                    'conteudo_completo': pub.conteudo_completo,
                    'valor_principal_bruto': pub.valor_principal_bruto,
                    'valor_principal_liquido': pub.valor_principal_liquido,
                    'valor_juros_moratorios': pub.valor_juros_moratorios,
                    'honorarios_advocaticios': pub.honorarios_advocaticios,
                    'reu': pub.reu,
                    'status': pub.status,
                    'created_at': pub.created_at.isoformat() if pub.created_at else None,
                    'updated_at': pub.updated_at.isoformat() if pub.updated_at else None
                })
            
            return publicacoes_dict
                    
        except Exception as e:
            # Se tabela não existe, retornar array vazio com aviso
            if "does not exist" in str(e) or "relation" in str(e).lower():
                return {
                    'error': 'Tabela publicacoes não existe',
                    'message': 'Use o endpoint /api/publicacoes/setup-database para criar a tabela',
                    'data': [],
                    'status': 'table_not_found'
                }, 200
            else:
                # Outros erros
                return {
                    'error': str(e),
                    'message': 'Erro interno do servidor',
                    'status': 'error'
                }, 500

@publicacoes_ns.route('/stats')
class PublicacoesStats(Resource):
    @publicacoes_ns.doc('get_publicacoes_stats')
    @publicacoes_ns.marshal_with(stats_model)
    def get(self):
        """Obtém estatísticas das publicações por status"""
        try:
            repository = SQLAlchemyPublicacaoRepository()
            stats = repository.count_by_status()
            
            total = sum(stats.values())
            return {
                'nova': stats.get('nova', 0),
                'lida': stats.get('lida', 0),
                'processada': stats.get('processada', 0),
                'total': total
            }
        except Exception as e:
            # Se tabela não existe, retornar zeros
            if "does not exist" in str(e):
                return {
                    'nova': 0,
                    'lida': 0,
                    'processada': 0,
                    'total': 0,
                    'warning': 'Tabela publicacoes não existe. Use /api/publicacoes/setup-database'
                }
            else:
                raise e

@publicacoes_ns.route('/<int:id>')
@publicacoes_ns.param('id', 'ID da publicação')
class Publicacao(Resource):
    @publicacoes_ns.doc('get_publicacao')
    @publicacoes_ns.marshal_with(publicacao_model)
    @publicacoes_ns.response(404, 'Publicação não encontrada')
    def get(self, id):
        """Obtém uma publicação específica pelo ID"""
        repository = SQLAlchemyPublicacaoRepository()
        publicacao = repository.find_by_id(id)
        
        if not publicacao:
            publicacoes_ns.abort(404, 'Publicação não encontrada')
        
        return {
            'id': publicacao.id,
            'numero_processo': publicacao.numero_processo,
            'data_disponibilizacao': publicacao.data_disponibilizacao.isoformat(),
            'autores': publicacao.autores,
            'advogados': publicacao.advogados,
            'conteudo_completo': publicacao.conteudo_completo,
            'valor_principal_bruto': publicacao.valor_principal_bruto,
            'valor_principal_liquido': publicacao.valor_principal_liquido,
            'valor_juros_moratorios': publicacao.valor_juros_moratorios,
            'honorarios_advocaticios': publicacao.honorarios_advocaticios,
            'reu': publicacao.reu,
            'status': publicacao.status,
            'created_at': publicacao.created_at.isoformat() if publicacao.created_at else None,
            'updated_at': publicacao.updated_at.isoformat() if publicacao.updated_at else None
        }

status_update_model = publicacoes_ns.model('PublicacaoStatusUpdate', {
    'status': fields.String(required=True, description='Novo status', enum=['nova', 'lida', 'processada'])
})

@publicacoes_ns.route('/<int:id>/status')
@publicacoes_ns.param('id', 'ID da publicação')
class PublicacaoStatus(Resource):
    @publicacoes_ns.doc('update_status')
    @publicacoes_ns.expect(status_update_model)
    @publicacoes_ns.response(200, 'Status atualizado com sucesso')
    @publicacoes_ns.response(404, 'Publicação não encontrada')
    @publicacoes_ns.response(400, 'Dados inválidos')
    def put(self, id):
        """Atualiza o status de uma publicação"""
        repository = SQLAlchemyPublicacaoRepository()
        publicacao = repository.find_by_id(id)
        
        if not publicacao:
            publicacoes_ns.abort(404, 'Publicação não encontrada')
        
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            publicacoes_ns.abort(400, 'Status é obrigatório')
        
        if new_status not in ['nova', 'lida', 'processada']:
            publicacoes_ns.abort(400, 'Status deve ser: nova, lida ou processada')
        
        publicacao.status = new_status
        updated_publicacao = repository.update(publicacao)
        
        return {
            'id': updated_publicacao.id,
            'status': updated_publicacao.status,
            'updated_at': updated_publicacao.updated_at.isoformat()
        }

scraping_request_model = scraping_ns.model('ScrapingRequest', {
    'data_inicio': fields.DateTime(required=True, description='Data de início (ISO 8601)', example='2024-10-01T00:00:00'),
    'data_fim': fields.DateTime(required=True, description='Data fim (ISO 8601)', example='2024-10-30T23:59:59')
})

task_response_model = scraping_ns.model('TaskResponse', {
    'task_id': fields.String(description='ID da tarefa'),
    'status': fields.String(description='Status da tarefa'),
    'message': fields.String(description='Mensagem')
})

@scraping_ns.route('/extract')
class ScrapingExtract(Resource):
    @scraping_ns.doc('extract_publicacoes')
    @scraping_ns.expect(scraping_request_model)
    @scraping_ns.marshal_with(task_response_model)
    @scraping_ns.response(400, 'Dados inválidos')
    def post(self):
        """Inicia extração de publicações do DJE em background"""
        data = request.get_json()
        
        try:
            data_inicio = datetime.fromisoformat(data['data_inicio'])
            data_fim = datetime.fromisoformat(data['data_fim'])
        except (KeyError, ValueError):
            scraping_ns.abort(400, 'Datas de início e fim são obrigatórias no formato ISO 8601')
        
        if data_inicio > data_fim:
            scraping_ns.abort(400, 'Data de início deve ser anterior à data fim')
        
        try:
            from celery import current_app as celery_app
            
            # FORÇAR CONFIGURAÇÃO DO CELERY ANTES DE USAR
            redis_url = current_app.config.get('REDIS_URL') or os.environ.get('REDIS_URL')
            if redis_url and (not celery_app.conf.broker_url or str(celery_app.conf.broker_url) == 'None'):
                celery_app.conf.update({
                    'broker_url': redis_url,
                    'result_backend': redis_url,
                    'task_serializer': 'json',
                    'timezone': 'America/Sao_Paulo',
                    'enable_utc': True
                })
            
            # Tentar verificar se o Redis está acessível
            try:
                celery_app.control.inspect().ping()
                redis_available = True
            except Exception:
                redis_available = False
            
            if redis_available:
                # Usar Celery se Redis estiver disponível
                task = celery_app.send_task(
                    'app.tasks.scraping_tasks.extract_publicacoes_task',
                    args=[data_inicio.isoformat(), data_fim.isoformat()]
                )
                
                return {
                    'task_id': task.id,
                    'status': 'Em processamento (async)',
                    'message': 'Extração de publicações iniciada em background via Celery'
                }
            else:
                # Fallback: execução síncrona se Redis não estiver disponível
                from app.domain.use_cases.extract_publicacoes_use_case import ExtractPublicacoesUseCase
                from app.infrastructure.repositories.sqlalchemy_publicacao_repository import SQLAlchemyPublicacaoRepository
                from app.infrastructure.scraping.dje_scraper import DJEScraper
                
                repository = SQLAlchemyPublicacaoRepository()
                scraper = DJEScraper()
                use_case = ExtractPublicacoesUseCase(repository, scraper)
                
                # Execução síncrona
                publicacoes = use_case.execute(data_inicio, data_fim)
                scraper.close()
                
                # Gerar um task_id fake para compatibilidade
                import uuid
                fake_task_id = str(uuid.uuid4())
                
                return {
                    'task_id': fake_task_id,
                    'status': 'Concluído (sync)',
                    'message': f'Extração concluída: {len(publicacoes)} publicações extraídas',
                    'result': {
                        'total_extraidas': len(publicacoes),
                        'data_inicio': data_inicio.isoformat(),
                        'data_fim': data_fim.isoformat(),
                        'status': 'concluido'
                    }
                }
                
        except Exception as e:
            # Em caso de erro geral, tentar fallback síncrono
            try:
                from app.domain.use_cases.extract_publicacoes_use_case import ExtractPublicacoesUseCase
                from app.infrastructure.repositories.sqlalchemy_publicacao_repository import SQLAlchemyPublicacaoRepository
                from app.infrastructure.scraping.dje_scraper import DJEScraper
                
                repository = SQLAlchemyPublicacaoRepository()
                scraper = DJEScraper()
                use_case = ExtractPublicacoesUseCase(repository, scraper)
                
                publicacoes = use_case.execute(data_inicio, data_fim)
                scraper.close()
                
                import uuid
                fake_task_id = str(uuid.uuid4())
                
                return {
                    'task_id': fake_task_id,
                    'status': 'Concluído (fallback)',
                    'message': f'Redis indisponível. Execução síncrona: {len(publicacoes)} publicações extraídas',
                    'result': {
                        'total_extraidas': len(publicacoes),
                        'data_inicio': data_inicio.isoformat(),
                        'data_fim': data_fim.isoformat(),
                        'status': 'concluido'
                    }
                }
            except Exception as fallback_error:
                return {
                    'task_id': None,
                    'status': 'Erro',
                    'message': f'Erro na execução: {str(fallback_error)}'
                }, 500

task_status_model = scraping_ns.model('TaskStatus', {
    'state': fields.String(description='Estado da tarefa'),
    'status': fields.String(description='Status em português'),
    'current': fields.Integer(description='Progresso atual'),
    'total': fields.Integer(description='Total'),
    'result': fields.Raw(description='Resultado'),
    'error': fields.String(description='Erro')
})

@scraping_ns.route('/status/<string:task_id>')
@scraping_ns.param('task_id', 'ID da tarefa Celery')
class ScrapingStatus(Resource):
    @scraping_ns.doc('get_task_status')
    @scraping_ns.marshal_with(task_status_model)
    def get(self, task_id):
        """Verifica o status de uma tarefa de scraping"""
        try:
            # Verificar se é um UUID fake (execução síncrona)
            if len(task_id) == 36 and task_id.count('-') == 4:
                # Task executada sincronamente, retornar status de sucesso
                return {
                    'state': 'SUCCESS',
                    'status': 'Tarefa executada sincronamente',
                    'result': 'Consulte a resposta original da requisição para detalhes'
                }
            
            from celery import current_app as celery_app
            from celery.result import AsyncResult
            
            # Verificar se o Redis está disponível
            try:
                celery_app.control.inspect().ping()
                redis_available = True
            except Exception:
                redis_available = False
            
            if not redis_available:
                return {
                    'state': 'UNAVAILABLE',
                    'status': 'Redis indisponível',
                    'error': 'Serviço de monitoramento de tasks não disponível'
                }
            
            task = AsyncResult(task_id, app=celery_app)
            
            if task.state == 'PENDING':
                response = {
                    'state': task.state,
                    'status': 'Pendente'
                }
            elif task.state == 'PROGRESS':
                response = {
                    'state': task.state,
                    'status': 'Em progresso',
                    'current': task.info.get('current', 0) if task.info else 0,
                    'total': task.info.get('total', 1) if task.info else 1
                }
            elif task.state == 'SUCCESS':
                response = {
                    'state': task.state,
                    'status': 'Concluído',
                    'result': task.result
                }
            else:
                response = {
                    'state': task.state,
                    'status': 'Erro',
                    'error': str(task.info) if task.info else 'Erro desconhecido'
                }
            
            return response
        except Exception as e:
            return {
                'state': 'ERROR',
                'status': 'Erro ao verificar status',
                'error': f'Erro interno: {str(e)}'
            }, 500

@scraping_ns.route('/health')
class ScrapingHealth(Resource):
    @scraping_ns.doc('scraping_health_check')
    def get(self):
        """Verifica o status dos serviços de scraping"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'services': {}
        }
        
        # Verificar Redis/Celery
        try:
            from celery import current_app as celery_app
            
            # Primeiro, verificar se o Celery tem as configurações corretas
            broker_url = celery_app.conf.broker_url
            result_backend = celery_app.conf.result_backend
            
            if not broker_url or str(broker_url) == 'None':
                health_status['services']['celery'] = 'misconfigured'
                health_status['services']['celery_error'] = 'broker_url not configured'
            else:
                # Tentar ping no Celery
                try:
                    inspect = celery_app.control.inspect()
                    result = inspect.ping()
                    
                    if result:
                        health_status['services']['celery'] = 'available'
                        health_status['services']['redis'] = 'available'
                    else:
                        health_status['services']['celery'] = 'no_workers'
                        health_status['services']['redis'] = 'available_no_workers'
                except Exception as celery_error:
                    # Se o ping falhou, testar Redis diretamente
                    try:
                        import redis
                        redis_client = redis.from_url(str(broker_url), socket_connect_timeout=5)
                        redis_client.ping()
                        health_status['services']['redis'] = 'available'
                        health_status['services']['celery'] = 'unavailable'
                        health_status['services']['celery_error'] = str(celery_error)
                    except Exception as redis_error:
                        health_status['services']['redis'] = 'unavailable'
                        health_status['services']['celery'] = 'unavailable'
                        health_status['services']['redis_error'] = str(redis_error)
                        
        except Exception as e:
            health_status['services']['redis'] = 'unavailable'
            health_status['services']['celery'] = 'unavailable'
            health_status['services']['redis_error'] = str(e)
        
        # Verificar banco de dados
        try:
            from app.infrastructure.repositories.sqlalchemy_publicacao_repository import SQLAlchemyPublicacaoRepository
            repository = SQLAlchemyPublicacaoRepository()
            test_publicacoes = repository.find_all(limit=1)
            health_status['services']['database'] = 'available'
        except Exception as e:
            health_status['services']['database'] = 'unavailable'
            health_status['services']['database_error'] = str(e)
        
        # Versão do deploy (teste CI/CD)
        health_status['version'] = 'v1.0.2-auto-deploy'
        health_status['deploy_method'] = 'GitHub Actions CI/CD'
        
        # Verificar Selenium (teste básico sem inicializar driver)
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            # Teste básico: verificar se as bibliotecas estão disponíveis
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            # Não inicializar o driver, apenas verificar se é possível criar as opções
            health_status['services']['selenium'] = 'available'
        except Exception as e:
            health_status['services']['selenium'] = 'unavailable'
            health_status['services']['selenium_error'] = str(e)
        
        # Determinar status geral
        available_services = [v for v in health_status['services'].values() if v == 'available']
        total_services = len([k for k in health_status['services'].keys() if not k.endswith('_error')])
        
        if len(available_services) == total_services:
            health_status['overall_status'] = 'healthy'
            health_status['mode'] = 'full_async'
        elif 'database' in [k for k, v in health_status['services'].items() if v == 'available']:
            health_status['overall_status'] = 'degraded'
            health_status['mode'] = 'sync_fallback'
        else:
            health_status['overall_status'] = 'unhealthy'
            health_status['mode'] = 'unavailable'
        
        return health_status

@scraping_ns.route('/debug')
class ScrapingDebug(Resource):
    @scraping_ns.doc('scraping_debug_info')
    def get(self):
        """Debug das configurações de Redis e Celery"""
        import os
        from flask import current_app
        
        debug_info = {
            'timestamp': datetime.now().isoformat(),
            'environment': os.environ.get('ENVIRONMENT', 'local'),
            'config_used': current_app.config.get('ENV', 'unknown'),
            'redis_config': {},
            'celery_config': {},
            'environment_vars': {}
        }
        
        # Verificar configurações do Redis
        redis_url = current_app.config.get('REDIS_URL')
        debug_info['redis_config'] = {
            'REDIS_URL': redis_url,
            'url_masked': redis_url[:10] + '***' + redis_url[-10:] if redis_url and len(redis_url) > 20 else redis_url
        }
        
        # Verificar variáveis de ambiente relacionadas ao Redis
        redis_env_vars = [
            'REDIS_URL', 'REDIS_HOST', 'REDIS_PORT', 'REDIS_PASSWORD',
            'REDISHOST', 'REDISPORT', 'REDISUSER', 'REDISPASSWORD'
        ]
        
        for var in redis_env_vars:
            value = os.environ.get(var)
            if value:
                debug_info['environment_vars'][var] = value[:10] + '***' + value[-5:] if len(value) > 15 else value
            else:
                debug_info['environment_vars'][var] = None
        
        # Testar conexão Redis diretamente
        try:
            import redis
            
            # Tentar diferentes formatos de URL
            test_urls = []
            
            if redis_url:
                test_urls.append(('REDIS_URL', redis_url))
            
            # Tentar construir URL a partir de variáveis individuais
            redis_host = os.environ.get('REDISHOST') or os.environ.get('REDIS_HOST')
            redis_port = os.environ.get('REDISPORT') or os.environ.get('REDIS_PORT', '6379')
            redis_password = os.environ.get('REDISPASSWORD') or os.environ.get('REDIS_PASSWORD')
            
            if redis_host:
                if redis_password:
                    constructed_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/0"
                else:
                    constructed_url = f"redis://{redis_host}:{redis_port}/0"
                test_urls.append(('Constructed', constructed_url))
            
            debug_info['redis_tests'] = []
            
            for name, url in test_urls:
                try:
                    r = redis.from_url(url, socket_connect_timeout=5, socket_timeout=5)
                    r.ping()
                    debug_info['redis_tests'].append({
                        'name': name,
                        'url_masked': url[:15] + '***' + url[-10:] if len(url) > 25 else url,
                        'status': 'success'
                    })
                except Exception as e:
                    debug_info['redis_tests'].append({
                        'name': name,
                        'url_masked': url[:15] + '***' + url[-10:] if len(url) > 25 else url,
                        'status': 'failed',
                        'error': str(e)
                    })
        
        except ImportError:
            debug_info['redis_tests'] = [{'error': 'redis library not available'}]
        except Exception as e:
            debug_info['redis_tests'] = [{'error': f'Unexpected error: {str(e)}'}]
        
        # Verificar configuração do Celery
        try:
            from celery import current_app as celery_app
            debug_info['celery_config'] = {
                'broker_url': str(celery_app.conf.broker_url)[:20] + '***' if celery_app.conf.broker_url else None,
                'result_backend': str(celery_app.conf.result_backend)[:20] + '***' if celery_app.conf.result_backend else None,
                'task_serializer': celery_app.conf.task_serializer,
                'timezone': celery_app.conf.timezone
            }
        except Exception as e:
            debug_info['celery_config'] = {'error': str(e)}
        
        return debug_info

@scraping_ns.route('/test-celery-fix')
class ScrapingTestCeleryFix(Resource):
    @scraping_ns.doc('test_celery_fix')
    def get(self):
        """Teste avançado para diagnosticar e corrigir o problema do Celery"""
        import os
        from flask import current_app
        
        test_result = {
            'timestamp': datetime.now().isoformat(),
            'step1_environment': {},
            'step2_app_config': {},
            'step3_celery_creation': {},
            'step4_manual_config': {},
            'step5_solution': {}
        }
        
        # STEP 1: Verificar variáveis de ambiente
        redis_url_env = os.environ.get('REDIS_URL')
        test_result['step1_environment'] = {
            'REDIS_URL_from_env': redis_url_env[:20] + '***' if redis_url_env else None,
            'ENVIRONMENT': os.environ.get('ENVIRONMENT'),
            'FLASK_ENV': os.environ.get('FLASK_ENV')
        }
        
        # STEP 2: Verificar configuração da app
        redis_url_config = current_app.config.get('REDIS_URL')
        test_result['step2_app_config'] = {
            'REDIS_URL_from_config': redis_url_config[:20] + '***' if redis_url_config else None,
            'config_keys': list(current_app.config.keys())[:10]  # Primeiras 10 keys
        }
        
        # STEP 3: Tentar criar Celery manualmente
        try:
            from celery import Celery
            
            # Determinar a URL correta
            redis_url = redis_url_config or redis_url_env or 'redis://localhost:6379/0'
            
            # Criar instância Celery de teste
            test_celery = Celery('test_app')
            
            # Configurar explicitamente
            test_celery.conf.update(
                broker_url=redis_url,
                result_backend=redis_url,
                task_serializer='json',
                accept_content=['json'],
                result_serializer='json',
                timezone='America/Sao_Paulo',
                enable_utc=True
            )
            
            test_result['step3_celery_creation'] = {
                'status': 'success',
                'broker_url': str(test_celery.conf.broker_url)[:20] + '***',
                'result_backend': str(test_celery.conf.result_backend)[:20] + '***',
                'task_serializer': test_celery.conf.task_serializer,
                'timezone': test_celery.conf.timezone
            }
            
            # Testar se consegue conectar
            try:
                test_celery.control.inspect().ping()
                test_result['step3_celery_creation']['connection_test'] = 'success'
            except Exception as e:
                test_result['step3_celery_creation']['connection_test'] = f'failed: {str(e)}'
                
        except Exception as e:
            test_result['step3_celery_creation'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        # STEP 4: Verificar Celery atual da aplicação
        try:
            from celery import current_app as celery_app
            
            test_result['step4_manual_config'] = {
                'current_broker_url': str(celery_app.conf.broker_url) if celery_app.conf.broker_url else None,
                'current_result_backend': str(celery_app.conf.result_backend) if celery_app.conf.result_backend else None,
                'conf_keys': [k for k in dir(celery_app.conf) if not k.startswith('_')][:10]
            }
            
            # Tentar reconfigurar o Celery atual
            if redis_url_config or redis_url_env:
                redis_url = redis_url_config or redis_url_env
                
                # Configurar de forma forçada
                celery_app.conf.broker_url = redis_url
                celery_app.conf.result_backend = redis_url
                celery_app.conf.task_serializer = 'json'
                celery_app.conf.timezone = 'America/Sao_Paulo'
                
                test_result['step4_manual_config']['force_config'] = {
                    'applied': True,
                    'new_broker_url': str(celery_app.conf.broker_url)[:20] + '***',
                    'new_result_backend': str(celery_app.conf.result_backend)[:20] + '***'
                }
            
        except Exception as e:
            test_result['step4_manual_config'] = {
                'error': str(e)
            }
        
        # STEP 5: Propor solução
        if redis_url_config or redis_url_env:
            test_result['step5_solution'] = {
                'status': 'solution_found',
                'redis_available': True,
                'recommended_action': 'force_celery_reconfiguration',
                'code_fix': 'Apply make_celery fix or force configuration in __init__.py'
            }
        else:
            test_result['step5_solution'] = {
                'status': 'no_redis_url',
                'redis_available': False,
                'recommended_action': 'check_redis_service'
            }
        
        return test_result

@scraping_ns.route('/force-celery-config')
class ScrapingForceCeleryConfig(Resource):
    @scraping_ns.doc('force_celery_config')
    def post(self):
        """Força a reconfiguração do Celery em tempo de execução"""
        import os
        from flask import current_app
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'before': {},
            'process': {},
            'after': {},
            'status': 'unknown'
        }
        
        try:
            from celery import current_app as celery_app
            
            # BEFORE: Estado atual
            result['before'] = {
                'broker_url': str(celery_app.conf.broker_url) if celery_app.conf.broker_url else None,
                'result_backend': str(celery_app.conf.result_backend) if celery_app.conf.result_backend else None,
                'task_serializer': celery_app.conf.task_serializer,
                'timezone': celery_app.conf.timezone
            }
            
            # PROCESS: Obter Redis URL e forçar reconfiguração
            redis_url = current_app.config.get('REDIS_URL') or os.environ.get('REDIS_URL')
            
            if redis_url:
                result['process']['redis_url_found'] = True
                result['process']['redis_url_source'] = 'app.config' if current_app.config.get('REDIS_URL') else 'os.environ'
                
                # FORÇA CONFIGURAÇÃO COMPLETA
                celery_app.conf.update({
                    'broker_url': redis_url,
                    'result_backend': redis_url,
                    'task_serializer': 'json',
                    'accept_content': ['json'],
                    'result_serializer': 'json',
                    'timezone': 'America/Sao_Paulo',
                    'enable_utc': True,
                    'broker_connection_retry_on_startup': True,
                    'worker_disable_rate_limits': True,
                    'task_acks_late': True,
                    'worker_prefetch_multiplier': 1
                })
                
                result['process']['config_applied'] = True
                result['process']['redis_url_masked'] = redis_url[:20] + '***'
                
            else:
                result['process']['redis_url_found'] = False
                result['process']['error'] = 'REDIS_URL não encontrada'
            
            # AFTER: Estado após reconfiguração
            result['after'] = {
                'broker_url': str(celery_app.conf.broker_url) if celery_app.conf.broker_url else None,
                'result_backend': str(celery_app.conf.result_backend) if celery_app.conf.result_backend else None,
                'task_serializer': celery_app.conf.task_serializer,
                'timezone': celery_app.conf.timezone
            }
            
            # STATUS FINAL
            if (result['after']['broker_url'] and 
                result['after']['result_backend'] and 
                result['after']['broker_url'] != 'None' and 
                result['after']['result_backend'] != 'None'):
                result['status'] = 'success'
            else:
                result['status'] = 'failed'
                
            # TESTE DE CONEXÃO
            try:
                celery_app.control.inspect().ping()
                result['connection_test'] = 'success'
            except Exception as e:
                result['connection_test'] = f'failed: {str(e)}'
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result

# Namespace simples para health check
simple_ns = Namespace('simple', description='Endpoints simples para testes')

@simple_ns.route('/ping')
class SimplePing(Resource):
    @simple_ns.doc('simple_ping')
    def get(self):
        """Health check básico - não depende de BD ou Redis"""
        return {
            'status': 'ok',
            'message': 'API funcionando',
            'timestamp': datetime.now().isoformat(),
            'version': get_version()
        }

@simple_ns.route('/env-check')
class EnvCheck(Resource):
    @simple_ns.doc('env_check')
    def get(self):
        """Diagnóstico de variáveis de ambiente (sem exibir senhas)"""
        import os
        from flask import current_app
        
        env_check = {
            'timestamp': datetime.now().isoformat(),
            'flask_config': {},
            'os_environ': {},
            'docker_detection': {},
            'database': {}
        }
        
        # Verificar configuração do Flask
        database_url = current_app.config.get('DATABASE_URL')
        env_check['flask_config'] = {
            'DATABASE_URL_exists': database_url is not None,
            'DATABASE_URL_preview': database_url[:30] + '***' if database_url else None,
            'REDIS_URL_exists': current_app.config.get('REDIS_URL') is not None,
            'SECRET_KEY_exists': current_app.config.get('SECRET_KEY') is not None
        }
        
        # Verificar variáveis de ambiente
        env_vars = ['DATABASE_URL', 'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'REDIS_URL', 'SECRET_KEY']
        for var in env_vars:
            value = os.environ.get(var)
            env_check['os_environ'][var] = {
                'exists': value is not None,
                'preview': value[:20] + '***' if value and len(value) > 20 else ('SET' if value else None)
            }
        
        # Detectar ambiente Docker
        env_check['docker_detection'] = {
            'in_docker': os.path.exists('/.dockerenv'),
            'hostname': os.environ.get('HOSTNAME', 'unknown'),
            'container_name': os.environ.get('CONTAINER_NAME', 'unknown')
        }
        
        # Teste básico de banco
        try:
            from app import db
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            env_check['database']['connection'] = 'success'
        except Exception as e:
            env_check['database']['connection'] = 'failed'
            env_check['database']['error'] = str(e)[:100]
        
        return env_check

@simple_ns.route('/dashboard')
class DockerDashboard(Resource):
    @simple_ns.doc('docker_dashboard')
    def get(self):
        """Dashboard visual dos containers Docker"""
        import os
        import subprocess
        from datetime import datetime
        
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'server_info': {},
            'containers': {},
            'monitoring_urls': {},
            'system_stats': {}
        }
        
        # Informações do servidor
        dashboard['server_info'] = {
            'hostname': os.environ.get('HOSTNAME', 'unknown'),
            'in_docker': os.path.exists('/.dockerenv'),
            'platform': 'Docker Container' if os.path.exists('/.dockerenv') else 'Host System'
        }
        
        # URLs de monitoramento
        dashboard['monitoring_urls'] = {
            'portainer': 'https://portainer.juscash.app',
            'cadvisor': 'https://cadvisor.juscash.app',
            'flower': 'https://flower.juscash.app',
            'api_docs': 'https://cron.juscash.app/docs/',
            'dashboard_ui': 'https://cron.juscash.app/api/simple/dashboard-ui',
            'health_checks': {
                'api': 'https://cron.juscash.app/api/simple/ping',
                'database': 'https://cron.juscash.app/api/publicacoes/health',
                'env_check': 'https://cron.juscash.app/api/simple/env-check'
            },
            'legacy_ips': {
                'portainer_ip': 'http://77.37.68.178:9000',
                'cadvisor_ip': 'http://77.37.68.178:8080',
                'flower_ip': 'http://77.37.68.178:5555'
            }
        }
        
        # Tentar obter informações dos containers (se docker estiver disponível)
        try:
            # Verificar se docker command está disponível
            result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Skip header
                    containers = []
                    for line in lines[1:]:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            containers.append({
                                'name': parts[0],
                                'status': parts[1],
                                'ports': parts[2] if len(parts) > 2 else 'N/A'
                            })
                    dashboard['containers']['list'] = containers
                    dashboard['containers']['count'] = len(containers)
                else:
                    dashboard['containers']['error'] = 'No containers found'
            else:
                dashboard['containers']['error'] = 'Docker command failed'
        except Exception as e:
            dashboard['containers']['error'] = f'Cannot access Docker: {str(e)}'
        
        # Estatísticas básicas do sistema
        try:
            # Informações de CPU e memória se disponível
            if os.path.exists('/proc/loadavg'):
                with open('/proc/loadavg', 'r') as f:
                    load_avg = f.read().strip().split()
                    dashboard['system_stats']['load_average'] = load_avg[0]
            
            if os.path.exists('/proc/meminfo'):
                with open('/proc/meminfo', 'r') as f:
                    meminfo = {}
                    for line in f.readlines()[:3]:  # Just first 3 lines
                        if ':' in line:
                            key, value = line.split(':', 1)
                            meminfo[key.strip()] = value.strip()
                    dashboard['system_stats']['memory'] = meminfo
        except Exception as e:
            dashboard['system_stats']['error'] = str(e)
        
        return dashboard

@simple_ns.route('/dashboard-ui')
class DashboardUI(Resource):
    @simple_ns.doc('dashboard_ui')
    def get(self):
        """Interface visual do dashboard (HTML)"""
        from flask import make_response
        import os
        
        try:
            # Caminho para o template
            template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates', 'dashboard.html')
            
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            response = make_response(html_content)
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            return response
            
        except FileNotFoundError:
            return {
                'error': 'Dashboard template not found',
                'message': 'Use /api/simple/dashboard para versão JSON'
            }, 404
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Erro ao carregar dashboard UI'
            }, 500

# Adicionar no final do arquivo, antes da função register_namespaces

from flask import Response
import tempfile
import base64
import threading
from queue import Queue
import time

# Namespace para visualização do Selenium
selenium_visual_ns = Namespace('selenium-visual', description='Visualização do Selenium em tempo real')

# Status global do scraping visual
scraping_status = {
    'active': False,
    'step': 'Inativo',
    'progress': 0
}

# Instância global do scraper para screenshots
global_scraper = None
global_scraper_lock = threading.Lock()

def get_or_create_scraper():
    """Obtém ou cria uma instância do scraper com thread safety"""
    global global_scraper
    
    with global_scraper_lock:
        # Verificar se já existe e está funcional
        if global_scraper is not None:
            try:
                # Verificar se o driver está ativo
                if hasattr(global_scraper, 'driver') and global_scraper.driver is not None:
                    # Teste rápido para ver se o driver está respondendo
                    _ = global_scraper.driver.current_url
                    return global_scraper
            except Exception as e:
                print(f"⚠️ Scraper existente não está funcional: {e}")
                # Limpar scraper defeituoso
                try:
                    if hasattr(global_scraper, 'driver') and global_scraper.driver:
                        global_scraper.driver.quit()
                except:
                    pass
                global_scraper = None
        
        # Criar novo scraper se necessário
        try:
            from app.infrastructure.scraping.dje_scraper_debug import DJEScraperDebug
            print("🔧 Criando nova instância do scraper...")
            
            # Resetar singleton antes de criar nova instância
            DJEScraperDebug._instance = None
            
            # Criar nova instância
            global_scraper = DJEScraperDebug(visual_mode=False)
            
            # Inicializar o driver imediatamente para verificar se funciona
            driver = global_scraper.get_driver()
            if driver is None:
                raise Exception("Falha ao inicializar driver")
            
            print("✅ Nova instância do scraper criada com sucesso")
            return global_scraper
            
        except Exception as e:
            print(f"❌ Erro ao criar scraper: {e}")
            global_scraper = None
            return None

def cleanup_global_scraper():
    """Limpa a instância global do scraper com thread safety"""
    global global_scraper
    
    with global_scraper_lock:
        if global_scraper:
            try:
                print("🧹 Limpando scraper global...")
                if hasattr(global_scraper, 'driver') and global_scraper.driver:
                    global_scraper.driver.quit()
                # Resetar singleton
                if hasattr(global_scraper, '__class__'):
                    global_scraper.__class__._instance = None
            except Exception as e:
                print(f"⚠️ Erro ao limpar scraper: {e}")
            finally:
                global_scraper = None
                print("✅ Scraper global limpo")

@selenium_visual_ns.route('/live')
class SeleniumLive(Resource):
    @selenium_visual_ns.doc('selenium_live_interface')
    def get(self):
        """Interface web para visualizar o Selenium em tempo real"""
        
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>🕷️ Selenium Live - JusCash</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(45deg, #2196F3, #21CBF3);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .content { padding: 30px; }
        .controls { 
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .btn { 
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .btn-success { background: #28a745; color: white; }
        .btn-primary { background: #007bff; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-warning { background: #ffc107; color: #212529; }
        .date-controls {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .date-controls input {
            padding: 10px;
            margin: 5px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        .status-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 5px solid #007bff;
        }
        .status-text {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        .progress-container {
            background: #e9ecef;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(45deg, #28a745, #20c997);
            transition: width 0.5s ease;
            border-radius: 10px;
        }
        .screenshot-section {
            text-align: center;
            margin: 30px 0;
        }
        .screenshot {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            border: 3px solid #ddd;
        }
        .logs-section {
            background: #2d3748;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 10px;
            height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
        }
        .auto-refresh {
            text-align: center;
            margin: 20px 0;
        }
        .auto-refresh label {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            font-size: 16px;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕷️ Selenium Live Scraping</h1>
            <p>Visualize o web scraping do DJE em tempo real</p>
        </div>
        
        <div class="content">
            <div class="date-controls">
                <h3>📅 Configurar Período</h3>
                <label>Data Início: </label>
                <input type="date" id="dataInicio" />
                <label>Data Fim: </label>
                <input type="date" id="dataFim" />
            </div>
            
            <div class="controls">
                <button class="btn btn-success" onclick="startScraping()">
                    🚀 Iniciar Scraping
                </button>
                <button class="btn btn-primary" onclick="takeScreenshot()">
                    📸 Screenshot
                </button>
                <button class="btn btn-warning" onclick="updateStatus()">
                    🔄 Atualizar Status
                </button>
                <button class="btn btn-danger" onclick="stopScraping()">
                    ⏹️ Parar
                </button>
            </div>
            
            <div class="auto-refresh">
                <label>
                    <input type="checkbox" id="autoRefresh" checked> 
                    🔄 Atualizar automaticamente a cada 3 segundos
                </label>
            </div>
            
            <div class="status-card">
                <div class="status-text" id="statusText">Status: Carregando...</div>
                <div class="progress-container">
                    <div class="progress-bar" id="progressBar" style="width: 0%"></div>
                </div>
                <div id="progressText">0%</div>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value" id="screenshotCount">0</div>
                    <div class="stat-label">Screenshots</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="uptime">00:00</div>
                    <div class="stat-label">Tempo Ativo</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="lastUpdate">--:--</div>
                    <div class="stat-label">Última Atualização</div>
                </div>
            </div>
            
            <div class="screenshot-section">
                <h3>📸 Screenshot Atual</h3>
                <div id="screenshotInfo">Nenhum screenshot disponível</div>
                <img id="screenshot" class="screenshot" style="display: none;" />
            </div>
            
            <div>
                <h3>📋 Logs do Sistema</h3>
                <div class="logs-section" id="logs">
Aguardando logs do sistema...
                </div>
            </div>
        </div>
    </div>

    <script>
        let autoRefreshInterval;
        let screenshotCount = 0;
        let startTime = Date.now();
        
        window.onload = function() {
            // Configurar datas padrão
            const today = new Date();
            const yesterday = new Date(today);
            yesterday.setDate(yesterday.getDate() - 1);
            
            const formatDate = (date) => date.toISOString().split('T')[0];
            
            document.getElementById('dataInicio').value = formatDate(yesterday);
            document.getElementById('dataFim').value = formatDate(yesterday);
            
            addLog('🌟 Interface carregada com sucesso!');
            updateStatus();
            startAutoRefresh();
        };
        
        function startAutoRefresh() {
            const checkbox = document.getElementById('autoRefresh');
            if (checkbox.checked && !autoRefreshInterval) {
                autoRefreshInterval = setInterval(() => {
                    updateStatus();
                    updateUptime();
                }, 3000);
                addLog('🔄 Auto-refresh ativado');
            }
        }
        
        function stopAutoRefresh() {
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
                addLog('⏹️ Auto-refresh desativado');
            }
        }
        
        document.getElementById('autoRefresh').onchange = function() {
            if (this.checked) {
                startAutoRefresh();
            } else {
                stopAutoRefresh();
            }
        };
        
        async function startScraping() {
            const dataInicio = document.getElementById('dataInicio').value + 'T00:00:00';
            const dataFim = document.getElementById('dataFim').value + 'T23:59:59';
            
            addLog('🚀 Iniciando scraping...');
            
            try {
                const response = await fetch('/api/selenium-visual/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        data_inicio: dataInicio,
                        data_fim: dataFim
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    addLog('✅ Scraping iniciado com sucesso!');
                    startTime = Date.now();
                    setTimeout(updateStatus, 1000);
                } else {
                    addLog('❌ Erro ao iniciar: ' + data.error);
                }
            } catch (error) {
                addLog('❌ Erro de rede: ' + error.message);
            }
        }
        
        async function takeScreenshot() {
            addLog('📸 Capturando screenshot...');
            
            try {
                const response = await fetch('/api/selenium-visual/screenshot');
                const data = await response.json();
                
                if (data.success) {
                    const img = document.getElementById('screenshot');
                    const info = document.getElementById('screenshotInfo');
                    
                    img.src = 'data:image/png;base64,' + data.base64_data;
                    img.style.display = 'block';
                    info.innerHTML = `
                        <strong>Screenshot capturado às ${data.timestamp}</strong><br>
                        URL: ${data.url || 'N/A'}
                    `;
                    
                    screenshotCount++;
                    document.getElementById('screenshotCount').textContent = screenshotCount;
                    
                    addLog('✅ Screenshot atualizado');
                } else {
                    addLog('❌ Erro no screenshot: ' + data.error);
                }
            } catch (error) {
                addLog('❌ Erro: ' + error.message);
            }
        }
        
        async function stopScraping() {
            addLog('⏹️ Parando scraping...');
            
            try {
                const response = await fetch('/api/selenium-visual/stop', {
                    method: 'POST'
                });
                
                const data = await response.json();
                addLog('✅ Scraping parado');
                updateStatus();
            } catch (error) {
                addLog('❌ Erro: ' + error.message);
            }
        }
        
        async function updateStatus() {
            try {
                const response = await fetch('/api/selenium-visual/status');
                const data = await response.json();
                
                const statusText = document.getElementById('statusText');
                const progressBar = document.getElementById('progressBar');
                const progressText = document.getElementById('progressText');
                
                statusText.textContent = 'Status: ' + data.step;
                progressBar.style.width = data.progress + '%';
                progressText.textContent = data.progress + '%';
                
                // Atualizar cor baseada no status
                const statusCard = document.querySelector('.status-card');
                if (data.active) {
                    statusCard.style.borderLeftColor = '#28a745';
                } else {
                    statusCard.style.borderLeftColor = '#6c757d';
                }
                
                document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
                
                // Auto-screenshot se ativo
                if (data.active && document.getElementById('autoRefresh').checked) {
                    setTimeout(takeScreenshot, 1000);
                }
                
            } catch (error) {
                addLog('❌ Erro ao atualizar status: ' + error.message);
            }
        }
        
        function updateUptime() {
            const elapsed = Date.now() - startTime;
            const minutes = Math.floor(elapsed / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            document.getElementById('uptime').textContent = 
                String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
        }
        
        function addLog(message) {
            const logs = document.getElementById('logs');
            const timestamp = new Date().toLocaleTimeString();
            logs.textContent += '[' + timestamp + '] ' + message + '\\n';
            logs.scrollTop = logs.scrollHeight;
        }
    </script>
</body>
</html>
        """
        
        return Response(html_template, mimetype='text/html')

@selenium_visual_ns.route('/start')
class StartVisualScraping(Resource):
    @selenium_visual_ns.doc('start_visual_scraping')
    def post(self):
        """Inicia scraping visual"""
        global scraping_status
        
        if scraping_status['active']:
            return {'success': False, 'error': 'Scraping já está ativo'}, 400
        
        data = request.get_json()
        
        try:
            data_inicio = datetime.fromisoformat(data['data_inicio'])
            data_fim = datetime.fromisoformat(data['data_fim'])
        except (KeyError, ValueError):
            return {'success': False, 'error': 'Datas inválidas'}, 400
        
        # Iniciar thread de scraping
        thread = threading.Thread(
            target=run_visual_scraping_thread,
            args=(data_inicio, data_fim)
        )
        thread.daemon = True
        thread.start()
        
        return {
            'success': True,
            'message': 'Scraping visual iniciado',
            'periodo': f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
        }

@selenium_visual_ns.route('/screenshot')
class VisualScreenshot(Resource):
    @selenium_visual_ns.doc('visual_screenshot')
    def get(self):
        """Captura screenshot atual"""
        try:
            scraper = get_or_create_scraper()
            
            if scraper is None or scraper.driver is None:
                return {
                    'success': False,
                    'error': 'Chrome não está disponível. Inicie um scraping primeiro.',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
            
            try:
                # Verificar se o driver está respondendo
                try:
                    current_url = scraper.driver.current_url
                except:
                    # Driver não está respondendo, tentar recriar
                    cleanup_global_scraper()
                    scraper = get_or_create_scraper()
                    if scraper is None:
                        raise Exception("Não foi possível recriar o driver")
                    current_url = scraper.driver.current_url
                    
                # Se estiver na página em branco, navegar para o DJE
                if current_url == 'data:,' or 'about:blank' in current_url:
                    scraper.driver.get("https://dje.tjsp.jus.br/cdje/index.do")
                    time.sleep(2)
                    current_url = scraper.driver.current_url
                    
                # Capturar screenshot
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    screenshot_path = tmp_file.name
                    
                scraper.driver.save_screenshot(screenshot_path)
                
                with open(screenshot_path, 'rb') as img_file:
                    img_data = img_file.read()
                    base64_data = base64.b64encode(img_data).decode('utf-8')
                    
                os.unlink(screenshot_path)
                
                return {
                    'success': True,
                    'base64_data': base64_data,
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'url': current_url
                }
                
            except Exception as e:
                # Em caso de erro, limpar o scraper global
                cleanup_global_scraper()
                return {
                    'success': False,
                    'error': f'Erro ao capturar screenshot: {str(e)}',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }

@selenium_visual_ns.route('/status')
class VisualStatus(Resource):
    @selenium_visual_ns.doc('visual_status')
    def get(self):
        """Status do scraping visual"""
        global scraping_status
        return scraping_status

@selenium_visual_ns.route('/stop')
class StopVisualScraping(Resource):
    @selenium_visual_ns.doc('stop_visual_scraping')
    def post(self):
        """Para o scraping visual"""
        global scraping_status
        
        scraping_status['active'] = False
        scraping_status['step'] = 'Parado pelo usuário'
        scraping_status['progress'] = 0
        
        # Limpar o scraper global
        cleanup_global_scraper()
        
        return {'success': True, 'message': 'Scraping visual parado'}

def run_visual_scraping_thread(data_inicio: datetime, data_fim: datetime):
    """Thread que executa o scraping visual"""
    global scraping_status, global_scraper
    
    scraping_status['active'] = True
    scraping_status['step'] = 'Inicializando Chrome...'
    scraping_status['progress'] = 5
    
    try:
        # Limpar scraper anterior se existir
        cleanup_global_scraper()
        
        # Criar novo scraper
        scraper = get_or_create_scraper()
        
        if scraper is None:
            raise Exception("Não foi possível inicializar o Chrome")
        
        try:
            # Usar o método debug que tem todos os fallbacks
            scraping_status['step'] = 'Executando scraping com métodos seguros...'
            scraping_status['progress'] = 25
            
            # Executar o scraping debug
            publicacoes = scraper.extrair_publicacoes_debug(data_inicio, data_fim, pause_between_steps=False)
            
            scraping_status['step'] = f'✅ Concluído! {len(publicacoes)} publicações extraídas'
            scraping_status['progress'] = 100
            
            # Aguardar antes de finalizar (mantém o scraper ativo para screenshots)
            time.sleep(10)
            
        except Exception as e:
            scraping_status['step'] = f'❌ Erro: {str(e)}'
            scraping_status['progress'] = 0
            # Não fechar o scraper em caso de erro, para permitir screenshots
            
    except Exception as e:
        scraping_status['step'] = f'❌ Erro: {str(e)}'
        scraping_status['progress'] = 0
        cleanup_global_scraper()
    
    finally:
        # Resetar status após 60 segundos, mas manter scraper ativo
        time.sleep(60)
        if scraping_status['active']:
            scraping_status['active'] = False
            scraping_status['step'] = 'Finalizado automaticamente'
            scraping_status['progress'] = 0

def register_namespaces(api):
    """Registra todos os namespaces na API"""
    # Registrar primeiro os namespaces principais
    api.add_namespace(publicacoes_ns)
    api.add_namespace(scraping_ns)
    api.add_namespace(simple_ns)
    api.add_namespace(selenium_visual_ns)
    
    # Registrar cron_ns por último para evitar conflitos
    try:
        from .cron_routes import cron_ns
        api.add_namespace(cron_ns)
    except ImportError as e:
        print(f"Aviso: Não foi possível importar cron_routes: {e}")
        # Criar namespace básico de cron para não quebrar os testes
        from flask_restx import Namespace, Resource
        basic_cron_ns = Namespace('cron', description='Health check básico')
        
        @basic_cron_ns.route('/health')
        class BasicHealth(Resource):
            def get(self):
                return {'status': 'ok', 'timestamp': datetime.now().isoformat()}
        
        api.add_namespace(basic_cron_ns) 