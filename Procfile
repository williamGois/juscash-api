web: flask upgrade-db && python railway-production.py
worker: celery -A celery_worker.celery worker --loglevel=info --concurrency=1
beat: celery -A celery_worker.celery beat --loglevel=info
flower: celery -A celery_worker.celery flower --port=5555 