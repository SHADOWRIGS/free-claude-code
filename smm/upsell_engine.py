"""Upsell engine — structured configs for cross-sell and upsell flows.

Generates:
- Product upgrade paths
- Bundle recommendations
- Trigger conditions
- Upsell message templates
- Revenue projections per scenario
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

UPGRADE_PATHS: list[dict[str, str | int]] = [
    {
        "from_product": "Cyber Security & Ethical Hacking",
        "to_product": "Red Team / Offensive Security",
        "discount_pct": 25,
        "trigger": "Завершение 70% курса Cyber Security",
        "message": "Готовы к атакующей стороне? Скидка 25% на Red Team!",
    },
    {
        "from_product": "Blue Team / Defensive Security",
        "to_product": "Cyber Security & Ethical Hacking",
        "discount_pct": 20,
        "trigger": "Завершение модуля SIEM/SOC",
        "message": "Усильте защиту пониманием атак — Cyber Security со скидкой 20%!",
    },
    {
        "from_product": "Red Team / Offensive Security",
        "to_product": "Blue Team / Defensive Security",
        "discount_pct": 20,
        "trigger": "Прохождение модуля пентест-отчётов",
        "message": "Знаете как атаковать — научитесь защищать! Blue Team -20%",
    },
    {
        "from_product": "Machine Learning & AI",
        "to_product": "Cyber Security & Ethical Hacking",
        "discount_pct": 15,
        "trigger": "Завершение проекта по детекции аномалий",
        "message": "Примените ML в кибербезопасности — Cyber Security -15%!",
    },
    {
        "from_product": "AliExpress Gadgets (покупатель)",
        "to_product": "Cyber Security & Ethical Hacking",
        "discount_pct": 30,
        "trigger": "Покупка 3+ гаджетов через реферальную ссылку",
        "message": "У вас уже есть инструменты — научитесь ими владеть! -30%",
    },
]

BUNDLE_OFFERS: list[dict[str, str | int]] = [
    {
        "name": "Starter Bundle",
        "products": "Cyber Security + AliExpress подборка",
        "regular_price": 227,
        "bundle_price": 177,
        "savings_pct": 22,
        "target_audience": "Новички в кибербезопасности",
    },
    {
        "name": "Full Stack Security",
        "products": "Cyber Security + Blue Team + Red Team",
        "regular_price": 591,
        "bundle_price": 397,
        "savings_pct": 33,
        "target_audience": "Серьёзные специалисты, карьерный рост",
    },
    {
        "name": "AI Security Pro",
        "products": "Machine Learning + Cyber Security",
        "regular_price": 394,
        "bundle_price": 297,
        "savings_pct": 25,
        "target_audience": "Аналитики, SOC-инженеры, исследователи",
    },
    {
        "name": "All Access Pass",
        "products": "Все 4 курса + VIP-поддержка",
        "regular_price": 788,
        "bundle_price": 497,
        "savings_pct": 37,
        "target_audience": "Максимальный результат, карьерный прорыв",
    },
    {
        "name": "Team License (5 мест)",
        "products": "Любой курс x5 мест + командный дашборд",
        "regular_price": 985,
        "bundle_price": 697,
        "savings_pct": 29,
        "target_audience": "Компании, SOC-команды, HR",
    },
]

TRIGGER_CONDITIONS: list[dict[str, str | int]] = [
    {
        "trigger": "Завершение курса",
        "timing": "Сразу после финального теста",
        "channel": "Email + In-app",
        "priority": 1,
        "conversion_rate_expected": 12,
    },
    {
        "trigger": "Прохождение 50% курса",
        "timing": "После 50% прогресса",
        "channel": "In-app уведомление",
        "priority": 2,
        "conversion_rate_expected": 8,
    },
    {
        "trigger": "Высокий NPS (9-10)",
        "timing": "Через 24ч после оценки",
        "channel": "Email персональный",
        "priority": 3,
        "conversion_rate_expected": 15,
    },
    {
        "trigger": "Реферальная покупка",
        "timing": "После первой успешной реферальной транзакции",
        "channel": "Telegram + Email",
        "priority": 4,
        "conversion_rate_expected": 10,
    },
    {
        "trigger": "Сезонная акция",
        "timing": "Black Friday / Новый год / 11.11",
        "channel": "Все каналы",
        "priority": 5,
        "conversion_rate_expected": 18,
    },
    {
        "trigger": "Истечение доступа (7 дней до)",
        "timing": "За 7 дней до окончания подписки",
        "channel": "Email + Push",
        "priority": 1,
        "conversion_rate_expected": 20,
    },
]

MESSAGE_TEMPLATES: list[dict[str, str]] = [
    {
        "type": "completion_upsell",
        "subject": "Поздравляем с завершением! Следующий шаг ждёт",
        "body": "Вы завершили {course_name}! "
        "Следующий логичный шаг — {next_course}. "
        "Специально для выпускников: скидка {discount}%.",
        "cta": "Получить скидку",
    },
    {
        "type": "bundle_promo",
        "subject": "Бандл {bundle_name} — экономия {savings}%",
        "body": "Объедините курсы и сэкономьте! "
        "{bundle_name}: {products} всего за ${price}.",
        "cta": "Собрать бандл",
    },
    {
        "type": "nps_followup",
        "subject": "Спасибо за высокую оценку! Подарок внутри",
        "body": "Вы поставили нам {score}/10 — это невероятно! "
        "В благодарность: персональная скидка {discount}% на {product}.",
        "cta": "Активировать скидку",
    },
    {
        "type": "expiry_reminder",
        "subject": "Доступ истекает через {days} дней",
        "body": "Ваш доступ к {course_name} заканчивается {date}. "
        "Продлите сейчас со скидкой {discount}% или обновите до бандла!",
        "cta": "Продлить доступ",
    },
    {
        "type": "referral_reward",
        "subject": "Ваш друг купил курс — вот ваш бонус!",
        "body": "Благодаря вашей рекомендации {friend} присоединился! "
        "Ваша награда: скидка {discount}% на любой следующий курс.",
        "cta": "Использовать бонус",
    },
]

REVENUE_PROJECTIONS: list[dict[str, str | int | float]] = [
    {
        "scenario": "Базовый (без апсейла)",
        "monthly_customers": 100,
        "avg_order": 197,
        "upsell_rate_pct": 0,
        "monthly_revenue": 19700,
        "annual_revenue": 236400,
    },
    {
        "scenario": "Лёгкий апсейл (10%)",
        "monthly_customers": 100,
        "avg_order": 197,
        "upsell_rate_pct": 10,
        "monthly_revenue": 23640,
        "annual_revenue": 283680,
    },
    {
        "scenario": "Средний апсейл (20%)",
        "monthly_customers": 100,
        "avg_order": 197,
        "upsell_rate_pct": 20,
        "monthly_revenue": 27580,
        "annual_revenue": 330960,
    },
    {
        "scenario": "Агрессивный апсейл (30%)",
        "monthly_customers": 100,
        "avg_order": 197,
        "upsell_rate_pct": 30,
        "monthly_revenue": 31520,
        "annual_revenue": 378240,
    },
]


@dataclass(frozen=True, slots=True)
class UpgradePath:
    from_product: str
    to_product: str
    discount_pct: int
    trigger: str
    message: str


@dataclass(frozen=True, slots=True)
class BundleOffer:
    name: str
    products: str
    regular_price: int
    bundle_price: int
    savings_pct: int
    target_audience: str


@dataclass(frozen=True, slots=True)
class TriggerCondition:
    trigger: str
    timing: str
    channel: str
    priority: int
    conversion_rate_expected: int


@dataclass(frozen=True, slots=True)
class MessageTemplate:
    type: str
    subject: str
    body: str
    cta: str


@dataclass(frozen=True, slots=True)
class RevenueProjection:
    scenario: str
    monthly_customers: int
    avg_order: int
    upsell_rate_pct: int
    monthly_revenue: int
    annual_revenue: int


@dataclass(frozen=True, slots=True)
class UpsellEngine:
    upgrade_paths: tuple[UpgradePath, ...]
    bundle_offers: tuple[BundleOffer, ...]
    trigger_conditions: tuple[TriggerCondition, ...]
    message_templates: tuple[MessageTemplate, ...]
    revenue_projections: tuple[RevenueProjection, ...]


def generate_upsell_engine() -> UpsellEngine:
    return UpsellEngine(
        upgrade_paths=tuple(
            UpgradePath(
                from_product=up["from_product"],
                to_product=up["to_product"],
                discount_pct=int(up["discount_pct"]),
                trigger=up["trigger"],
                message=up["message"],
            )
            for up in UPGRADE_PATHS
        ),
        bundle_offers=tuple(
            BundleOffer(
                name=bo["name"],
                products=bo["products"],
                regular_price=int(bo["regular_price"]),
                bundle_price=int(bo["bundle_price"]),
                savings_pct=int(bo["savings_pct"]),
                target_audience=bo["target_audience"],
            )
            for bo in BUNDLE_OFFERS
        ),
        trigger_conditions=tuple(
            TriggerCondition(
                trigger=tc["trigger"],
                timing=tc["timing"],
                channel=tc["channel"],
                priority=int(tc["priority"]),
                conversion_rate_expected=int(tc["conversion_rate_expected"]),
            )
            for tc in TRIGGER_CONDITIONS
        ),
        message_templates=tuple(
            MessageTemplate(
                type=mt["type"],
                subject=mt["subject"],
                body=mt["body"],
                cta=mt["cta"],
            )
            for mt in MESSAGE_TEMPLATES
        ),
        revenue_projections=tuple(
            RevenueProjection(
                scenario=rp["scenario"],
                monthly_customers=int(rp["monthly_customers"]),
                avg_order=int(rp["avg_order"]),
                upsell_rate_pct=int(rp["upsell_rate_pct"]),
                monthly_revenue=int(rp["monthly_revenue"]),
                annual_revenue=int(rp["annual_revenue"]),
            )
            for rp in REVENUE_PROJECTIONS
        ),
    )


def export_upsell_json(ue: UpsellEngine, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "upgrade_paths": [
            {
                "from_product": up.from_product,
                "to_product": up.to_product,
                "discount_pct": up.discount_pct,
                "trigger": up.trigger,
                "message": up.message,
            }
            for up in ue.upgrade_paths
        ],
        "bundle_offers": [
            {
                "name": bo.name,
                "products": bo.products,
                "regular_price": bo.regular_price,
                "bundle_price": bo.bundle_price,
                "savings_pct": bo.savings_pct,
                "target_audience": bo.target_audience,
            }
            for bo in ue.bundle_offers
        ],
        "trigger_conditions": [
            {
                "trigger": tc.trigger,
                "timing": tc.timing,
                "channel": tc.channel,
                "priority": tc.priority,
                "conversion_rate_expected": tc.conversion_rate_expected,
            }
            for tc in ue.trigger_conditions
        ],
        "message_templates": [
            {
                "type": mt.type,
                "subject": mt.subject,
                "body": mt.body,
                "cta": mt.cta,
            }
            for mt in ue.message_templates
        ],
        "revenue_projections": [
            {
                "scenario": rp.scenario,
                "monthly_customers": rp.monthly_customers,
                "avg_order": rp.avg_order,
                "upsell_rate_pct": rp.upsell_rate_pct,
                "monthly_revenue": rp.monthly_revenue,
                "annual_revenue": rp.annual_revenue,
            }
            for rp in ue.revenue_projections
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_upsell_txt(ue: UpsellEngine, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "ДВИЖОК АПСЕЙЛА И КРОСС-ПРОДАЖ",
        "=" * 60,
        "\n📈 ПУТИ АПГРЕЙДА",
        "━" * 50,
    ]
    for up in ue.upgrade_paths:
        lines.append(f"\n  {up.from_product} --> {up.to_product} (-{up.discount_pct}%)")
        lines.append(f"    Триггер: {up.trigger}")
        lines.append(f"    Сообщение: {up.message}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🎁 БАНДЛЫ")
    lines.append("━" * 50)
    for bo in ue.bundle_offers:
        lines.append(
            f"\n  [{bo.name}] ${bo.bundle_price} "
            f"(вместо ${bo.regular_price}, экономия {bo.savings_pct}%)"
        )
        lines.append(f"    Состав: {bo.products}")
        lines.append(f"    Аудитория: {bo.target_audience}")

    lines.append(f"\n{'━' * 50}")
    lines.append("⚡ ТРИГГЕРЫ")
    lines.append("━" * 50)
    for tc in ue.trigger_conditions:
        lines.append(
            f"\n  [{tc.trigger}] приоритет: {tc.priority}, "
            f"CR ожидаемый: {tc.conversion_rate_expected}%"
        )
        lines.append(f"    Тайминг: {tc.timing}")
        lines.append(f"    Канал: {tc.channel}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📧 ШАБЛОНЫ СООБЩЕНИЙ")
    lines.append("━" * 50)
    lines.extend(
        f"  [{mt.type}] {mt.subject} | CTA: {mt.cta}" for mt in ue.message_templates
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("💰 ПРОЕКЦИИ ДОХОДА")
    lines.append("━" * 50)
    lines.extend(
        f"  [{rp.scenario}] апсейл {rp.upsell_rate_pct}% | "
        f"${rp.monthly_revenue}/мес | ${rp.annual_revenue}/год"
        for rp in ue.revenue_projections
    )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def upsell_summary(ue: UpsellEngine) -> str:
    return (
        f"Апсейл: "
        f"{len(ue.upgrade_paths)} путей апгрейда, "
        f"{len(ue.bundle_offers)} бандлов, "
        f"{len(ue.trigger_conditions)} триггеров, "
        f"{len(ue.message_templates)} шаблонов, "
        f"{len(ue.revenue_projections)} сценариев дохода"
    )
