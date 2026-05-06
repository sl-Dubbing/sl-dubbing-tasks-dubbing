# shared/celery_setup.py
"""
🎯 Celery configuration - مشترك بين كل الـ workers

كل worker له queue منفصل:
  - dubbing  → sl-dubbing-tasks-dubbing
  - tts      → sl-dubbing-tasks-tts  
  - stt      → sl-dubbing-tasks-stt

عندما web يرسل task، يحدّد الـ queue.
كل worker يستمع لـ queue واحد فقط.
"""
from celery import Celery
from . import config


# ==========================================
# 🎯 Queue Names (مشترك بين كل الـ services)
# ==========================================
QUEUE_DUBBING = 'dubbing'
QUEUE_TTS = 'tts'
QUEUE_STT = 'stt'


def make_celery_app(name='shared', queue_name=None):
    """
    🚀 ينشئ Celery app
    
    Args:
        name: اسم الـ app (مثل: 'tasks-dubbing')
        queue_name: queue الذي يستمع له هذا worker
                    إذا None → web app (يرسل فقط لا يستقبل)
    
    استخدام:
        # في tasks_dubbing/tasks.py
        celery_app = make_celery_app('tasks-dubbing', queue_name=QUEUE_DUBBING)
        
        # في app.py (web)
        celery_app = make_celery_app('web')  # يرسل tasks فقط
    """
    app = Celery(
        name,
        broker=config.REDIS_URL,
        backend=config.REDIS_URL,
    )
    
    # إعدادات عامة
    app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        task_reject_on_worker_lost=True,
        task_time_limit=1800,  # 30 دقيقة max
        task_soft_time_limit=1500,
        # 🎯 مهم جداً: route كل task للـ queue المناسب
        task_routes={
            'tasks_dubbing.*': {'queue': QUEUE_DUBBING},
            'tasks_tts.*': {'queue': QUEUE_TTS},
            'tasks_stt.*': {'queue': QUEUE_STT},
        },
    )
    
    # إذا worker محدد، نخبره فقط يستمع لـ queue معيّن
    if queue_name:
        app.conf.task_default_queue = queue_name
        app.conf.task_queues = {
            queue_name: {
                'exchange': queue_name,
                'routing_key': queue_name,
            },
        }
    
    return app


# ==========================================
# 📤 Helper: send task from web to worker
# ==========================================
def send_task(task_name, queue, args=None, kwargs=None, **options):
    """
    🚀 يرسل task لـ queue معيّن
    
    استخدام في web app:
        send_task('tasks_dubbing.process_dub', QUEUE_DUBBING, kwargs={...})
    """
    app = make_celery_app('web-sender')
    return app.send_task(
        task_name,
        args=args or [],
        kwargs=kwargs or {},
        queue=queue,
        **options
    )
