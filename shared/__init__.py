# shared/__init__.py
"""
🔧 Shared utilities - يُكرَّر في كل repo
"""
from . import config
from . import auth
from . import r2_client
from . import routing
from . import celery_setup

__all__ = ['config', 'auth', 'r2_client', 'routing', 'celery_setup']
