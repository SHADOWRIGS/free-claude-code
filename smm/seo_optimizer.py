"""SEO optimizer — keywords, meta descriptions, YouTube tags.

Generates SEO assets for:
- YouTube video titles and descriptions (per pillar)
- Meta descriptions for landing pages
- Keyword clusters per pillar
- Alt-text templates for images
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

KEYWORD_CLUSTERS: dict[str, list[str]] = {
    "Cyber Security & Ethical Hacking": [
        "кибербезопасность курс",
        "этичный хакинг обучение",
        "bug bounty с нуля",
        "пентест курс",
        "cybersecurity course",
        "ethical hacking tutorial",
        "OWASP top 10",
        "Burp Suite обучение",
        "Kali Linux уроки",
        "информационная безопасность",
    ],
    "Blue Team / Defensive Security": [
        "blue team курс",
        "SOC аналитик обучение",
        "SIEM настройка",
        "incident response",
        "защита инфраструктуры",
        "defensive security course",
        "threat hunting",
        "log analysis",
        "security monitoring",
        "SOAR автоматизация",
    ],
    "Red Team / Offensive Security": [
        "red team курс",
        "offensive security обучение",
        "OSCP подготовка",
        "Active Directory пентест",
        "privilege escalation",
        "lateral movement",
        "red team operations",
        "evasion techniques",
        "post-exploitation",
        "pivoting tutorial",
    ],
    "Machine Learning & AI": [
        "машинное обучение курс",
        "ML с нуля",
        "Python для data science",
        "нейросети обучение",
        "deep learning tutorial",
        "TensorFlow PyTorch",
        "AI курс на русском",
        "computer vision",
        "NLP обработка текста",
        "machine learning portfolio",
    ],
    "AliExpress — Гаджеты": [
        "гаджеты для хакеров",
        "WiFi адаптер пентест",
        "SDR приёмник",
        "USB Rubber Ducky",
        "hacker gadgets aliexpress",
        "сетевое оборудование",
        "лаборатория кибербез",
        "Flipper Zero аналог",
        "мини-сервер для лаб",
        "гаджеты aliexpress обзор",
    ],
}

YT_TITLE_TEMPLATES: list[str] = [
    "{keyword} — Полный гайд для начинающих [{year}]",
    "{keyword}: от нуля до профи за 30 дней",
    "Топ-5 ошибок в {topic} (и как их избежать)",
    "{keyword} | Бесплатный мини-курс",
    "Как заработать на {topic} в {year}",
]

META_DESCRIPTIONS: dict[str, str] = {
    "Cyber Security & Ethical Hacking": (
        "Онлайн-курс по кибербезопасности и этичному хакингу. "
        "Научись находить уязвимости, зарабатывать на Bug Bounty. "
        "Практика на реальных лабах. Менторская поддержка."
    ),
    "Blue Team / Defensive Security": (
        "Курс по защитной кибербезопасности: SOC, SIEM, Incident Response. "
        "Построй карьеру в Blue Team. Реальные кейсы инцидентов."
    ),
    "Red Team / Offensive Security": (
        "Курс по наступательной безопасности: пентест, AD, OSCP. "
        "Атакуй как профи. Лабы Active Directory и реальные сценарии."
    ),
    "Machine Learning & AI": (
        "Курс Machine Learning и AI на русском. Первая ML-модель за 45 минут. "
        "8 проектов для портфолио. Помощь с трудоустройством."
    ),
    "AliExpress — Гаджеты": (
        "Лучшие гаджеты для хакеров с AliExpress: WiFi-адаптеры, SDR, "
        "Rubber Ducky, мини-серверы. Честные обзоры и проверенные продавцы."
    ),
}

ALT_TEXT_TEMPLATES: list[str] = [
    "Инфографика: {topic} — ключевые шаги для начинающих",
    "Скриншот: демонстрация {tool} в действии",
    "Схема: архитектура {concept} от простого к сложному",
    "Фото: {gadget} — внешний вид и комплектация",
    "Диаграмма: воронка {process} с метриками конверсии",
]


@dataclass(frozen=True, slots=True)
class KeywordCluster:
    pillar: str
    keywords: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class YTTitleTemplate:
    template: str


@dataclass(frozen=True, slots=True)
class MetaDescription:
    pillar: str
    description: str


@dataclass(frozen=True, slots=True)
class SEOPack:
    keyword_clusters: tuple[KeywordCluster, ...]
    yt_title_templates: tuple[YTTitleTemplate, ...]
    meta_descriptions: tuple[MetaDescription, ...]
    alt_text_templates: tuple[str, ...]


def generate_seo_pack() -> SEOPack:
    return SEOPack(
        keyword_clusters=tuple(
            KeywordCluster(pillar=p, keywords=tuple(kws))
            for p, kws in KEYWORD_CLUSTERS.items()
        ),
        yt_title_templates=tuple(
            YTTitleTemplate(template=t) for t in YT_TITLE_TEMPLATES
        ),
        meta_descriptions=tuple(
            MetaDescription(pillar=p, description=d)
            for p, d in META_DESCRIPTIONS.items()
        ),
        alt_text_templates=tuple(ALT_TEXT_TEMPLATES),
    )


def export_seo_json(pack: SEOPack, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "keyword_clusters": [
            {"pillar": c.pillar, "keywords": list(c.keywords)}
            for c in pack.keyword_clusters
        ],
        "yt_title_templates": [t.template for t in pack.yt_title_templates],
        "meta_descriptions": [
            {"pillar": m.pillar, "description": m.description}
            for m in pack.meta_descriptions
        ],
        "alt_text_templates": list(pack.alt_text_templates),
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_seo_txt(pack: SEOPack, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "SEO-ОПТИМИЗАЦИЯ — КЛЮЧЕВЫЕ СЛОВА И МЕТА-ДАННЫЕ",
        "=" * 60,
        "\n🔑 КЛАСТЕРЫ КЛЮЧЕВЫХ СЛОВ",
        "━" * 50,
    ]
    for c in pack.keyword_clusters:
        lines.append(f"\n  [{c.pillar}]")
        lines.extend(f"    • {kw}" for kw in c.keywords)

    lines.append(f"\n{'━' * 50}")
    lines.append("🎬 ШАБЛОНЫ ЗАГОЛОВКОВ YOUTUBE")
    lines.append("━" * 50)
    lines.extend(f"  • {t.template}" for t in pack.yt_title_templates)

    lines.append(f"\n{'━' * 50}")
    lines.append("📝 МЕТА-ОПИСАНИЯ ЛЕНДИНГОВ")
    lines.append("━" * 50)
    for m in pack.meta_descriptions:
        lines.append(f"\n  [{m.pillar}]")
        lines.append(f"  {m.description}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🖼 ALT-ТЕКСТЫ ДЛЯ ИЗОБРАЖЕНИЙ")
    lines.append("━" * 50)
    lines.extend(f"  • {alt}" for alt in pack.alt_text_templates)

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def seo_summary(pack: SEOPack) -> str:
    total_kws = sum(len(c.keywords) for c in pack.keyword_clusters)
    return (
        f"SEO-пак: {len(pack.keyword_clusters)} кластеров "
        f"({total_kws} ключевых слов), "
        f"{len(pack.yt_title_templates)} шаблонов YT, "
        f"{len(pack.meta_descriptions)} мета-описаний, "
        f"{len(pack.alt_text_templates)} alt-текстов"
    )
