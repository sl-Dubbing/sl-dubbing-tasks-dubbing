# tasks_dubbing.py — V2.2 (Final Production Fix)
import os
import time
import logging
import tempfile
import subprocess
import shutil
import requests
from datetime import datetime

from shared import config, r2_client, routing
from shared.celery_setup import make_celery_app, QUEUE_DUBBING
from shared.models import db, DubbingJob, CreditTransaction

# إعداد السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# تهيئة Celery لهذا العامل
celery_app = make_celery_app('tasks-dubbing', queue_name=QUEUE_DUBBING)

# تهيئة Flask للوصول لقاعدة البيانات (مع إصلاح الرابط)
from flask import Flask
flask_app = Flask(__name__)
# 🚨 إصلاح رابط قاعدة البيانات ليتوافق مع Railway/Supabase
flask_app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL.replace('postgres://', 'postgresql://', 1)
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(flask_app)

def _merge_video_audio_locally(video_url, audio_url):
    """🎬 دمج الفيديو والصوت باستخدام FFmpeg المحلي"""
    temp_dir = tempfile.mkdtemp()
    try:
        video_path = os.path.join(temp_dir, "video.mp4")
        audio_path = os.path.join(temp_dir, "audio.wav")
        output_path = os.path.join(temp_dir, "merged.mp4")
        
        # تحميل الملفات من الروابط
        for url, path in [(video_url, video_path), (audio_url, audio_path)]:
            with requests.get(url, stream=True, timeout=300) as r:
                r.raise_for_status()
                with open(path, "wb") as f:
                    for chunk in r.iter_content(1024 * 1024):
                        f.write(chunk)
        
        # تنفيذ FFmpeg (تحويل الصوت لـ AAC ودمجه)
        subprocess.run([
            "ffmpeg", "-y",
            "-i", video_path, "-i", audio_path,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest", output_path
        ], capture_output=True, timeout=600, check=True)
        
        return r2_client.upload_file(output_path, prefix='results', ext='mp4')
    except Exception as e:
        logger.error(f"FFmpeg Merge failed: {e}")
        return None
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def call_backend(backend_url, payload, timeout=1500):
    """🎯 استدعاء الـ Backend المناسب (RunPod أو Modal)"""
    if 'runpod.ai' in backend_url or 'runpod.io' in backend_url:
        headers = {'Authorization': f'Bearer {config.RUNPOD_API_KEY}', 'Content-Type': 'application/json'}
        r = requests.post(f"{backend_url.rstrip('/')}/run", json={'input': payload}, headers=headers, timeout=60)
        r.raise_for_status()
        job_id = r.json().get('id')
        
        while True:
            status_res = requests.get(f"{backend_url.rstrip('/')}/status/{job_id}", headers=headers, timeout=30)
            status_data = status_res.json()
            if status_data.get('status') == 'COMPLETED':
                return status_data.get('output')
            if status_data.get('status') in ['FAILED', 'CANCELLED']:
                raise Exception(f"RunPod Backend failed: {status_data.get('error')}")
            time.sleep(5)
    else:
        # Modal / Local
        r = requests.post(f"{backend_url.rstrip('/')}/upload-from-url", json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()

@celery_app.task(name='tasks_dubbing.process_dub', bind=True, max_retries=2)
def process_dub(self, job_id, user_id, file_key, lang, cost=100, **kwargs):
    """🚀 المهمة الأساسية لمعالجة الدبلجة"""
    with flask_app.app_context():
        job = DubbingJob.query.get(job_id)
        if not job: return
        
        job.status = 'processing'
        db.session.commit()
        
        try:
            # 🚨 الخطوة الحاسمة: توليد رابط تحميل مؤقت للملف الأصلي من R2
            media_url = r2_client.generate_download_url(file_key)
            if not media_url: raise Exception("Failed to generate media_url from R2")

            backend_url = routing.get_dubbing_url()
            payload = {
                'media_url': media_url, 
                'lang': lang,
                'voice_id': kwargs.get('voice_id', 'source'),
                'engine': kwargs.get('engine', '')
            }
            
            # 1. طلب الدبلجة
            data = call_backend(backend_url, payload)
            audio_url = data.get('audio_url')
            if not audio_url: raise Exception("Backend did not return audio_url")
            
            # 2. الدمج مع الفيديو الأصلي
            if kwargs.get('return_video', True):
                final_url = _merge_video_audio_locally(media_url, audio_url)
            else:
                final_url = audio_url

            # 3. تحديث قاعدة البيانات وخصم الرصيد
            job.status = 'completed'
            job.output_url = final_url or audio_url
            
            tx = CreditTransaction(
                user_id=str(user_id), 
                amount=-cost, 
                reason=f'Dubbing: {lang}', 
                job_id=job_id, 
                job_type='dub'
            )
            db.session.add(tx)
            db.session.commit()
            logger.info(f"✅ Job {job_id} completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Task Failed for Job {job_id}: {e}")
            job.status = 'failed'
            job.error = str(e)
            db.session.commit()
