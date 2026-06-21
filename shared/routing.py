# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/routing.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/routing.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/routing.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/routing.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/routing.py
# # AR وحدة الدبلجة — رفع، بدء مهمة، polling، أصوات
# # CONVENTION — # FN / # AR فوق كل دالة، # قبل كل خطوة — see FUNCTION_INDEX.md
# shared/routing.py — V2.0 (Triple Backend Routing)
"""
🧭 Smart Backend Routing
   Local (RTX 3060) ↔ RunPod (Cheap) ↔ Modal (Premium)
"""
import logging
import requests
from . import config

logger = logging.getLogger(__name__)


# # FN get_backend_for_task
# # AR جلب backend for task (get_backend_for_task)
# # FN get_backend_for_task
# # AR دالة get_backend_for_task (get_backend_for_task)
# # KW عام,general
# # FN get_backend_for_task
# # AR دالة get_backend_for_task (get_backend_for_task)
# # KW عام,general
# # FN get_backend_for_task
# # AR دالة get_backend_for_task (get_backend_for_task)
# # KW عام,general
# # FN get_backend_for_task
# # AR دالة get_backend_for_task (get_backend_for_task)
# # KW عام,general
def get_backend_for_task(task_type='dubbing'):
    """
    🎯 يختار backend مناسب
    
    PROCESSING_BACKEND values:
    - 'local'   → Local فقط
    - 'runpod'  → RunPod فقط
    - 'modal'   → Modal فقط
    - 'auto'    → Smart routing (الموصى به)
    
    Auto strategy:
      - lipsync, prosody, f5 → Modal (الـ images جاهزة)
      - dubbing, tts, stt → RunPod (40% أرخص)
      - fallback → Modal
    # # block — توليد صوت TTS
    """
    backend = config.PROCESSING_BACKEND
    
    if backend == 'local':
        if config.LOCAL_PROCESSING_URL and _is_alive(config.LOCAL_PROCESSING_URL):
            # # block — توليد صوت TTS
            logger.info(f"🏠 LOCAL for {task_type}")
            # # block — توليد صوت TTS
            # # block — توليد صوت TTS
            # # return — إرجاع النتيجة
            # # block — حلقة/تكرار
            return config.LOCAL_PROCESSING_URL
        logger.warning("⚠️ Local down, fallback")
        # # return — إرجاع النتيجة
        # # block — إرجاع نتيجة
        # # block — إرجاع نتيجة
        # # block — إرجاع نتيجة
        return _get_fallback(task_type)
    
    if backend == 'runpod':
        url = _get_runpod_url(task_type)
        # # block — إرجاع نتيجة
        # # block — إرجاع نتيجة
        if url and _is_alive(url):
            logger.info(f"⚡ RUNPOD for {task_type}")
            # # block — حلقة/تكرار
            # # block — حلقة/تكرار
            # # return — إرجاع النتيجة
            return url
        # # block — حلقة/تكرار
        logger.warning("⚠️ RunPod failed, fallback to Modal")
        # # return — إرجاع النتيجة
        # # block — حلقة/تكرار
        # # block — إرجاع نتيجة
        return _get_modal_url(task_type)
    
    # # block — إرجاع نتيجة
    # # block — إرجاع نتيجة
    if backend == 'modal':
        # # return — إرجاع النتيجة
        return _get_modal_url(task_type)
    
    # Auto mode - الذكي
    if backend == 'auto':
        # Heavy tasks → Modal (premium)
        # # block — إرجاع نتيجة
        if task_type in ('lipsync', 'prosody', 'f5'):
            # # block — إرجاع نتيجة
            # # block — حلقة/تكرار
            # # block — حلقة/تكرار
            logger.info(f"☁️ MODAL (premium) for {task_type}")
            # # return — إرجاع النتيجة
            return _get_modal_url(task_type)
        
        # Cheap tasks → RunPod
        # # block — حلقة/تكرار
        # # block — حلقة/تكرار
        runpod_url = _get_runpod_url(task_type)
        if runpod_url and _is_alive(runpod_url):
            logger.info(f"⚡ RUNPOD (cheap+fast) for {task_type}")
            # # block — حلقة/تكرار
            # # block — حلقة/تكرار
            # # return — إرجاع النتيجة
            # # block — حلقة/تكرار
            # # block — حلقة/تكرار
            return runpod_url
        
        logger.warning(f"⚠️ RunPod down, fallback to Modal")
        # # return — إرجاع النتيجة
        return _get_modal_url(task_type)
    
    # # block — إرجاع نتيجة
    # # block — إرجاع نتيجة
    # # return — إرجاع النتيجة
    # # block — إرجاع نتيجة
    # # block — إرجاع نتيجة
    return _get_modal_url(task_type)


# # FN _is_alive
# # AR هل alive (_is_alive)
# # block — إرجاع نتيجة
# # FN _is_alive
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # AR دالة _is_alive (_is_alive)
# # KW عام,general
# # FN _is_alive
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR دالة _is_alive (_is_alive)
# # KW عام,general
# # FN _is_alive
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR دالة _is_alive (_is_alive)
# # KW عام,general
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN _is_alive
# # AR دالة _is_alive (_is_alive)
# # KW عام,general
def _is_alive(url):
    if not url: return False
    # # try — معالجة عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # block — معالجة أخطاء
    # # block — معالجة أخطاء
    # # try — عملية قد تفشل
    try:
        # # block — معالجة أخطاء
        # # HTTP — طلب outbound
        # # block — معالجة أخطاء
        # # block — معالجة أخطاء
        # # HTTP — outbound
        # # HTTP — outbound
        # # block — تنفيذ منطق — راجع الأسطر التالية
        # # HTTP — outbound
        # # HTTP — outbound
        r = requests.get(f"{url.rstrip('/')}/health", timeout=5)
        # # block — طلب HTTP/API
        # # return — إرجاع النتيجة
        # # block — طلب HTTP/API
        return r.status_code == 200
    # # catch — التقاط الخطأ
    # # block — طلب HTTP/API
    # # catch — التقاط خطأ
    # # block — معالجة أخطاء
    # # block — طلب HTTP/API
    # # catch — التقاط خطأ
    except Exception:
        # # block — معالجة أخطاء
        return False


# # block — معالجة أخطاء
# # block — معالجة أخطاء
# # FN _get_runpod_url
# # AR جلب runpod url (_get_runpod_url)
# # FN _get_runpod_url
# # AR دالة _get_runpod_url (_get_runpod_url)
# # block — إرجاع نتيجة
# # block — تنفيذ منطق — راجع الأسطر التالية
# # block — تنفيذ منطق — راجع الأسطر التالية
# # block — تنفيذ منطق — راجع الأسطر التالية
# # KW عام,general
# # FN _get_runpod_url
# # AR دالة _get_runpod_url (_get_runpod_url)
# # KW عام,general
# # FN _get_runpod_url
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR دالة _get_runpod_url (_get_runpod_url)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # KW عام,general
# # FN _get_runpod_url
# # AR دالة _get_runpod_url (_get_runpod_url)
# # KW عام,general
def _get_runpod_url(task_type):
    urls = {
        'dubbing': config.RUNPOD_DUBBING_URL,
        'tts': config.RUNPOD_TTS_URL or config.RUNPOD_DUBBING_URL,
        'stt': config.RUNPOD_STT_URL or config.RUNPOD_DUBBING_URL,
    }
    # # block — توليد صوت TTS
    # # block — توليد صوت TTS
    # # block — توليد صوت TTS
    # # block — توليد صوت TTS
    # # return — إرجاع النتيجة
    return urls.get(task_type, '')


# # FN _get_modal_url
# # block — توليد صوت TTS
# # AR جلب modal url (_get_modal_url)
# # block — توليد صوت TTS
# # FN _get_modal_url
# # block — إرجاع نتيجة
# # AR Local/Cloud parity (_get_modal_url)
# # block — إرجاع نتيجة
# # block — توليد صوت TTS
# # KW تنفيذ,local,cloud,modal,parity
# # FN _get_modal_url
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR Local/Cloud parity (_get_modal_url)
# # KW تنفيذ,local,cloud,modal,parity
# # FN _get_modal_url
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR Local/Cloud parity (_get_modal_url)
# # KW تنفيذ,local,cloud,modal,parity
# # FN _get_modal_url
# # AR Local/Cloud parity (_get_modal_url)
# # KW تنفيذ,local,cloud,modal,parity
def _get_modal_url(task_type):
    urls = {
        'dubbing': config.MODAL_DUBBING_URL,
        'tts': config.MODAL_TTS_URL or config.MODAL_DUBBING_URL,
        'stt': config.MODAL_STT_URL or config.MODAL_DUBBING_URL,
        'lipsync': config.MODAL_LIPSYNC_URL,
        # # block — توليد صوت TTS
        # # block — توليد صوت TTS
        # # block — توليد صوت TTS
        # # block — توليد صوت TTS
        'prosody': config.MODAL_PROSODY_URL,
        'f5': config.MODAL_DUBBING_URL,
    }
    # # block — توليد صوت TTS
    # # return — إرجاع النتيجة
    # # block — توليد صوت TTS
    return urls.get(task_type, config.MODAL_DUBBING_URL)


# # block — إرجاع نتيجة
# # FN _get_fallback
# # block — إرجاع نتيجة
# # block — توليد صوت TTS
# # AR جلب fallback (_get_fallback)
# # FN _get_fallback
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR دالة _get_fallback (_get_fallback)
# # KW عام,general
# # block — تنفيذ منطق — راجع الأسطر التالية
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN _get_fallback
# # AR دالة _get_fallback (_get_fallback)
# # KW عام,general
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN _get_fallback
# # AR دالة _get_fallback (_get_fallback)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # KW عام,general
# # FN _get_fallback
# # AR دالة _get_fallback (_get_fallback)
# # KW عام,general
def _get_fallback(task_type):
    runpod = _get_runpod_url(task_type)
    if runpod and _is_alive(runpod):
        # # return — إرجاع النتيجة
        return runpod
    # # return — إرجاع النتيجة
    # # block — إرجاع نتيجة
    # # block — إرجاع نتيجة
    # # block — إرجاع نتيجة
    # # block — إرجاع نتيجة
    return _get_modal_url(task_type)


# Public API
# # FN get_dubbing_url
# # AR جلب dubbing url (get_dubbing_url)
# # block — إرجاع نتيجة
# # FN get_dubbing_url
# # block — إرجاع نتيجة
# # AR دالة get_dubbing_url (get_dubbing_url)
# # block — إرجاع نتيجة
# # KW عام,general
# # FN get_dubbing_url
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR دالة get_dubbing_url (get_dubbing_url)
# # KW عام,general
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN get_dubbing_url
# # AR دالة get_dubbing_url (get_dubbing_url)
# # KW عام,general
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN get_dubbing_url
# # AR دالة get_dubbing_url (get_dubbing_url)
# # KW عام,general
def get_dubbing_url(): return get_backend_for_task('dubbing')
# # FN get_tts_url
# # AR جلب tts url (get_tts_url)
# # FN get_tts_url
# # AR Text-to-speech (get_tts_url)
# # KW توليد_صوت,TTS,synthesis
# # block — توليد صوت TTS
# # block — توليد صوت TTS
# # block — توليد صوت TTS
# # FN get_tts_url
# # AR Text-to-speech (get_tts_url)
# # KW توليد_صوت,TTS,synthesis
# # FN get_tts_url
# # block — توليد صوت TTS
# # AR Text-to-speech (get_tts_url)
# # block — توليد صوت TTS
# # KW توليد_صوت,TTS,synthesis
# # FN get_tts_url
# # AR Text-to-speech (get_tts_url)
# # KW توليد_صوت,TTS,synthesis
def get_tts_url(): return get_backend_for_task('tts')
# # FN get_stt_url
# # AR جلب stt url (get_stt_url)
# # FN get_stt_url
# # AR Speech-to-text (get_stt_url)
# # KW تفريغ,ASR,STT,whisper,deepgram
# # block — تفريغ كلام ASR
# # block — تفريغ كلام ASR
# # block — تفريغ كلام ASR
# # FN get_stt_url
# # AR Speech-to-text (get_stt_url)
# # KW تفريغ,ASR,STT,whisper,deepgram
# # FN get_stt_url
# # block — تفريغ كلام ASR
# # AR Speech-to-text (get_stt_url)
# # block — تفريغ كلام ASR
# # KW تفريغ,ASR,STT,whisper,deepgram
# # FN get_stt_url
# # AR Speech-to-text (get_stt_url)
# # KW تفريغ,ASR,STT,whisper,deepgram
def get_stt_url(): return get_backend_for_task('stt')
# # FN get_lipsync_url
# # AR جلب lipsync url (get_lipsync_url)
# # FN get_lipsync_url
# # AR دالة get_lipsync_url (get_lipsync_url)
# # KW عام,general
# # block — تنفيذ منطق — راجع الأسطر التالية
# # block — تنفيذ منطق — راجع الأسطر التالية
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN get_lipsync_url
# # AR دالة get_lipsync_url (get_lipsync_url)
# # KW عام,general
# # FN get_lipsync_url
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR دالة get_lipsync_url (get_lipsync_url)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # KW عام,general
# # FN get_lipsync_url
# # AR دالة get_lipsync_url (get_lipsync_url)
# # KW عام,general
def get_lipsync_url(): return get_backend_for_task('lipsync')
# # FN get_prosody_url
# # AR جلب prosody url (get_prosody_url)
# # FN get_prosody_url
# # AR دالة get_prosody_url (get_prosody_url)
# # KW عام,general
# # block — تنفيذ منطق — راجع الأسطر التالية
# # block — تنفيذ منطق — راجع الأسطر التالية
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN get_prosody_url
# # AR دالة get_prosody_url (get_prosody_url)
# # KW عام,general
# # FN get_prosody_url
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR دالة get_prosody_url (get_prosody_url)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # KW عام,general
# # FN get_prosody_url
# # AR دالة get_prosody_url (get_prosody_url)
# # KW عام,general
def get_prosody_url(): return get_backend_for_task('prosody')


# # FN get_backend_status
# # AR جلب backend status (get_backend_status)
# # FN get_backend_status
# # AR حالة المهمة (get_backend_status)
# # KW حالة,webhook,SSE,status
# # block — تنفيذ منطق — راجع الأسطر التالية
# # block — تنفيذ منطق — راجع الأسطر التالية
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN get_backend_status
# # AR حالة المهمة (get_backend_status)
# # KW حالة,webhook,SSE,status
# # FN get_backend_status
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR حالة المهمة (get_backend_status)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # KW حالة,webhook,SSE,status
# # FN get_backend_status
# # AR حالة المهمة (get_backend_status)
# # KW حالة,webhook,SSE,status
def get_backend_status():
    """🔍 يفحص كل backends"""
    status = {
        'mode': config.PROCESSING_BACKEND,
        'backends': {
            'local': {'url': config.LOCAL_PROCESSING_URL, 'alive': False, 'engines': []},
            # # block — تنفيذ منطق — راجع الأسطر التالية
            # # block — تنفيذ منطق — راجع الأسطر التالية
            # # block — تنفيذ منطق — راجع الأسطر التالية
            # # block — تنفيذ منطق — راجع الأسطر التالية
            'runpod': {
                'dubbing': {'url': config.RUNPOD_DUBBING_URL, 'alive': False},
                'tts': {'url': config.RUNPOD_TTS_URL, 'alive': False},
                # # block — توليد صوت TTS
                'stt': {'url': config.RUNPOD_STT_URL, 'alive': False},
            # # block — توليد صوت TTS
            },
            # # block — توليد صوت TTS
            'modal': {
                # # block — توليد صوت TTS
                # # block — توليد صوت TTS
                'dubbing': {'url': config.MODAL_DUBBING_URL, 'alive': False},
                'lipsync': {'url': config.MODAL_LIPSYNC_URL, 'alive': False},
                # # block — توليد صوت TTS
                'prosody': {'url': config.MODAL_PROSODY_URL, 'alive': False},
                'tts': {'url': config.MODAL_TTS_URL, 'alive': False},
                # # block — توليد صوت TTS
                # # block — توليد صوت TTS
                'stt': {'url': config.MODAL_STT_URL, 'alive': False},
            }
        # # block — توليد صوت TTS
        # # block — توليد صوت TTS
        }
    }
    
    # # block — توليد صوت TTS
    if config.LOCAL_PROCESSING_URL:
        # # block — توليد صوت TTS
        # # try — معالجة عملية قد تفشل
        # # try — عملية قد تفشل
        # # block — توليد صوت TTS
        # # try — عملية قد تفشل
        # # block — توليد صوت TTS
        # # try — عملية قد تفشل
        # # try — عملية قد تفشل
        try:
            # # block — معالجة أخطاء
            # # HTTP — طلب outbound
            # # block — معالجة أخطاء
            # # block — معالجة أخطاء
            # # block — معالجة أخطاء
            # # HTTP — outbound
            # # HTTP — outbound
            # # HTTP — outbound
            # # HTTP — outbound
            r = requests.get(
                # # block — طلب HTTP/API
                f"{config.LOCAL_PROCESSING_URL.rstrip('/')}/health",
                timeout=5
            # # block — طلب HTTP/API
            )
            # # block — طلب HTTP/API
            # # block — طلب HTTP/API
            # # block — تنفيذ منطق — راجع الأسطر التالية
            if r.status_code == 200:
                # # parse — قراءة JSON من الاستجابة
                data = r.json()
                # # block — parse/serialize JSON
                status['backends']['local']['alive'] = True
                status['backends']['local']['engines'] = data.get('supported_engines', [])
                # # block — parse/serialize JSON
                # # block — parse/serialize JSON
                status['backends']['local']['gpu'] = data.get('gpu_name', '')
        # # block — parse/serialize JSON
        # # catch — التقاط الخطأ
        # # block — معالجة أخطاء
        # # catch — التقاط خطأ
        # # block — معالجة أخطاء
        # # catch — التقاط خطأ
        except Exception:
            # # block — معالجة أخطاء
            pass
    
    for backend in ['runpod', 'modal']:
        # # block — معالجة أخطاء
        # # block — معالجة أخطاء
        for service, info in status['backends'][backend].items():
            # # block — معالجة أخطاء
            url = info.get('url', '')
            if url:
                # # block — معالجة أخطاء
                # # try — معالجة عملية قد تفشل
                # # block — معالجة أخطاء
                # # block — معالجة أخطاء
                # # try — عملية قد تفشل
                # # try — عملية قد تفشل
                # # try — عملية قد تفشل
                # # try — عملية قد تفشل
                try:
                    # # block — معالجة أخطاء
                    # # HTTP — طلب outbound
                    # # block — معالجة أخطاء
                    # # block — معالجة أخطاء
                    # # block — معالجة أخطاء
                    # # HTTP — outbound
                    # # HTTP — outbound
                    # # block — تنفيذ منطق — راجع الأسطر التالية
                    # # HTTP — outbound
                    # # HTTP — outbound
                    r = requests.get(f"{url.rstrip('/')}/health", timeout=5)
                    info['alive'] = r.status_code == 200
                # # block — طلب HTTP/API
                # # catch — التقاط الخطأ
                # # block — طلب HTTP/API
                # # catch — التقاط خطأ
                # # block — طلب HTTP/API
                # # catch — التقاط خطأ
                except Exception:
                    # # block — طلب HTTP/API
                    # # block — معالجة أخطاء
                    # # block — معالجة أخطاء
                    pass
    
    # # return — إرجاع النتيجة
    return status
