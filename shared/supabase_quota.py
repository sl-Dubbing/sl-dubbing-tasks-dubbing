# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/supabase_quota.py
# # AR Celery workers
# # KW مصادقة,auth
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/supabase_quota.py
# # AR Celery workers
# # KW مصادقة,auth
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/supabase_quota.py
# # AR وحدة الدبلجة — رفع، بدء مهمة، polling، أصوات
# # CONVENTION — # FN / # AR فوق كل دالة، # قبل كل خطوة — see FUNCTION_INDEX.md
# shared/supabase_quota.py — Supabase quota helpers (dubbing worker)
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Dict

import requests

logger = logging.getLogger(__name__)


# # FN build_supabase_rest_headers
# # AR بناء supabase rest headers (build_supabase_rest_headers)
# # FN build_supabase_rest_headers
# # AR المصادقة والجلسة (build_supabase_rest_headers)
# # KW مصادقة,auth,JWT,supabase
# # FN build_supabase_rest_headers
# # AR المصادقة والجلسة (build_supabase_rest_headers)
# # KW مصادقة,auth,JWT,supabase
def build_supabase_rest_headers() -> Dict[str, str]:
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    # # return — إرجاع النتيجة
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        # # block — إرجاع نتيجة
        # # block — إرجاع نتيجة
        "Content-Type": "application/json",
    }


# # FN fetch_user_quota_row
# # AR جلب user quota row (fetch_user_quota_row)
# # FN fetch_user_quota_row
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR المصادقة والجلسة (fetch_user_quota_row)
# # block — قاعدة بيانات
# # KW مصادقة,auth,JWT,supabase
# # FN fetch_user_quota_row
# # AR المصادقة والجلسة (fetch_user_quota_row)
# # KW مصادقة,auth,JWT,supabase
def fetch_user_quota_row(user_id: str) -> dict:
    # # try — معالجة عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    try:
        base = os.environ.get("SUPABASE_URL", "")
        # # block — معالجة أخطاء
        if not base or user_id == "default_user":
            # # block — معالجة أخطاء
            # # return — إرجاع النتيجة
            return {}
        # # HTTP — طلب outbound
        # # HTTP — outbound
        # # block — إرجاع نتيجة
        # # HTTP — outbound
        res = requests.get(
            f"{base}/rest/v1/user_quotas?user_id=eq.{user_id}&select=*",
            # # block — طلب HTTP/API
            headers=build_supabase_rest_headers(),
            timeout=10,
        # # block — طلب HTTP/API
        )
        # # parse — قراءة JSON من الاستجابة
        if res.ok and res.json():
            # # return — إرجاع النتيجة
            # # block — parse/serialize JSON
            return res.json()[0]
    # # block — parse/serialize JSON
    # # catch — التقاط الخطأ
    # # catch — التقاط خطأ
    # # catch — التقاط خطأ
    except Exception as exc:
        logger.warning("fetch_user_quota_row failed: %s", exc)
    # # return — إرجاع النتيجة
    # # block — معالجة أخطاء
    # # block — معالجة أخطاء
    return {}


# # FN increment_dub_seconds_used
# # AR increment dub seconds used (increment_dub_seconds_used)
# # FN increment_dub_seconds_used
# # AR المصادقة والجلسة (increment_dub_seconds_used)
# # block — إرجاع نتيجة
# # KW مصادقة,auth,JWT,supabase
# # FN increment_dub_seconds_used
# # AR المصادقة والجلسة (increment_dub_seconds_used)
# # KW مصادقة,auth,JWT,supabase
def increment_dub_seconds_used(user_id: str, seconds_used: int) -> dict:
    # # try — معالجة عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    try:
        base = os.environ.get("SUPABASE_URL", "")
        # # block — معالجة أخطاء
        if not base:
            # # block — معالجة أخطاء
            # # return — إرجاع النتيجة
            return {}
        # # HTTP — طلب outbound
        # # HTTP — outbound
        # # block — إرجاع نتيجة
        # # HTTP — outbound
        res = requests.post(
            f"{base}/rest/v1/rpc/increment_dub_usage",
            # # block — طلب HTTP/API
            json={"p_user_id": user_id, "p_seconds": seconds_used},
            headers={**build_supabase_rest_headers(), "Prefer": "return=representation"},
            # # block — طلب HTTP/API
            timeout=10,
        )
        if res.ok:
            # # return — إرجاع النتيجة
            # # block — parse/serialize JSON
            return res.json() or {}
    # # block — parse/serialize JSON
    # # catch — التقاط الخطأ
    # # catch — التقاط خطأ
    # # catch — التقاط خطأ
    except Exception as exc:
        logger.warning("increment_dub_seconds_used failed: %s", exc)
    # # return — إرجاع النتيجة
    # # block — معالجة أخطاء
    # # block — معالجة أخطاء
    return {}


# # FN format_quota_reset_date
# # AR format quota إعادة ضبط date (format_quota_reset_date)
# # FN format_quota_reset_date
# # AR المصادقة والجلسة (format_quota_reset_date)
# # block — إرجاع نتيجة
# # KW مصادقة,auth,JWT,supabase
# # FN format_quota_reset_date
# # AR المصادقة والجلسة (format_quota_reset_date)
# # KW مصادقة,auth,JWT,supabase
def format_quota_reset_date(reset_date: Any) -> str:
    # # try — معالجة عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    try:
        return datetime.fromisoformat(str(reset_date).replace("Z", "")).strftime("%b %d, %Y")
    # # block — معالجة أخطاء
    # # catch — التقاط الخطأ
    # # block — معالجة أخطاء
    # # catch — التقاط خطأ
    # # catch — التقاط خطأ
    except Exception:
        # # return — إرجاع النتيجة
        # # block — معالجة أخطاء
        return "next month"


# # FN send_dub_quota_notifications
# # AR send dub quota notifications (send_dub_quota_notifications)
# # block — معالجة أخطاء
# # FN send_dub_quota_notifications
# # AR المصادقة والجلسة (send_dub_quota_notifications)
# # block — قاعدة بيانات
# # KW مصادقة,auth,JWT,supabase
# # FN send_dub_quota_notifications
# # AR المصادقة والجلسة (send_dub_quota_notifications)
# # KW مصادقة,auth,JWT,supabase
def send_dub_quota_notifications(user_info: dict, quota: dict) -> None:
    # # try — معالجة عملية قد تفشل
    # # try — عملية قد تفشل
    # # try — عملية قد تفشل
    try:
        from email_service import send_quota_exhausted, send_quota_warning

        # # block — معالجة أخطاء
        email = (user_info.get("email") or "").strip()
        # # block — معالجة أخطاء
        if not email:
            # # return — إرجاع النتيجة
            return
        name = user_info.get("name", "User")
        # # block — إرجاع نتيجة
        plan = quota.get("plan", "free")
        user_id = quota.get("user_id", "")
        # # block — إرجاع نتيجة
        dub_used = quota.get("dub_seconds_used", 0)
        dub_limit = quota.get("dub_seconds_limit", 1) or 1
        dub_pct = dub_used / dub_limit * 100
        # # block — تنفيذ منطق — راجع الأسطر التالية
        reset_date = format_quota_reset_date(quota.get("reset_date", "next month"))

        if dub_pct >= 100:
            send_quota_exhausted(email, name, plan, reset_date)
        # # block — فرع شرطي
        elif dub_pct >= 80 and not quota.get("warned_80"):
            send_quota_warning(
                # # block — فرع شرطي
                email,
                name,
                quota.get("tts_chars_used", 0),
                quota.get("tts_chars_limit", 1),
                # # block — توليد صوت TTS
                dub_used,
                # # block — توليد صوت TTS
                dub_limit,
                quota.get("stt_minutes_used", 0),
                quota.get("stt_minutes_limit", 1),
                plan,
            )
            # # block — معالجة أخطاء
            # # block — معالجة أخطاء
            # # try — معالجة عملية قد تفشل
            # # try — عملية قد تفشل
            # # try — عملية قد تفشل
            try:
                base = os.environ.get("SUPABASE_URL", "")
                # # HTTP — طلب outbound
                # # block — معالجة أخطاء
                # # HTTP — outbound
                # # block — طلب HTTP/API
                # # HTTP — outbound
                requests.patch(
                    f"{base}/rest/v1/user_quotas?user_id=eq.{user_id}",
                    json={"warned_80": True},
                    # # block — طلب HTTP/API
                    headers=build_supabase_rest_headers(),
                    timeout=5,
                )
            # # block — معالجة أخطاء
            # # catch — التقاط الخطأ
            # # catch — التقاط خطأ
            # # block — معالجة أخطاء
            # # catch — التقاط خطأ
            except Exception:
                pass
    # # catch — التقاط الخطأ
    # # catch — التقاط خطأ
    # # block — معالجة أخطاء
    # # block — معالجة أخطاء
    # # catch — التقاط خطأ
    except Exception as exc:
        logger.error("send_dub_quota_notifications error: %s", exc)
