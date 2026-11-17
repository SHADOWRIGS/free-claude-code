"""Retention strategy — keeping customers engaged and reducing churn.

Generates structured configs for:
- Churn risk signals and scoring
- Retention tactics per lifecycle stage
- Win-back campaigns
- Loyalty program tiers
- Health score metrics
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CHURN_SIGNALS: list[dict[str, str | int]] = [
    {
        "signal": "Нет логинов 7+ дней",
        "risk_score": 30,
        "category": "engagement",
        "action": "Push-уведомление + email с новым контентом",
    },
    {
        "signal": "Прогресс курса < 20% после 14 дней",
        "risk_score": 40,
        "category": "progress",
        "action": "Персональное сообщение от ментора",
    },
    {
        "signal": "Нет активности в чате 14+ дней",
        "risk_score": 25,
        "category": "community",
        "action": "Приглашение в тематический челлендж",
    },
    {
        "signal": "Запрос возврата",
        "risk_score": 90,
        "category": "critical",
        "action": "Немедленный звонок/ЛС, предложить альтернативу",
    },
    {
        "signal": "Негативный отзыв / жалоба",
        "risk_score": 70,
        "category": "satisfaction",
        "action": "Эскалация, решение проблемы, компенсация",
    },
    {
        "signal": "Не открывает email 30+ дней",
        "risk_score": 50,
        "category": "communication",
        "action": "Re-engagement серия, сменить канал на Telegram",
    },
]

RETENTION_TACTICS: list[dict[str, str]] = [
    {
        "stage": "Первая неделя",
        "tactic": "Quick Win",
        "description": "Дать первый ощутимый результат за 7 дней",
        "implementation": "Мини-проект: настроить Nmap за 1 час",
        "expected_effect": "Retention +25% на день 7",
    },
    {
        "stage": "Первый месяц",
        "tactic": "Привычка обучения",
        "description": "Создать ежедневную привычку (5-15 мин)",
        "implementation": "Daily challenge в Telegram + streak-бейдж",
        "expected_effect": "Retention +15% на день 30",
    },
    {
        "stage": "Месяц 2-3",
        "tactic": "Социальная привязка",
        "description": "Включить в группу, дать роль, создать связи",
        "implementation": "Пары для практики, групповые CTF",
        "expected_effect": "Retention +20% на день 60",
    },
    {
        "stage": "Месяц 3-6",
        "tactic": "Прогресс и признание",
        "description": "Визуализация прогресса, сертификаты, бейджи",
        "implementation": "Промежуточные сертификаты, рейтинг студентов",
        "expected_effect": "Retention +10% на день 90",
    },
    {
        "stage": "Месяц 6+",
        "tactic": "Апсейл и углубление",
        "description": "Следующий курс, менторство, реальные проекты",
        "implementation": "Скидка 30% на следующий курс, стажировка",
        "expected_effect": "LTV +40%, retention бессрочный",
    },
]

WINBACK_CAMPAIGNS: list[dict[str, str | int]] = [
    {
        "campaign": "Мягкое напоминание",
        "trigger_days_inactive": 14,
        "channel": "Email",
        "offer": "Новый бесплатный урок по актуальной теме",
        "tone": "Дружелюбный, без давления",
    },
    {
        "campaign": "Скидочный стимул",
        "trigger_days_inactive": 30,
        "channel": "Email + Telegram",
        "offer": "Скидка 25% на продолжение или новый курс",
        "tone": "Выгода, дефицит (7 дней)",
    },
    {
        "campaign": "Персональный контакт",
        "trigger_days_inactive": 45,
        "channel": "Telegram ЛС",
        "offer": "Бесплатная менторская сессия (15 мин)",
        "tone": "Персональный, заботливый",
    },
    {
        "campaign": "Финальный оффер",
        "trigger_days_inactive": 60,
        "channel": "Email",
        "offer": "Максимальная скидка 40% + бонусный модуль",
        "tone": "Последний шанс, честный",
    },
    {
        "campaign": "Опрос причин ухода",
        "trigger_days_inactive": 90,
        "channel": "Email",
        "offer": "Подарок за заполнение опроса (PDF-гайд)",
        "tone": "Уважительный, исследовательский",
    },
]

LOYALTY_TIERS: list[dict[str, str | int]] = [
    {
        "tier": "Ученик",
        "min_days_active": 0,
        "perks": "Базовый доступ, чат поддержки",
        "badge_color": "#6B7280",
    },
    {
        "tier": "Практик",
        "min_days_active": 30,
        "perks": "Доступ к бонусным материалам, приоритетная поддержка",
        "badge_color": "#10B981",
    },
    {
        "tier": "Эксперт",
        "min_days_active": 90,
        "perks": "Скидка 15% на всё, ранний доступ к новым курсам",
        "badge_color": "#3B82F6",
    },
    {
        "tier": "Мастер",
        "min_days_active": 180,
        "perks": "Скидка 25%, менторские сессии, реферальный бонус x2",
        "badge_color": "#8B5CF6",
    },
    {
        "tier": "Легенда",
        "min_days_active": 365,
        "perks": "Бесплатный курс/год, персональный ментор, амбассадор",
        "badge_color": "#F59E0B",
    },
]

HEALTH_METRICS: list[dict[str, str | float]] = [
    {
        "metric": "DAU/MAU Ratio",
        "target": 0.3,
        "description": "Доля ежедневных активных от месячных",
        "interpretation": "> 0.3 отлично, 0.15-0.3 норма, < 0.15 проблема",
    },
    {
        "metric": "Completion Rate",
        "target": 40.0,
        "description": "Процент студентов, завершивших курс",
        "interpretation": "> 40% отлично, 20-40% норма, < 20% проблема",
    },
    {
        "metric": "NPS (Net Promoter Score)",
        "target": 50.0,
        "description": "Готовность рекомендовать (от -100 до +100)",
        "interpretation": "> 50 отлично, 30-50 хорошо, < 30 нужна работа",
    },
    {
        "metric": "Churn Rate (месячный)",
        "target": 5.0,
        "description": "Процент клиентов, уходящих за месяц",
        "interpretation": "< 5% отлично, 5-10% норма, > 10% критично",
    },
    {
        "metric": "Repeat Purchase Rate",
        "target": 25.0,
        "description": "Процент покупателей, купивших повторно",
        "interpretation": "> 25% отлично, 15-25% норма, < 15% нужен апсейл",
    },
]


@dataclass(frozen=True, slots=True)
class ChurnSignal:
    signal: str
    risk_score: int
    category: str
    action: str


@dataclass(frozen=True, slots=True)
class RetentionTactic:
    stage: str
    tactic: str
    description: str
    implementation: str
    expected_effect: str


@dataclass(frozen=True, slots=True)
class WinbackCampaign:
    campaign: str
    trigger_days_inactive: int
    channel: str
    offer: str
    tone: str


@dataclass(frozen=True, slots=True)
class LoyaltyTier:
    tier: str
    min_days_active: int
    perks: str
    badge_color: str


@dataclass(frozen=True, slots=True)
class HealthMetric:
    metric: str
    target: float
    description: str
    interpretation: str


@dataclass(frozen=True, slots=True)
class RetentionStrategy:
    churn_signals: tuple[ChurnSignal, ...]
    tactics: tuple[RetentionTactic, ...]
    winback_campaigns: tuple[WinbackCampaign, ...]
    loyalty_tiers: tuple[LoyaltyTier, ...]
    health_metrics: tuple[HealthMetric, ...]


def generate_retention_strategy() -> RetentionStrategy:
    return RetentionStrategy(
        churn_signals=tuple(
            ChurnSignal(
                signal=cs["signal"],
                risk_score=int(cs["risk_score"]),
                category=cs["category"],
                action=cs["action"],
            )
            for cs in CHURN_SIGNALS
        ),
        tactics=tuple(
            RetentionTactic(
                stage=rt["stage"],
                tactic=rt["tactic"],
                description=rt["description"],
                implementation=rt["implementation"],
                expected_effect=rt["expected_effect"],
            )
            for rt in RETENTION_TACTICS
        ),
        winback_campaigns=tuple(
            WinbackCampaign(
                campaign=wc["campaign"],
                trigger_days_inactive=int(wc["trigger_days_inactive"]),
                channel=wc["channel"],
                offer=wc["offer"],
                tone=wc["tone"],
            )
            for wc in WINBACK_CAMPAIGNS
        ),
        loyalty_tiers=tuple(
            LoyaltyTier(
                tier=lt["tier"],
                min_days_active=int(lt["min_days_active"]),
                perks=lt["perks"],
                badge_color=lt["badge_color"],
            )
            for lt in LOYALTY_TIERS
        ),
        health_metrics=tuple(
            HealthMetric(
                metric=hm["metric"],
                target=float(hm["target"]),
                description=hm["description"],
                interpretation=hm["interpretation"],
            )
            for hm in HEALTH_METRICS
        ),
    )


def export_retention_json(rs: RetentionStrategy, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "churn_signals": [
            {
                "signal": cs.signal,
                "risk_score": cs.risk_score,
                "category": cs.category,
                "action": cs.action,
            }
            for cs in rs.churn_signals
        ],
        "tactics": [
            {
                "stage": rt.stage,
                "tactic": rt.tactic,
                "description": rt.description,
                "implementation": rt.implementation,
                "expected_effect": rt.expected_effect,
            }
            for rt in rs.tactics
        ],
        "winback_campaigns": [
            {
                "campaign": wc.campaign,
                "trigger_days_inactive": wc.trigger_days_inactive,
                "channel": wc.channel,
                "offer": wc.offer,
                "tone": wc.tone,
            }
            for wc in rs.winback_campaigns
        ],
        "loyalty_tiers": [
            {
                "tier": lt.tier,
                "min_days_active": lt.min_days_active,
                "perks": lt.perks,
                "badge_color": lt.badge_color,
            }
            for lt in rs.loyalty_tiers
        ],
        "health_metrics": [
            {
                "metric": hm.metric,
                "target": hm.target,
                "description": hm.description,
                "interpretation": hm.interpretation,
            }
            for hm in rs.health_metrics
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_retention_txt(rs: RetentionStrategy, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "СТРАТЕГИЯ УДЕРЖАНИЯ КЛИЕНТОВ",
        "=" * 60,
        "\n🚨 СИГНАЛЫ ОТТОКА",
        "━" * 50,
    ]
    for cs in rs.churn_signals:
        lines.append(f"\n  [{cs.signal}] риск: {cs.risk_score}/100 ({cs.category})")
        lines.append(f"    Действие: {cs.action}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🎯 ТАКТИКИ УДЕРЖАНИЯ")
    lines.append("━" * 50)
    for rt in rs.tactics:
        lines.append(f"\n  [{rt.stage}] {rt.tactic}")
        lines.append(f"    {rt.description}")
        lines.append(f"    Реализация: {rt.implementation}")
        lines.append(f"    Эффект: {rt.expected_effect}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🔄 WIN-BACK КАМПАНИИ")
    lines.append("━" * 50)
    for wc in rs.winback_campaigns:
        lines.append(f"\n  [{wc.campaign}] триггер: {wc.trigger_days_inactive} дней")
        lines.append(f"    Канал: {wc.channel}")
        lines.append(f"    Оффер: {wc.offer}")
        lines.append(f"    Тон: {wc.tone}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🏅 ПРОГРАММА ЛОЯЛЬНОСТИ")
    lines.append("━" * 50)
    for lt in rs.loyalty_tiers:
        lines.append(f"\n  [{lt.tier}] от {lt.min_days_active} дней")
        lines.append(f"    Привилегии: {lt.perks}")

    lines.append(f"\n{'━' * 50}")
    lines.append("💊 МЕТРИКИ ЗДОРОВЬЯ")
    lines.append("━" * 50)
    lines.extend(
        f"  {hm.metric}: цель {hm.target} | {hm.interpretation}"
        for hm in rs.health_metrics
    )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def retention_summary(rs: RetentionStrategy) -> str:
    return (
        f"Удержание: "
        f"{len(rs.churn_signals)} сигналов оттока, "
        f"{len(rs.tactics)} тактик, "
        f"{len(rs.winback_campaigns)} win-back кампаний, "
        f"{len(rs.loyalty_tiers)} уровней лояльности, "
        f"{len(rs.health_metrics)} метрик здоровья"
    )
