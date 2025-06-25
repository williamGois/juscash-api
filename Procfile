web: ./railway-start.sh
worker: celery -A celery_worker.celery worker --loglevel=info --concurrency=1
beat: celery -A celery_worker.celery beat --loglevel=info
flower: flower -A celery_worker.celery --port=5555 --basic_auth=admin:admin123 