"""Partnership program — affiliate and referral partner structure.

Generates structured partnership configs:
- Commission tiers (affiliate levels and payouts)
- Partner types (blogger, school, agency, community)
- Promo materials for partners (banners, links, scripts)
- Onboarding flow for new partners
- Performance tracking metrics
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

COMMISSION_TIERS: list[dict[str, str | int | float]] = [
    {
        "tier": "Старт",
        "level": 1,
        "commission_percent": 15,
        "min_sales": 0,
        "payout_threshold_usd": 50,
        "cookie_days": 30,
        "description": "Базовый уровень для новых партнёров",
    },
    {
        "tier": "Серебро",
        "level": 2,
        "commission_percent": 20,
        "min_sales": 10,
        "payout_threshold_usd": 50,
        "cookie_days": 60,
        "description": "10+ продаж, повышенная комиссия",
    },
    {
        "tier": "Золото",
        "level": 3,
        "commission_percent": 25,
        "min_sales": 50,
        "payout_threshold_usd": 30,
        "cookie_days": 90,
        "description": "Топ-партнёры с большим объёмом",
    },
    {
        "tier": "Платина",
        "level": 4,
        "commission_percent": 30,
        "min_sales": 200,
        "payout_threshold_usd": 0,
        "cookie_days": 120,
        "description": "Эксклюзивные условия для лидеров",
    },
]

PARTNER_TYPES: list[dict[str, str | list[str]]] = [
    {
        "type": "blogger",
        "name": "Блогер / Инфлюенсер",
        "description": "YouTube, Instagram, TikTok авторы с IT-аудиторией",
        "ideal_audience": "1K-100K подписчиков в IT-нише",
        "formats": ["обзор курса", "промо-код в видео", "сторис с ссылкой"],
    },
    {
        "type": "school",
        "name": "Онлайн-школа / Преподаватель",
        "description": "Платформы и преподаватели, ищущие доп. курсы для студентов",
        "ideal_audience": "Студенты IT-программ",
        "formats": ["кросс-продажа", "бандл с курсами", "рекомендация"],
    },
    {
        "type": "agency",
        "name": "Digital-агентство",
        "description": "Агентства, предлагающие обучение клиентам",
        "ideal_audience": "Корпоративные клиенты",
        "formats": ["white-label", "пакетное предложение", "корпоративная скидка"],
    },
    {
        "type": "community",
        "name": "IT-сообщество",
        "description": "Telegram-каналы, Discord-серверы, форумы",
        "ideal_audience": "Активные IT-энтузиасты",
        "formats": ["пост в канале", "закреп", "розыгрыш доступа"],
    },
    {
        "type": "gadget_reviewer",
        "name": "Обзорщик гаджетов",
        "description": "Авторы обзоров хакерского оборудования",
        "ideal_audience": "Гик-аудитория 18-35",
        "formats": ["обзор + реферальная ссылка", "подборка", "распаковка"],
    },
]

PROMO_MATERIALS: list[dict[str, str]] = [
    {
        "material": "banner_set",
        "name": "Набор баннеров",
        "description": "10 баннеров (1080x1080, 1920x1080, 300x250) для каждого курса",
        "format": "PNG + PSD исходники",
    },
    {
        "material": "text_templates",
        "name": "Текстовые шаблоны",
        "description": "5 готовых текстов для постов/email с промо-кодом",
        "format": "TXT / Google Docs",
    },
    {
        "material": "video_scripts",
        "name": "Видео-сценарии",
        "description": "3 сценария для YouTube-интеграции (30с, 60с, 2мин)",
        "format": "TXT / Google Docs",
    },
    {
        "material": "landing_links",
        "name": "Персональные ссылки",
        "description": "UTM-ссылки с трекингом для каждого партнёра",
        "format": "URL + QR-код",
    },
    {
        "material": "promo_codes",
        "name": "Промо-коды",
        "description": "Уникальный код на скидку 10-20% для аудитории партнёра",
        "format": "Текстовый код",
    },
    {
        "material": "media_kit",
        "name": "Медиа-кит",
        "description": "Логотипы, скриншоты курсов, отзывы студентов",
        "format": "ZIP-архив",
    },
]

ONBOARDING_STEPS: list[dict[str, str | int]] = [
    {
        "step": 1,
        "name": "Регистрация",
        "description": "Заполнить анкету партнёра (имя, площадка, аудитория)",
        "duration_days": 1,
    },
    {
        "step": 2,
        "name": "Верификация",
        "description": "Проверка аккаунта и аудитории модератором",
        "duration_days": 2,
    },
    {
        "step": 3,
        "name": "Доступ к материалам",
        "description": "Получение баннеров, ссылок, промо-кодов",
        "duration_days": 1,
    },
    {
        "step": 4,
        "name": "Первая публикация",
        "description": "Партнёр делает первый промо-пост",
        "duration_days": 7,
    },
    {
        "step": 5,
        "name": "Первая выплата",
        "description": "Начисление комиссии после первых конверсий",
        "duration_days": 30,
    },
]

TRACKING_METRICS: list[dict[str, str]] = [
    {
        "metric": "clicks",
        "name": "Клики по ссылке",
        "description": "Количество переходов по партнёрской ссылке",
    },
    {
        "metric": "registrations",
        "name": "Регистрации",
        "description": "Новые аккаунты через партнёрскую ссылку",
    },
    {
        "metric": "conversions",
        "name": "Конверсии (покупки)",
        "description": "Оплаченные курсы от привлечённых пользователей",
    },
    {
        "metric": "revenue",
        "name": "Доход партнёра",
        "description": "Суммарная комиссия за период",
    },
    {
        "metric": "cr",
        "name": "Конверсия клик→покупка",
        "description": "Процент покупателей от кликнувших",
    },
    {
        "metric": "avg_order",
        "name": "Средний чек",
        "description": "Средняя стоимость покупки от партнёрского трафика",
    },
]


@dataclass(frozen=True, slots=True)
class CommissionTier:
    tier: str
    level: int
    commission_percent: int
    min_sales: int
    payout_threshold_usd: int
    cookie_days: int
    description: str


@dataclass(frozen=True, slots=True)
class PartnerType:
    type: str
    name: str
    description: str
    ideal_audience: str
    formats: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PromoMaterial:
    material: str
    name: str
    description: str
    format: str


@dataclass(frozen=True, slots=True)
class OnboardingStep:
    step: int
    name: str
    description: str
    duration_days: int


@dataclass(frozen=True, slots=True)
class TrackingMetric:
    metric: str
    name: str
    description: str


@dataclass(frozen=True, slots=True)
class PartnershipProgram:
    commission_tiers: tuple[CommissionTier, ...]
    partner_types: tuple[PartnerType, ...]
    promo_materials: tuple[PromoMaterial, ...]
    onboarding: tuple[OnboardingStep, ...]
    tracking_metrics: tuple[TrackingMetric, ...]


def generate_partnership_program() -> PartnershipProgram:
    return PartnershipProgram(
        commission_tiers=tuple(
            CommissionTier(
                tier=t["tier"],
                level=int(t["level"]),
                commission_percent=int(t["commission_percent"]),
                min_sales=int(t["min_sales"]),
                payout_threshold_usd=int(t["payout_threshold_usd"]),
                cookie_days=int(t["cookie_days"]),
                description=t["description"],
            )
            for t in COMMISSION_TIERS
        ),
        partner_types=tuple(
            PartnerType(
                type=p["type"],
                name=p["name"],
                description=p["description"],
                ideal_audience=p["ideal_audience"],
                formats=tuple(p["formats"]),
            )
            for p in PARTNER_TYPES
        ),
        promo_materials=tuple(
            PromoMaterial(
                material=m["material"],
                name=m["name"],
                description=m["description"],
                format=m["format"],
            )
            for m in PROMO_MATERIALS
        ),
        onboarding=tuple(
            OnboardingStep(
                step=int(s["step"]),
                name=s["name"],
                description=s["description"],
                duration_days=int(s["duration_days"]),
            )
            for s in ONBOARDING_STEPS
        ),
        tracking_metrics=tuple(
            TrackingMetric(
                metric=m["metric"],
                name=m["name"],
                description=m["description"],
            )
            for m in TRACKING_METRICS
        ),
    )


def export_partnership_json(pp: PartnershipProgram, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "commission_tiers": [
            {
                "tier": t.tier,
                "level": t.level,
                "commission_percent": t.commission_percent,
                "min_sales": t.min_sales,
                "payout_threshold_usd": t.payout_threshold_usd,
                "cookie_days": t.cookie_days,
                "description": t.description,
            }
            for t in pp.commission_tiers
        ],
        "partner_types": [
            {
                "type": p.type,
                "name": p.name,
                "description": p.description,
                "ideal_audience": p.ideal_audience,
                "formats": list(p.formats),
            }
            for p in pp.partner_types
        ],
        "promo_materials": [
            {
                "material": m.material,
                "name": m.name,
                "description": m.description,
                "format": m.format,
            }
            for m in pp.promo_materials
        ],
        "onboarding": [
            {
                "step": s.step,
                "name": s.name,
                "description": s.description,
                "duration_days": s.duration_days,
            }
            for s in pp.onboarding
        ],
        "tracking_metrics": [
            {
                "metric": m.metric,
                "name": m.name,
                "description": m.description,
            }
            for m in pp.tracking_metrics
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_partnership_txt(pp: PartnershipProgram, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "ПАРТНЁРСКАЯ ПРОГРАММА — AFFILIATE & REFERRAL",
        "=" * 60,
        "\n💰 КОМИССИОННЫЕ УРОВНИ",
        "━" * 50,
    ]
    for t in pp.commission_tiers:
        lines.append(f"\n  [{t.tier}] Уровень {t.level}")
        lines.append(f"    Комиссия: {t.commission_percent}%")
        lines.append(f"    Мин. продаж: {t.min_sales} | Cookie: {t.cookie_days} дней")
        lines.append(f"    Порог выплаты: ${t.payout_threshold_usd}")
        lines.append(f"    {t.description}")

    lines.append(f"\n{'━' * 50}")
    lines.append("👥 ТИПЫ ПАРТНЁРОВ")
    lines.append("━" * 50)
    for p in pp.partner_types:
        lines.append(f"\n  [{p.type}] {p.name}")
        lines.append(f"    {p.description}")
        lines.append(f"    Аудитория: {p.ideal_audience}")
        lines.append(f"    Форматы: {', '.join(p.formats)}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📦 ПРОМО-МАТЕРИАЛЫ")
    lines.append("━" * 50)
    for m in pp.promo_materials:
        lines.append(f"\n  [{m.material}] {m.name}")
        lines.append(f"    {m.description}")
        lines.append(f"    Формат: {m.format}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🚀 ОНБОРДИНГ ПАРТНЁРА")
    lines.append("━" * 50)
    lines.extend(
        f"  {s.step}. {s.name} ({s.duration_days} дн.) — {s.description}"
        for s in pp.onboarding
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("📊 МЕТРИКИ ОТСЛЕЖИВАНИЯ")
    lines.append("━" * 50)
    lines.extend(
        f"  • {m.name} ({m.metric}) — {m.description}"
        for m in pp.tracking_metrics
    )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def partnership_summary(pp: PartnershipProgram) -> str:
    return (
        f"Партнёрская программа: "
        f"{len(pp.commission_tiers)} уровней комиссии, "
        f"{len(pp.partner_types)} типов партнёров, "
        f"{len(pp.promo_materials)} промо-материалов, "
        f"{len(pp.onboarding)} шагов онбординга, "
        f"{len(pp.tracking_metrics)} метрик"
    )
