"""Ad creative templates — paid promotion across Meta, TikTok, YouTube.

Generates structured ad sets:
- Ad copy per pillar and platform
- Audience targeting configs
- Budget allocation recommendations
- A/B test variants for ads
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

AD_PLATFORMS: tuple[str, ...] = ("meta", "tiktok", "youtube")

AD_OBJECTIVES: dict[str, str] = {
    "awareness": "Узнаваемость бренда",
    "traffic": "Трафик на лендинг",
    "leads": "Генерация лидов",
    "conversions": "Конверсии (покупки)",
    "engagement": "Вовлечённость",
}

AD_COPIES: list[dict[str, str]] = [
    {
        "pillar": "Cyber Security & Ethical Hacking",
        "headline": "Стань этичным хакером за 3 месяца",
        "body": (
            "Научись находить уязвимости и зарабатывать на Bug Bounty.\n"
            "Практика на реальных лабах + менторская поддержка.\n"
            "Первый урок — бесплатно!"
        ),
        "cta": "Начать бесплатно",
        "platform": "meta",
    },
    {
        "pillar": "Cyber Security & Ethical Hacking",
        "headline": "Хочешь зарабатывать на Bug Bounty?",
        "body": (
            "От нуля до первого бага за 30 дней.\n"
            "Kali Linux, Burp Suite, реальные цели.\n"
            "Скачай чеклист бесплатно 👇"
        ),
        "cta": "Скачать чеклист",
        "platform": "tiktok",
    },
    {
        "pillar": "Blue Team / Defensive Security",
        "headline": "Построй SOC с нуля — курс Blue Team",
        "body": (
            "SIEM, SOAR, Incident Response.\n"
            "Реальные кейсы инцидентов.\n"
            "Старт карьеры в кибербезопасности."
        ),
        "cta": "Узнать подробнее",
        "platform": "meta",
    },
    {
        "pillar": "Red Team / Offensive Security",
        "headline": "Атакуй как профи — Red Team курс",
        "body": (
            "Active Directory, pivoting, evasion.\n"
            "Подготовка к OSCP.\n"
            "Лабы и реальные сценарии."
        ),
        "cta": "Начать обучение",
        "platform": "youtube",
    },
    {
        "pillar": "Machine Learning & AI",
        "headline": "Первая ML-модель за 45 минут",
        "body": (
            "Python + ML библиотеки.\n"
            "8 проектов для портфолио.\n"
            "Помощь с трудоустройством."
        ),
        "cta": "Попробовать бесплатно",
        "platform": "meta",
    },
    {
        "pillar": "Machine Learning & AI",
        "headline": "AI-революция: войди в тренд",
        "body": (
            "Нейросети, deep learning, NLP.\nПортфолио за месяц.\nМенторы из индустрии."
        ),
        "cta": "Начать бесплатно",
        "platform": "tiktok",
    },
    {
        "pillar": "AliExpress — Гаджеты",
        "headline": "Топ гаджетов для хакеров 2024",
        "body": (
            "WiFi-адаптеры, SDR, Rubber Ducky.\n"
            "Проверенные продавцы.\n"
            "Скидки для подписчиков."
        ),
        "cta": "Смотреть каталог",
        "platform": "youtube",
    },
    {
        "pillar": "AliExpress — Гаджеты",
        "headline": "Гаджеты, о которых мечтает каждый хакер",
        "body": (
            "Мини-серверы, Flipper-аналоги, пентест-наборы.\n"
            "Всё с AliExpress по лучшим ценам.\n"
            "Ссылка в профиле 👆"
        ),
        "cta": "Перейти к товарам",
        "platform": "tiktok",
    },
]

AUDIENCE_TARGETS: list[dict[str, str | list[str]]] = [
    {
        "name": "IT-новички (18-25)",
        "age_range": "18-25",
        "interests": ["программирование", "IT", "кибербезопасность", "хакинг"],
        "geo": "RU, UA, KZ, BY",
        "best_for": "Cyber Security, ML",
    },
    {
        "name": "IT-специалисты (25-35)",
        "age_range": "25-35",
        "interests": ["DevOps", "Linux", "сетевая безопасность", "Python"],
        "geo": "RU, UA, KZ, BY",
        "best_for": "Blue Team, Red Team",
    },
    {
        "name": "Гик-аудитория (18-30)",
        "age_range": "18-30",
        "interests": ["гаджеты", "электроника", "DIY", "AliExpress"],
        "geo": "RU, UA, KZ, BY, международная",
        "best_for": "AliExpress — Гаджеты",
    },
    {
        "name": "Студенты IT (18-22)",
        "age_range": "18-22",
        "interests": ["учёба", "IT карьера", "стажировки", "портфолио"],
        "geo": "RU, UA, KZ",
        "best_for": "ML, Cyber Security",
    },
]

BUDGET_TIERS: list[dict[str, str | int | float]] = [
    {
        "tier": "Тест",
        "daily_usd": 10,
        "monthly_usd": 300,
        "split": "60% Meta, 25% TikTok, 15% YouTube",
        "goal": "Валидация креативов и аудиторий",
    },
    {
        "tier": "Рост",
        "daily_usd": 30,
        "monthly_usd": 900,
        "split": "50% Meta, 30% TikTok, 20% YouTube",
        "goal": "Масштабирование выигрышных связок",
    },
    {
        "tier": "Масштаб",
        "daily_usd": 100,
        "monthly_usd": 3000,
        "split": "40% Meta, 35% TikTok, 25% YouTube",
        "goal": "Максимальный охват и конверсии",
    },
]


@dataclass(frozen=True, slots=True)
class AdCopy:
    pillar: str
    headline: str
    body: str
    cta: str
    platform: str


@dataclass(frozen=True, slots=True)
class AudienceTarget:
    name: str
    age_range: str
    interests: tuple[str, ...]
    geo: str
    best_for: str


@dataclass(frozen=True, slots=True)
class BudgetTier:
    tier: str
    daily_usd: int
    monthly_usd: int
    split: str
    goal: str


@dataclass(frozen=True, slots=True)
class AdCreativePack:
    ads: tuple[AdCopy, ...]
    audiences: tuple[AudienceTarget, ...]
    budgets: tuple[BudgetTier, ...]
    objectives: dict[str, str]


def generate_ad_creatives() -> AdCreativePack:
    return AdCreativePack(
        ads=tuple(
            AdCopy(
                pillar=a["pillar"],
                headline=a["headline"],
                body=a["body"],
                cta=a["cta"],
                platform=a["platform"],
            )
            for a in AD_COPIES
        ),
        audiences=tuple(
            AudienceTarget(
                name=t["name"],
                age_range=t["age_range"],
                interests=tuple(t["interests"]),
                geo=t["geo"],
                best_for=t["best_for"],
            )
            for t in AUDIENCE_TARGETS
        ),
        budgets=tuple(
            BudgetTier(
                tier=b["tier"],
                daily_usd=int(b["daily_usd"]),
                monthly_usd=int(b["monthly_usd"]),
                split=b["split"],
                goal=b["goal"],
            )
            for b in BUDGET_TIERS
        ),
        objectives=dict(AD_OBJECTIVES),
    )


def export_ad_json(pack: AdCreativePack, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "ads": [
            {
                "pillar": a.pillar,
                "headline": a.headline,
                "body": a.body,
                "cta": a.cta,
                "platform": a.platform,
            }
            for a in pack.ads
        ],
        "audiences": [
            {
                "name": t.name,
                "age_range": t.age_range,
                "interests": list(t.interests),
                "geo": t.geo,
                "best_for": t.best_for,
            }
            for t in pack.audiences
        ],
        "budgets": [
            {
                "tier": b.tier,
                "daily_usd": b.daily_usd,
                "monthly_usd": b.monthly_usd,
                "split": b.split,
                "goal": b.goal,
            }
            for b in pack.budgets
        ],
        "objectives": pack.objectives,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_ad_txt(pack: AdCreativePack, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "РЕКЛАМНЫЕ КРЕАТИВЫ — ПЛАТНОЕ ПРОДВИЖЕНИЕ",
        "=" * 60,
        "\n📢 РЕКЛАМНЫЕ КОПИИ",
        "━" * 50,
    ]
    for a in pack.ads:
        lines.append(f"\n  [{a.pillar} | {a.platform}]")
        lines.append(f"  Заголовок: {a.headline}")
        lines.extend(f"  {line}" for line in a.body.split("\n"))
        lines.append(f"  CTA: {a.cta}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🎯 ЦЕЛЕВЫЕ АУДИТОРИИ")
    lines.append("━" * 50)
    for t in pack.audiences:
        lines.append(f"\n  [{t.name}]")
        lines.append(f"    Возраст: {t.age_range}")
        lines.append(f"    Интересы: {', '.join(t.interests)}")
        lines.append(f"    Гео: {t.geo}")
        lines.append(f"    Для: {t.best_for}")

    lines.append(f"\n{'━' * 50}")
    lines.append("💰 БЮДЖЕТНЫЕ УРОВНИ")
    lines.append("━" * 50)
    for b in pack.budgets:
        lines.append(f"\n  [{b.tier}]")
        lines.append(f"    ${b.daily_usd}/день (${b.monthly_usd}/мес)")
        lines.append(f"    Распределение: {b.split}")
        lines.append(f"    Цель: {b.goal}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def ad_creative_summary(pack: AdCreativePack) -> str:
    return (
        f"Рекламные креативы: {len(pack.ads)} объявлений, "
        f"{len(pack.audiences)} аудиторий, "
        f"{len(pack.budgets)} бюджетных уровней, "
        f"{len(pack.objectives)} целей"
    )
