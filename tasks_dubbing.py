# tasks_dubbing.py — V3.0 (Pure Router - GPU Delegation Fix)
import os
import time
import logging
import requests
from datetime import datetime

from shared import config, r2_client, routing
from shared.celery_setup import make_celery_app, QUEUE_DUBBING
from shared.models import db, DubbingJob, CreditTransaction

# إعداد السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# تهيئة Celery
celery_app = make_celery_app('tasks-dubbing', queue_name=QUEUE_DUBBING)

from flask import Flask
flask_app = Flask(__name__)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL.replace('postgres://', 'postgresql://', 1)
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(flask_app)

def call_backend(backend_url, payload, timeout=1500):
    """🎯 استدعاء السيرفر المحلي أو السحابي"""
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
        # Modal / Local (Cloudflare Tunnel)
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
            # 1. توليد رابط تحميل مؤقت للملف الأصلي من R2
            media_url = r2_client.generate_download_url(file_key)
            if not media_url: raise Exception("Failed to generate media_url from R2")

            backend_url = routing.get_dubbing_url()
            
            # 2. تجهيز الطلب لجهازك (ملاحظة: return_video مفعلة إجبارياً)
            payload = {
                'media_url': media_url, 
                'lang': lang,
                'voice_id': kwargs.get('voice_id', 'source'),
                'engine': kwargs.get('engine', ''),
                'return_video': True  # 👈 هذا السطر هو الذي سيجعل جهازك يدمج الفيديو!
            }
            
            # 3. إرسال الطلب لجهازك واستلام الرابط النهائي
            data = call_backend(backend_url, payload)
            
            # استخراج الرابط (سواء أرجعه جهازك باسم output_url أو audio_url)
            final_url = data.get('output_url') or data.get('audio_url')
            if not final_url: raise Exception("Backend did not return output URL")

            # 4. تحديث قاعدة البيانات بالرابط النهائي
            job.status = 'completed'
            job.output_url = final_url
            
            # (تم تعطيل كود الرصيد مؤقتاً لضمان عمل الفيديو)
            # tx = CreditTransaction(...)
            # db.session.add(tx)
            
            db.session.commit()
            logger.info(f"✅ Job {job_id} completed successfully and output URL saved!")
            
        except Exception as e:
            logger.error(f"❌ Task Failed for Job {job_id}: {e}")
            job.status = 'failed'
            job.error = str(e)
            db.session.commit()
