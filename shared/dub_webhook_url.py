# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/dub_webhook_url.py
# # AR Celery workers
# # KW حالة,webhook
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/dub_webhook_url.py
# # AR Celery workers
# # KW حالة,webhook
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/dub_webhook_url.py
# # AR وحدة الدبلجة — رفع، بدء مهمة، polling، أصوات
# # CONVENTION — # FN / # AR فوق كل دالة، # قبل كل خطوة — see FUNCTION_INDEX.md
# shared/dub_webhook_url.py — Modal callback URL for dubbing worker
import os


# # FN build_modal_dub_webhook_url
# # AR بناء modal dub webhook url (build_modal_dub_webhook_url)
# # FN build_modal_dub_webhook_url
# # AR Local/Cloud parity (build_modal_dub_webhook_url)
# # KW تنفيذ,local,cloud,modal,parity,حالة,webhook,SSE,status
# # FN build_modal_dub_webhook_url
# # AR Local/Cloud parity (build_modal_dub_webhook_url)
# # KW تنفيذ,local,cloud,modal,parity,حالة,webhook,SSE,status
def build_modal_dub_webhook_url(job_id: str) -> str:
    base = (
        os.environ.get("BACKEND_PUBLIC_URL")
        or os.environ.get("PUBLIC_API_URL")
        or os.environ.get("API_BASE_URL")
        or "https://api.glotix.ai"
    # # block — تنفيذ منطق — راجع الأسطر التالية
    # # block — تنفيذ منطق — راجع الأسطر التالية
    ).strip().rstrip("/")
    if not base:
        # # return — إرجاع النتيجة
        return ""
    # # return — إرجاع النتيجة
    # # block — إرجاع نتيجة
    return f"{base}/api/dub/webhook/{job_id}"
