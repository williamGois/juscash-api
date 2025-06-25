web: python railway-production.py
worker: celery -A celery_worker.celery worker --loglevel=info --concurrency=1
beat: celery -A celery_worker.celery beat --loglevel=info
flower: python flower-railway.py 