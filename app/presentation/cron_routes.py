from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from app.tasks.scraping_tasks import extract_daily_publicacoes, extract_full_period_publicacoes, extract_custom_period_publicacoes
from app.tasks.maintenance_tasks import cleanup_old_logs, generate_daily_stats, health_check
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
            task = extract_daily_publicacoes.delay()
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
            task = extract_full_period_publicacoes.delay()
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
            
            # Validar formato das datas
            try:
                datetime.strptime(data_inicio_str, '%Y-%m-%d')
                datetime.strptime(data_fim_str, '%Y-%m-%d')
            except ValueError:
                return {
                    'task_id': None,
                    'status': 'error',
                    'message': 'Formato de data inválido. Use YYYY-MM-DD'
                }, 400
            
            task = extract_custom_period_publicacoes.delay(
                data_inicio_str + 'T00:00:00',
                data_fim_str + 'T23:59:59'
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
            task = cleanup_old_logs.delay()
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
            task = generate_daily_stats.delay()
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
            result = health_check.delay()
            return result.get(timeout=30)  # Aguardar até 30 segundos
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Erro no health check: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, 500

@cron_ns.route('/tasks/<string:task_id>')
class TaskStatus(Resource):
    @cron_ns.doc('get_task_status')
    def get(self, task_id):
        """Verificar status de uma tarefa específica"""
        from celery.result import AsyncResult
        from app import celery
        
        task = AsyncResult(task_id, app=celery)
        
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Tarefa pendente'
            }
        elif task.state == 'PROGRESS':
            response = {
                'state': task.state,
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 1),
                'status': task.info.get('status', '')
            }
        elif task.state == 'SUCCESS':
            response = {
                'state': task.state,
                'result': task.result
            }
        else:  # FAILURE
            response = {
                'state': task.state,
                'error': str(task.info)
            }
        
        return response 