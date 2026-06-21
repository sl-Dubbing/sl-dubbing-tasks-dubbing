# # FILE backend/sl-dubbing-tasks-dubbing-main/tasks_dubbing.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/tasks_dubbing.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/tasks_dubbing.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/tasks_dubbing.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/tasks_dubbing.py
# # AR وحدة الدبلجة — رفع، بدء مهمة، polling، أصوات
# # CONVENTION — # FN / # AR فوق كل دالة، # قبل كل خطوة — see FUNCTION_INDEX.md
# tasks_dubbing.py — Celery dubbing worker: R2 → RunPod or Modal
import os
os.environ["SPEAKER_EMB_CACHE_DISABLED"] = "1"
os.environ["TORCHAUDIO_USE_TORCHCODEC"] = "0"
import logging

from flask import Flask

from shared import config
from shared.celery_setup import QUEUE_DUBBING, make_celery_app
from shared.dub_worker_submit import fail_dub_job_permanently, run_dub_worker_pipeline
from shared.job_events import publish_job_status
from shared.models import DubbingJob, db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

celery_app = make_celery_app("tasks-dubbing", queue_name=QUEUE_DUBBING)

flask_app = Flask(__name__)
flask_app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URL.replace(
    "postgres://", "postgresql://", 1,
)
flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(flask_app)


@celery_app.task(name="tasks_dubbing.process_dub", bind=True, max_retries=0)
# # FN process_dub
# # AR process dub (process_dub)
# # FN process_dub
# # AR دالة process_dub (process_dub)
# # KW عام,general
# # FN process_dub
# # AR دالة process_dub (process_dub)
# # KW عام,general
# # FN process_dub
# # AR دالة process_dub (process_dub)
# # KW عام,general
# # FN process_dub
# # AR دالة process_dub (process_dub)
# # KW عام,general
def process_dub(
    self,
    job_id,
    user_id,
    file_key,
    lang,
    # # block — رفع أو تخزين ملف
    # # block — رفع أو تخزين ملف
    # # block — رفع أو تخزين ملف
    # # block — معالجة صوت/استنساخ
    voice_config=None,
    return_video=True,
    **kwargs,
# # block — معالجة صوت/استنساخ
):
    # # block — معالجة صوت/استنساخ
    with flask_app.app_context():
        # # block — معالجة صوت/استنساخ
        job = DubbingJob.query.get(job_id)
        # # block — قاعدة بيانات
        # # block — قاعدة بيانات
        if not job:
            logger.error("Job %s not found", job_id)
            # # block — قاعدة بيانات
            return

        job.status = "processing"
        # # block — إرجاع نتيجة
        # # block — إرجاع نتيجة
        db.session.commit()
        publish_job_status(job_id, {"status": "processing"})

        # # block — معالجة أخطاء
        # # block — معالجة أخطاء
        # # try — عملية قد تفشل
        # # try — عملية قد تفشل
        # # block — معالجة أخطاء
        # # try — عملية قد تفشل
        # # try — عملية قد تفشل
        try:
            # # block — معالجة أخطاء
            run_dub_worker_pipeline(
                # # block — معالجة أخطاء
                # # block — معالجة أخطاء
                job,
                job_id,
                user_id,
                # # block — رفع أو تخزين ملف
                file_key,
                # # block — رفع أو تخزين ملف
                # # block — رفع أو تخزين ملف
                # # block — رفع أو تخزين ملف
                lang,
                voice_config,
                return_video,
                **kwargs,
            )
        # # block — معالجة صوت/استنساخ
        # # block — معالجة صوت/استنساخ
        # # block — معالجة صوت/استنساخ
        # # block — معالجة صوت/استنساخ
        # # catch — التقاط خطأ
        # # catch — التقاط خطأ
        except Exception as exc:
            # # block — معالجة أخطاء
            fail_dub_job_permanently(job, job_id, exc)
