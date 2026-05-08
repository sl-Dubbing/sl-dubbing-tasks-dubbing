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

def get_client():
    global _client
    if _client is None:
        if not config.R2_ENDPOINT_URL:
            raise ValueError("R2_ENDPOINT_URL not configured")
        
        _client = boto3.client(
            's3',
            endpoint_url=config.R2_ENDPOINT_URL,
            aws_access_key_id=config.R2_ACCESS_KEY_ID,
            aws_secret_access_key=config.R2_SECRET_ACCESS_KEY,
            region_name=config.R2_REGION,
            config=Config(
                signature_version=config.S3_SIGNATURE_VERSION,
                s3={'addressing_style': 'path'} if config.R2_FORCE_PATH_STYLE else {}
            ),
        )
    return _client

def generate_upload_url(user_id, filename, content_type=''):
    """🔼 presigned URL للرفع"""
    try:
        safe_name = filename.replace(' ', '_').replace('..', '')
        ext = safe_name.rsplit('.', 1)[-1].lower() if '.' in safe_name else 'bin'
        user_short = user_id[:8] if user_id else 'anon'
        file_key = f"uploads/u{user_short}/{uuid.uuid4().hex}.{ext}"
        
        s3 = get_client()
        upload_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': config.R2_BUCKET_NAME,
                'Key': file_key,
                'ContentType': content_type or 'application/octet-stream',
            },
            ExpiresIn=3600,
        )
        return {'upload_url': upload_url, 'file_key': file_key, 'expires_in': 3600}
    except Exception as e:
        logger.exception(f"generate_upload_url failed: {e}")
        return None

def generate_download_url(file_key, expires_in=604800):
    """🔽 presigned URL للتحميل"""
    try:
        s3 = get_client()
        return s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': config.R2_BUCKET_NAME, 'Key': file_key},
            ExpiresIn=expires_in,
        )
    except Exception as e:
        logger.exception(f"generate_download_url failed: {e}")
        return None

def upload_file(local_path, prefix='results', ext='wav'):
    """🚀 رفع ملف محلي"""
    try:
        s3 = get_client()
        key = f"{prefix}/{prefix}_{uuid.uuid4().hex}.{ext}"
        s3.upload_file(local_path, config.R2_BUCKET_NAME, key)
        return generate_download_url(key)
    except Exception as e:
        logger.exception(f"upload_file failed: {e}")
        return None

def delete_file(file_key):
    try:
        s3 = get_client()
        s3.delete_object(Bucket=config.R2_BUCKET_NAME, Key=file_key)
        return True
    except ClientError as e:
        logger.warning(f"delete_file failed: {e}")
        return False

def file_exists(file_key):
    try:
        s3 = get_client()
        s3.head_object(Bucket=config.R2_BUCKET_NAME, Key=file_key)
        return True
    except ClientError:
        return False

def get_file_size(file_key):
    try:
        s3 = get_client()
        resp = s3.head_object(Bucket=config.R2_BUCKET_NAME, Key=file_key)
        return resp.get('ContentLength', 0)
    except ClientError:
        return 0
