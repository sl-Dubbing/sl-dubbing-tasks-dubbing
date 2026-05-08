# shared/__init__.py
"""
🔧 Shared utilities - يُكرَّر في كل repo
"""
from . import config
from . import r2_client
from . import routing
from . import celery_setup

# قمنا بإزالة auth لتجنب مشكلة الاستدعاء الدائري في الـ Workers
__all__ = ['config', 'r2_client', 'routing', 'celery_setup']
