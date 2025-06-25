web: ./railway-start.sh
worker: celery -A celery_worker.celery worker --loglevel=info --concurrency=1
beat: celery -A celery_worker.celery beat --loglevel=info
flower: python flower-start.py 