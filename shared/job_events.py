# shared/job_events.py — Redis pub/sub for SSE job status
import json
import logging

import redis

from shared import config

logger = logging.getLogger(__name__)


def job_channel(job_id: str) -> str:
    return f"job:{job_id}"


def publish_job_status(job_id: str, payload: dict) -> None:
    """Publish job status so /api/dub/status SSE subscribers receive updates."""
    try:
        client = redis.from_url(config.REDIS_URL, decode_responses=True)
        client.publish(job_channel(job_id), json.dumps(payload))
        client.close()
    except Exception as exc:
        logger.warning("publish_job_status failed for %s: %s", job_id, exc)
