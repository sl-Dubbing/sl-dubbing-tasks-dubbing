# shared/__init__.py — V2.0 (Fixing Circular Import)
"""
🔧 Shared utilities - تم تنظيفه لحل مشكلة الـ ImportError
"""
from . import config
from . import r2_client
from . import routing
from . import celery_setup
from . import models  # تأكد من إضافة models هنا

# قمنا بإزالة auth مؤقتاً لحل مشكلة التعليق في Railway
__all__ = ['config', 'r2_client', 'routing', 'celery_setup', 'models']
