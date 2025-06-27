from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from datetime import datetime

cron_ns = Namespace('cron', description='Operações de agendamento e manutenção')

task_result_model = cron_ns.model('TaskResult', {
    'task_id': fields.String(required=True, description='ID da tarefa'),
    'status': fields.String(required=True, description='Status da tarefa'),
    'message': fields.String(required=True, description='Mensagem de resultado')
})

custom_period_model = cron_ns.model('CustomPeriod', {
    'data_inicio': fields.String(required=True, description='Data início (YYYY-MM-DD)', example='2024-10-01'),
    'data_fim': fields.String(required=True, description='Data fim (YYYY-MM-DD)', example='2024-10-31')
})

@cron_ns.route('/scraping/daily')
class DailyScraping(Resource):
    @cron_ns.doc('trigger_daily_scraping')
    @cron_ns.marshal_with(task_result_model)
    def post(self):
        """Executar raspagem diária manualmente"""
        try:
            from celery import current_app as celery_app
            task = celery_app.send_task('app.tasks.scraping_tasks.extract_daily_publicacoes')
            return {
                'task_id': task.id,
                'status': 'started',
                'message': 'Raspagem diária iniciada'
            }
        except Exception as e:
            return {
                'task_id': None,
                'status': 'error',  
                'message': f'Erro ao iniciar raspagem diária: {str(e)}'
            }, 500

@cron_ns.route('/scraping/full-period')
class FullPeriodScraping(Resource):
    @cron_ns.doc('trigger_full_period_scraping')
    @cron_ns.marshal_with(task_result_model)
    def post(self):
        """Executar raspagem do período completo manualmente"""
        try:
            from celery import current_app as celery_app
            task = celery_app.send_task('app.tasks.scraping_tasks.extract_full_period_publicacoes')
            return {
                'task_id': task.id,
                'status': 'started',
                'message': 'Raspagem do período completo iniciada'
            }
        except Exception as e:
            return {
                'task_id': None,
                'status': 'error',
                'message': f'Erro ao iniciar raspagem completa: {str(e)}'
            }, 500

@cron_ns.route('/scraping/custom-period')
class CustomPeriodScraping(Resource):
    @cron_ns.doc('trigger_custom_period_scraping')
    @cron_ns.expect(custom_period_model)
    @cron_ns.marshal_with(task_result_model)
    def post(self):
        """Executar raspagem de período customizado"""
        try:
            data = request.get_json()
            data_inicio_str = data['data_inicio']
            data_fim_str = data['data_fim']
            
            try:
                datetime.strptime(data_inicio_str, '%Y-%m-%d')
                datetime.strptime(data_fim_str, '%Y-%m-%d')
            except ValueError:
                return {
                    'task_id': None,
                    'status': 'error',
                    'message': 'Formato de data inválido. Use YYYY-MM-DD'
                }, 400
            
            from celery import current_app as celery_app
            task = celery_app.send_task(
                'app.tasks.scraping_tasks.extract_custom_period_publicacoes',
                args=[data_inicio_str + 'T00:00:00', data_fim_str + 'T23:59:59']
            )
            
            return {
                'task_id': task.id,
                'status': 'started',
                'message': f'Raspagem customizada iniciada para período {data_inicio_str} a {data_fim_str}'
            }
            
        except Exception as e:
            return {
                'task_id': None,
                'status': 'error',
                'message': f'Erro ao iniciar raspagem customizada: {str(e)}'
            }, 500

@cron_ns.route('/maintenance/cleanup')
class CleanupLogs(Resource):
    @cron_ns.doc('trigger_cleanup')
    @cron_ns.marshal_with(task_result_model)
    def post(self):
        """Executar limpeza de logs manualmente"""
        try:
            from celery import current_app as celery_app
            task = celery_app.send_task('app.tasks.maintenance_tasks.cleanup_old_logs')
            return {
                'task_id': task.id,
                'status': 'started',
                'message': 'Limpeza de logs iniciada'
            }
        except Exception as e:
            return {
                'task_id': None,
                'status': 'error',
                'message': f'Erro ao iniciar limpeza: {str(e)}'
            }, 500

@cron_ns.route('/maintenance/stats')
class DailyStats(Resource):
    @cron_ns.doc('generate_stats')
    @cron_ns.marshal_with(task_result_model)
    def post(self):
        """Gerar estatísticas diárias manualmente"""
        try:
            from celery import current_app as celery_app
            task = celery_app.send_task('app.tasks.maintenance_tasks.generate_daily_stats')
            return {
                'task_id': task.id,
                'status': 'started',
                'message': 'Geração de estatísticas iniciada'
            }
        except Exception as e:
            return {
                'task_id': None,
                'status': 'error',
                'message': f'Erro ao gerar estatísticas: {str(e)}'
            }, 500

@cron_ns.route('/health')
class HealthCheck(Resource):
    @cron_ns.doc('health_check')
    def get(self):
        """Verificar saúde do sistema"""
        try:
            from app.tasks.maintenance_tasks import health_check
            result = health_check()
            return result
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Erro no health check: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, 500

@cron_ns.route('/tasks/active')
class ActiveTasks(Resource):
    @cron_ns.doc('list_active_tasks')
    def get(self):
        """Lista todas as tarefas ativas no Celery"""
        try:
            from celery import current_app as celery_app
            
            # Obter inspect instance
            inspect = celery_app.control.inspect()
            
            # Obter tarefas ativas
            active_tasks = inspect.active()
            scheduled_tasks = inspect.scheduled()
            reserved_tasks = inspect.reserved()
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'workers': {},
                'summary': {
                    'total_workers': 0,
                    'total_active': 0,
                    'total_scheduled': 0,
                    'total_reserved': 0
                }
            }
            
            # Processar tarefas ativas
            if active_tasks:
                for worker, tasks in active_tasks.items():
                    result['workers'][worker] = {
                        'active': tasks,
                        'scheduled': scheduled_tasks.get(worker, []) if scheduled_tasks else [],
                        'reserved': reserved_tasks.get(worker, []) if reserved_tasks else []
                    }
                    result['summary']['total_active'] += len(tasks)
                    
            # Processar tarefas agendadas
            if scheduled_tasks:
                for worker, tasks in scheduled_tasks.items():
                    if worker not in result['workers']:
                        result['workers'][worker] = {'active': [], 'scheduled': tasks, 'reserved': []}
                    else:
                        result['workers'][worker]['scheduled'] = tasks
                    result['summary']['total_scheduled'] += len(tasks)
                    
            # Processar tarefas reservadas
            if reserved_tasks:
                for worker, tasks in reserved_tasks.items():
                    if worker not in result['workers']:
                        result['workers'][worker] = {'active': [], 'scheduled': [], 'reserved': tasks}
                    else:
                        result['workers'][worker]['reserved'] = tasks
                    result['summary']['total_reserved'] += len(tasks)
            
            result['summary']['total_workers'] = len(result['workers'])
            
            return result
            
        except Exception as e:
            return {
                'error': f'Erro ao listar tarefas ativas: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, 500

@cron_ns.route('/workers/stats')
class WorkerStats(Resource):
    @cron_ns.doc('get_worker_stats')
    def get(self):
        """Estatísticas dos workers Celery"""
        try:
            from celery import current_app as celery_app
            
            inspect = celery_app.control.inspect()
            
            # Obter estatísticas
            stats = inspect.stats()
            registered_tasks = inspect.registered()
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'workers': stats or {},
                'registered_tasks': registered_tasks or {},
                'summary': {
                    'total_workers': len(stats) if stats else 0,
                    'workers_online': list(stats.keys()) if stats else []
                }
            }
            
            return result
            
        except Exception as e:
                         return {
                 'error': f'Erro ao obter estatísticas dos workers: {str(e)}',
                 'timestamp': datetime.now().isoformat()
             }, 500

@cron_ns.route('/tasks/<string:task_id>')
class TaskStatus(Resource):
    @cron_ns.doc('get_task_status')
    def get(self, task_id):
        """Verificar status de uma tarefa específica"""
        try:
            from celery.result import AsyncResult
            from celery import current_app as celery_app
            
            task = AsyncResult(task_id, app=celery_app)
            
            if task.state == 'PENDING':
                response = {
                    'state': task.state,
                    'status': 'Tarefa pendente'
                }
            elif task.state == 'PROGRESS':
                response = {
                    'state': task.state,
                    'current': task.info.get('current', 0) if task.info else 0,
                    'total': task.info.get('total', 1) if task.info else 1,
                    'status': task.info.get('status', '') if task.info else ''
                }
            elif task.state == 'SUCCESS':
                response = {
                    'state': task.state,
                    'result': task.result
                }
            else:
                response = {
                    'state': task.state,
                    'error': str(task.info) if task.info else 'Erro desconhecido'
                }
            
            return response
        except Exception as e:
            return {
                'state': 'ERROR',
                'error': f'Erro ao verificar status: {str(e)}'
            }, 500 