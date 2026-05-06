# tasks_dubbing.py — V2.0 (Triple Backend Support)
"""
🎬 Dubbing Worker - يدعم 3 backends
   - Local PC (sync HTTP)
   - RunPod (async polling)
   - Modal (sync HTTP)
"""
import os
import time
import logging
import tempfile
import subprocess
import shutil
import requests
from datetime import datetime

from shared import config, auth, r2_client, routing
from shared.celery_setup import make_celery_app, QUEUE_DUBBING
from models import db, DubbingJob, CreditTransaction

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

celery_app = make_celery_app('tasks-dubbing', queue_name=QUEUE_DUBBING)

from flask import Flask
flask_app = Flask(__name__)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(flask_app)


# ==========================================
# 🎬 ffmpeg merge
# ==========================================
def _merge_video_audio_locally(video_url, audio_url):
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        if result.returncode != 0:
            return None
    except Exception:
        return None
    
    temp_dir = tempfile.mkdtemp()
    try:
        video_path = os.path.join(temp_dir, "video.mp4")
        audio_path = os.path.join(temp_dir, "audio.wav")
        output_path = os.path.join(temp_dir, "merged.mp4")
        
        for url, path in [(video_url, video_path), (audio_url, audio_path)]:
            with requests.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(path, "wb") as f:
                    for chunk in r.iter_content(1024 * 1024):
                        f.write(chunk)
        
        subprocess.run([
            "ffmpeg", "-y",
            "-i", video_path, "-i", audio_path,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest", output_path
        ], capture_output=True, timeout=300, check=True)
        
        if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
            return None
        
        return r2_client.upload_file(output_path, prefix='results', ext='mp4')
    except Exception as e:
        logger.exception(f"merge failed: {e}")
        return None
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# ==========================================
# 🚀 Backend callers
# ==========================================
def call_modal_or_local(backend_url, payload, timeout=1500):
    """استدعاء sync لـ Modal أو Local"""
    url = f"{backend_url.rstrip('/')}/upload-from-url"
    logger.info(f"→ {url[:80]}")
    
    r = requests.post(url, json=payload, timeout=timeout)
    
    if r.status_code != 200:
        raise Exception(f"Backend HTTP {r.status_code}: {r.text[:300]}")
    
    data = r.json()
    if not data.get('success'):
        raise Exception(data.get('error', 'Backend failed'))
    
    return data


def call_runpod(backend_url, payload, timeout=1500):
    """
    استدعاء RunPod (async polling)
    
    RunPod API:
      1. POST /run → تستلم job_id
      2. GET /status/{job_id} → poll حتى COMPLETED
    """
    api_key = config.RUNPOD_API_KEY
    if not api_key:
        raise Exception("RUNPOD_API_KEY not set")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    # 1. Submit job
    submit_url = f"{backend_url.rstrip('/')}/run"
    logger.info(f"→ RunPod submit: {submit_url[:80]}")
    
    r = requests.post(
        submit_url,
        json={'input': payload},
        headers=headers,
        timeout=60,
    )
    
    if r.status_code != 200:
        raise Exception(f"RunPod submit failed: {r.status_code} {r.text[:200]}")
    
    data = r.json()
    job_id = data.get('id')
    if not job_id:
        raise Exception(f"No job_id from RunPod: {data}")
    
    logger.info(f"📋 RunPod job: {job_id}")
    
    # 2. Poll
    status_url = f"{backend_url.rstrip('/')}/status/{job_id}"
    start_time = time.time()
    poll_interval = 3
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            # Cancel
            try:
                requests.post(
                    f"{backend_url.rstrip('/')}/cancel/{job_id}",
                    headers=headers, timeout=10
                )
            except Exception:
                pass
            raise Exception(f"RunPod timeout after {int(elapsed)}s")
        
        r = requests.get(status_url, headers=headers, timeout=30)
        if r.status_code != 200:
            time.sleep(poll_interval)
            continue
        
        status_data = r.json()
        status = status_data.get('status', '')
        
        if status == 'COMPLETED':
            output = status_data.get('output', {})
            if not output.get('success'):
                raise Exception(output.get('error', 'RunPod failed'))
            return output
        
        if status in ('FAILED', 'CANCELLED'):
            error = status_data.get('error', f'Status: {status}')
            raise Exception(f"RunPod {status}: {error}")
        
        # IN_QUEUE or IN_PROGRESS
        time.sleep(poll_interval)


def call_backend(backend_url, payload, timeout=1500):
    """
    🎯 يختار طريقة الاستدعاء المناسبة
       - RunPod: async polling
       - Modal/Local: sync HTTP
    """
    if 'runpod.ai' in backend_url or 'runpod.io' in backend_url:
        return call_runpod(backend_url, payload, timeout)
    return call_modal_or_local(backend_url, payload, timeout)


# ==========================================
# 🎯 Main Task
# ==========================================
@celery_app.task(name='tasks_dubbing.process_dub', bind=True, max_retries=2)
def process_dub(self, job_id, user_id, media_url, file_key, lang,
                voice_id='source', sample_b64='', edge_voice='', engine='',
                with_lipsync=False, return_video=True, cost=100):
    """🚀 معالجة دبلجة"""
    
    with flask_app.app_context():
        job = DubbingJob.query.get(job_id)
        if not job:
            logger.error(f"[job={job_id}] not found")
            return
        
        job.status = 'processing'
        job.updated_at = datetime.utcnow()
        db.session.commit()
        
        try:
            # 🎯 اختر backend
            backend_url = routing.get_dubbing_url()
            if not backend_url:
                raise Exception("No backend available")
            
            backend_name = (
                'RunPod' if 'runpod' in backend_url else
                'Modal' if 'modal.run' in backend_url else
                'Local'
            )
            logger.info(f"[job={job_id}] backend: {backend_name}")
            
            # 📤 إرسال
            payload = {
                'media_url': media_url, 'lang': lang,
                'voice_id': voice_id, 'sample_b64': sample_b64,
                'edge_voice': edge_voice, 'engine': engine,
            }
            
            data = call_backend(backend_url, payload, timeout=1500)
            
            audio_url = data.get('audio_url')
            final_url = audio_url
            
            # 🎬 Video output
            source_str = (file_key or media_url or '').lower()
            video_exts = ['.mp4', '.mov', '.mkv', '.webm', '.avi', '.mpg', '.mpeg']
            is_video = any(ext in source_str for ext in video_exts)
            
            if is_video and return_video and media_url:
                if with_lipsync:
                    # LipSync دائماً Modal
                    lipsync_url = routing.get_lipsync_url()
                    if lipsync_url:
                        try:
                            logger.info(f"[job={job_id}] 🎬 → LatentSync")
                            sresp = requests.post(
                                f"{lipsync_url.rstrip('/')}/dub-video",
                                json={
                                    'media_url': media_url,
                                    'dubbed_audio_url': audio_url,
                                    'preserve_background': True,
                                    'auto_lipsync': True,
                                    'force_lipsync': True,
                                }, timeout=1500
                            )
                            if sresp.status_code == 200:
                                sd = sresp.json()
                                if sd.get('success'):
                                    final_url = sd.get('output_url', audio_url)
                                    logger.info(f"[job={job_id}] ✅ LipSync done")
                        except Exception as e:
                            logger.warning(f"[job={job_id}] LipSync failed: {e}")
                else:
                    logger.info(f"[job={job_id}] 🎬 → ffmpeg merge")
                    merged = _merge_video_audio_locally(media_url, audio_url)
                    if merged:
                        final_url = merged
                        logger.info(f"[job={job_id}] ✅ Merged")
            
            job.status = 'completed'
            job.output_url = final_url
            job.updated_at = datetime.utcnow()
            db.session.commit()
            
            tx = CreditTransaction(
                user_id=str(user_id), amount=-cost,
                reason=f'Dubbing to {lang} ({backend_name})',
                job_id=job_id, job_type='dub'
            )
            db.session.add(tx)
            db.session.commit()
            
            logger.info(f"[job={job_id}] 🎉 done via {backend_name}")
        
        except Exception as e:
            logger.exception(f"[job={job_id}] ❌ failed: {e}")
            job.status = 'failed'
            job.error = str(e)[:500]
            job.updated_at = datetime.utcnow()
            db.session.commit()
            
            try:
                auth.add_credits(user_id, cost, f'Refund: {job_id}')
            except Exception:
                pass
