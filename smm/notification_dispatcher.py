"""Notification dispatcher — multi-channel notification configs.

Generates:
- Channel configurations (Email, Telegram, Push, In-app)
- Event-to-channel routing rules
- Template registry per event type
- Rate limiting and batching rules
- Escalation chains
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CHANNEL_CONFIGS: list[dict[str, str | int]] = [
    {
        "channel": "Email",
        "provider": "SMTP / SendGrid / Mailgun",
        "max_per_day": 5,
        "priority_range": "medium-high",
        "best_for": "Дайджесты, отчёты, важные обновления",
        "delivery_speed": "1-5 минут",
    },
    {
        "channel": "Telegram",
        "provider": "Telegram Bot API",
        "max_per_day": 20,
        "priority_range": "low-critical",
        "best_for": "Алерты, быстрые уведомления, диалоги",
        "delivery_speed": "мгновенно",
    },
    {
        "channel": "Push (мобильный)",
        "provider": "Firebase Cloud Messaging",
        "max_per_day": 10,
        "priority_range": "medium-critical",
        "best_for": "Срочные алерты, напоминания",
        "delivery_speed": "мгновенно",
    },
    {
        "channel": "In-App",
        "provider": "WebSocket / Polling",
        "max_per_day": 50,
        "priority_range": "low-medium",
        "best_for": "Контекстные подсказки, прогресс, бейджи",
        "delivery_speed": "мгновенно (при активной сессии)",
    },
    {
        "channel": "SMS",
        "provider": "Twilio / SMS.ru",
        "max_per_day": 2,
        "priority_range": "critical",
        "best_for": "Критические алерты (оплата, безопасность)",
        "delivery_speed": "10-30 секунд",
    },
]

ROUTING_RULES: list[dict[str, str]] = [
    {
        "event": "Новый подписчик",
        "channels": "In-App, Telegram",
        "priority": "low",
        "batch": "Каждые 4 часа, агрегировать",
        "condition": "Всегда",
    },
    {
        "event": "Новая покупка курса",
        "channels": "Telegram, Email",
        "priority": "high",
        "batch": "Мгновенно",
        "condition": "Всегда",
    },
    {
        "event": "Реферальная конверсия",
        "channels": "Telegram, Email, In-App",
        "priority": "high",
        "batch": "Мгновенно",
        "condition": "Всегда",
    },
    {
        "event": "ER упал ниже порога",
        "channels": "Telegram, Push",
        "priority": "critical",
        "batch": "Мгновенно",
        "condition": "ER < 2% более 3 дней подряд",
    },
    {
        "event": "Негативный отзыв / жалоба",
        "channels": "Telegram, Email, Push",
        "priority": "critical",
        "batch": "Мгновенно",
        "condition": "Sentiment score < -0.5",
    },
    {
        "event": "Контент опубликован",
        "channels": "In-App",
        "priority": "low",
        "batch": "Каждый час",
        "condition": "Всегда",
    },
    {
        "event": "Еженедельный отчёт готов",
        "channels": "Email, Telegram",
        "priority": "medium",
        "batch": "Понедельник 10:00",
        "condition": "Всегда",
    },
    {
        "event": "Бюджет рекламы исчерпан",
        "channels": "Telegram, Push, SMS",
        "priority": "critical",
        "batch": "Мгновенно",
        "condition": "Расход >= 90% дневного лимита",
    },
]

TEMPLATE_REGISTRY: list[dict[str, str]] = [
    {
        "event": "new_purchase",
        "channel": "Telegram",
        "template": "🎉 Новая покупка!\n"
        "Курс: {course_name}\n"
        "Сумма: ${amount}\n"
        "Студент: {student_name}",
    },
    {
        "event": "new_purchase",
        "channel": "Email",
        "template": "Тема: Новая покупка — {course_name}\n"
        "Студент {student_name} купил курс {course_name} за ${amount}.",
    },
    {
        "event": "referral_conversion",
        "channel": "Telegram",
        "template": "💰 Реферальная конверсия!\n"
        "Партнёр: {partner}\n"
        "Продукт: {product}\n"
        "Комиссия: ${commission}",
    },
    {
        "event": "er_drop_alert",
        "channel": "Telegram",
        "template": "⚠ ER упал!\n"
        "Платформа: {platform}\n"
        "Текущий ER: {current_er}%\n"
        "Порог: {threshold}%\n"
        "Дней подряд: {days}",
    },
    {
        "event": "weekly_report",
        "channel": "Email",
        "template": "Тема: Недельный отчёт SMM ({date_range})\n"
        "Подписчики: {followers} (+{growth})\n"
        "ER: {er}% | CTR: {ctr}%\n"
        "Доход: ${revenue}",
    },
    {
        "event": "negative_review",
        "channel": "Telegram",
        "template": "🚨 Негативный отзыв!\n"
        "Автор: {author}\n"
        "Платформа: {platform}\n"
        "Текст: {text}\n"
        "Действие: ответить в течение 24ч",
    },
]

RATE_LIMITS: list[dict[str, str | int]] = [
    {
        "rule": "Глобальный лимит",
        "max_per_hour": 20,
        "max_per_day": 100,
        "action_on_exceed": "Батчить и отложить на следующий час",
    },
    {
        "rule": "Лимит на канал (Email)",
        "max_per_hour": 3,
        "max_per_day": 5,
        "action_on_exceed": "Перенаправить в Telegram",
    },
    {
        "rule": "Лимит на канал (SMS)",
        "max_per_hour": 1,
        "max_per_day": 2,
        "action_on_exceed": "Перенаправить в Push",
    },
    {
        "rule": "Тихие часы (23:00-07:00)",
        "max_per_hour": 0,
        "max_per_day": 0,
        "action_on_exceed": "Отложить до 07:00, кроме critical",
    },
    {
        "rule": "Дедупликация",
        "max_per_hour": 1,
        "max_per_day": 1,
        "action_on_exceed": "Не отправлять повторное уведомление того же типа",
    },
]

ESCALATION_CHAINS: list[dict[str, str | int]] = [
    {
        "level": 1,
        "name": "Автоматическое уведомление",
        "delay_minutes": 0,
        "channels": "In-App, Telegram",
        "condition": "Любое событие",
    },
    {
        "level": 2,
        "name": "Повторное напоминание",
        "delay_minutes": 30,
        "channels": "Push, Email",
        "condition": "Нет реакции на level 1 за 30 мин (critical только)",
    },
    {
        "level": 3,
        "name": "Эскалация владельцу",
        "delay_minutes": 120,
        "channels": "SMS, Telegram ЛС",
        "condition": "Нет реакции на level 2 за 2ч (critical только)",
    },
    {
        "level": 4,
        "name": "Автоматическое действие",
        "delay_minutes": 240,
        "channels": "Автоматика",
        "condition": "Пауза рекламы / блок контента / авто-ответ",
    },
]


@dataclass(frozen=True, slots=True)
class ChannelConfig:
    channel: str
    provider: str
    max_per_day: int
    priority_range: str
    best_for: str
    delivery_speed: str


@dataclass(frozen=True, slots=True)
class RoutingRule:
    event: str
    channels: str
    priority: str
    batch: str
    condition: str


@dataclass(frozen=True, slots=True)
class NotificationTemplate:
    event: str
    channel: str
    template: str


@dataclass(frozen=True, slots=True)
class RateLimit:
    rule: str
    max_per_hour: int
    max_per_day: int
    action_on_exceed: str


@dataclass(frozen=True, slots=True)
class EscalationLevel:
    level: int
    name: str
    delay_minutes: int
    channels: str
    condition: str


@dataclass(frozen=True, slots=True)
class NotificationDispatcher:
    channel_configs: tuple[ChannelConfig, ...]
    routing_rules: tuple[RoutingRule, ...]
    templates: tuple[NotificationTemplate, ...]
    rate_limits: tuple[RateLimit, ...]
    escalation_chain: tuple[EscalationLevel, ...]


def generate_notification_dispatcher() -> NotificationDispatcher:
    return NotificationDispatcher(
        channel_configs=tuple(
            ChannelConfig(
                channel=cc["channel"],
                provider=cc["provider"],
                max_per_day=int(cc["max_per_day"]),
                priority_range=cc["priority_range"],
                best_for=cc["best_for"],
                delivery_speed=cc["delivery_speed"],
            )
            for cc in CHANNEL_CONFIGS
        ),
        routing_rules=tuple(
            RoutingRule(
                event=rr["event"],
                channels=rr["channels"],
                priority=rr["priority"],
                batch=rr["batch"],
                condition=rr["condition"],
            )
            for rr in ROUTING_RULES
        ),
        templates=tuple(
            NotificationTemplate(
                event=nt["event"],
                channel=nt["channel"],
                template=nt["template"],
            )
            for nt in TEMPLATE_REGISTRY
        ),
        rate_limits=tuple(
            RateLimit(
                rule=rl["rule"],
                max_per_hour=int(rl["max_per_hour"]),
                max_per_day=int(rl["max_per_day"]),
                action_on_exceed=rl["action_on_exceed"],
            )
            for rl in RATE_LIMITS
        ),
        escalation_chain=tuple(
            EscalationLevel(
                level=int(el["level"]),
                name=el["name"],
                delay_minutes=int(el["delay_minutes"]),
                channels=el["channels"],
                condition=el["condition"],
            )
            for el in ESCALATION_CHAINS
        ),
    )


def export_dispatcher_json(nd: NotificationDispatcher, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "channel_configs": [
            {
                "channel": cc.channel,
                "provider": cc.provider,
                "max_per_day": cc.max_per_day,
                "priority_range": cc.priority_range,
                "best_for": cc.best_for,
                "delivery_speed": cc.delivery_speed,
            }
            for cc in nd.channel_configs
        ],
        "routing_rules": [
            {
                "event": rr.event,
                "channels": rr.channels,
                "priority": rr.priority,
                "batch": rr.batch,
                "condition": rr.condition,
            }
            for rr in nd.routing_rules
        ],
        "templates": [
            {"event": nt.event, "channel": nt.channel, "template": nt.template}
            for nt in nd.templates
        ],
        "rate_limits": [
            {
                "rule": rl.rule,
                "max_per_hour": rl.max_per_hour,
                "max_per_day": rl.max_per_day,
                "action_on_exceed": rl.action_on_exceed,
            }
            for rl in nd.rate_limits
        ],
        "escalation_chain": [
            {
                "level": el.level,
                "name": el.name,
                "delay_minutes": el.delay_minutes,
                "channels": el.channels,
                "condition": el.condition,
            }
            for el in nd.escalation_chain
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_dispatcher_txt(nd: NotificationDispatcher, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "ДИСПЕТЧЕР УВЕДОМЛЕНИЙ",
        "=" * 60,
        "\n📡 КАНАЛЫ",
        "━" * 50,
    ]
    for cc in nd.channel_configs:
        lines.append(
            f"\n  [{cc.channel}] макс {cc.max_per_day}/день | {cc.delivery_speed}"
        )
        lines.append(f"    Провайдер: {cc.provider}")
        lines.append(f"    Лучше для: {cc.best_for}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🔀 МАРШРУТИЗАЦИЯ")
    lines.append("━" * 50)
    for rr in nd.routing_rules:
        lines.append(f"\n  [{rr.event}] приоритет: {rr.priority}")
        lines.append(f"    Каналы: {rr.channels}")
        lines.append(f"    Батчинг: {rr.batch}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📝 ШАБЛОНЫ")
    lines.append("━" * 50)
    lines.extend(f"  [{nt.event}] канал: {nt.channel}" for nt in nd.templates)

    lines.append(f"\n{'━' * 50}")
    lines.append("⏱ ЛИМИТЫ")
    lines.append("━" * 50)
    for rl in nd.rate_limits:
        lines.append(f"  [{rl.rule}] {rl.max_per_hour}/ч, {rl.max_per_day}/день")
        lines.append(f"    При превышении: {rl.action_on_exceed}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🔺 ЭСКАЛАЦИЯ")
    lines.append("━" * 50)
    lines.extend(
        f"  Level {el.level}: [{el.name}] +{el.delay_minutes}мин | {el.channels}"
        for el in nd.escalation_chain
    )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def dispatcher_summary(nd: NotificationDispatcher) -> str:
    return (
        f"Диспетчер уведомлений: "
        f"{len(nd.channel_configs)} каналов, "
        f"{len(nd.routing_rules)} правил маршрутизации, "
        f"{len(nd.templates)} шаблонов, "
        f"{len(nd.rate_limits)} лимитов, "
        f"{len(nd.escalation_chain)} уровней эскалации"
    )
