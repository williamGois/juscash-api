web: python -m pip install -r requirements.txt --quiet && python create-tables.py && python simple-start.py
worker: celery -A celery_worker.celery worker --loglevel=info --concurrency=1
beat: celery -A celery_worker.celery beat --loglevel=info
flower: python flower-railway.py 