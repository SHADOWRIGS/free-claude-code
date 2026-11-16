"""Notification system — alerts for metrics, milestones, and deadlines.

Generates structured notification configs:
- Alert rules (metric thresholds, growth/drop triggers)
- Notification channels (Telegram, email, push)
- Milestone templates (subscriber counts, revenue goals)
- Content deadline reminders
- Escalation policies
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ALERT_RULES: list[dict[str, str | int | float]] = [
    {
        "name": "Просадка охвата",
        "metric": "reach",
        "condition": "drop",
        "threshold_percent": 20,
        "window": "7 дней",
        "severity": "high",
        "action": "Пересмотреть контент-план, проверить алгоритмы",
    },
    {
        "name": "Рост подписчиков",
        "metric": "followers",
        "condition": "growth",
        "threshold_percent": 10,
        "window": "7 дней",
        "severity": "info",
        "action": "Зафиксировать что сработало, масштабировать",
    },
    {
        "name": "Низкая вовлечённость",
        "metric": "engagement_rate",
        "condition": "below",
        "threshold_percent": 2,
        "window": "7 дней",
        "severity": "medium",
        "action": "Добавить больше интерактива (опросы, квизы)",
    },
    {
        "name": "Конверсия упала",
        "metric": "conversion_rate",
        "condition": "drop",
        "threshold_percent": 15,
        "window": "7 дней",
        "severity": "high",
        "action": "Проверить CTA, лендинги, воронку",
    },
    {
        "name": "Бюджет превышен",
        "metric": "ad_spend",
        "condition": "above",
        "threshold_percent": 110,
        "window": "30 дней",
        "severity": "critical",
        "action": "Приостановить кампании, пересмотреть бюджет",
    },
    {
        "name": "Новые лиды",
        "metric": "leads",
        "condition": "growth",
        "threshold_percent": 25,
        "window": "7 дней",
        "severity": "info",
        "action": "Ускорить обработку, подключить nurture-цепочку",
    },
]

NOTIFICATION_CHANNELS: list[dict[str, str | bool]] = [
    {
        "channel": "telegram",
        "name": "Telegram-бот",
        "description": "Мгновенные уведомления в личный чат",
        "enabled": True,
        "for_severity": "all",
    },
    {
        "channel": "email",
        "name": "Email-дайджест",
        "description": "Ежедневная/еженедельная сводка на почту",
        "enabled": True,
        "for_severity": "medium, high, critical",
    },
    {
        "channel": "push",
        "name": "Push-уведомления",
        "description": "Браузерные пуши для критических алертов",
        "enabled": False,
        "for_severity": "high, critical",
    },
]

MILESTONES: list[dict[str, str | int]] = [
    {
        "name": "Первые 100 подписчиков",
        "metric": "followers",
        "target": 100,
        "message": "Поздравляем! Первая сотня подписчиков! 🎉",
        "reward": "Пост-благодарность + розыгрыш",
    },
    {
        "name": "1000 подписчиков",
        "metric": "followers",
        "target": 1000,
        "message": "1К подписчиков! Вы в игре! 🚀",
        "reward": "Эксклюзивный контент для подписчиков",
    },
    {
        "name": "Первая продажа курса",
        "metric": "course_sales",
        "target": 1,
        "message": "Первая продажа! Воронка работает! 💰",
        "reward": "Кейс-стади для соцсетей",
    },
    {
        "name": "10 продаж курса",
        "metric": "course_sales",
        "target": 10,
        "message": "10 продаж! Пора масштабировать! 📈",
        "reward": "Запустить реферальную программу",
    },
    {
        "name": "Первый реферальный доход",
        "metric": "referral_revenue",
        "target": 1,
        "message": "Реферальная программа приносит доход! 🤑",
        "reward": "Расширить каталог товаров",
    },
    {
        "name": "ROI > 200%",
        "metric": "roi_percent",
        "target": 200,
        "message": "ROI превысил 200%! Отличная эффективность! 🏆",
        "reward": "Увеличить рекламный бюджет",
    },
]

DEADLINE_TEMPLATES: list[dict[str, str | int]] = [
    {
        "name": "Контент на завтра",
        "trigger": "24 часа до публикации",
        "hours_before": 24,
        "message": "Напоминание: {count} постов на завтра ожидают финализации",
        "channel": "telegram",
    },
    {
        "name": "Недельный план",
        "trigger": "Воскресенье 18:00",
        "hours_before": 0,
        "message": "Пора сгенерировать контент-план на следующую неделю",
        "channel": "telegram",
    },
    {
        "name": "Аналитический отчёт",
        "trigger": "Понедельник 10:00",
        "hours_before": 0,
        "message": "Время собрать аналитику за прошлую неделю",
        "channel": "email",
    },
    {
        "name": "A/B тест завершён",
        "trigger": "7 дней после запуска",
        "hours_before": 0,
        "message": "A/B тест «{test_name}» завершён, пора анализировать результаты",
        "channel": "telegram",
    },
]

ESCALATION_POLICIES: list[dict[str, str | int]] = [
    {
        "severity": "info",
        "first_notify": "telegram",
        "repeat_after_hours": 0,
        "escalate_to": "none",
        "description": "Информационные — однократно в Telegram",
    },
    {
        "severity": "medium",
        "first_notify": "telegram",
        "repeat_after_hours": 24,
        "escalate_to": "email",
        "description": "Средние — Telegram, через 24ч email",
    },
    {
        "severity": "high",
        "first_notify": "telegram + email",
        "repeat_after_hours": 12,
        "escalate_to": "push",
        "description": "Высокие — Telegram + email, через 12ч push",
    },
    {
        "severity": "critical",
        "first_notify": "telegram + email + push",
        "repeat_after_hours": 6,
        "escalate_to": "phone",
        "description": "Критические — все каналы, через 6ч звонок",
    },
]


@dataclass(frozen=True, slots=True)
class AlertRule:
    name: str
    metric: str
    condition: str
    threshold_percent: int
    window: str
    severity: str
    action: str


@dataclass(frozen=True, slots=True)
class NotificationChannel:
    channel: str
    name: str
    description: str
    enabled: bool
    for_severity: str


@dataclass(frozen=True, slots=True)
class Milestone:
    name: str
    metric: str
    target: int
    message: str
    reward: str


@dataclass(frozen=True, slots=True)
class DeadlineTemplate:
    name: str
    trigger: str
    hours_before: int
    message: str
    channel: str


@dataclass(frozen=True, slots=True)
class EscalationPolicy:
    severity: str
    first_notify: str
    repeat_after_hours: int
    escalate_to: str
    description: str


@dataclass(frozen=True, slots=True)
class NotificationSystem:
    alert_rules: tuple[AlertRule, ...]
    channels: tuple[NotificationChannel, ...]
    milestones: tuple[Milestone, ...]
    deadlines: tuple[DeadlineTemplate, ...]
    escalation: tuple[EscalationPolicy, ...]


def generate_notification_system() -> NotificationSystem:
    return NotificationSystem(
        alert_rules=tuple(
            AlertRule(
                name=r["name"],
                metric=r["metric"],
                condition=r["condition"],
                threshold_percent=int(r["threshold_percent"]),
                window=r["window"],
                severity=r["severity"],
                action=r["action"],
            )
            for r in ALERT_RULES
        ),
        channels=tuple(
            NotificationChannel(
                channel=c["channel"],
                name=c["name"],
                description=c["description"],
                enabled=bool(c["enabled"]),
                for_severity=c["for_severity"],
            )
            for c in NOTIFICATION_CHANNELS
        ),
        milestones=tuple(
            Milestone(
                name=m["name"],
                metric=m["metric"],
                target=int(m["target"]),
                message=m["message"],
                reward=m["reward"],
            )
            for m in MILESTONES
        ),
        deadlines=tuple(
            DeadlineTemplate(
                name=d["name"],
                trigger=d["trigger"],
                hours_before=int(d["hours_before"]),
                message=d["message"],
                channel=d["channel"],
            )
            for d in DEADLINE_TEMPLATES
        ),
        escalation=tuple(
            EscalationPolicy(
                severity=e["severity"],
                first_notify=e["first_notify"],
                repeat_after_hours=int(e["repeat_after_hours"]),
                escalate_to=e["escalate_to"],
                description=e["description"],
            )
            for e in ESCALATION_POLICIES
        ),
    )


def export_notifications_json(ns: NotificationSystem, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "alert_rules": [
            {
                "name": r.name,
                "metric": r.metric,
                "condition": r.condition,
                "threshold_percent": r.threshold_percent,
                "window": r.window,
                "severity": r.severity,
                "action": r.action,
            }
            for r in ns.alert_rules
        ],
        "channels": [
            {
                "channel": c.channel,
                "name": c.name,
                "description": c.description,
                "enabled": c.enabled,
                "for_severity": c.for_severity,
            }
            for c in ns.channels
        ],
        "milestones": [
            {
                "name": m.name,
                "metric": m.metric,
                "target": m.target,
                "message": m.message,
                "reward": m.reward,
            }
            for m in ns.milestones
        ],
        "deadlines": [
            {
                "name": d.name,
                "trigger": d.trigger,
                "hours_before": d.hours_before,
                "message": d.message,
                "channel": d.channel,
            }
            for d in ns.deadlines
        ],
        "escalation": [
            {
                "severity": e.severity,
                "first_notify": e.first_notify,
                "repeat_after_hours": e.repeat_after_hours,
                "escalate_to": e.escalate_to,
                "description": e.description,
            }
            for e in ns.escalation
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_notifications_txt(ns: NotificationSystem, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "СИСТЕМА ОПОВЕЩЕНИЙ — АЛЕРТЫ И ДЕДЛАЙНЫ",
        "=" * 60,
        "\n🚨 ПРАВИЛА АЛЕРТОВ",
        "━" * 50,
    ]
    for r in ns.alert_rules:
        lines.append(f"\n  [{r.name}] ({r.severity})")
        lines.append(f"    Метрика: {r.metric} | {r.condition} {r.threshold_percent}%")
        lines.append(f"    Окно: {r.window}")
        lines.append(f"    Действие: {r.action}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📡 КАНАЛЫ УВЕДОМЛЕНИЙ")
    lines.append("━" * 50)
    for c in ns.channels:
        status = "✅" if c.enabled else "❌"
        lines.append(f"  {status} {c.name} ({c.channel}) — {c.description}")
        lines.append(f"      Для: {c.for_severity}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🏆 ВЕХИ (MILESTONES)")
    lines.append("━" * 50)
    for m in ns.milestones:
        lines.append(f"\n  [{m.name}] → {m.metric} = {m.target}")
        lines.append(f"    {m.message}")
        lines.append(f"    Награда: {m.reward}")

    lines.append(f"\n{'━' * 50}")
    lines.append("⏰ ДЕДЛАЙНЫ")
    lines.append("━" * 50)
    for d in ns.deadlines:
        lines.append(f"\n  [{d.name}] → {d.trigger}")
        lines.append(f"    {d.message}")
        lines.append(f"    Канал: {d.channel}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📶 ПОЛИТИКА ЭСКАЛАЦИИ")
    lines.append("━" * 50)
    for e in ns.escalation:
        lines.append(f"\n  [{e.severity}] {e.description}")
        lines.append(f"    Первичный: {e.first_notify}")
        repeat = (
            f"через {e.repeat_after_hours}ч → {e.escalate_to}"
            if e.repeat_after_hours > 0
            else "без повтора"
        )
        lines.append(f"    Эскалация: {repeat}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def notification_summary(ns: NotificationSystem) -> str:
    return (
        f"Система оповещений: "
        f"{len(ns.alert_rules)} алертов, "
        f"{len(ns.channels)} каналов, "
        f"{len(ns.milestones)} вех, "
        f"{len(ns.deadlines)} дедлайнов, "
        f"{len(ns.escalation)} политик эскалации"
    )
