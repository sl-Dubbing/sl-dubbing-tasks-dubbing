# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/dub_engine_policy.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/dub_engine_policy.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/dub_engine_policy.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/dub_engine_policy.py
# # AR Celery workers
# # KW عام,general
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/dub_engine_policy.py
# # AR وحدة الدبلجة — رفع، بدء مهمة، polling، أصوات
# # CONVENTION — # FN / # AR فوق كل دالة، # قبل كل خطوة — see FUNCTION_INDEX.md
# shared/dub_engine_policy.py — Unified dubbing voice quality & engine policy
from __future__ import annotations

from typing import Any, Dict, Optional

_ENGINE_ALIASES = {
    "cosy": "cosyvoice",
    "cosyvoice2": "cosyvoice",
    "cosy-voice": "cosyvoice",
    "xtts_v2": "chatterbox",
    "xtts-v2": "chatterbox",
    "xtts2": "chatterbox",
    "xtts": "chatterbox",
    "chatterbox-tts": "chatterbox",
}

DEFAULT_DUB_QUALITY = "studio"


# # FN normalize_dub_engine
# # AR تطبيع dub engine (normalize_dub_engine)
# # FN normalize_dub_engine
# # AR دالة normalize_dub_engine (normalize_dub_engine)
# # KW عام,general
# # FN normalize_dub_engine
# # AR دالة normalize_dub_engine (normalize_dub_engine)
# # KW عام,general
# # FN normalize_dub_engine
# # AR دالة normalize_dub_engine (normalize_dub_engine)
# # KW عام,general
# # FN normalize_dub_engine
# # AR دالة normalize_dub_engine (normalize_dub_engine)
# # KW عام,general
def normalize_dub_engine(name: str) -> str:
    key = (name or "").strip().lower()
    # # return — إرجاع النتيجة
    return _ENGINE_ALIASES.get(key, key)


# # FN resolve_dub_force_engine
# # AR حل/استنتاج dub force engine (resolve_dub_force_engine)
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # FN resolve_dub_force_engine
# # AR دالة resolve_dub_force_engine (resolve_dub_force_engine)
# # KW عام,general
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN resolve_dub_force_engine
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR دالة resolve_dub_force_engine (resolve_dub_force_engine)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # KW عام,general
# # FN resolve_dub_force_engine
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR دالة resolve_dub_force_engine (resolve_dub_force_engine)
# # KW عام,general
# # FN resolve_dub_force_engine
# # AR دالة resolve_dub_force_engine (resolve_dub_force_engine)
# # KW عام,general
def resolve_dub_force_engine(
    *,
    body: Optional[dict] = None,
    voice_config: Optional[dict] = None,
    catalog_engine: str = "",
) -> Optional[str]:
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    body = body or {}
    vc = voice_config or {}
    explicit = (
        # # block — معالجة صوت/استنساخ
        body.get("force_engine")
        # # block — معالجة صوت/استنساخ
        or body.get("engine")
        # # block — معالجة صوت/استنساخ
        or vc.get("force_engine")
        # # block — معالجة صوت/استنساخ
        # # block — تنفيذ منطق — راجع الأسطر التالية
        or vc.get("engine")
        or catalog_engine
        # # block — تنفيذ منطق — راجع الأسطر التالية
        or ""
    ).strip()
    # # block — تنفيذ منطق — راجع الأسطر التالية
    # # block — تنفيذ منطق — راجع الأسطر التالية
    normalized = normalize_dub_engine(explicit)
    return normalized or None


# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # FN resolve_dub_quality
# # AR حل/استنتاج dub quality (resolve_dub_quality)
# # block — إرجاع نتيجة
# # FN resolve_dub_quality
# # block — إرجاع نتيجة
# # AR دالة resolve_dub_quality (resolve_dub_quality)
# # KW عام,general
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN resolve_dub_quality
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR دالة resolve_dub_quality (resolve_dub_quality)
# # KW عام,general
# # FN resolve_dub_quality
# # AR دالة resolve_dub_quality (resolve_dub_quality)
# # KW عام,general
# # FN resolve_dub_quality
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR دالة resolve_dub_quality (resolve_dub_quality)
# # KW عام,general
def resolve_dub_quality(
    *,
    body: Optional[dict] = None,
    voice_config: Optional[dict] = None,
    default: str = DEFAULT_DUB_QUALITY,
) -> str:
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    body = body or {}
    vc = voice_config or {}
    q = (
        # # block — معالجة صوت/استنساخ
        body.get("quality")
        # # block — معالجة صوت/استنساخ
        or vc.get("quality")
        # # block — معالجة صوت/استنساخ
        or default
        # # block — معالجة صوت/استنساخ
        # # block — تنفيذ منطق — راجع الأسطر التالية
        or DEFAULT_DUB_QUALITY
    )
    # # block — إرجاع نتيجة
    return str(q).strip() or DEFAULT_DUB_QUALITY


# # FN apply_high_quality_voice_defaults
# # block — معالجة صوت/استنساخ
# # block — معالجة صوت/استنساخ
# # AR تطبيق high quality voice defaults (apply_high_quality_voice_defaults)
# # FN apply_high_quality_voice_defaults
# # block — معالجة صوت/استنساخ
# # block — معالجة صوت/استنساخ
# # AR الصوت والاستنساخ (apply_high_quality_voice_defaults)
# # KW صوت,استنساخ,voice,clone,sample
# # block — معالجة صوت/استنساخ
# # FN apply_high_quality_voice_defaults
# # block — معالجة صوت/استنساخ
# # AR الصوت والاستنساخ (apply_high_quality_voice_defaults)
# # KW صوت,استنساخ,voice,clone,sample
# # block — معالجة صوت/استنساخ
# # FN apply_high_quality_voice_defaults
# # block — معالجة صوت/استنساخ
# # AR الصوت والاستنساخ (apply_high_quality_voice_defaults)
# # KW صوت,استنساخ,voice,clone,sample
# # FN apply_high_quality_voice_defaults
# # AR الصوت والاستنساخ (apply_high_quality_voice_defaults)
# # KW صوت,استنساخ,voice,clone,sample
def apply_high_quality_voice_defaults(voice_config: dict, *, quality: str = "") -> dict:
    vc = dict(voice_config or {})
    vc["quality"] = resolve_dub_quality(voice_config=vc, default=quality or DEFAULT_DUB_QUALITY)
    # # return — إرجاع النتيجة
    return vc


# # FN attach_engine_fields
# # block — معالجة صوت/استنساخ
# # block — معالجة صوت/استنساخ
# # block — معالجة صوت/استنساخ
# # block — معالجة صوت/استنساخ
# # AR attach engine fields (attach_engine_fields)
# # FN attach_engine_fields
# # AR دالة attach_engine_fields (attach_engine_fields)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # KW عام,general
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN attach_engine_fields
# # block — تنفيذ منطق — راجع الأسطر التالية
# # AR دالة attach_engine_fields (attach_engine_fields)
# # KW عام,general
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN attach_engine_fields
# # AR دالة attach_engine_fields (attach_engine_fields)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # KW عام,general
# # FN attach_engine_fields
# # AR دالة attach_engine_fields (attach_engine_fields)
# # block — تنفيذ منطق — راجع الأسطر التالية
# # KW عام,general
def attach_engine_fields(payload: Dict[str, Any], force_engine: Optional[str]) -> Dict[str, Any]:
    p = dict(payload)
    if force_engine:
        p["force_engine"] = force_engine
        p["engine"] = force_engine
    else:
        # # block — تنفيذ منطق — راجع الأسطر التالية
        # # block — تنفيذ منطق — راجع الأسطر التالية
        # # block — تنفيذ منطق — راجع الأسطر التالية
        # # block — تنفيذ منطق — راجع الأسطر التالية
        p.pop("force_engine", None)
        p.pop("engine", None)
    # # return — إرجاع النتيجة
    # # block — إرجاع نتيجة
    return p
