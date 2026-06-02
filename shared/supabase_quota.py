# shared/supabase_quota.py — Supabase quota helpers (dubbing worker)
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Dict

import requests

logger = logging.getLogger(__name__)


def build_supabase_rest_headers() -> Dict[str, str]:
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def fetch_user_quota_row(user_id: str) -> dict:
    try:
        base = os.environ.get("SUPABASE_URL", "")
        if not base or user_id == "default_user":
            return {}
        res = requests.get(
            f"{base}/rest/v1/user_quotas?user_id=eq.{user_id}&select=*",
            headers=build_supabase_rest_headers(),
            timeout=10,
        )
        if res.ok and res.json():
            return res.json()[0]
    except Exception as exc:
        logger.warning("fetch_user_quota_row failed: %s", exc)
    return {}


def increment_dub_seconds_used(user_id: str, seconds_used: int) -> dict:
    try:
        base = os.environ.get("SUPABASE_URL", "")
        if not base:
            return {}
        res = requests.post(
            f"{base}/rest/v1/rpc/increment_dub_usage",
            json={"p_user_id": user_id, "p_seconds": seconds_used},
            headers={**build_supabase_rest_headers(), "Prefer": "return=representation"},
            timeout=10,
        )
        if res.ok:
            return res.json() or {}
    except Exception as exc:
        logger.warning("increment_dub_seconds_used failed: %s", exc)
    return {}


def format_quota_reset_date(reset_date: Any) -> str:
    try:
        return datetime.fromisoformat(str(reset_date).replace("Z", "")).strftime("%b %d, %Y")
    except Exception:
        return "next month"


def send_dub_quota_notifications(user_info: dict, quota: dict) -> None:
    try:
        from email_service import send_quota_exhausted, send_quota_warning

        email = (user_info.get("email") or "").strip()
        if not email:
            return
        name = user_info.get("name", "User")
        plan = quota.get("plan", "free")
        user_id = quota.get("user_id", "")
        dub_used = quota.get("dub_seconds_used", 0)
        dub_limit = quota.get("dub_seconds_limit", 1) or 1
        dub_pct = dub_used / dub_limit * 100
        reset_date = format_quota_reset_date(quota.get("reset_date", "next month"))

        if dub_pct >= 100:
            send_quota_exhausted(email, name, plan, reset_date)
        elif dub_pct >= 80 and not quota.get("warned_80"):
            send_quota_warning(
                email,
                name,
                quota.get("tts_chars_used", 0),
                quota.get("tts_chars_limit", 1),
                dub_used,
                dub_limit,
                quota.get("stt_minutes_used", 0),
                quota.get("stt_minutes_limit", 1),
                plan,
            )
            try:
                base = os.environ.get("SUPABASE_URL", "")
                requests.patch(
                    f"{base}/rest/v1/user_quotas?user_id=eq.{user_id}",
                    json={"warned_80": True},
                    headers=build_supabase_rest_headers(),
                    timeout=5,
                )
            except Exception:
                pass
    except Exception as exc:
        logger.error("send_dub_quota_notifications error: %s", exc)
