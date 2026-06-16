# sl-dubbing-tasks-dubbing-main — Celery Worker الدبلجة (REPOSITORY)

> يستقبل مهام الدبلجة من Redis queue وينفّذها عبر Modal GPU أو RunPod.
> يعمل على **Railway** بدون GPU — الـ GPU يكون في Modal.

---

## الهيكل

```
sl-dubbing-tasks-dubbing-main/
├── tasks_dubbing.py          ← نقطة الدخول (Celery task)
├── shared/                   ← مكتبات مُخففة
│   ├── dub_worker_submit.py  ← الدالة الرئيسية للـ Worker
│   ├── dub_runpod.py         ← بديل RunPod
│   ├── inference_provider.py ← اختيار مزود GPU
│   ├── dub_engine_policy.py  ← اختيار محرك TTS
│   ├── job_events.py         ← Redis pub/sub
│   ├── celery_setup.py       ← Celery factory
│   ├── models.py             ← DubbingJob
│   ├── r2_client.py          ← R2
│   ├── config.py             ← متغيرات البيئة
│   ├── lang_profiles.py      ← اللغات المدعومة
│   ├── modal_job_map.py      ← تتبع Modal calls
│   ├── supabase_quota.py     ← الحصة
│   ├── dub_webhook_url.py    ← webhook URL
│   └── routing.py            ← توجيه
├── Procfile                  ← Railway process command
└── nixpacks.toml             ← إعداد بناء Railway
```

---

## tasks_dubbing.py

```python
celery_app = make_celery_app()

@celery_app.task(name="process_dub", queue="dubbing")
def process_dub(payload: dict) → dict:
    """
    payload: {job_id, user_id, file_key, lang, voice_config, webhook_url}
    """
    publish_job_status(job_id, {"status": "processing"})
    result = run_dub_worker_pipeline(payload)
    DubbingJob.update_status(job_id, "done" if result["ok"] else "failed", result.get("dubbed_url"))
    return result
```

---

## تدفق التنفيذ

```
Redis queue "dubbing"
    ↓ Celery worker يستقبل المهمة
tasks_dubbing.process_dub(payload)
    ↓ publish_job_status("processing")
    ↓ dub_worker_submit.run_dub_worker_pipeline(payload)
        ↓ inference_provider.trigger_dubbing_job()
            → Modal: dubbing_factory.run_dubbing_pipeline.remote()
                ← يرجع {ok, dubbed_url}
    ↓ DubbingJob.update_status("done", dubbed_url)
```

---

## إعداد النشر على Railway

**Procfile:**
```
worker: celery -A tasks_dubbing worker --loglevel=info -Q dubbing --concurrency=2
```

**متغيرات البيئة المطلوبة:**
```
MODAL_TOKEN_ID, MODAL_TOKEN_SECRET
REDIS_URL
SUPABASE_URL, SUPABASE_KEY
R2_ENDPOINT, R2_ACCESS_KEY, R2_SECRET_KEY, R2_BUCKET
```

---

## للتفاصيل

- [shared/README.md](shared/README.md) — كل المكتبات
