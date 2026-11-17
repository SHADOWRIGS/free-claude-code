"""Funnel automation — subscriber journey from follow to purchase.

Generates structured funnel configs:
- Funnel stages with triggers and actions
- Automated message sequences per stage
- Segmentation rules
- Conversion checkpoints
- Re-engagement rules for stalled leads
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

FUNNEL_STAGES: list[dict[str, str | int]] = [
    {
        "id": "awareness",
        "name": "Осведомлённость",
        "description": "Подписчик видит контент впервые",
        "trigger": "Подписка / первый визит",
        "goal": "Привлечь внимание, вызвать интерес",
        "duration_days": 3,
    },
    {
        "id": "interest",
        "name": "Интерес",
        "description": "Подписчик активно потребляет контент",
        "trigger": "3+ взаимодействия за 7 дней",
        "goal": "Углубить знакомство с темой",
        "duration_days": 7,
    },
    {
        "id": "consideration",
        "name": "Рассмотрение",
        "description": "Подписчик изучает курсы и предложения",
        "trigger": "Клик по ссылке на курс / лид-магнит",
        "goal": "Показать ценность продукта",
        "duration_days": 5,
    },
    {
        "id": "decision",
        "name": "Решение",
        "description": "Подписчик готов к покупке",
        "trigger": "Посещение лендинга / корзина",
        "goal": "Снять последние возражения",
        "duration_days": 3,
    },
    {
        "id": "purchase",
        "name": "Покупка",
        "description": "Подписчик совершил покупку",
        "trigger": "Оплата / активация доступа",
        "goal": "Онбординг и первая ценность",
        "duration_days": 1,
    },
    {
        "id": "retention",
        "name": "Удержание",
        "description": "Клиент активно использует продукт",
        "trigger": "Завершение первого модуля",
        "goal": "Максимизировать LTV, апсейл",
        "duration_days": 30,
    },
]

AUTO_MESSAGES: list[dict[str, str]] = [
    {
        "stage": "awareness",
        "channel": "instagram_dm",
        "delay": "0ч",
        "message": "Привет! Рад видеть тебя в сообществе. Вот бесплатный гайд для старта: {lead_magnet_url}",
    },
    {
        "stage": "awareness",
        "channel": "telegram",
        "delay": "24ч",
        "message": "Знаешь, с чего начать в кибербезе? Вот 5 шагов для новичка: {blog_url}",
    },
    {
        "stage": "interest",
        "channel": "email",
        "delay": "0ч",
        "message": "Ты уже активно изучаешь наш контент! Вот подборка лучших материалов по {pillar}: {curated_url}",
    },
    {
        "stage": "interest",
        "channel": "telegram",
        "delay": "48ч",
        "message": "Хочешь проверить свои знания? Пройди мини-тест: {quiz_url}",
    },
    {
        "stage": "consideration",
        "channel": "email",
        "delay": "0ч",
        "message": "Ты смотрел курс {course_name}. Вот что говорят выпускники: {testimonials_url}",
    },
    {
        "stage": "consideration",
        "channel": "instagram_dm",
        "delay": "24ч",
        "message": "Есть вопросы по курсу? Напиши — отвечу лично!",
    },
    {
        "stage": "decision",
        "channel": "email",
        "delay": "0ч",
        "message": "Специально для тебя: скидка {discount}% на {course_name}. Код: {promo_code}",
    },
    {
        "stage": "decision",
        "channel": "telegram",
        "delay": "48ч",
        "message": "Скидка истекает через 24 часа! Не упусти: {checkout_url}",
    },
    {
        "stage": "purchase",
        "channel": "email",
        "delay": "0ч",
        "message": "Поздравляю с покупкой! Вот твой доступ: {access_url}. Начни с модуля 1.",
    },
    {
        "stage": "retention",
        "channel": "email",
        "delay": "7д",
        "message": "Ты прошёл {progress}% курса! Продолжай — впереди самое интересное.",
    },
]

SEGMENTS: list[dict[str, str]] = [
    {
        "id": "cold",
        "name": "Холодные",
        "criteria": "Подписались, но 0 взаимодействий за 14 дней",
        "action": "Серия реактивации (3 сообщения за 7 дней)",
    },
    {
        "id": "warm",
        "name": "Тёплые",
        "criteria": "3-10 взаимодействий, нет кликов по ссылкам",
        "action": "Персонализированный контент по интересам",
    },
    {
        "id": "hot",
        "name": "Горячие",
        "criteria": "Кликали по ссылкам на курсы, не купили",
        "action": "Триггерное предложение со скидкой",
    },
    {
        "id": "buyer",
        "name": "Покупатели",
        "criteria": "Совершили хотя бы 1 покупку",
        "action": "Апсейл и кросс-продажи через 14 дней",
    },
    {
        "id": "vip",
        "name": "VIP",
        "criteria": "2+ покупки или реферальный доход",
        "action": "Эксклюзивные предложения, ранний доступ",
    },
]

REENGAGEMENT_RULES: list[dict[str, str | int]] = [
    {
        "name": "Стагнация на Awareness",
        "trigger_days": 7,
        "action": "Отправить серию из 3 вовлекающих постов",
        "channel": "instagram_dm",
    },
    {
        "name": "Брошенная корзина",
        "trigger_days": 1,
        "action": "Напоминание + скидка 5%",
        "channel": "email",
    },
    {
        "name": "Пауза в обучении",
        "trigger_days": 14,
        "action": "Мотивационное письмо + бонусный контент",
        "channel": "email",
    },
    {
        "name": "Неактивный подписчик",
        "trigger_days": 30,
        "action": "Опрос: что не так? + спецпредложение",
        "channel": "telegram",
    },
]

CHECKPOINTS: list[dict[str, str]] = [
    {
        "name": "Lead Captured",
        "metric": "Контакт получен (email или TG username)",
        "conversion_target": "30% от подписчиков",
    },
    {
        "name": "Lead Qualified",
        "metric": "Определён интерес (клик по столпу)",
        "conversion_target": "50% от лидов",
    },
    {
        "name": "Sales Qualified",
        "metric": "Посетил лендинг курса",
        "conversion_target": "25% от qualified",
    },
    {
        "name": "Purchase",
        "metric": "Оплата совершена",
        "conversion_target": "5-10% от SQL",
    },
    {
        "name": "Repeat Purchase",
        "metric": "Вторая покупка / апсейл",
        "conversion_target": "20% от buyers",
    },
]


@dataclass(frozen=True, slots=True)
class FunnelStage:
    id: str
    name: str
    description: str
    trigger: str
    goal: str
    duration_days: int


@dataclass(frozen=True, slots=True)
class AutoMessage:
    stage: str
    channel: str
    delay: str
    message: str


@dataclass(frozen=True, slots=True)
class Segment:
    id: str
    name: str
    criteria: str
    action: str


@dataclass(frozen=True, slots=True)
class ReengagementRule:
    name: str
    trigger_days: int
    action: str
    channel: str


@dataclass(frozen=True, slots=True)
class Checkpoint:
    name: str
    metric: str
    conversion_target: str


@dataclass(frozen=True, slots=True)
class FunnelAutomation:
    stages: tuple[FunnelStage, ...]
    messages: tuple[AutoMessage, ...]
    segments: tuple[Segment, ...]
    reengagement: tuple[ReengagementRule, ...]
    checkpoints: tuple[Checkpoint, ...]


def generate_funnel_automation() -> FunnelAutomation:
    return FunnelAutomation(
        stages=tuple(
            FunnelStage(
                id=s["id"],
                name=s["name"],
                description=s["description"],
                trigger=s["trigger"],
                goal=s["goal"],
                duration_days=int(s["duration_days"]),
            )
            for s in FUNNEL_STAGES
        ),
        messages=tuple(
            AutoMessage(
                stage=m["stage"],
                channel=m["channel"],
                delay=m["delay"],
                message=m["message"],
            )
            for m in AUTO_MESSAGES
        ),
        segments=tuple(
            Segment(
                id=sg["id"],
                name=sg["name"],
                criteria=sg["criteria"],
                action=sg["action"],
            )
            for sg in SEGMENTS
        ),
        reengagement=tuple(
            ReengagementRule(
                name=r["name"],
                trigger_days=int(r["trigger_days"]),
                action=r["action"],
                channel=r["channel"],
            )
            for r in REENGAGEMENT_RULES
        ),
        checkpoints=tuple(
            Checkpoint(
                name=cp["name"],
                metric=cp["metric"],
                conversion_target=cp["conversion_target"],
            )
            for cp in CHECKPOINTS
        ),
    )


def export_funnel_json(fa: FunnelAutomation, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "stages": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "trigger": s.trigger,
                "goal": s.goal,
                "duration_days": s.duration_days,
            }
            for s in fa.stages
        ],
        "messages": [
            {
                "stage": m.stage,
                "channel": m.channel,
                "delay": m.delay,
                "message": m.message,
            }
            for m in fa.messages
        ],
        "segments": [
            {
                "id": sg.id,
                "name": sg.name,
                "criteria": sg.criteria,
                "action": sg.action,
            }
            for sg in fa.segments
        ],
        "reengagement": [
            {
                "name": r.name,
                "trigger_days": r.trigger_days,
                "action": r.action,
                "channel": r.channel,
            }
            for r in fa.reengagement
        ],
        "checkpoints": [
            {
                "name": cp.name,
                "metric": cp.metric,
                "conversion_target": cp.conversion_target,
            }
            for cp in fa.checkpoints
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_funnel_txt(fa: FunnelAutomation, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "АВТОМАТИЗАЦИЯ ВОРОНКИ — ОТ ПОДПИСКИ ДО ПОКУПКИ",
        "=" * 60,
        "\n📊 ЭТАПЫ ВОРОНКИ",
        "━" * 50,
    ]
    for s in fa.stages:
        lines.append(f"\n  [{s.id}] {s.name} ({s.duration_days} дней)")
        lines.append(f"    {s.description}")
        lines.append(f"    Триггер: {s.trigger}")
        lines.append(f"    Цель: {s.goal}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📨 АВТОСООБЩЕНИЯ")
    lines.append("━" * 50)
    for m in fa.messages:
        lines.append(f"\n  [{m.stage}] {m.channel} (через {m.delay})")
        lines.append(f"    {m.message}")

    lines.append(f"\n{'━' * 50}")
    lines.append("👥 СЕГМЕНТЫ")
    lines.append("━" * 50)
    for sg in fa.segments:
        lines.append(f"\n  [{sg.id}] {sg.name}")
        lines.append(f"    Критерий: {sg.criteria}")
        lines.append(f"    Действие: {sg.action}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🔄 РЕАКТИВАЦИЯ")
    lines.append("━" * 50)
    for r in fa.reengagement:
        lines.append(f"\n  {r.name} (через {r.trigger_days} дней)")
        lines.append(f"    {r.action} [{r.channel}]")

    lines.append(f"\n{'━' * 50}")
    lines.append("🎯 ЧЕКПОИНТЫ КОНВЕРСИИ")
    lines.append("━" * 50)
    for cp in fa.checkpoints:
        lines.append(f"\n  {cp.name}")
        lines.append(f"    Метрика: {cp.metric}")
        lines.append(f"    Цель: {cp.conversion_target}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def funnel_summary(fa: FunnelAutomation) -> str:
    return (
        f"Воронка: "
        f"{len(fa.stages)} этапов, "
        f"{len(fa.messages)} автосообщений, "
        f"{len(fa.segments)} сегментов, "
        f"{len(fa.reengagement)} правил реактивации, "
        f"{len(fa.checkpoints)} чекпоинтов"
    )
