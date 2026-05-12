# tasks_dubbing.py — V5.0 (With Quota Check & Email Notifications)
import os
import time
import logging
import requests
from datetime import datetime
from shared import config, r2_client, routing
from shared.celery_setup import make_celery_app, QUEUE_DUBBING
from shared.models import db, DubbingJob

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

celery_app = make_celery_app('tasks-dubbing', queue_name=QUEUE_DUBBING)

from flask import Flask
flask_app = Flask(__name__)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL.replace('postgres://', 'postgresql://', 1)
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(flask_app)

# ══════════════════════════════════════════
# Supabase Helpers
# ══════════════════════════════════════════
def _supa_headers():
    return {
        "apikey":        os.environ.get('SUPABASE_SERVICE_KEY', ''),
        "Authorization": f"Bearer {os.environ.get('SUPABASE_SERVICE_KEY', '')}",
        "Content-Type":  "application/json"
    }

def get_user_info(user_id: str) -> dict:
    try:
        url = os.environ.get('SUPABASE_URL', '')
        if not url or user_id == 'default_user':
            return {}
        res = requests.get(
            f"{url}/rest/v1/user_quotas?user_id=eq.{user_id}&select=*",
            headers=_supa_headers(), timeout=10
        )
        if res.ok and res.json():
            return res.json()[0]
    except Exception as e:
        logger.warning(f"⚠️ get_user_info failed: {e}")
    return {}


def update_dub_usage(user_id: str, seconds_used: int) -> dict:
    try:
        url = os.environ.get('SUPABASE_URL', '')
        if not url:
            return {}
        res = requests.post(
            f"{url}/rest/v1/rpc/increment_dub_usage",
            json={"p_user_id": user_id, "p_seconds": seconds_used},
            headers={**_supa_headers(), "Prefer": "return=representation"},
            timeout=10
        )
        if res.ok:
            return res.json() or {}
    except Exception as e:
        logger.warning(f"⚠️ update_dub_usage failed: {e}")
    return {}


def notify_quota_if_needed(user_info: dict, quota: dict):
    try:
        from email_service import send_quota_warning, send_quota_exhausted

        email   = user_info.get('email', '')
        name    = user_info.get('name', 'User')
        plan    = quota.get('plan', 'free')
        user_id = quota.get('user_id', '')

        if not email:
            return

        dub_used  = quota.get('dub_seconds_used', 0)
        dub_limit = quota.get('dub_seconds_limit', 1)
        tts_used  = quota.get('tts_chars_used', 0)
        tts_limit = quota.get('tts_chars_limit', 1)
        stt_used  = quota.get('stt_minutes_used', 0)
        stt_limit = quota.get('stt_minutes_limit', 1)
        dub_pct   = dub_used / dub_limit * 100 if dub_limit else 0

        reset_date = quota.get('reset_date', 'next month')
        try:
            reset_date = datetime.fromisoformat(
                str(reset_date).replace('Z', '')
            ).strftime("%b %d, %Y")
        except:
            pass

        if dub_pct >= 100:
            send_quota_exhausted(email, name, plan, reset_date)
            logger.info(f"📧 Quota exhausted → {email}")

        elif dub_pct >= 80 and not quota.get('warned_80'):
            send_quota_warning(
                email, name,
                tts_used, tts_limit,
                dub_used, dub_limit,
                stt_used, stt_limit,
                plan
            )
            logger.info(f"📧 Quota 80% warning → {email}")
            try:
                supa_url = os.environ.get('SUPABASE_URL', '')
                requests.patch(
                    f"{supa_url}/rest/v1/user_quotas?user_id=eq.{user_id}",
                    json={"warned_80": True},
                    headers=_supa_headers(), timeout=5
                )
            except:
                pass

    except Exception as e:
        logger.error(f"❌ notify_quota error: {e}")


# ══════════════════════════════════════════
# Backend Call (Modal / RunPod)
# ══════════════════════════════════════════
def call_backend(backend_url, payload, timeout=1500):
    if 'runpod.ai' in backend_url or 'runpod.io' in backend_url:
        headers = {
            'Authorization': f'Bearer {config.RUNPOD_API_KEY}',
            'Content-Type':  'application/json'
        }
        r = requests.post(
            f"{backend_url.rstrip('/')}/run",
            json={'input': payload}, headers=headers, timeout=60
        )
        r.raise_for_status()
        job_id = r.json().get('id')
        while True:
            status_data = requests.get(
                f"{backend_url.rstrip('/')}/status/{job_id}",
                headers=headers, timeout=30
            ).json()
            if status_data.get('status') == 'COMPLETED':
                return status_data.get('output')
            if status_data.get('status') in ['FAILED', 'CANCELLED']:
                raise Exception(f"RunPod failed: {status_data.get('error')}")
            time.sleep(5)
    else:
        r = requests.post(
            f"{backend_url.rstrip('/')}/upload-from-url",
            json=payload, timeout=timeout
        )
        r.raise_for_status()
        return r.json()


# ══════════════════════════════════════════
# Main Task
# ══════════════════════════════════════════
@celery_app.task(name='tasks_dubbing.process_dub', bind=True, max_retries=2)
def process_dub(self, job_id, user_id, file_key, lang, voice_config=None, return_video=True, **kwargs):
    with flask_app.app_context():
        job = DubbingJob.query.get(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        job.status = 'processing'
        db.session.commit()

        try:
            # 1. Generate download URL from R2
            media_url = r2_client.generate_download_url(file_key)
            if not media_url:
                raise Exception("Failed to generate media_url from R2")

            backend_url  = routing.get_dubbing_url()
            voice_source = voice_config.get('source', 'original') if voice_config else 'original'
            sample_file  = voice_config.get('file') if voice_config else None

            payload = {
                'media_url':    media_url,
                'lang':         lang,
                'voice_source': voice_source,
                'sample_file':  sample_file,
                'engine':       kwargs.get('engine', 'xtts'),
                'return_video': return_video
            }

            # 2. Send to backend
            data = call_backend(backend_url, payload)

            # 3. Extract result
            final_url        = data.get('output_url') or data.get('audio_url') or data.get('video_url')
            duration_seconds = int(data.get('duration_seconds', 0))

            if not final_url:
                raise Exception("Backend did not return output URL")

            # 4. Update database
            job.status     = 'completed'
            job.output_url = final_url
            db.session.commit()
            logger.info(f"✅ Job {job_id} completed — {duration_seconds}s")

            # 5. تحديث الكوتا + إيميل إذا لزم
            if duration_seconds > 0 and user_id and user_id != 'default_user':
                user_info     = get_user_info(user_id)
                updated_quota = update_dub_usage(user_id, duration_seconds)
                if user_info and updated_quota:
                    notify_quota_if_needed(user_info, updated_quota)

        except Exception as e:
            logger.error(f"❌ Job {job_id} failed: {e}")
            job.status = 'failed'
            job.error  = str(e)
            db.session.commit()
            raise self.retry(exc=e, countdown=60)
