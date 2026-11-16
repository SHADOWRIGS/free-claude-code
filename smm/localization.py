"""Localization — multilingual content adaptation rules.

Generates structured localization configs:
- Translation templates (RU→EN) for key content types
- Terminology glossary (cybersecurity terms bilingual)
- Platform-specific adaptation rules
- Cultural adaptation notes
- Language detection triggers
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

GLOSSARY: list[dict[str, str]] = [
    {"ru": "Кибербезопасность", "en": "Cybersecurity", "context": "general"},
    {"ru": "Этичный хакинг", "en": "Ethical Hacking", "context": "course name"},
    {"ru": "Красная команда", "en": "Red Team", "context": "offensive security"},
    {"ru": "Синяя команда", "en": "Blue Team", "context": "defensive security"},
    {"ru": "Уязвимость", "en": "Vulnerability", "context": "technical"},
    {"ru": "Пентест", "en": "Penetration Testing", "context": "technical"},
    {"ru": "Нейросеть", "en": "Neural Network", "context": "ML/AI"},
    {"ru": "Машинное обучение", "en": "Machine Learning", "context": "ML/AI"},
    {"ru": "Вредоносное ПО", "en": "Malware", "context": "technical"},
    {"ru": "Брандмауэр", "en": "Firewall", "context": "technical"},
    {"ru": "Шифрование", "en": "Encryption", "context": "technical"},
    {"ru": "Инцидент безопасности", "en": "Security Incident", "context": "blue team"},
    {"ru": "Обратная разработка", "en": "Reverse Engineering", "context": "red team"},
    {"ru": "Социальная инженерия", "en": "Social Engineering", "context": "offensive"},
    {"ru": "Глубокое обучение", "en": "Deep Learning", "context": "ML/AI"},
    {"ru": "Компьютерное зрение", "en": "Computer Vision", "context": "ML/AI"},
    {"ru": "Обработка языка", "en": "NLP", "context": "ML/AI"},
    {"ru": "Гаджет", "en": "Gadget", "context": "products"},
    {"ru": "Хакерский набор", "en": "Hacking Kit", "context": "products"},
    {"ru": "Сетевой адаптер", "en": "Network Adapter", "context": "products"},
]

TRANSLATION_TEMPLATES: list[dict[str, str]] = [
    {
        "content_type": "post_caption",
        "name": "Подпись поста",
        "ru_template": "{hook}\n\n{body}\n\n{cta}\n\n{hashtags}",
        "en_template": "{hook}\n\n{body}\n\n{cta}\n\n{hashtags}",
        "notes": "CTA адаптировать под локальный рынок, хештеги — на EN",
    },
    {
        "content_type": "video_title",
        "name": "Заголовок видео",
        "ru_template": "{keyword} — {benefit} | {brand}",
        "en_template": "{keyword} — {benefit} | {brand}",
        "notes": "SEO-ключевые слова выбирать под язык аудитории",
    },
    {
        "content_type": "ad_copy",
        "name": "Рекламный текст",
        "ru_template": "{headline}\n{body}\n{cta_button}",
        "en_template": "{headline}\n{body}\n{cta_button}",
        "notes": "CTA-кнопки: Начать бесплатно → Start Free, Узнать → Learn More",
    },
    {
        "content_type": "email_subject",
        "name": "Тема письма",
        "ru_template": "{urgency} {benefit} — {brand}",
        "en_template": "{urgency} {benefit} — {brand}",
        "notes": "Тестировать A/B для каждого языка отдельно",
    },
    {
        "content_type": "cta",
        "name": "Призыв к действию",
        "ru_template": "{action_verb} {object}",
        "en_template": "{action_verb} {object}",
        "notes": "RU: императив (Начни, Скачай). EN: infinitive (Start, Download)",
    },
]

CTA_TRANSLATIONS: list[dict[str, str]] = [
    {"ru": "Начать бесплатно", "en": "Start Free"},
    {"ru": "Узнать подробнее", "en": "Learn More"},
    {"ru": "Скачать чеклист", "en": "Download Checklist"},
    {"ru": "Смотреть каталог", "en": "Browse Catalog"},
    {"ru": "Записаться на курс", "en": "Enroll Now"},
    {"ru": "Попробовать бесплатно", "en": "Try for Free"},
    {"ru": "Получить доступ", "en": "Get Access"},
    {"ru": "Перейти к товарам", "en": "Shop Now"},
]

PLATFORM_RULES: list[dict[str, str]] = [
    {
        "platform": "Instagram",
        "ru_rule": "Эмодзи после каждого абзаца, хештеги внизу",
        "en_rule": "Emojis per paragraph, hashtags at bottom",
        "adaptation": "EN-аудитория предпочитает меньше эмодзи",
    },
    {
        "platform": "TikTok",
        "ru_rule": "Сленг допустим, субтитры обязательны",
        "en_rule": "Slang OK, captions mandatory",
        "adaptation": "EN: более быстрый темп, trending sounds",
    },
    {
        "platform": "YouTube",
        "ru_rule": "Структурированные главы, таймкоды",
        "en_rule": "Structured chapters, timestamps",
        "adaptation": "EN: описания длиннее, больше ключевых слов",
    },
]

CULTURAL_NOTES: list[dict[str, str]] = [
    {
        "topic": "Обращение",
        "ru": "«Ты» для молодой аудитории, «Вы» для корпоративной",
        "en": "Always 'you' (no formal/informal distinction)",
    },
    {
        "topic": "Юмор",
        "ru": "Мемы из российского IT-сообщества, отсылки к Хабру",
        "en": "Reddit/HackerNews memes, Stack Overflow references",
    },
    {
        "topic": "Числа и валюта",
        "ru": "Цены в рублях (₽), тысячи через пробел: 1 000 ₽",
        "en": "Prices in USD ($), comma separator: $1,000",
    },
    {
        "topic": "Даты",
        "ru": "ДД.ММ.ГГГГ (16.11.2026)",
        "en": "MM/DD/YYYY (11/16/2026) or Month DD, YYYY",
    },
    {
        "topic": "Сертификации",
        "ru": "Упоминать OSCP, CEH, CompTIA — международные стандарты",
        "en": "Same certs, but emphasize industry recognition",
    },
]


@dataclass(frozen=True, slots=True)
class GlossaryEntry:
    ru: str
    en: str
    context: str


@dataclass(frozen=True, slots=True)
class TranslationTemplate:
    content_type: str
    name: str
    ru_template: str
    en_template: str
    notes: str


@dataclass(frozen=True, slots=True)
class CTATranslation:
    ru: str
    en: str


@dataclass(frozen=True, slots=True)
class PlatformRule:
    platform: str
    ru_rule: str
    en_rule: str
    adaptation: str


@dataclass(frozen=True, slots=True)
class CulturalNote:
    topic: str
    ru: str
    en: str


@dataclass(frozen=True, slots=True)
class LocalizationPack:
    glossary: tuple[GlossaryEntry, ...]
    templates: tuple[TranslationTemplate, ...]
    cta_translations: tuple[CTATranslation, ...]
    platform_rules: tuple[PlatformRule, ...]
    cultural_notes: tuple[CulturalNote, ...]
    primary_language: str
    secondary_language: str


def generate_localization() -> LocalizationPack:
    return LocalizationPack(
        glossary=tuple(
            GlossaryEntry(ru=g["ru"], en=g["en"], context=g["context"])
            for g in GLOSSARY
        ),
        templates=tuple(
            TranslationTemplate(
                content_type=t["content_type"],
                name=t["name"],
                ru_template=t["ru_template"],
                en_template=t["en_template"],
                notes=t["notes"],
            )
            for t in TRANSLATION_TEMPLATES
        ),
        cta_translations=tuple(
            CTATranslation(ru=c["ru"], en=c["en"]) for c in CTA_TRANSLATIONS
        ),
        platform_rules=tuple(
            PlatformRule(
                platform=r["platform"],
                ru_rule=r["ru_rule"],
                en_rule=r["en_rule"],
                adaptation=r["adaptation"],
            )
            for r in PLATFORM_RULES
        ),
        cultural_notes=tuple(
            CulturalNote(topic=n["topic"], ru=n["ru"], en=n["en"])
            for n in CULTURAL_NOTES
        ),
        primary_language="ru",
        secondary_language="en",
    )


def export_localization_json(lp: LocalizationPack, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "primary_language": lp.primary_language,
        "secondary_language": lp.secondary_language,
        "glossary": [
            {"ru": g.ru, "en": g.en, "context": g.context} for g in lp.glossary
        ],
        "templates": [
            {
                "content_type": t.content_type,
                "name": t.name,
                "ru_template": t.ru_template,
                "en_template": t.en_template,
                "notes": t.notes,
            }
            for t in lp.templates
        ],
        "cta_translations": [{"ru": c.ru, "en": c.en} for c in lp.cta_translations],
        "platform_rules": [
            {
                "platform": r.platform,
                "ru_rule": r.ru_rule,
                "en_rule": r.en_rule,
                "adaptation": r.adaptation,
            }
            for r in lp.platform_rules
        ],
        "cultural_notes": [
            {"topic": n.topic, "ru": n.ru, "en": n.en} for n in lp.cultural_notes
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_localization_txt(lp: LocalizationPack, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        f"ЛОКАЛИЗАЦИЯ — {lp.primary_language.upper()} ↔ {lp.secondary_language.upper()}",
        "=" * 60,
        "\n📖 ГЛОССАРИЙ ТЕРМИНОВ",
        "━" * 50,
    ]
    lines.extend(f"  {g.ru} → {g.en} [{g.context}]" for g in lp.glossary)

    lines.append(f"\n{'━' * 50}")
    lines.append("📝 ШАБЛОНЫ ПЕРЕВОДА")
    lines.append("━" * 50)
    for t in lp.templates:
        lines.append(f"\n  [{t.content_type}] {t.name}")
        lines.append(f"    Примечание: {t.notes}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🔘 CTA-ПЕРЕВОДЫ")
    lines.append("━" * 50)
    lines.extend(f"  {c.ru} → {c.en}" for c in lp.cta_translations)

    lines.append(f"\n{'━' * 50}")
    lines.append("📱 ПРАВИЛА ПО ПЛАТФОРМАМ")
    lines.append("━" * 50)
    for r in lp.platform_rules:
        lines.append(f"\n  [{r.platform}]")
        lines.append(f"    RU: {r.ru_rule}")
        lines.append(f"    EN: {r.en_rule}")
        lines.append(f"    Адаптация: {r.adaptation}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🌍 КУЛЬТУРНЫЕ ЗАМЕТКИ")
    lines.append("━" * 50)
    for n in lp.cultural_notes:
        lines.append(f"\n  [{n.topic}]")
        lines.append(f"    RU: {n.ru}")
        lines.append(f"    EN: {n.en}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def localization_summary(lp: LocalizationPack) -> str:
    return (
        f"Локализация ({lp.primary_language}→{lp.secondary_language}): "
        f"{len(lp.glossary)} терминов, "
        f"{len(lp.templates)} шаблонов, "
        f"{len(lp.cta_translations)} CTA-переводов, "
        f"{len(lp.platform_rules)} правил платформ, "
        f"{len(lp.cultural_notes)} культурных заметок"
    )
