web: python -m pip install -r requirements.txt --quiet && python create-tables.py && python simple-start.py
worker: celery -A celery_worker.celery worker -B --loglevel=info --concurrency=1
flower: python flower-railway.py 