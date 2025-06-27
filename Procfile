web: gunicorn --bind 0.0.0.0:5000 --worker-class gthread --threads 4 --timeout 120 run:main()
worker: celery -A celery_worker.celery worker -B --loglevel=info --concurrency=1
flower: python flower-start.py