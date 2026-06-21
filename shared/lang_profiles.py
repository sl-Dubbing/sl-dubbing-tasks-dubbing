# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/lang_profiles.py
# # AR Celery workers
# # KW لغة,language
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/lang_profiles.py
# # AR Celery workers
# # KW لغة,language
# # CONVENTION — FN/AR/KW + # block كل ~6 أسطر — FUNCTION_INDEX.md DOMAIN_INDEX.md
# # FILE backend/sl-dubbing-tasks-dubbing-main/shared/lang_profiles.py
# # AR وحدة الدبلجة — رفع، بدء مهمة، polling، أصوات
# # CONVENTION — # FN / # AR فوق كل دالة، # قبل كل خطوة — see FUNCTION_INDEX.md
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
    # # FN tts_lang
    # # AR tts lang (tts_lang)
    # # FN tts_lang
    # # AR Text-to-speech (tts_lang)
    # # KW توليد_صوت,TTS,synthesis,لغة,language,dialect
    # # FN tts_lang
    # # AR Text-to-speech (tts_lang)
    # # KW توليد_صوت,TTS,synthesis,لغة,language,dialect
    def tts_lang(self) -> str:
        """Base code for XTTS / Whisper-style TTS (matches Modal _tts_lang_code)."""
        # # return — إرجاع النتيجة
        return self.base_lang

    @property
    # # FN is_arabic_dialect
    # # AR هل arabic dialect (is_arabic_dialect)
    # # FN is_arabic_dialect
    # # AR اللغات واللهجات (is_arabic_dialect)
    # # KW لغة,language,dialect
    # # FN is_arabic_dialect
    # # AR اللغات واللهجات (is_arabic_dialect)
    # # KW لغة,language,dialect
    def is_arabic_dialect(self) -> bool:
        # # return — إرجاع النتيجة
        return self.base_lang == "ar" and self.lang_code != "ar"


# # FN _norm_code
# # AR norm code (_norm_code)
# # FN _norm_code
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # AR اللغات واللهجات (_norm_code)
# # KW لغة,language,dialect
# # FN _norm_code
# # AR اللغات واللهجات (_norm_code)
# # KW لغة,language,dialect
def _norm_code(code: str) -> str:
    # # return — إرجاع النتيجة
    return (code or "en-us").strip().lower().replace("_", "-")


_AR: Dict[str, Dict[str, str]] = {
    "ar": {"dialect": "الفصحى", "name": "Arabic (MSA)"},
    "ar-sa": {"dialect": "السعودية", "name": "Arabic (Saudi)"},
    # # block — إرجاع نتيجة
    # # block — إرجاع نتيجة
    "ar-ae": {"dialect": "الإماراتية", "name": "Arabic (Emirati)"},
    "ar-kw": {"dialect": "الكويتية", "name": "Arabic (Kuwaiti)"},
    "ar-qa": {"dialect": "القطرية", "name": "Arabic (Qatari)"},
    "ar-bh": {"dialect": "البحرينية", "name": "Arabic (Bahraini)"},
    "ar-om": {"dialect": "العمانية", "name": "Arabic (Omani)"},
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ar-ye": {"dialect": "اليمنية", "name": "Arabic (Yemeni)"},
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ar-eg": {"dialect": "المصرية", "name": "Arabic (Egyptian)"},
    "ar-sd": {"dialect": "السودانية", "name": "Arabic (Sudanese)"},
    "ar-lb": {"dialect": "اللبنانية", "name": "Arabic (Lebanese)"},
    "ar-sy": {"dialect": "السورية", "name": "Arabic (Syrian)"},
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ar-jo": {"dialect": "الأردنية", "name": "Arabic (Jordanian)"},
    "ar-ps": {"dialect": "الفلسطينية", "name": "Arabic (Palestinian)"},
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ar-iq": {"dialect": "العراقية", "name": "Arabic (Iraqi)"},
    "ar-ma": {"dialect": "المغربية", "name": "Arabic (Moroccan)"},
    "ar-dz": {"dialect": "الجزائرية", "name": "Arabic (Algerian)"},
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ar-tn": {"dialect": "التونسية", "name": "Arabic (Tunisian)"},
    "ar-ly": {"dialect": "الليبية", "name": "Arabic (Libyan)"},
}

# # block — معالجة صوت/استنساخ
_EDGE_VOICE_BY_LANG: Dict[str, str] = {
    "en-us": "en-US-AriaNeural",
    # # block — معالجة صوت/استنساخ
    "en-gb": "en-GB-SoniaNeural",
    "en-au": "en-AU-NatashaNeural",
    "en-ca": "en-CA-ClaraNeural",
    "en-in": "en-IN-NeerjaNeural",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "es-es": "es-ES-ElviraNeural",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "es-mx": "es-MX-DaliaNeural",
    "es-ar": "es-AR-ElenaNeural",
    "es-co": "es-CO-SalomeNeural",
    "fr-fr": "fr-FR-DeniseNeural",
    "fr-ca": "fr-CA-SylvieNeural",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "fr-be": "fr-BE-CharlineNeural",
    "de-de": "de-DE-KatjaNeural",
    "de-at": "de-AT-IngridNeural",
    "de-ch": "de-CH-LeniNeural",
    "it-it": "it-IT-ElsaNeural",
    "pt-br": "pt-BR-FranciscaNeural",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "pt-pt": "pt-PT-RaquelNeural",
    "ru-ru": "ru-RU-SvetlanaNeural",
    "ja-jp": "ja-JP-NanamiNeural",
    "ko-kr": "ko-KR-SunHiNeural",
    "zh-cn": "zh-CN-XiaoxiaoNeural",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "zh-tw": "zh-TW-HsiaoChenNeural",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "tr-tr": "tr-TR-EmelNeural",
    "hi-in": "hi-IN-SwaraNeural",
    "pl-pl": "pl-PL-ZofiaNeural",
    "nl-nl": "nl-NL-FennaNeural",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ar": "ar-SA-HamedNeural",
    "ar-sa": "ar-SA-HamedNeural",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ar-eg": "ar-EG-ShakirNeural",
    "ar-ae": "ar-AE-HamdanNeural",
    "ar-kw": "ar-KW-FahedNeural",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ar-qa": "ar-QA-MoazNeural",
    "ar-bh": "ar-BH-AliNeural",
    "ar-om": "ar-OM-AbdullahNeural",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ar-ye": "ar-YE-SalehNeural",
    "ar-lb": "ar-LB-RamiNeural",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ar-sy": "ar-SY-AmanyNeural",
    "ar-jo": "ar-JO-TaimNeural",
    "ar-ps": "ar-PS-MoazNeural",
    "ar-iq": "ar-IQ-RanaNeural",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ar-ma": "ar-MA-JamalNeural",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ar-dz": "ar-DZ-IsmaelNeural",
    "ar-tn": "ar-TN-HediNeural",
    "ar-ly": "ar-LY-ImanNeural",
    "ar-sd": "ar-SA-HamedNeural",
    "fa-ir": "fa-IR-DilaraNeural",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "he-il": "he-IL-HilaNeural",
    "id-id": "id-ID-GadisNeural",
    "vi-vn": "vi-VN-HoaiMyNeural",
    "th-th": "th-TH-PremwadeeNeural",
    "uk-ua": "uk-UA-PolinaNeural",
}

# # block — تنفيذ منطق — راجع الأسطر التالية
# # block — معالجة صوت/استنساخ
_PLAYHT_VOICE_BY_LANG: Dict[str, str] = {
    "en-us": "Dexter (English (US)/American)",
    "en-gb": "George (English (UK)/British)",
    "en-au": "Charlotte (English (Australia)/Australian)",
    "es-es": "Pedro (Spanish (Spain)/Castilian)",
    # # block — معالجة صوت/استنساخ
    "es-mx": "Miguel (Spanish (Mexico)/Mexican)",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "fr-fr": "Antoine (French (France)/Parisian)",
    "fr-ca": "Antoine (French (Canada)/Canadian)",
    "de-de": "Matthias (German (Germany)/Standard)",
    "it-it": "Lily (Italian (Italy)/Standard)",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "pt-br": "Pedro (Portuguese (Brazil)/Brazilian)",
    "pt-pt": "Pedro (Portuguese (Portugal)/European)",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ja-jp": "Kaori (Japanese (Japan)/Standard)",
    "ko-kr": "Seoyeon (Korean (Korea)/Standard)",
    "zh-cn": "Xiaoxiao (Chinese (Mandarin)/Standard)",
    # # block — معالجة أخطاء
    "ru-ru": "Dmitry (Russian (Russia)/Standard)",
    "tr-tr": "Emel (Turkish (Turkey)/Standard)",
    "hi-in": "Devi (Hindi (India)/Standard)",
    # # block — معالجة أخطاء
    "ar": "Ayman (Arabic)/Standard",
    "ar-sa": "Ayman (Arabic)/Standard",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ar-eg": "Yasmin (Arabic)/Standard",
    "ar-ae": "Ayman (Arabic)/Standard",
    "ar-lb": "Yasmin (Arabic)/Standard",
    "ar-ma": "Yasmin (Arabic)/Standard",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ar-iq": "Ayman (Arabic)/Standard",
# # block — تنفيذ منطق — راجع الأسطر التالية
}

_ELEVEN_VOICE_BY_LANG: Dict[str, str] = {
    "en-us": "Rachel",
    "en-gb": "George",
    "en-au": "Charlotte",
    # # block — معالجة صوت/استنساخ
    # # block — معالجة صوت/استنساخ
    "es-es": "Matilda",
    "es-mx": "Valentina",
    "fr-fr": "Charlotte",
    "fr-ca": "Charlotte",
    "de-de": "Serena",
    "it-it": "Matilda",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "pt-br": "Jessica",
    "pt-pt": "Jessica",
    "ja-jp": "Adam",
    "ko-kr": "Adam",
    "zh-cn": "Adam",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ru-ru": "Adam",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "tr-tr": "Adam",
    "hi-in": "Adam",
    "ar": "Adam",
    "ar-sa": "Adam",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ar-eg": "Adam",
    "ar-ae": "Adam",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ar-lb": "Adam",
    "ar-ma": "Adam",
    "ar-iq": "Adam",
# # block — تنفيذ منطق — راجع الأسطر التالية
}

_ELEVEN_LANG_CODE: Dict[str, str] = {
    "ar": "ar",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "en": "en",
    "es": "es",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "fr": "fr",
    "de": "de",
    "it": "it",
    "pt": "pt",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ja": "ja",
    # # block — تنفيذ منطق — راجع الأسطر التالية
    "ko": "ko",
    "zh": "zh",
    "ru": "ru",
    "tr": "tr",
    "hi": "hi",
# # block — تنفيذ منطق — راجع الأسطر التالية
# # block — تنفيذ منطق — راجع الأسطر التالية
}


# # FN _base_lang
# # AR base lang (_base_lang)
# # FN _base_lang
# # AR اللغات واللهجات (_base_lang)
# # KW لغة,language,dialect
# # block — تنفيذ منطق — راجع الأسطر التالية
# # FN _base_lang
# # AR اللغات واللهجات (_base_lang)
# # KW لغة,language,dialect
def _base_lang(code: str) -> str:
    c = _norm_code(code)
    if not c or c == "auto":
        # # return — إرجاع النتيجة
        return "en"
    # # return — إرجاع النتيجة
    # # block — إرجاع نتيجة
    # # block — إرجاع نتيجة
    return c.split("-")[0]


# # FN _lookup_voice
# # AR lookup voice (_lookup_voice)
# # FN _lookup_voice
# # AR الصوت والاستنساخ (_lookup_voice)
# # block — معالجة صوت/استنساخ
# # KW صوت,استنساخ,voice,clone,sample,لغة,language,dialect
# # FN _lookup_voice
# # AR الصوت والاستنساخ (_lookup_voice)
# # KW صوت,استنساخ,voice,clone,sample,لغة,language,dialect
def _lookup_voice(table: Dict[str, str], lang_code: str, base: str, default: str) -> str:
    # # return — إرجاع النتيجة
    return table.get(lang_code) or table.get(base) or default


# # FN resolve_target_language_profile
# # AR حل/استنتاج target language profile (resolve_target_language_profile)
# # FN resolve_target_language_profile
# # block — إرجاع نتيجة
# # block — إرجاع نتيجة
# # AR اللغات واللهجات (resolve_target_language_profile)
# # KW لغة,language,dialect
# # FN resolve_target_language_profile
# # AR اللغات واللهجات (resolve_target_language_profile)
# # KW لغة,language,dialect
def resolve_target_language_profile(
    target_lang: str,
    dialect_override: str = "",
) -> TargetLangProfile:
    """Resolve full target profile from UI lang code (e.g. ar-eg)."""
    lang_code = _norm_code(target_lang)
    # # block — تنفيذ منطق — راجع الأسطر التالية
    # # block — تنفيذ منطق — راجع الأسطر التالية
    base = _base_lang(lang_code)

    ar_meta = _AR.get(lang_code) or _AR.get(base) or {}
    dialect = (dialect_override or ar_meta.get("dialect") or "").strip()
    if base == "ar" and not dialect and lang_code == "ar":
        dialect = "الفصحى"

    # # block — تنفيذ منطق — راجع الأسطر التالية
    display = ar_meta.get("name") or lang_code

    # # block — معالجة صوت/استنساخ
    edge = _lookup_voice(_EDGE_VOICE_BY_LANG, lang_code, base, "en-US-AriaNeural")
    playht = _lookup_voice(_PLAYHT_VOICE_BY_LANG, lang_code, base, "Dexter (English (US)/American)")
    eleven = _lookup_voice(_ELEVEN_VOICE_BY_LANG, lang_code, base, "Rachel")
    eleven_lc = _ELEVEN_LANG_CODE.get(base, base)

    # # block — معالجة صوت/استنساخ
    supports_clone = base in (
        "ar", "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "hi", "tr", "pl", "nl", "cs", "hu"
    # # block — معالجة صوت/استنساخ
    )

    return TargetLangProfile(
        lang_code=lang_code,
        # # block — إرجاع نتيجة
        base_lang=base,
        dialect=dialect,
        display_name=display,
        # # block — معالجة صوت/استنساخ
        edge_voice=edge,
        playht_voice=playht,
        # # block — معالجة صوت/استنساخ
        eleven_voice=eleven,
        eleven_language_code=eleven_lc,
        supports_clone=supports_clone,
    )
