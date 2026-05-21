# shared/config.py — Unified V3.0 (All Microservices)
"""⚙️ مركز الإعدادات الموحد للباك-إند والعمال"""
import os

# Security & Database
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')
DATABASE_URL = os.environ.get('DATABASE_URL', '')
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
SUPABASE_JWT_SECRET = os.environ.get('SUPABASE_JWT_SECRET', '')

# Redis
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Cloudflare R2 Storage
R2_BUCKET_NAME = os.environ.get('R2_BUCKET_NAME', 'sl-dubbing-media')
R2_ENDPOINT_URL = os.environ.get('R2_ENDPOINT_URL', '')
R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID', '')
R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY', '')
R2_REGION = os.environ.get('R2_REGION', 'auto')
S3_SIGNATURE_VERSION = os.environ.get('S3_SIGNATURE_VERSION', 's3v4')
R2_FORCE_PATH_STYLE = os.environ.get('R2_FORCE_PATH_STYLE', 'true').lower() == 'true'

# Endpoints
MODAL_DUBBING_URL = os.environ.get('MODAL_DUBBING_URL', '')
MODAL_LIPSYNC_URL = os.environ.get('MODAL_LIPSYNC_URL', '')
MODAL_PROSODY_URL = os.environ.get('MODAL_PROSODY_URL', '')
MODAL_TTS_URL = os.environ.get('MODAL_TTS_URL', '')
MODAL_STT_URL = os.environ.get('MODAL_STT_URL', '')

RUNPOD_API_KEY = os.environ.get('RUNPOD_API_KEY', '')
RUNPOD_DUBBING_URL = os.environ.get('RUNPOD_DUBBING_URL', '')
RUNPOD_TTS_URL = os.environ.get('RUNPOD_TTS_URL', '')
RUNPOD_STT_URL = os.environ.get('RUNPOD_STT_URL', '')

LOCAL_PROCESSING_URL = os.environ.get('LOCAL_PROCESSING_URL', '')

PROCESSING_BACKEND = os.environ.get('PROCESSING_BACKEND', 'auto').lower()
INFERENCE_PROVIDER = (os.environ.get('INFERENCE_PROVIDER') or 'modal').strip().lower()
ACTIVE_INFERENCE_PROVIDER = (
    os.environ.get('ACTIVE_INFERENCE_PROVIDER')
    or INFERENCE_PROVIDER
).strip().lower()
MODAL_TOKEN_SECRET = os.environ.get('MODAL_TOKEN_SECRET', '')
FAL_KEY = (os.environ.get('FAL_KEY') or os.environ.get('FAL_API_KEY') or '').strip()
FAL_DUBBING_ENDPOINT = os.environ.get('FAL_DUBBING_ENDPOINT', '').strip()
FAL_TTS_ENDPOINT = os.environ.get('FAL_TTS_ENDPOINT', '').strip()

# Pricing & Credits
WELCOME_CREDITS = int(os.environ.get('WELCOME_CREDITS', '1000'))
DUB_COST = int(os.environ.get('DUB_COST', '100'))
LIPSYNC_COST = int(os.environ.get('LIPSYNC_COST', '150'))
TTS_COST = int(os.environ.get('TTS_COST', '20'))
STT_COST = int(os.environ.get('STT_COST', '15'))

# CORS & Upload Limits
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*')
MAX_UPLOAD_MB = int(os.environ.get('MAX_UPLOAD_MB', '500'))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {
    'video': ['mp4', 'mov', 'mkv', 'webm', 'avi', 'mpg', 'mpeg', 'm4v'],
    'audio': ['mp3', 'wav', 'm4a', 'aac', 'ogg', 'flac', 'opus'],
}

ADMIN_SECRET = os.environ.get('ADMIN_SECRET', 'change-me')

def is_video_file(filename):
    if not filename: return False
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in ALLOWED_EXTENSIONS['video']

def is_audio_file(filename):
    if not filename: return False
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in ALLOWED_EXTENSIONS['audio']

def get_file_extension(url_or_path):
    if not url_or_path: return ''
    clean = url_or_path.split('?')[0]
    return clean.rsplit('.', 1)[-1].lower() if '.' in clean else ''

def is_video_url(url):
    return get_file_extension(url) in ALLOWED_EXTENSIONS['video']
