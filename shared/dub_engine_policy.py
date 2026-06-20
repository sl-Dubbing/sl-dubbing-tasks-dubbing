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


def normalize_dub_engine(name: str) -> str:
    key = (name or "").strip().lower()
    return _ENGINE_ALIASES.get(key, key)


def resolve_dub_force_engine(
    *,
    body: Optional[dict] = None,
    voice_config: Optional[dict] = None,
    catalog_engine: str = "",
) -> Optional[str]:
    body = body or {}
    vc = voice_config or {}
    explicit = (
        body.get("force_engine")
        or body.get("engine")
        or vc.get("force_engine")
        or vc.get("engine")
        or catalog_engine
        or ""
    ).strip()
    normalized = normalize_dub_engine(explicit)
    return normalized or None


def resolve_dub_quality(
    *,
    body: Optional[dict] = None,
    voice_config: Optional[dict] = None,
    default: str = DEFAULT_DUB_QUALITY,
) -> str:
    body = body or {}
    vc = voice_config or {}
    q = (
        body.get("quality")
        or vc.get("quality")
        or default
        or DEFAULT_DUB_QUALITY
    )
    return str(q).strip() or DEFAULT_DUB_QUALITY


def apply_high_quality_voice_defaults(voice_config: dict, *, quality: str = "") -> dict:
    vc = dict(voice_config or {})
    vc["quality"] = resolve_dub_quality(voice_config=vc, default=quality or DEFAULT_DUB_QUALITY)
    return vc


def attach_engine_fields(payload: Dict[str, Any], force_engine: Optional[str]) -> Dict[str, Any]:
    p = dict(payload)
    if force_engine:
        p["force_engine"] = force_engine
        p["engine"] = force_engine
    else:
        p.pop("force_engine", None)
        p.pop("engine", None)
    return p
