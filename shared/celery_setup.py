# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/celery_setup.py
# # AR Celery workers
# # KW مهمة,job
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/celery_setup.py
# # AR Celery workers
# # KW مهمة,job
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/celery_setup.py
# # AR Celery workers
# # KW مهمة,job
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/celery_setup.py
# # AR Celery workers
# # KW مهمة,job
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/celery_setup.py
# # AR وحدة الدبلجة — رفع، بدء مهمة، polling، أصوات
# # CONVENTION — # FN / # AR فوق كل دالة، # قبل كل خطوة — see FUNCTION_INDEX.md
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

# # FN make_celery_app
# # AR make celery app (make_celery_app)
# # FN make_celery_app
# # AR مهام المعالجة (make_celery_app)
# # KW مهمة,job,polling,celery,worker
# # FN make_celery_app
# # AR مهام المعالجة (make_celery_app)
# # KW مهمة,job,polling,celery,worker
# # FN make_celery_app
# # AR مهام المعالجة (make_celery_app)
# # KW مهمة,job,polling,celery,worker
# # FN make_celery_app
# # AR مهام المعالجة (make_celery_app)
# # KW مهمة,job,polling,celery,worker
def make_celery_app(name='sl-dubbing-app', task_module=None, queue_name=None):
    include_list = [task_module] if task_module else []
    
    app = Celery(
        name,
        broker=config.REDIS_URL,
        backend=config.REDIS_URL,
        # # block — enqueue Celery
        # # block — enqueue Celery
        # # block — enqueue Celery
        # # block — enqueue Celery
        include=include_list
    )
    
    app.conf.update(
        # # block — enqueue Celery
        task_serializer='json',
        # # block — enqueue Celery
        accept_content=['json'],
        # # block — تنفيذ منطق — راجع الأسطر التالية
        result_serializer='json',
        # # block — تنفيذ منطق — راجع الأسطر التالية
        # # block — enqueue Celery
        timezone='UTC',
        enable_utc=True,
        # # block — تنفيذ منطق — راجع الأسطر التالية
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        # # block — تنفيذ منطق — راجع الأسطر التالية
        # # block — تنفيذ منطق — راجع الأسطر التالية
        task_reject_on_worker_lost=True,
    )
    
    # # block — تنفيذ منطق — راجع الأسطر التالية
    # # block — تنفيذ منطق — راجع الأسطر التالية
    if queue_name:
        app.conf.task_default_queue = queue_name
    # # block — إرجاع نتيجة
    # # return — إرجاع النتيجة
    # # block — إرجاع نتيجة
    return app

# كائن افتراضي للباك-إند
celery_app = make_celery_app('tasks-dubbing', queue_name=QUEUE_DUBBING)
