# shared/dub_webhook_url.py — Modal callback URL for dubbing worker
import os


def build_modal_dub_webhook_url(job_id: str) -> str:
    base = (
        os.environ.get("BACKEND_PUBLIC_URL")
        or os.environ.get("PUBLIC_API_URL")
        or os.environ.get("API_BASE_URL")
        or "https://api.glotix.ai"
    ).strip().rstrip("/")
    if not base:
        return ""
    return f"{base}/api/dub/webhook/{job_id}"
