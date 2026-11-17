"""Social listening — brand mention monitoring and trend tracking.

Generates structured configs for:
- Keyword tracking lists per pillar
- Sentiment analysis rules
- Alert triggers
- Competitor mention tracking
- Trend detection parameters
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

KEYWORD_TRACKS: list[dict[str, str | list[str]]] = [
    {
        "pillar": "Cyber Security & Ethical Hacking",
        "brand_keywords": ["ShadowRigs", "shadowrigs", "shadow rigs"],
        "topic_keywords": [
            "ethical hacking",
            "pentesting",
            "bug bounty",
            "CTF",
            "cybersecurity course",
        ],
        "negative_keywords": ["scam", "fraud", "leak"],
    },
    {
        "pillar": "Blue Team / Defensive Security",
        "brand_keywords": ["ShadowRigs", "shadowrigs"],
        "topic_keywords": [
            "SOC analyst",
            "SIEM",
            "incident response",
            "threat hunting",
            "blue team training",
        ],
        "negative_keywords": ["breach", "data loss", "vulnerability"],
    },
    {
        "pillar": "Red Team / Offensive Security",
        "brand_keywords": ["ShadowRigs", "shadowrigs"],
        "topic_keywords": [
            "red team",
            "adversary simulation",
            "exploit dev",
            "social engineering",
            "offensive security course",
        ],
        "negative_keywords": ["illegal", "malware", "ransomware"],
    },
    {
        "pillar": "Machine Learning & AI",
        "brand_keywords": ["ShadowRigs", "shadowrigs"],
        "topic_keywords": [
            "machine learning",
            "AI course",
            "deep learning",
            "neural network",
            "ML engineering",
        ],
        "negative_keywords": ["AI scam", "fake AI"],
    },
    {
        "pillar": "AliExpress Gadgets",
        "brand_keywords": ["ShadowRigs", "shadowrigs"],
        "topic_keywords": [
            "hacker gadgets",
            "WiFi Pineapple",
            "Flipper Zero",
            "USB Rubber Ducky",
            "network tools",
        ],
        "negative_keywords": ["counterfeit", "fake", "broken"],
    },
]

SENTIMENT_RULES: list[dict[str, str]] = [
    {
        "sentiment": "positive",
        "signals": "Благодарности, рекомендации, хвалебные отзывы, репосты",
        "action": "Репост, благодарность, добавить в social proof",
        "priority": "medium",
    },
    {
        "sentiment": "negative",
        "signals": "Жалобы, критика, возвраты, негативные отзывы",
        "action": "Немедленный ответ (< 1ч), эскалация, кризисный протокол",
        "priority": "critical",
    },
    {
        "sentiment": "neutral",
        "signals": "Вопросы, упоминания без оценки, сравнения",
        "action": "Информативный ответ, вовлечение в диалог",
        "priority": "low",
    },
    {
        "sentiment": "competitive",
        "signals": "Сравнение с конкурентами, выбор между курсами",
        "action": "Подготовить сравнение, предложить пробный доступ",
        "priority": "high",
    },
]

ALERT_TRIGGERS: list[dict[str, str | int]] = [
    {
        "trigger": "Всплеск упоминаний",
        "threshold": 50,
        "unit": "упоминаний/час",
        "action": "Проверить причину, подготовить ответ",
        "severity": "high",
    },
    {
        "trigger": "Негативный тренд",
        "threshold": 20,
        "unit": "% негатива за 24ч",
        "action": "Активировать кризисный протокол",
        "severity": "critical",
    },
    {
        "trigger": "Упоминание конкурентом",
        "threshold": 1,
        "unit": "упоминание",
        "action": "Анализ контекста, подготовка ответа",
        "severity": "medium",
    },
    {
        "trigger": "Вирусный контент",
        "threshold": 500,
        "unit": "шеров/час",
        "action": "Усилить продвижение, добавить CTA",
        "severity": "high",
    },
    {
        "trigger": "Инфлюенсер упомянул",
        "threshold": 10000,
        "unit": "подписчиков у автора",
        "action": "Связаться для коллаборации",
        "severity": "high",
    },
]

COMPETITOR_TRACKS: list[dict[str, str | list[str]]] = [
    {
        "competitor": "HackerU",
        "keywords": ["HackerU", "hackeru.com", "хакер-ю"],
        "focus": "Ценообразование, отзывы студентов",
    },
    {
        "competitor": "Offensive Security (OffSec)",
        "keywords": ["OSCP", "OffSec", "offensive security"],
        "focus": "Сертификации, сложность, стоимость",
    },
    {
        "competitor": "TryHackMe",
        "keywords": ["TryHackMe", "tryhackme"],
        "focus": "Геймификация, бесплатный контент, подписная модель",
    },
    {
        "competitor": "HackTheBox",
        "keywords": ["HackTheBox", "HTB", "hack the box"],
        "focus": "CTF-площадка, комьюнити, про-подписка",
    },
]

TREND_PARAMS: dict[str, str | int] = {
    "scan_frequency": "каждые 4 часа",
    "lookback_days": 7,
    "min_mentions_for_trend": 10,
    "trend_growth_threshold": "200% за 24ч",
    "platforms": "Instagram, TikTok, YouTube, Twitter/X, Telegram, Reddit",
    "language_filter": "ru, en",
    "geo_filter": "RU, UA, KZ, BY, worldwide",
}


@dataclass(frozen=True, slots=True)
class KeywordTrack:
    pillar: str
    brand_keywords: tuple[str, ...]
    topic_keywords: tuple[str, ...]
    negative_keywords: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SentimentRule:
    sentiment: str
    signals: str
    action: str
    priority: str


@dataclass(frozen=True, slots=True)
class AlertTrigger:
    trigger: str
    threshold: int
    unit: str
    action: str
    severity: str


@dataclass(frozen=True, slots=True)
class CompetitorTrack:
    competitor: str
    keywords: tuple[str, ...]
    focus: str


@dataclass(frozen=True, slots=True)
class SocialListening:
    keyword_tracks: tuple[KeywordTrack, ...]
    sentiment_rules: tuple[SentimentRule, ...]
    alert_triggers: tuple[AlertTrigger, ...]
    competitor_tracks: tuple[CompetitorTrack, ...]
    trend_params: dict[str, str | int]


def generate_social_listening() -> SocialListening:
    return SocialListening(
        keyword_tracks=tuple(
            KeywordTrack(
                pillar=kt["pillar"],
                brand_keywords=tuple(kt["brand_keywords"]),
                topic_keywords=tuple(kt["topic_keywords"]),
                negative_keywords=tuple(kt["negative_keywords"]),
            )
            for kt in KEYWORD_TRACKS
        ),
        sentiment_rules=tuple(
            SentimentRule(
                sentiment=sr["sentiment"],
                signals=sr["signals"],
                action=sr["action"],
                priority=sr["priority"],
            )
            for sr in SENTIMENT_RULES
        ),
        alert_triggers=tuple(
            AlertTrigger(
                trigger=at["trigger"],
                threshold=int(at["threshold"]),
                unit=at["unit"],
                action=at["action"],
                severity=at["severity"],
            )
            for at in ALERT_TRIGGERS
        ),
        competitor_tracks=tuple(
            CompetitorTrack(
                competitor=ct["competitor"],
                keywords=tuple(ct["keywords"]),
                focus=ct["focus"],
            )
            for ct in COMPETITOR_TRACKS
        ),
        trend_params=dict(TREND_PARAMS),
    )


def export_listening_json(sl: SocialListening, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "keyword_tracks": [
            {
                "pillar": kt.pillar,
                "brand_keywords": list(kt.brand_keywords),
                "topic_keywords": list(kt.topic_keywords),
                "negative_keywords": list(kt.negative_keywords),
            }
            for kt in sl.keyword_tracks
        ],
        "sentiment_rules": [
            {
                "sentiment": sr.sentiment,
                "signals": sr.signals,
                "action": sr.action,
                "priority": sr.priority,
            }
            for sr in sl.sentiment_rules
        ],
        "alert_triggers": [
            {
                "trigger": at.trigger,
                "threshold": at.threshold,
                "unit": at.unit,
                "action": at.action,
                "severity": at.severity,
            }
            for at in sl.alert_triggers
        ],
        "competitor_tracks": [
            {
                "competitor": ct.competitor,
                "keywords": list(ct.keywords),
                "focus": ct.focus,
            }
            for ct in sl.competitor_tracks
        ],
        "trend_params": sl.trend_params,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_listening_txt(sl: SocialListening, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "СОЦИАЛЬНЫЙ МОНИТОРИНГ (SOCIAL LISTENING)",
        "=" * 60,
        "\n🔑 ОТСЛЕЖИВАЕМЫЕ КЛЮЧЕВЫЕ СЛОВА",
        "━" * 50,
    ]
    for kt in sl.keyword_tracks:
        lines.append(f"\n  [{kt.pillar}]")
        lines.append(f"    Бренд: {', '.join(kt.brand_keywords)}")
        lines.append(f"    Темы: {', '.join(kt.topic_keywords)}")
        lines.append(f"    Минус-слова: {', '.join(kt.negative_keywords)}")

    lines.append(f"\n{'━' * 50}")
    lines.append("😊 ПРАВИЛА ТОНАЛЬНОСТИ")
    lines.append("━" * 50)
    for sr in sl.sentiment_rules:
        lines.append(f"\n  [{sr.sentiment.upper()}] приоритет: {sr.priority}")
        lines.append(f"    Сигналы: {sr.signals}")
        lines.append(f"    Действие: {sr.action}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🚨 ТРИГГЕРЫ ОПОВЕЩЕНИЙ")
    lines.append("━" * 50)
    for at in sl.alert_triggers:
        lines.append(
            f"\n  [{at.trigger}] порог: {at.threshold} {at.unit} ({at.severity})"
        )
        lines.append(f"    Действие: {at.action}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🏢 МОНИТОРИНГ КОНКУРЕНТОВ")
    lines.append("━" * 50)
    for ct in sl.competitor_tracks:
        lines.append(f"\n  [{ct.competitor}]")
        lines.append(f"    Ключевые слова: {', '.join(ct.keywords)}")
        lines.append(f"    Фокус: {ct.focus}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📈 ПАРАМЕТРЫ ТРЕНДОВ")
    lines.append("━" * 50)
    for key, val in sl.trend_params.items():
        lines.append(f"  {key}: {val}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def listening_summary(sl: SocialListening) -> str:
    total_kw = sum(
        len(kt.brand_keywords) + len(kt.topic_keywords) for kt in sl.keyword_tracks
    )
    return (
        f"Social Listening: "
        f"{len(sl.keyword_tracks)} треков ({total_kw} ключевых слов), "
        f"{len(sl.sentiment_rules)} правил тональности, "
        f"{len(sl.alert_triggers)} триггеров, "
        f"{len(sl.competitor_tracks)} конкурентов"
    )
