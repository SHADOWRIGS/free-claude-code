"""Compliance checker — platform rules and content policy validation.

Generates structured compliance configs:
- Platform content policies (IG, TT, YT)
- Prohibited content categories
- Disclosure requirements (ads, affiliates)
- Copyright guidelines
- Age restriction rules
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

PLATFORM_POLICIES: list[dict[str, str | list[str]]] = [
    {
        "platform": "Instagram",
        "max_hashtags": "30",
        "caption_limit": "2200 символов",
        "link_in_bio": "Ссылки только в био и сторис (10K+)",
        "forbidden": [
            "Оружие и наркотики",
            "Нагота и сексуальный контент",
            "Спам и накрутка",
            "Нарушение авторских прав",
        ],
        "disclosure": "Платное партнёрство через тег Paid Partnership",
    },
    {
        "platform": "TikTok",
        "max_hashtags": "5-8 рекомендуется",
        "caption_limit": "2200 символов",
        "link_in_bio": "Ссылка в био (1000+ подписчиков)",
        "forbidden": [
            "Опасные действия и челленджи",
            "Дезинформация",
            "Буллинг и харассмент",
            "Эксплуатация несовершеннолетних",
        ],
        "disclosure": "Переключатель Branded Content в настройках видео",
    },
    {
        "platform": "YouTube",
        "max_hashtags": "15 (больше = удаление всех)",
        "caption_limit": "5000 символов описания",
        "link_in_bio": "Ссылки в описании и подсказках",
        "forbidden": [
            "Вредоносный контент и малварь",
            "Спам и обманные практики",
            "Контент для взрослых без маркировки",
            "Нарушения DMCA",
        ],
        "disclosure": "Чекбокс Contains paid promotion",
    },
]

PROHIBITED_CATEGORIES: list[dict[str, str]] = [
    {
        "category": "Вредоносное ПО",
        "description": "Распространение малвари, эксплойтов для атак",
        "risk": "Бан аккаунта, юридические последствия",
        "alternative": "Показывать концепции без рабочего кода атаки",
    },
    {
        "category": "Взлом без разрешения",
        "description": "Демонстрация реальных несанкционированных атак",
        "risk": "Уголовная ответственность, бан платформы",
        "alternative": "Использовать CTF-площадки и лабораторные среды",
    },
    {
        "category": "Персональные данные",
        "description": "Утечки, дампы баз данных, PII",
        "risk": "Нарушение GDPR/ФЗ-152, бан",
        "alternative": "Анонимизированные примеры, тестовые данные",
    },
    {
        "category": "Финансовое мошенничество",
        "description": "Фишинг-шаблоны, скам-схемы",
        "risk": "Бан + юридическая ответственность",
        "alternative": "Показывать как распознать мошенничество",
    },
    {
        "category": "Дискриминация",
        "description": "Контент, унижающий по расе, полу, религии",
        "risk": "Бан аккаунта, репутационный ущерб",
        "alternative": "Инклюзивная подача, нейтральный тон",
    },
]

DISCLOSURE_RULES: list[dict[str, str]] = [
    {
        "type": "Партнёрская ссылка",
        "requirement": "Указать что ссылка партнёрская/реферальная",
        "placement": "В начале подписи или описания",
        "example": "Партнёрская ссылка* / Содержит реферальную ссылку",
    },
    {
        "type": "Платная реклама",
        "requirement": "Маркировка через инструменты платформы",
        "placement": "Тег Paid Partnership / Branded Content",
        "example": "Оплаченное партнёрство с @brand",
    },
    {
        "type": "Бесплатный продукт",
        "requirement": "Указать что продукт получен бесплатно",
        "placement": "В подписи или описании видео",
        "example": "Продукт предоставлен для обзора",
    },
    {
        "type": "Собственный продукт",
        "requirement": "Не обязательно, но рекомендуется честность",
        "placement": "В описании / био",
        "example": "Мой курс / Мой продукт",
    },
]

COPYRIGHT_RULES: list[dict[str, str]] = [
    {
        "type": "Музыка",
        "rule": "Только royalty-free или лицензированная библиотека платформы",
        "source": "Epidemic Sound, Artlist, библиотека YouTube/IG",
    },
    {
        "type": "Изображения",
        "rule": "Стоковые фото с CC0/коммерческой лицензией, или свои",
        "source": "Unsplash, Pexels, Canva, собственные скриншоты",
    },
    {
        "type": "Скриншоты ПО",
        "rule": "Fair use для обзоров, указывать источник",
        "source": "Личные скриншоты с разрешения/fair use",
    },
    {
        "type": "Цитаты и данные",
        "rule": "Указывать первоисточник, не выдавать за своё",
        "source": "Ссылка на оригинал в подписи/описании",
    },
    {
        "type": "Логотипы брендов",
        "rule": "Только для упоминания/обзора, не для мисрепрезентации",
        "source": "Официальные пресс-киты или скриншоты",
    },
]

AGE_RESTRICTIONS: list[dict[str, str]] = [
    {
        "content_type": "Инструменты пентеста",
        "restriction": "Маркировка 16+ рекомендуется",
        "reason": "Инструменты двойного назначения",
    },
    {
        "content_type": "Разбор уязвимостей",
        "restriction": "Образовательный контекст обязателен",
        "reason": "Без контекста выглядит как инструкция к атаке",
    },
    {
        "content_type": "Гаджеты (AliExpress)",
        "restriction": "Нет ограничений",
        "reason": "Обычная электроника и аксессуары",
    },
]


@dataclass(frozen=True, slots=True)
class PlatformPolicy:
    platform: str
    max_hashtags: str
    caption_limit: str
    link_in_bio: str
    forbidden: tuple[str, ...]
    disclosure: str


@dataclass(frozen=True, slots=True)
class ProhibitedCategory:
    category: str
    description: str
    risk: str
    alternative: str


@dataclass(frozen=True, slots=True)
class DisclosureRule:
    type: str
    requirement: str
    placement: str
    example: str


@dataclass(frozen=True, slots=True)
class CopyrightRule:
    type: str
    rule: str
    source: str


@dataclass(frozen=True, slots=True)
class AgeRestriction:
    content_type: str
    restriction: str
    reason: str


@dataclass(frozen=True, slots=True)
class ComplianceChecker:
    platform_policies: tuple[PlatformPolicy, ...]
    prohibited: tuple[ProhibitedCategory, ...]
    disclosures: tuple[DisclosureRule, ...]
    copyright_rules: tuple[CopyrightRule, ...]
    age_restrictions: tuple[AgeRestriction, ...]


def generate_compliance_checker() -> ComplianceChecker:
    return ComplianceChecker(
        platform_policies=tuple(
            PlatformPolicy(
                platform=p["platform"],
                max_hashtags=p["max_hashtags"],
                caption_limit=p["caption_limit"],
                link_in_bio=p["link_in_bio"],
                forbidden=tuple(p["forbidden"]),
                disclosure=p["disclosure"],
            )
            for p in PLATFORM_POLICIES
        ),
        prohibited=tuple(
            ProhibitedCategory(
                category=c["category"],
                description=c["description"],
                risk=c["risk"],
                alternative=c["alternative"],
            )
            for c in PROHIBITED_CATEGORIES
        ),
        disclosures=tuple(
            DisclosureRule(
                type=d["type"],
                requirement=d["requirement"],
                placement=d["placement"],
                example=d["example"],
            )
            for d in DISCLOSURE_RULES
        ),
        copyright_rules=tuple(
            CopyrightRule(
                type=cr["type"],
                rule=cr["rule"],
                source=cr["source"],
            )
            for cr in COPYRIGHT_RULES
        ),
        age_restrictions=tuple(
            AgeRestriction(
                content_type=ar["content_type"],
                restriction=ar["restriction"],
                reason=ar["reason"],
            )
            for ar in AGE_RESTRICTIONS
        ),
    )


def export_compliance_json(cc: ComplianceChecker, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "platform_policies": [
            {
                "platform": p.platform,
                "max_hashtags": p.max_hashtags,
                "caption_limit": p.caption_limit,
                "link_in_bio": p.link_in_bio,
                "forbidden": list(p.forbidden),
                "disclosure": p.disclosure,
            }
            for p in cc.platform_policies
        ],
        "prohibited": [
            {
                "category": c.category,
                "description": c.description,
                "risk": c.risk,
                "alternative": c.alternative,
            }
            for c in cc.prohibited
        ],
        "disclosures": [
            {
                "type": d.type,
                "requirement": d.requirement,
                "placement": d.placement,
                "example": d.example,
            }
            for d in cc.disclosures
        ],
        "copyright_rules": [
            {"type": cr.type, "rule": cr.rule, "source": cr.source}
            for cr in cc.copyright_rules
        ],
        "age_restrictions": [
            {
                "content_type": ar.content_type,
                "restriction": ar.restriction,
                "reason": ar.reason,
            }
            for ar in cc.age_restrictions
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_compliance_txt(cc: ComplianceChecker, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "КОМПЛАЕНС — ПРОВЕРКА СООТВЕТСТВИЯ ПРАВИЛАМ ПЛАТФОРМ",
        "=" * 60,
        "\n📋 ПОЛИТИКИ ПЛАТФОРМ",
        "━" * 50,
    ]
    for p in cc.platform_policies:
        lines.append(f"\n  [{p.platform}]")
        lines.append(f"    Хештеги: макс. {p.max_hashtags}")
        lines.append(f"    Подпись: {p.caption_limit}")
        lines.append(f"    Ссылки: {p.link_in_bio}")
        lines.append(f"    Раскрытие: {p.disclosure}")
        lines.append(f"    Запрещено: {', '.join(p.forbidden)}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🚫 ЗАПРЕЩЁННЫЙ КОНТЕНТ")
    lines.append("━" * 50)
    for c in cc.prohibited:
        lines.append(f"\n  [{c.category}]")
        lines.append(f"    {c.description}")
        lines.append(f"    Риск: {c.risk}")
        lines.append(f"    Альтернатива: {c.alternative}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📢 ПРАВИЛА РАСКРЫТИЯ")
    lines.append("━" * 50)
    for d in cc.disclosures:
        lines.append(f"\n  [{d.type}]")
        lines.append(f"    {d.requirement}")
        lines.append(f"    Размещение: {d.placement}")
        lines.append(f"    Пример: {d.example}")

    lines.append(f"\n{'━' * 50}")
    lines.append("(C) АВТОРСКИЕ ПРАВА")
    lines.append("━" * 50)
    for cr in cc.copyright_rules:
        lines.append(f"\n  [{cr.type}]")
        lines.append(f"    {cr.rule}")
        lines.append(f"    Источник: {cr.source}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🔞 ВОЗРАСТНЫЕ ОГРАНИЧЕНИЯ")
    lines.append("━" * 50)
    for ar in cc.age_restrictions:
        lines.append(f"\n  [{ar.content_type}]")
        lines.append(f"    {ar.restriction}")
        lines.append(f"    Причина: {ar.reason}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def compliance_summary(cc: ComplianceChecker) -> str:
    return (
        f"Комплаенс: "
        f"{len(cc.platform_policies)} политик платформ, "
        f"{len(cc.prohibited)} запретов, "
        f"{len(cc.disclosures)} правил раскрытия, "
        f"{len(cc.copyright_rules)} правил копирайта, "
        f"{len(cc.age_restrictions)} возрастных ограничений"
    )
