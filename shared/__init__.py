# shared/__init__.py — V2.0 (Fixing Circular Import)
"""
🔧 Shared utilities - تم تنظيفه لحل مشكلة الـ ImportError في Railway
"""
from . import config
from . import r2_client
from . import routing
from . import celery_setup
from . import models

# أزلنا auth نهائياً لأنه يسبب دوامة استيراد (Circular Import)
__all__ = ['config', 'r2_client', 'routing', 'celery_setup', 'models']
