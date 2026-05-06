# shared/routing.py — V2.0 (Triple Backend Routing)
"""
🧭 Smart Backend Routing
   Local (RTX 3060) ↔ RunPod (Cheap) ↔ Modal (Premium)
"""
import logging
import requests
from . import config

logger = logging.getLogger(__name__)


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
    """
    backend = config.PROCESSING_BACKEND
    
    if backend == 'local':
        if config.LOCAL_PROCESSING_URL and _is_alive(config.LOCAL_PROCESSING_URL):
            logger.info(f"🏠 LOCAL for {task_type}")
            return config.LOCAL_PROCESSING_URL
        logger.warning("⚠️ Local down, fallback")
        return _get_fallback(task_type)
    
    if backend == 'runpod':
        url = _get_runpod_url(task_type)
        if url and _is_alive(url):
            logger.info(f"⚡ RUNPOD for {task_type}")
            return url
        logger.warning("⚠️ RunPod failed, fallback to Modal")
        return _get_modal_url(task_type)
    
    if backend == 'modal':
        return _get_modal_url(task_type)
    
    # Auto mode - الذكي
    if backend == 'auto':
        # Heavy tasks → Modal (premium)
        if task_type in ('lipsync', 'prosody', 'f5'):
            logger.info(f"☁️ MODAL (premium) for {task_type}")
            return _get_modal_url(task_type)
        
        # Cheap tasks → RunPod
        runpod_url = _get_runpod_url(task_type)
        if runpod_url and _is_alive(runpod_url):
            logger.info(f"⚡ RUNPOD (cheap+fast) for {task_type}")
            return runpod_url
        
        logger.warning(f"⚠️ RunPod down, fallback to Modal")
        return _get_modal_url(task_type)
    
    return _get_modal_url(task_type)


def _is_alive(url):
    if not url: return False
    try:
        r = requests.get(f"{url.rstrip('/')}/health", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def _get_runpod_url(task_type):
    urls = {
        'dubbing': config.RUNPOD_DUBBING_URL,
        'tts': config.RUNPOD_TTS_URL or config.RUNPOD_DUBBING_URL,
        'stt': config.RUNPOD_STT_URL or config.RUNPOD_DUBBING_URL,
    }
    return urls.get(task_type, '')


def _get_modal_url(task_type):
    urls = {
        'dubbing': config.MODAL_DUBBING_URL,
        'tts': config.MODAL_TTS_URL or config.MODAL_DUBBING_URL,
        'stt': config.MODAL_STT_URL or config.MODAL_DUBBING_URL,
        'lipsync': config.MODAL_LIPSYNC_URL,
        'prosody': config.MODAL_PROSODY_URL,
        'f5': config.MODAL_DUBBING_URL,
    }
    return urls.get(task_type, config.MODAL_DUBBING_URL)


def _get_fallback(task_type):
    runpod = _get_runpod_url(task_type)
    if runpod and _is_alive(runpod):
        return runpod
    return _get_modal_url(task_type)


# Public API
def get_dubbing_url(): return get_backend_for_task('dubbing')
def get_tts_url(): return get_backend_for_task('tts')
def get_stt_url(): return get_backend_for_task('stt')
def get_lipsync_url(): return get_backend_for_task('lipsync')
def get_prosody_url(): return get_backend_for_task('prosody')


def get_backend_status():
    """🔍 يفحص كل backends"""
    status = {
        'mode': config.PROCESSING_BACKEND,
        'backends': {
            'local': {'url': config.LOCAL_PROCESSING_URL, 'alive': False, 'engines': []},
            'runpod': {
                'dubbing': {'url': config.RUNPOD_DUBBING_URL, 'alive': False},
                'tts': {'url': config.RUNPOD_TTS_URL, 'alive': False},
                'stt': {'url': config.RUNPOD_STT_URL, 'alive': False},
            },
            'modal': {
                'dubbing': {'url': config.MODAL_DUBBING_URL, 'alive': False},
                'lipsync': {'url': config.MODAL_LIPSYNC_URL, 'alive': False},
                'prosody': {'url': config.MODAL_PROSODY_URL, 'alive': False},
                'tts': {'url': config.MODAL_TTS_URL, 'alive': False},
                'stt': {'url': config.MODAL_STT_URL, 'alive': False},
            }
        }
    }
    
    if config.LOCAL_PROCESSING_URL:
        try:
            r = requests.get(
                f"{config.LOCAL_PROCESSING_URL.rstrip('/')}/health",
                timeout=5
            )
            if r.status_code == 200:
                data = r.json()
                status['backends']['local']['alive'] = True
                status['backends']['local']['engines'] = data.get('supported_engines', [])
                status['backends']['local']['gpu'] = data.get('gpu_name', '')
        except Exception:
            pass
    
    for backend in ['runpod', 'modal']:
        for service, info in status['backends'][backend].items():
            url = info.get('url', '')
            if url:
                try:
                    r = requests.get(f"{url.rstrip('/')}/health", timeout=5)
                    info['alive'] = r.status_code == 200
                except Exception:
                    pass
    
    return status
