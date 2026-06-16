# shared — مكتبات Celery Worker الدبلجة

> **داخل مستودع `sl-dubbing-tasks-dubbing-main`**
> نسخ مُخففة من مكتبات `sl-dubbing-backend-main/shared/` — فقط ما يحتاجه Worker بدون GPU.

---

## الملفات

### dub_worker_submit.py
```python
def run_dub_worker_pipeline(payload: dict) → dict
```
الدالة الرئيسية للـ Worker:
1. يستدعي `inference_provider.trigger_dubbing_job(payload)` → Modal call
2. ينتظر النتيجة (blocking)
3. يُعيد `{ok: True, dubbed_url}` أو `{ok: False, error}`

### dub_runpod.py
```python
def submit_to_runpod(payload: dict) → str       # → runpod_job_id
def poll_runpod_job(job_id: str) → dict         # يستطلع حتى الاكتمال
def run_runpod_pipeline(payload: dict) → dict   # submit + poll
```
بديل RunPod للـ GPU inference عند عدم توفر Modal.

### inference_provider.py
```python
def trigger_dubbing_job(payload) → str   # يختار Modal أو RunPod
def trigger_modal_cancel(job_id, call_id)
```

### dub_engine_policy.py
```python
def resolve_tts_chain(voice_id, lang, dialect) → list[str]
def normalize_dub_engine(engine_name) → str
```

### job_events.py
```python
def publish_job_status(job_id, event: dict)
# يُرسل عبر Redis pub/sub: {"status": "processing", "progress": 0.5}
```

### celery_setup.py
```python
def make_celery_app() → Celery
# Queue: "dubbing"
# Backend: Redis
```

### models.py
```python
class DubbingJob:
    def update_status(self, status, output_url=None)
    @classmethod
    def get_by_id(cls, job_id) → DubbingJob
```
نسخة مُخففة — فقط عمليات تحديث الحالة.

### r2_client.py
```python
def upload_to_r2(file_key, data, content_type) → str
def get_presigned_url(file_key) → str
```

### config.py
```python
MODAL_TOKEN_ID, MODAL_TOKEN_SECRET
REDIS_URL
SUPABASE_URL, SUPABASE_KEY
R2_ENDPOINT, R2_ACCESS_KEY, R2_SECRET_KEY, R2_BUCKET
RUNPOD_API_KEY, RUNPOD_ENDPOINT_ID
```

### lang_profiles.py
```python
SUPPORTED_LANGUAGES: dict[str, str]
def is_supported(lang_code) → bool
```

### modal_job_map.py
```python
def register_job(job_id, call_id)
def get_call_id(job_id) → str | None
def remove_job(job_id)
```

### supabase_quota.py
```python
def check_quota(user_id) → bool
def increment_usage(user_id, minutes)
```

### dub_webhook_url.py
```python
def build_webhook_url(job_id) → str
```

### routing.py
```python
def get_queue_name() → str   # → "dubbing"
```
