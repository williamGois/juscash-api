from flask import request
from flask_restx import Namespace, Resource, fields
from datetime import datetime
from app.domain.use_cases.extract_publicacoes_use_case import ExtractPublicacoesUseCase
from app.infrastructure.repositories.sqlalchemy_publicacao_repository import SQLAlchemyPublicacaoRepository
from app.infrastructure.scraping.dje_scraper import DJEScraper
from app.tasks.scraping_tasks import extract_publicacoes_task


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
            celery_app.control.inspect().ping()
            health_status['services']['redis'] = 'available'
            health_status['services']['celery'] = 'available'
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
        
        # Verificar Selenium
        try:
            from app.infrastructure.scraping.dje_scraper import DJEScraper
            scraper = DJEScraper()
            scraper.close()
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

def register_namespaces(api):
    """Registra todos os namespaces na API"""
    from .cron_routes import cron_ns
    
    api.add_namespace(publicacoes_ns)
    api.add_namespace(scraping_ns)
    api.add_namespace(cron_ns) 