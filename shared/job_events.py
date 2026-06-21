# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/job_events.py
# # AR Celery workers
# # KW مهمة,job
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/job_events.py
# # AR Celery workers
# # KW مهمة,job
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/job_events.py
# # AR Celery workers
# # KW مهمة,job
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/job_events.py
# # AR Celery workers
# # KW مهمة,job
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/job_events.py
# # AR وحدة الدبلجة — رفع، بدء مهمة، polling، أصوات
# # CONVENTION — # FN / # AR فوق كل دالة، # قبل كل خطوة — see FUNCTION_INDEX.md
# shared/job_events.py — Redis pub/sub for SSE job status
import json
import logging

import redis

from shared import config

logger = logging.getLogger(__name__)


# # FN job_channel
# # AR job channel (job_channel)
# # FN job_channel
# # AR مهام المعالجة (job_channel)
# # KW مهمة,job,polling,celery,worker
# # FN job_channel
# # AR مهام المعالجة (job_channel)
# # KW مهمة,job,polling,celery,worker
# # FN job_channel
# # AR مهام المعالجة (job_channel)
# # KW مهمة,job,polling,celery,worker
# # FN job_channel
# # AR مهام المعالجة (job_channel)
# # KW مهمة,job,polling,celery,worker
def job_channel(job_id: str) -> str:
    # # return — إرجاع النتيجة
    return f"job:{job_id}"


# # FN publish_job_status
# # AR publish job status (publish_job_status)
# # FN publish_job_status
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # AR مهام المعالجة (publish_job_status)
# # KW مهمة,job,polling,celery,worker,حالة,webhook,SSE,status
# # FN publish_job_status
# # block — enqueue Celery
# # AR مهام المعالجة (publish_job_status)
# # block — enqueue Celery
# # KW مهمة,job,polling,celery,worker,حالة,webhook,SSE,status
# # FN publish_job_status
# # AR مهام المعالجة (publish_job_status)
# # KW مهمة,job,polling,celery,worker,حالة,webhook,SSE,status
# # block — enqueue Celery
# # FN publish_job_status
# # AR مهام المعالجة (publish_job_status)
# # KW مهمة,job,polling,celery,worker,حالة,webhook,SSE,status
def publish_job_status(job_id: str, payload: dict) -> None:
    """Publish job status so /api/dub/status SSE subscribers receive updates."""
    # # try — معالجة عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # block — معالجة أخطاء
    # # block — معالجة أخطاء
    # # try — عملية قد تفشل
    try:
        # # block — معالجة أخطاء
        client = redis.from_url(config.REDIS_URL, decode_responses=True)
        # # block — معالجة أخطاء
        # # block — معالجة أخطاء
        # # تسلسل JSON للطلب
        client.publish(job_channel(job_id), json.dumps(payload))
        # # block — parse/serialize JSON
        client.close()
    # # catch — التقاط الخطأ
    # # block — parse/serialize JSON
    # # block — parse/serialize JSON
    # # catch — التقاط خطأ
    # # catch — التقاط خطأ
    except Exception as exc:
        # # block — معالجة أخطاء
        # # block — parse/serialize JSON
        logger.warning("publish_job_status failed for %s: %s", job_id, exc)
