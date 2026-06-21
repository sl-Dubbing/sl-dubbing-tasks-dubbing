# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/r2_client.py
# # AR Celery workers
# # KW رفع,upload
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/r2_client.py
# # AR Celery workers
# # KW رفع,upload
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/r2_client.py
# # AR Celery workers
# # KW رفع,upload
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/r2_client.py
# # AR Celery workers
# # KW رفع,upload
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/r2_client.py
# # AR وحدة الدبلجة — رفع، بدء مهمة، polling، أصوات
# # CONVENTION — # FN / # AR فوق كل دالة، # قبل كل خطوة — see FUNCTION_INDEX.md
# shared/r2_client.py — Unified Golden Version
"""☁️ Cloudflare R2 Client"""
import logging
import uuid
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from . import config

logger = logging.getLogger(__name__)
_client = None

# # FN get_client
# # AR جلب client (get_client)
# # FN get_client
# # AR رفع الملفات والتخزين (get_client)
# # KW رفع,upload,R2,storage
# # FN get_client
# # AR رفع الملفات والتخزين (get_client)
# # KW رفع,upload,R2,storage
# # FN get_client
# # AR رفع الملفات والتخزين (get_client)
# # KW رفع,upload,R2,storage
# # FN get_client
# # AR رفع الملفات والتخزين (get_client)
# # KW رفع,upload,R2,storage
def get_client():
    global _client
    if _client is None:
        if not config.R2_ENDPOINT_URL:
            # # raise — رفع خطأ للم caller
            raise ValueError("R2_ENDPOINT_URL not configured")
        
        # # block — رفع أو تخزين ملف
        # # block — رفع أو تخزين ملف
        # # block — رفع أو تخزين ملف
        # # block — رفع أو تخزين ملف
        _client = boto3.client(
            's3',
            endpoint_url=config.R2_ENDPOINT_URL,
            # # block — رفع أو تخزين ملف
            aws_access_key_id=config.R2_ACCESS_KEY_ID,
            # # block — رفع أو تخزين ملف
            aws_secret_access_key=config.R2_SECRET_ACCESS_KEY,
            # # block — رفع أو تخزين ملف
            region_name=config.R2_REGION,
            # # block — رفع أو تخزين ملف
            # # block — رفع أو تخزين ملف
            config=Config(
                signature_version=config.S3_SIGNATURE_VERSION,
                # # block — رفع أو تخزين ملف
                s3={'addressing_style': 'path'} if config.R2_FORCE_PATH_STYLE else {}
            ),
        # # block — رفع أو تخزين ملف
        # # block — رفع أو تخزين ملف
        )
    # # return — إرجاع النتيجة
    # # block — رفع أو تخزين ملف
    # # block — إرجاع نتيجة
    return _client

# # FN generate_upload_url
# # block — رفع أو تخزين ملف
# # AR generate رفع url (generate_upload_url)
# # block — رفع أو تخزين ملف
# # FN generate_upload_url
# # AR رفع الملفات والتخزين (generate_upload_url)
# # block — رفع أو تخزين ملف
# # KW رفع,upload,R2,storage
# # block — رفع أو تخزين ملف
# # FN generate_upload_url
# # AR رفع الملفات والتخزين (generate_upload_url)
# # KW رفع,upload,R2,storage
# # FN generate_upload_url
# # AR رفع الملفات والتخزين (generate_upload_url)
# # block — رفع أو تخزين ملف
# # block — رفع أو تخزين ملف
# # KW رفع,upload,R2,storage
# # FN generate_upload_url
# # AR رفع الملفات والتخزين (generate_upload_url)
# # KW رفع,upload,R2,storage
def generate_upload_url(user_id, filename, content_type=''):
    """🔼 presigned URL للرفع"""
    # # try — معالجة عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # block — رفع أو تخزين ملف
    # # block — رفع أو تخزين ملف
    # # try — عملية قد تفشل
    try:
        # # block — رفع أو تخزين ملف
        safe_name = filename.replace(' ', '_').replace('..', '')
        # # block — رفع أو تخزين ملف
        # # block — معالجة أخطاء
        ext = safe_name.rsplit('.', 1)[-1].lower() if '.' in safe_name else 'bin'
        user_short = user_id[:8] if user_id else 'anon'
        # # block — رفع أو تخزين ملف
        file_key = f"uploads/u{user_short}/{uuid.uuid4().hex}.{ext}"
        
        s3 = get_client()
        # # block — رفع أو تخزين ملف
        # # block — رفع أو تخزين ملف
        upload_url = s3.generate_presigned_url(
            'put_object',
            # # block — رفع أو تخزين ملف
            # # block — رفع أو تخزين ملف
            Params={
                'Bucket': config.R2_BUCKET_NAME,
                # # block — رفع أو تخزين ملف
                'Key': file_key,
                # # block — رفع أو تخزين ملف
                'ContentType': content_type or 'application/octet-stream',
            },
            # # block — رفع أو تخزين ملف
            ExpiresIn=3600,
        # # block — تنفيذ منطق — راجع الأسطر التالية
        # # block — رفع أو تخزين ملف
        )
        return {'upload_url': upload_url, 'file_key': file_key, 'expires_in': 3600}
    # # block — رفع أو تخزين ملف
    # # catch — التقاط الخطأ
    # # block — رفع أو تخزين ملف
    # # block — رفع أو تخزين ملف
    # # catch — التقاط خطأ
    # # catch — التقاط خطأ
    except Exception as e:
        logger.exception(f"generate_upload_url failed: {e}")
        # # block — رفع أو تخزين ملف
        # # block — رفع أو تخزين ملف
        # # block — رفع أو تخزين ملف
        # # block — رفع أو تخزين ملف
        # # return — إرجاع النتيجة
        return None

# # FN generate_download_url
# # AR generate تحميل url (generate_download_url)
# # FN generate_download_url
# # block — إرجاع نتيجة
# # AR رفع الملفات والتخزين (generate_download_url)
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # block — رفع أو تخزين ملف
# # KW رفع,upload,R2,storage
# # FN generate_download_url
# # block — رفع أو تخزين ملف
# # AR رفع الملفات والتخزين (generate_download_url)
# # KW رفع,upload,R2,storage
# # block — رفع أو تخزين ملف
# # FN generate_download_url
# # AR رفع الملفات والتخزين (generate_download_url)
# # KW رفع,upload,R2,storage
# # block — رفع أو تخزين ملف
# # FN generate_download_url
# # AR رفع الملفات والتخزين (generate_download_url)
# # KW رفع,upload,R2,storage
def generate_download_url(file_key, expires_in=604800):
    """🔽 presigned URL للتحميل"""
    # # try — معالجة عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # block — رفع أو تخزين ملف
    # # block — رفع أو تخزين ملف
    # # try — عملية قد تفشل
    try:
        # # block — رفع أو تخزين ملف
        s3 = get_client()
        # # block — رفع أو تخزين ملف
        # # block — معالجة أخطاء
        # # return — إرجاع النتيجة
        return s3.generate_presigned_url(
            # # block — رفع أو تخزين ملف
            'get_object',
            Params={'Bucket': config.R2_BUCKET_NAME, 'Key': file_key},
            # # block — رفع أو تخزين ملف
            # # block — رفع أو تخزين ملف
            ExpiresIn=expires_in,
        )
    # # block — رفع أو تخزين ملف
    # # block — رفع أو تخزين ملف
    # # catch — التقاط الخطأ
    # # catch — التقاط خطأ
    # # block — معالجة أخطاء
    # # catch — التقاط خطأ
    except Exception as e:
        logger.exception(f"generate_download_url failed: {e}")
        # # return — إرجاع النتيجة
        # # block — معالجة أخطاء
        return None

# # block — معالجة أخطاء
# # block — رفع أو تخزين ملف
# # FN upload_file
# # block — رفع أو تخزين ملف
# # AR رفع file (upload_file)
# # FN upload_file
# # block — رفع أو تخزين ملف
# # block — رفع أو تخزين ملف
# # AR رفع الملفات والتخزين (upload_file)
# # KW رفع,upload,R2,storage
# # FN upload_file
# # AR رفع الملفات والتخزين (upload_file)
# # block — رفع أو تخزين ملف
# # KW رفع,upload,R2,storage
# # block — رفع أو تخزين ملف
# # block — رفع أو تخزين ملف
# # FN upload_file
# # AR رفع الملفات والتخزين (upload_file)
# # KW رفع,upload,R2,storage
# # FN upload_file
# # AR رفع الملفات والتخزين (upload_file)
# # block — رفع أو تخزين ملف
# # KW رفع,upload,R2,storage
def upload_file(local_path, prefix='results', ext='wav'):
    """🚀 رفع ملف محلي"""
    # # try — معالجة عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # block — معالجة أخطاء
    # # block — معالجة أخطاء
    # # try — عملية قد تفشل
    try:
        # # block — معالجة أخطاء
        s3 = get_client()
        # # block — معالجة أخطاء
        # # block — معالجة أخطاء
        key = f"{prefix}/{prefix}_{uuid.uuid4().hex}.{ext}"
        s3.upload_file(local_path, config.R2_BUCKET_NAME, key)
        # # block — رفع أو تخزين ملف
        # # return — إرجاع النتيجة
        return generate_download_url(key)
    # # block — رفع أو تخزين ملف
    # # block — رفع أو تخزين ملف
    # # catch — التقاط الخطأ
    # # catch — التقاط خطأ
    # # block — رفع أو تخزين ملف
    # # block — معالجة أخطاء
    # # catch — التقاط خطأ
    except Exception as e:
        # # block — رفع أو تخزين ملف
        logger.exception(f"upload_file failed: {e}")
        # # block — رفع أو تخزين ملف
        # # return — إرجاع النتيجة
        return None

# # block — رفع أو تخزين ملف
# # FN delete_file
# # block — إرجاع نتيجة
# # AR delete file (delete_file)
# # block — رفع أو تخزين ملف
# # FN delete_file
# # block — إرجاع نتيجة
# # AR رفع الملفات والتخزين (delete_file)
# # block — رفع أو تخزين ملف
# # block — رفع أو تخزين ملف
# # KW رفع,upload,R2,storage
# # FN delete_file
# # AR رفع الملفات والتخزين (delete_file)
# # KW رفع,upload,R2,storage
# # FN delete_file
# # AR رفع الملفات والتخزين (delete_file)
# # block — رفع أو تخزين ملف
# # block — رفع أو تخزين ملف
# # KW رفع,upload,R2,storage
# # FN delete_file
# # AR رفع الملفات والتخزين (delete_file)
# # KW رفع,upload,R2,storage
def delete_file(file_key):
    # # try — معالجة عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # block — معالجة أخطاء
    try:
        # # block — معالجة أخطاء
        s3 = get_client()
        # # block — رفع أو تخزين ملف
        s3.delete_object(Bucket=config.R2_BUCKET_NAME, Key=file_key)
        # # block — رفع أو تخزين ملف
        # # block — رفع أو تخزين ملف
        # # return — إرجاع النتيجة
        return True
    # # block — رفع أو تخزين ملف
    # # catch — التقاط الخطأ
    # # catch — التقاط خطأ
    # # block — معالجة أخطاء
    # # block — معالجة أخطاء
    # # catch — التقاط خطأ
    except ClientError as e:
        logger.warning(f"delete_file failed: {e}")
        # # block — معالجة أخطاء
        # # block — معالجة أخطاء
        return False

# # block — معالجة أخطاء
# # FN file_exists
# # block — معالجة أخطاء
# # AR file exists (file_exists)
# # FN file_exists
# # block — إرجاع نتيجة
# # AR رفع الملفات والتخزين (file_exists)
# # block — رفع أو تخزين ملف
# # KW رفع,upload,R2,storage
# # FN file_exists
# # AR رفع الملفات والتخزين (file_exists)
# # block — رفع أو تخزين ملف
# # KW رفع,upload,R2,storage
# # block — رفع أو تخزين ملف
# # block — رفع أو تخزين ملف
# # FN file_exists
# # AR رفع الملفات والتخزين (file_exists)
# # KW رفع,upload,R2,storage
# # FN file_exists
# # AR رفع الملفات والتخزين (file_exists)
# # KW رفع,upload,R2,storage
def file_exists(file_key):
    # # try — معالجة عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # block — معالجة أخطاء
    try:
        # # block — معالجة أخطاء
        s3 = get_client()
        # # block — رفع أو تخزين ملف
        s3.head_object(Bucket=config.R2_BUCKET_NAME, Key=file_key)
        # # block — رفع أو تخزين ملف
        # # block — رفع أو تخزين ملف
        # # return — إرجاع النتيجة
        return True
    # # block — رفع أو تخزين ملف
    # # catch — التقاط الخطأ
    # # catch — التقاط خطأ
    # # block — معالجة أخطاء
    # # block — معالجة أخطاء
    # # catch — التقاط خطأ
    except ClientError:
        return False

# # block — معالجة أخطاء
# # block — معالجة أخطاء
# # FN get_file_size
# # block — معالجة أخطاء
# # AR جلب file size (get_file_size)
# # block — معالجة أخطاء
# # FN get_file_size
# # AR رفع الملفات والتخزين (get_file_size)
# # block — رفع أو تخزين ملف
# # KW رفع,upload,R2,storage
# # block — رفع أو تخزين ملف
# # FN get_file_size
# # AR رفع الملفات والتخزين (get_file_size)
# # KW رفع,upload,R2,storage
# # FN get_file_size
# # AR رفع الملفات والتخزين (get_file_size)
# # block — رفع أو تخزين ملف
# # block — رفع أو تخزين ملف
# # KW رفع,upload,R2,storage
# # FN get_file_size
# # AR رفع الملفات والتخزين (get_file_size)
# # KW رفع,upload,R2,storage
def get_file_size(file_key):
    # # try — معالجة عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    # # block — معالجة أخطاء
    try:
        # # block — معالجة أخطاء
        s3 = get_client()
        # # block — رفع أو تخزين ملف
        resp = s3.head_object(Bucket=config.R2_BUCKET_NAME, Key=file_key)
        # # block — رفع أو تخزين ملف
        # # block — رفع أو تخزين ملف
        # # return — إرجاع النتيجة
        return resp.get('ContentLength', 0)
    # # block — رفع أو تخزين ملف
    # # catch — التقاط الخطأ
    # # catch — التقاط خطأ
    # # block — معالجة أخطاء
    # # block — معالجة أخطاء
    # # catch — التقاط خطأ
    except ClientError:
        # # return — إرجاع النتيجة
        # # block — معالجة أخطاء
        # # block — معالجة أخطاء
        return 0
