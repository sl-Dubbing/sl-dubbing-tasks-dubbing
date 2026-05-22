# shared/lang_profiles.py — Target language / dialect profiles (mirrors languages.js + Modal Edge TTS)
"""
Maps UI language codes (e.g. ar-eg, en-gb) to:
  - Arabic dialect names for translation (same strings as languages.js)
  - Regional neural voices (Edge-style IDs)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class TargetLangProfile:
    lang_code: str
    base_lang: str
    dialect: str
    display_name: str
    edge_voice: str
    playht_voice: str
    eleven_voice: str
    eleven_language_code: str
    supports_clone: bool

    @property
    def tts_lang(self) -> str:
        """Base code for XTTS / Whisper-style TTS (matches Modal _tts_lang_code)."""
        return self.base_lang

    @property
    def is_arabic_dialect(self) -> bool:
        return self.base_lang == "ar" and self.lang_code != "ar"


def _norm_code(code: str) -> str:
    return (code or "en-us").strip().lower().replace("_", "-")


_AR: Dict[str, Dict[str, str]] = {
    "ar": {"dialect": "الفصحى", "name": "Arabic (MSA)"},
    "ar-sa": {"dialect": "السعودية", "name": "Arabic (Saudi)"},
    "ar-ae": {"dialect": "الإماراتية", "name": "Arabic (Emirati)"},
    "ar-kw": {"dialect": "الكويتية", "name": "Arabic (Kuwaiti)"},
    "ar-qa": {"dialect": "القطرية", "name": "Arabic (Qatari)"},
    "ar-bh": {"dialect": "البحرينية", "name": "Arabic (Bahraini)"},
    "ar-om": {"dialect": "العمانية", "name": "Arabic (Omani)"},
    "ar-ye": {"dialect": "اليمنية", "name": "Arabic (Yemeni)"},
    "ar-eg": {"dialect": "المصرية", "name": "Arabic (Egyptian)"},
    "ar-sd": {"dialect": "السودانية", "name": "Arabic (Sudanese)"},
    "ar-lb": {"dialect": "اللبنانية", "name": "Arabic (Lebanese)"},
    "ar-sy": {"dialect": "السورية", "name": "Arabic (Syrian)"},
    "ar-jo": {"dialect": "الأردنية", "name": "Arabic (Jordanian)"},
    "ar-ps": {"dialect": "الفلسطينية", "name": "Arabic (Palestinian)"},
    "ar-iq": {"dialect": "العراقية", "name": "Arabic (Iraqi)"},
    "ar-ma": {"dialect": "المغربية", "name": "Arabic (Moroccan)"},
    "ar-dz": {"dialect": "الجزائرية", "name": "Arabic (Algerian)"},
    "ar-tn": {"dialect": "التونسية", "name": "Arabic (Tunisian)"},
    "ar-ly": {"dialect": "الليبية", "name": "Arabic (Libyan)"},
}

_EDGE_VOICE_BY_LANG: Dict[str, str] = {
    "en-us": "en-US-AriaNeural",
    "en-gb": "en-GB-SoniaNeural",
    "en-au": "en-AU-NatashaNeural",
    "en-ca": "en-CA-ClaraNeural",
    "en-in": "en-IN-NeerjaNeural",
    "es-es": "es-ES-ElviraNeural",
    "es-mx": "es-MX-DaliaNeural",
    "es-ar": "es-AR-ElenaNeural",
    "es-co": "es-CO-SalomeNeural",
    "fr-fr": "fr-FR-DeniseNeural",
    "fr-ca": "fr-CA-SylvieNeural",
    "fr-be": "fr-BE-CharlineNeural",
    "de-de": "de-DE-KatjaNeural",
    "de-at": "de-AT-IngridNeural",
    "de-ch": "de-CH-LeniNeural",
    "it-it": "it-IT-ElsaNeural",
    "pt-br": "pt-BR-FranciscaNeural",
    "pt-pt": "pt-PT-RaquelNeural",
    "ru-ru": "ru-RU-SvetlanaNeural",
    "ja-jp": "ja-JP-NanamiNeural",
    "ko-kr": "ko-KR-SunHiNeural",
    "zh-cn": "zh-CN-XiaoxiaoNeural",
    "zh-tw": "zh-TW-HsiaoChenNeural",
    "tr-tr": "tr-TR-EmelNeural",
    "hi-in": "hi-IN-SwaraNeural",
    "pl-pl": "pl-PL-ZofiaNeural",
    "nl-nl": "nl-NL-FennaNeural",
    "ar": "ar-SA-HamedNeural",
    "ar-sa": "ar-SA-HamedNeural",
    "ar-eg": "ar-EG-ShakirNeural",
    "ar-ae": "ar-AE-HamdanNeural",
    "ar-kw": "ar-KW-FahedNeural",
    "ar-qa": "ar-QA-MoazNeural",
    "ar-bh": "ar-BH-AliNeural",
    "ar-om": "ar-OM-AbdullahNeural",
    "ar-ye": "ar-YE-SalehNeural",
    "ar-lb": "ar-LB-RamiNeural",
    "ar-sy": "ar-SY-AmanyNeural",
    "ar-jo": "ar-JO-TaimNeural",
    "ar-ps": "ar-PS-MoazNeural",
    "ar-iq": "ar-IQ-RanaNeural",
    "ar-ma": "ar-MA-JamalNeural",
    "ar-dz": "ar-DZ-IsmaelNeural",
    "ar-tn": "ar-TN-HediNeural",
    "ar-ly": "ar-LY-ImanNeural",
    "ar-sd": "ar-SA-HamedNeural",
    "fa-ir": "fa-IR-DilaraNeural",
    "he-il": "he-IL-HilaNeural",
    "id-id": "id-ID-GadisNeural",
    "vi-vn": "vi-VN-HoaiMyNeural",
    "th-th": "th-TH-PremwadeeNeural",
    "uk-ua": "uk-UA-PolinaNeural",
}

_PLAYHT_VOICE_BY_LANG: Dict[str, str] = {
    "en-us": "Dexter (English (US)/American)",
    "en-gb": "George (English (UK)/British)",
    "en-au": "Charlotte (English (Australia)/Australian)",
    "es-es": "Pedro (Spanish (Spain)/Castilian)",
    "es-mx": "Miguel (Spanish (Mexico)/Mexican)",
    "fr-fr": "Antoine (French (France)/Parisian)",
    "fr-ca": "Antoine (French (Canada)/Canadian)",
    "de-de": "Matthias (German (Germany)/Standard)",
    "it-it": "Lily (Italian (Italy)/Standard)",
    "pt-br": "Pedro (Portuguese (Brazil)/Brazilian)",
    "pt-pt": "Pedro (Portuguese (Portugal)/European)",
    "ja-jp": "Kaori (Japanese (Japan)/Standard)",
    "ko-kr": "Seoyeon (Korean (Korea)/Standard)",
    "zh-cn": "Xiaoxiao (Chinese (Mandarin)/Standard)",
    "ru-ru": "Dmitry (Russian (Russia)/Standard)",
    "tr-tr": "Emel (Turkish (Turkey)/Standard)",
    "hi-in": "Devi (Hindi (India)/Standard)",
    "ar": "Ayman (Arabic)/Standard",
    "ar-sa": "Ayman (Arabic)/Standard",
    "ar-eg": "Yasmin (Arabic)/Standard",
    "ar-ae": "Ayman (Arabic)/Standard",
    "ar-lb": "Yasmin (Arabic)/Standard",
    "ar-ma": "Yasmin (Arabic)/Standard",
    "ar-iq": "Ayman (Arabic)/Standard",
}

_ELEVEN_VOICE_BY_LANG: Dict[str, str] = {
    "en-us": "Rachel",
    "en-gb": "George",
    "en-au": "Charlotte",
    "es-es": "Matilda",
    "es-mx": "Valentina",
    "fr-fr": "Charlotte",
    "fr-ca": "Charlotte",
    "de-de": "Serena",
    "it-it": "Matilda",
    "pt-br": "Jessica",
    "pt-pt": "Jessica",
    "ja-jp": "Adam",
    "ko-kr": "Adam",
    "zh-cn": "Adam",
    "ru-ru": "Adam",
    "tr-tr": "Adam",
    "hi-in": "Adam",
    "ar": "Adam",
    "ar-sa": "Adam",
    "ar-eg": "Adam",
    "ar-ae": "Adam",
    "ar-lb": "Adam",
    "ar-ma": "Adam",
    "ar-iq": "Adam",
}

_ELEVEN_LANG_CODE: Dict[str, str] = {
    "ar": "ar",
    "en": "en",
    "es": "es",
    "fr": "fr",
    "de": "de",
    "it": "it",
    "pt": "pt",
    "ja": "ja",
    "ko": "ko",
    "zh": "zh",
    "ru": "ru",
    "tr": "tr",
    "hi": "hi",
}


def _base_lang(code: str) -> str:
    c = _norm_code(code)
    if not c or c == "auto":
        return "en"
    return c.split("-")[0]


def _lookup_voice(table: Dict[str, str], lang_code: str, base: str, default: str) -> str:
    return table.get(lang_code) or table.get(base) or default


def resolve_target_language_profile(
    target_lang: str,
    dialect_override: str = "",
) -> TargetLangProfile:
    """Resolve full target profile from UI lang code (e.g. ar-eg)."""
    lang_code = _norm_code(target_lang)
    base = _base_lang(lang_code)

    ar_meta = _AR.get(lang_code) or _AR.get(base) or {}
    dialect = (dialect_override or ar_meta.get("dialect") or "").strip()
    if base == "ar" and not dialect and lang_code == "ar":
        dialect = "الفصحى"

    display = ar_meta.get("name") or lang_code

    edge = _lookup_voice(_EDGE_VOICE_BY_LANG, lang_code, base, "en-US-AriaNeural")
    playht = _lookup_voice(_PLAYHT_VOICE_BY_LANG, lang_code, base, "Dexter (English (US)/American)")
    eleven = _lookup_voice(_ELEVEN_VOICE_BY_LANG, lang_code, base, "Rachel")
    eleven_lc = _ELEVEN_LANG_CODE.get(base, base)

    supports_clone = base in (
        "ar", "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "hi", "tr", "pl", "nl", "cs", "hu"
    )

    return TargetLangProfile(
        lang_code=lang_code,
        base_lang=base,
        dialect=dialect,
        display_name=display,
        edge_voice=edge,
        playht_voice=playht,
        eleven_voice=eleven,
        eleven_language_code=eleven_lc,
        supports_clone=supports_clone,
    )
