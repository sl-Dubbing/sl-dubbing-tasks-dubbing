# shared/celery_setup.py — V2.1 (Universal Celery Factory)
import os
import sys
from celery import Celery
from . import config

root_path = os.path.abspath(os.getcwd())
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# أسماء الطوابير الموحدة
QUEUE_DUBBING = 'dubbing'
QUEUE_TTS = 'tts'
QUEUE_STT = 'stt'

def make_celery_app(name='sl-dubbing-app', task_module=None, queue_name=None):
    include_list = [task_module] if task_module else []
    
    app = Celery(
        name,
        broker=config.REDIS_URL,
        backend=config.REDIS_URL,
        include=include_list
    )
    
    app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        task_reject_on_worker_lost=True,
    )
    
    if queue_name:
        app.conf.task_default_queue = queue_name
    return app

# كائن افتراضي للباك-إند
celery_app = make_celery_app('web-gateway')
