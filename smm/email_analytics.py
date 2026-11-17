"""Email analytics — campaign performance tracking and optimization.

Generates structured configs for:
- Campaign types with expected metrics
- Deliverability benchmarks
- Segmentation rules for targeting
- A/B test parameters for email
- Automation trigger rules
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CAMPAIGN_TYPES: list[dict[str, str | float]] = [
    {
        "type": "Welcome-серия",
        "frequency": "Авто (день 0, 1, 3, 7)",
        "expected_open_rate": 60.0,
        "expected_click_rate": 15.0,
        "goal": "Активация нового клиента",
        "pillar": "Все курсы",
    },
    {
        "type": "Nurture (прогрев)",
        "frequency": "2 раза в неделю",
        "expected_open_rate": 35.0,
        "expected_click_rate": 5.0,
        "goal": "Перевод из интереса в покупку",
        "pillar": "Все курсы",
    },
    {
        "type": "Промо-рассылка",
        "frequency": "1-2 раза в месяц",
        "expected_open_rate": 25.0,
        "expected_click_rate": 8.0,
        "goal": "Прямые продажи курсов",
        "pillar": "Все курсы",
    },
    {
        "type": "Дайджест контента",
        "frequency": "1 раз в неделю",
        "expected_open_rate": 30.0,
        "expected_click_rate": 4.0,
        "goal": "Удержание и вовлечённость",
        "pillar": "Все курсы + гаджеты",
    },
    {
        "type": "Abandoned cart",
        "frequency": "Авто (1ч, 24ч, 72ч)",
        "expected_open_rate": 45.0,
        "expected_click_rate": 12.0,
        "goal": "Возврат брошенных корзин",
        "pillar": "Все курсы",
    },
    {
        "type": "Реферальное приглашение",
        "frequency": "По событию (покупка)",
        "expected_open_rate": 40.0,
        "expected_click_rate": 10.0,
        "goal": "Рост через рекомендации",
        "pillar": "Партнёрская программа",
    },
]

DELIVERABILITY_BENCHMARKS: list[dict[str, str | float]] = [
    {
        "metric": "Delivery Rate",
        "target": 98.0,
        "warning": 95.0,
        "critical": 90.0,
        "unit": "%",
        "fix": "Очистить базу, проверить SPF/DKIM/DMARC",
    },
    {
        "metric": "Open Rate",
        "target": 30.0,
        "warning": 20.0,
        "critical": 15.0,
        "unit": "%",
        "fix": "A/B тест тем, сегментация, время отправки",
    },
    {
        "metric": "Click Rate",
        "target": 5.0,
        "warning": 3.0,
        "critical": 1.5,
        "unit": "%",
        "fix": "Улучшить CTA, релевантность контента",
    },
    {
        "metric": "Unsubscribe Rate",
        "target": 0.3,
        "warning": 0.5,
        "critical": 1.0,
        "unit": "%",
        "fix": "Снизить частоту, улучшить сегментацию",
    },
    {
        "metric": "Spam Complaint Rate",
        "target": 0.05,
        "warning": 0.1,
        "critical": 0.3,
        "unit": "%",
        "fix": "Double opt-in, видимая отписка, релевантность",
    },
    {
        "metric": "Bounce Rate",
        "target": 1.0,
        "warning": 3.0,
        "critical": 5.0,
        "unit": "%",
        "fix": "Верификация email при подписке, очистка базы",
    },
]

SEGMENTATION_RULES: list[dict[str, str]] = [
    {
        "segment": "Новые подписчики (0-7 дней)",
        "criteria": "Дата подписки < 7 дней",
        "content": "Welcome-серия, лид-магнит, знакомство с брендом",
        "frequency": "Ежедневно (автоматика)",
    },
    {
        "segment": "Вовлечённые (открывали 3+ писем за 30 дней)",
        "criteria": "Opens >= 3 за последние 30 дней",
        "content": "Промо-офферы, эксклюзивный контент, early access",
        "frequency": "2-3 раза в неделю",
    },
    {
        "segment": "Спящие (нет открытий 30+ дней)",
        "criteria": "Нет opens за 30 дней",
        "content": "Re-engagement серия, спецоффер, опрос",
        "frequency": "1 раз в 2 недели",
    },
    {
        "segment": "Покупатели",
        "criteria": "Есть хотя бы 1 покупка",
        "content": "Апсейл, кросс-сейл, реферальная программа",
        "frequency": "1-2 раза в неделю",
    },
    {
        "segment": "VIP (3+ покупки или LTV > $500)",
        "criteria": "Purchases >= 3 или LTV > 500",
        "content": "Эксклюзивные офферы, менторство, ранний доступ",
        "frequency": "Персональный подход",
    },
]

AB_TEST_EMAIL: list[dict[str, str]] = [
    {
        "element": "Тема письма",
        "variant_a": "Прямая выгода: 'Получи скидку 30% на курс'",
        "variant_b": "Любопытство: 'Секрет, который знают только хакеры'",
        "metric": "Open Rate",
        "min_sample": "500 на вариант",
    },
    {
        "element": "CTA-кнопка",
        "variant_a": "Текст: 'Начать обучение'",
        "variant_b": "Текст: 'Получить доступ сейчас'",
        "metric": "Click Rate",
        "min_sample": "300 на вариант",
    },
    {
        "element": "Время отправки",
        "variant_a": "Утро (9:00 MSK)",
        "variant_b": "Вечер (19:00 MSK)",
        "metric": "Open Rate + Click Rate",
        "min_sample": "1000 на вариант",
    },
    {
        "element": "Формат письма",
        "variant_a": "Текстовое (plain)",
        "variant_b": "HTML с визуалами",
        "metric": "Click Rate + Conversion",
        "min_sample": "500 на вариант",
    },
    {
        "element": "Персонализация",
        "variant_a": "Без имени: 'Привет!'",
        "variant_b": "С именем: 'Привет, {name}!'",
        "metric": "Open Rate",
        "min_sample": "500 на вариант",
    },
]

AUTO_TRIGGERS: list[dict[str, str | int]] = [
    {
        "trigger": "Подписка на рассылку",
        "delay_minutes": 0,
        "action": "Отправить welcome email + лид-магнит",
        "sequence": "welcome_series",
    },
    {
        "trigger": "Открыл 3 письма подряд",
        "delay_minutes": 60,
        "action": "Отправить промо-оффер",
        "sequence": "hot_lead_promo",
    },
    {
        "trigger": "Кликнул по ссылке курса",
        "delay_minutes": 1440,
        "action": "Отправить кейс студента + отзыв",
        "sequence": "social_proof_nudge",
    },
    {
        "trigger": "Добавил в корзину, не купил",
        "delay_minutes": 60,
        "action": "Abandoned cart email #1",
        "sequence": "abandoned_cart",
    },
    {
        "trigger": "Не открывал 14 дней",
        "delay_minutes": 0,
        "action": "Re-engagement email с опросом",
        "sequence": "reengagement",
    },
    {
        "trigger": "Завершил курс",
        "delay_minutes": 1440,
        "action": "Запросить отзыв + предложить следующий курс",
        "sequence": "post_course_upsell",
    },
]


@dataclass(frozen=True, slots=True)
class CampaignType:
    type: str
    frequency: str
    expected_open_rate: float
    expected_click_rate: float
    goal: str
    pillar: str


@dataclass(frozen=True, slots=True)
class DeliverabilityBenchmark:
    metric: str
    target: float
    warning: float
    critical: float
    unit: str
    fix: str


@dataclass(frozen=True, slots=True)
class SegmentRule:
    segment: str
    criteria: str
    content: str
    frequency: str


@dataclass(frozen=True, slots=True)
class ABTestEmail:
    element: str
    variant_a: str
    variant_b: str
    metric: str
    min_sample: str


@dataclass(frozen=True, slots=True)
class AutoTrigger:
    trigger: str
    delay_minutes: int
    action: str
    sequence: str


@dataclass(frozen=True, slots=True)
class EmailAnalytics:
    campaign_types: tuple[CampaignType, ...]
    benchmarks: tuple[DeliverabilityBenchmark, ...]
    segments: tuple[SegmentRule, ...]
    ab_tests: tuple[ABTestEmail, ...]
    auto_triggers: tuple[AutoTrigger, ...]


def generate_email_analytics() -> EmailAnalytics:
    return EmailAnalytics(
        campaign_types=tuple(
            CampaignType(
                type=ct["type"],
                frequency=ct["frequency"],
                expected_open_rate=float(ct["expected_open_rate"]),
                expected_click_rate=float(ct["expected_click_rate"]),
                goal=ct["goal"],
                pillar=ct["pillar"],
            )
            for ct in CAMPAIGN_TYPES
        ),
        benchmarks=tuple(
            DeliverabilityBenchmark(
                metric=db["metric"],
                target=float(db["target"]),
                warning=float(db["warning"]),
                critical=float(db["critical"]),
                unit=db["unit"],
                fix=db["fix"],
            )
            for db in DELIVERABILITY_BENCHMARKS
        ),
        segments=tuple(
            SegmentRule(
                segment=sr["segment"],
                criteria=sr["criteria"],
                content=sr["content"],
                frequency=sr["frequency"],
            )
            for sr in SEGMENTATION_RULES
        ),
        ab_tests=tuple(
            ABTestEmail(
                element=ab["element"],
                variant_a=ab["variant_a"],
                variant_b=ab["variant_b"],
                metric=ab["metric"],
                min_sample=ab["min_sample"],
            )
            for ab in AB_TEST_EMAIL
        ),
        auto_triggers=tuple(
            AutoTrigger(
                trigger=at["trigger"],
                delay_minutes=int(at["delay_minutes"]),
                action=at["action"],
                sequence=at["sequence"],
            )
            for at in AUTO_TRIGGERS
        ),
    )


def export_email_analytics_json(ea: EmailAnalytics, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "campaign_types": [
            {
                "type": ct.type,
                "frequency": ct.frequency,
                "expected_open_rate": ct.expected_open_rate,
                "expected_click_rate": ct.expected_click_rate,
                "goal": ct.goal,
                "pillar": ct.pillar,
            }
            for ct in ea.campaign_types
        ],
        "benchmarks": [
            {
                "metric": db.metric,
                "target": db.target,
                "warning": db.warning,
                "critical": db.critical,
                "unit": db.unit,
                "fix": db.fix,
            }
            for db in ea.benchmarks
        ],
        "segments": [
            {
                "segment": sr.segment,
                "criteria": sr.criteria,
                "content": sr.content,
                "frequency": sr.frequency,
            }
            for sr in ea.segments
        ],
        "ab_tests": [
            {
                "element": ab.element,
                "variant_a": ab.variant_a,
                "variant_b": ab.variant_b,
                "metric": ab.metric,
                "min_sample": ab.min_sample,
            }
            for ab in ea.ab_tests
        ],
        "auto_triggers": [
            {
                "trigger": at.trigger,
                "delay_minutes": at.delay_minutes,
                "action": at.action,
                "sequence": at.sequence,
            }
            for at in ea.auto_triggers
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_email_analytics_txt(ea: EmailAnalytics, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "АНАЛИТИКА EMAIL-КАМПАНИЙ",
        "=" * 60,
        "\n📧 ТИПЫ КАМПАНИЙ",
        "━" * 50,
    ]
    for ct in ea.campaign_types:
        lines.append(f"\n  [{ct.type}] ({ct.frequency})")
        lines.append(
            f"    OR: {ct.expected_open_rate:.0f}% | CR: {ct.expected_click_rate:.0f}%"
        )
        lines.append(f"    Цель: {ct.goal}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📊 БЕНЧМАРКИ ДОСТАВЛЯЕМОСТИ")
    lines.append("━" * 50)
    lines.extend(
        f"  {db.metric}: цель {db.target}{db.unit} | "
        f"warning {db.warning}{db.unit} | critical {db.critical}{db.unit}"
        for db in ea.benchmarks
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("👥 СЕГМЕНТАЦИЯ")
    lines.append("━" * 50)
    for sr in ea.segments:
        lines.append(f"\n  [{sr.segment}]")
        lines.append(f"    Критерий: {sr.criteria}")
        lines.append(f"    Контент: {sr.content}")
        lines.append(f"    Частота: {sr.frequency}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🧪 A/B ТЕСТЫ EMAIL")
    lines.append("━" * 50)
    for ab in ea.ab_tests:
        lines.append(f"\n  [{ab.element}] метрика: {ab.metric}")
        lines.append(f"    A: {ab.variant_a}")
        lines.append(f"    B: {ab.variant_b}")
        lines.append(f"    Min: {ab.min_sample}")

    lines.append(f"\n{'━' * 50}")
    lines.append("⚡ АВТО-ТРИГГЕРЫ")
    lines.append("━" * 50)
    for at in ea.auto_triggers:
        delay = f"{at.delay_minutes} мин" if at.delay_minutes > 0 else "сразу"
        lines.append(f"\n  [{at.trigger}] задержка: {delay}")
        lines.append(f"    Действие: {at.action}")
        lines.append(f"    Серия: {at.sequence}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def email_analytics_summary(ea: EmailAnalytics) -> str:
    return (
        f"Email-аналитика: "
        f"{len(ea.campaign_types)} типов кампаний, "
        f"{len(ea.benchmarks)} бенчмарков, "
        f"{len(ea.segments)} сегментов, "
        f"{len(ea.ab_tests)} A/B тестов, "
        f"{len(ea.auto_triggers)} авто-триггеров"
    )
