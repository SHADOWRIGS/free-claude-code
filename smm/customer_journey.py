"""Customer journey map — touchpoints from discovery to advocacy.

Generates structured journey configs:
- Journey stages with emotions and actions
- Touchpoint catalog per stage
- Pain points and opportunities
- Channel matrix (stage x channel)
- Success metrics per stage
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

JOURNEY_STAGES: list[dict[str, str]] = [
    {
        "stage": "Осведомлённость",
        "emotion": "Любопытство",
        "goal": "Узнать о ShadowRigs и продуктах",
        "user_thought": "Хочу научиться кибербезопасности, но не знаю с чего начать",
        "duration": "1-7 дней",
    },
    {
        "stage": "Интерес",
        "emotion": "Вдохновение",
        "goal": "Изучить контент и оценить экспертность",
        "user_thought": "Этот контент полезный, хочу узнать больше",
        "duration": "3-14 дней",
    },
    {
        "stage": "Рассмотрение",
        "emotion": "Сравнение",
        "goal": "Сравнить с конкурентами, оценить цену",
        "user_thought": "Стоит ли покупать именно этот курс?",
        "duration": "3-7 дней",
    },
    {
        "stage": "Решение",
        "emotion": "Волнение",
        "goal": "Принять решение о покупке",
        "user_thought": "Готов купить, но нужен последний аргумент",
        "duration": "1-3 дня",
    },
    {
        "stage": "Покупка",
        "emotion": "Ожидание",
        "goal": "Оформить заказ и получить доступ",
        "user_thought": "Надеюсь, всё пройдёт гладко",
        "duration": "1 день",
    },
    {
        "stage": "Онбординг",
        "emotion": "Энтузиазм",
        "goal": "Начать обучение, получить первый результат",
        "user_thought": "Хочу сразу применить знания на практике",
        "duration": "7-14 дней",
    },
    {
        "stage": "Удержание",
        "emotion": "Прогресс",
        "goal": "Пройти курс, получить навыки",
        "user_thought": "Вижу прогресс, хочу продолжать",
        "duration": "30-90 дней",
    },
    {
        "stage": "Адвокация",
        "emotion": "Гордость",
        "goal": "Рекомендовать другим, стать амбассадором",
        "user_thought": "Это реально помогло, расскажу друзьям",
        "duration": "бессрочно",
    },
]

TOUCHPOINTS: list[dict[str, str]] = [
    {
        "stage": "Осведомлённость",
        "touchpoint": "Reels/TikTok с хуком",
        "channel": "Instagram, TikTok",
        "content_type": "Вирусный контент, лайфхаки",
    },
    {
        "stage": "Осведомлённость",
        "touchpoint": "YouTube-видео (обзор темы)",
        "channel": "YouTube",
        "content_type": "Обучающее видео 10-15 мин",
    },
    {
        "stage": "Интерес",
        "touchpoint": "Карусель с полезным контентом",
        "channel": "Instagram",
        "content_type": "5-7 слайдов, чеклисты",
    },
    {
        "stage": "Интерес",
        "touchpoint": "Лид-магнит (PDF-гайд)",
        "channel": "Лендинг, email",
        "content_type": "Бесплатный материал за email",
    },
    {
        "stage": "Рассмотрение",
        "touchpoint": "Вебинар или мастер-класс",
        "channel": "Zoom, YouTube Live",
        "content_type": "Демо курса, Q&A",
    },
    {
        "stage": "Рассмотрение",
        "touchpoint": "Отзывы и кейсы студентов",
        "channel": "Лендинг, Instagram",
        "content_type": "Social proof",
    },
    {
        "stage": "Решение",
        "touchpoint": "Email-серия с оффером",
        "channel": "Email",
        "content_type": "Скидка, дедлайн, бонусы",
    },
    {
        "stage": "Решение",
        "touchpoint": "Ретаргетинг (реклама)",
        "channel": "Instagram, Facebook Ads",
        "content_type": "Напоминание, отзывы",
    },
    {
        "stage": "Покупка",
        "touchpoint": "Страница оплаты",
        "channel": "Лендинг",
        "content_type": "Простая форма, гарантия возврата",
    },
    {
        "stage": "Онбординг",
        "touchpoint": "Welcome email + Telegram-чат",
        "channel": "Email, Telegram",
        "content_type": "Инструкции, чеклист старта",
    },
    {
        "stage": "Удержание",
        "touchpoint": "Еженедельные напоминания",
        "channel": "Email, Telegram",
        "content_type": "Прогресс, мотивация, бонусы",
    },
    {
        "stage": "Адвокация",
        "touchpoint": "Реферальная программа",
        "channel": "Лендинг, email",
        "content_type": "Комиссия, бонусы за рекомендации",
    },
]

PAIN_POINTS: list[dict[str, str]] = [
    {
        "stage": "Осведомлённость",
        "pain": "Слишком много вариантов обучения",
        "opportunity": "Выделиться уникальным позиционированием (практика + гаджеты)",
    },
    {
        "stage": "Рассмотрение",
        "pain": "Страх потратить деньги впустую",
        "opportunity": "14-дневная гарантия возврата, бесплатный вебинар",
    },
    {
        "stage": "Покупка",
        "pain": "Сложный процесс оплаты",
        "opportunity": "Одна кнопка, несколько способов оплаты",
    },
    {
        "stage": "Онбординг",
        "pain": "Не знает с чего начать",
        "opportunity": "Пошаговый чеклист, mentor-бот",
    },
    {
        "stage": "Удержание",
        "pain": "Потеря мотивации на середине",
        "opportunity": "Геймификация, промежуточные сертификаты",
    },
]

CHANNEL_MATRIX: list[dict[str, str]] = [
    {
        "stage": "Осведомлённость",
        "instagram": "Reels",
        "tiktok": "Видео",
        "youtube": "Shorts",
        "email": "—",
        "telegram": "—",
    },
    {
        "stage": "Интерес",
        "instagram": "Карусели",
        "tiktok": "Серии",
        "youtube": "Туториалы",
        "email": "Лид-магнит",
        "telegram": "—",
    },
    {
        "stage": "Рассмотрение",
        "instagram": "Сторис",
        "tiktok": "Отзывы",
        "youtube": "Вебинар",
        "email": "Nurture",
        "telegram": "Чат",
    },
    {
        "stage": "Решение",
        "instagram": "Реклама",
        "tiktok": "—",
        "youtube": "—",
        "email": "Оффер",
        "telegram": "ЛС",
    },
    {
        "stage": "Покупка",
        "instagram": "—",
        "tiktok": "—",
        "youtube": "—",
        "email": "Чек",
        "telegram": "Доступ",
    },
    {
        "stage": "Онбординг",
        "instagram": "—",
        "tiktok": "—",
        "youtube": "—",
        "email": "Welcome",
        "telegram": "Чат учеников",
    },
    {
        "stage": "Удержание",
        "instagram": "UGC",
        "tiktok": "—",
        "youtube": "Доп. уроки",
        "email": "Прогресс",
        "telegram": "Поддержка",
    },
    {
        "stage": "Адвокация",
        "instagram": "Репосты",
        "tiktok": "Коллабы",
        "youtube": "Интервью",
        "email": "Реферал",
        "telegram": "Амбассадор",
    },
]

STAGE_METRICS: list[dict[str, str]] = [
    {
        "stage": "Осведомлённость",
        "metric": "Охват, показы, новые подписчики",
        "target": "50K охват/мес",
    },
    {
        "stage": "Интерес",
        "metric": "Сохранения, время просмотра, подписки email",
        "target": "500 email/мес",
    },
    {
        "stage": "Рассмотрение",
        "metric": "Регистрации на вебинар, просмотры лендинга",
        "target": "200 регистраций/мес",
    },
    {
        "stage": "Решение",
        "metric": "Клики по CTA, добавления в корзину",
        "target": "50 кликов/нед",
    },
    {
        "stage": "Покупка",
        "metric": "Конверсия, средний чек, количество продаж",
        "target": "CR 3%+",
    },
    {
        "stage": "Онбординг",
        "metric": "Активация день 1, первый урок за 3 дня",
        "target": "70% активация",
    },
    {
        "stage": "Удержание",
        "metric": "Прогресс курса, активность день 30",
        "target": "25% retention",
    },
    {
        "stage": "Адвокация",
        "metric": "NPS, реферальные продажи, отзывы",
        "target": "NPS 50+",
    },
]


@dataclass(frozen=True, slots=True)
class JourneyStage:
    stage: str
    emotion: str
    goal: str
    user_thought: str
    duration: str


@dataclass(frozen=True, slots=True)
class Touchpoint:
    stage: str
    touchpoint: str
    channel: str
    content_type: str


@dataclass(frozen=True, slots=True)
class PainPoint:
    stage: str
    pain: str
    opportunity: str


@dataclass(frozen=True, slots=True)
class ChannelEntry:
    stage: str
    instagram: str
    tiktok: str
    youtube: str
    email: str
    telegram: str


@dataclass(frozen=True, slots=True)
class StageMetric:
    stage: str
    metric: str
    target: str


@dataclass(frozen=True, slots=True)
class CustomerJourney:
    stages: tuple[JourneyStage, ...]
    touchpoints: tuple[Touchpoint, ...]
    pain_points: tuple[PainPoint, ...]
    channel_matrix: tuple[ChannelEntry, ...]
    stage_metrics: tuple[StageMetric, ...]


def generate_customer_journey() -> CustomerJourney:
    return CustomerJourney(
        stages=tuple(
            JourneyStage(
                stage=s["stage"],
                emotion=s["emotion"],
                goal=s["goal"],
                user_thought=s["user_thought"],
                duration=s["duration"],
            )
            for s in JOURNEY_STAGES
        ),
        touchpoints=tuple(
            Touchpoint(
                stage=tp["stage"],
                touchpoint=tp["touchpoint"],
                channel=tp["channel"],
                content_type=tp["content_type"],
            )
            for tp in TOUCHPOINTS
        ),
        pain_points=tuple(
            PainPoint(
                stage=pp["stage"],
                pain=pp["pain"],
                opportunity=pp["opportunity"],
            )
            for pp in PAIN_POINTS
        ),
        channel_matrix=tuple(
            ChannelEntry(
                stage=cm["stage"],
                instagram=cm["instagram"],
                tiktok=cm["tiktok"],
                youtube=cm["youtube"],
                email=cm["email"],
                telegram=cm["telegram"],
            )
            for cm in CHANNEL_MATRIX
        ),
        stage_metrics=tuple(
            StageMetric(
                stage=sm["stage"],
                metric=sm["metric"],
                target=sm["target"],
            )
            for sm in STAGE_METRICS
        ),
    )


def export_journey_json(cj: CustomerJourney, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "stages": [
            {
                "stage": s.stage,
                "emotion": s.emotion,
                "goal": s.goal,
                "user_thought": s.user_thought,
                "duration": s.duration,
            }
            for s in cj.stages
        ],
        "touchpoints": [
            {
                "stage": tp.stage,
                "touchpoint": tp.touchpoint,
                "channel": tp.channel,
                "content_type": tp.content_type,
            }
            for tp in cj.touchpoints
        ],
        "pain_points": [
            {"stage": pp.stage, "pain": pp.pain, "opportunity": pp.opportunity}
            for pp in cj.pain_points
        ],
        "channel_matrix": [
            {
                "stage": ce.stage,
                "instagram": ce.instagram,
                "tiktok": ce.tiktok,
                "youtube": ce.youtube,
                "email": ce.email,
                "telegram": ce.telegram,
            }
            for ce in cj.channel_matrix
        ],
        "stage_metrics": [
            {"stage": sm.stage, "metric": sm.metric, "target": sm.target}
            for sm in cj.stage_metrics
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_journey_txt(cj: CustomerJourney, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "КАРТА КЛИЕНТСКОГО ПУТИ (CUSTOMER JOURNEY MAP)",
        "=" * 60,
        "\n🗺 ЭТАПЫ ПУТИ",
        "━" * 50,
    ]
    for s in cj.stages:
        lines.append(f"\n  [{s.stage}] ({s.duration})")
        lines.append(f"    Эмоция: {s.emotion}")
        lines.append(f"    Цель: {s.goal}")
        lines.append(f'    Мысль клиента: "{s.user_thought}"')

    lines.append(f"\n{'━' * 50}")
    lines.append("📍 ТОЧКИ КОНТАКТА")
    lines.append("━" * 50)
    lines.extend(
        f"  [{tp.stage}] {tp.touchpoint} ({tp.channel})"
        for tp in cj.touchpoints
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("⚠ БОЛЕВЫЕ ТОЧКИ И ВОЗМОЖНОСТИ")
    lines.append("━" * 50)
    for pp in cj.pain_points:
        lines.append(f"\n  [{pp.stage}]")
        lines.append(f"    Боль: {pp.pain}")
        lines.append(f"    Возможность: {pp.opportunity}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📊 МЕТРИКИ ПО ЭТАПАМ")
    lines.append("━" * 50)
    lines.extend(
        f"  [{sm.stage}] {sm.metric} | цель: {sm.target}" for sm in cj.stage_metrics
    )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def journey_summary(cj: CustomerJourney) -> str:
    return (
        f"Customer Journey: "
        f"{len(cj.stages)} этапов, "
        f"{len(cj.touchpoints)} точек контакта, "
        f"{len(cj.pain_points)} болевых точек, "
        f"{len(cj.channel_matrix)} строк канал-матрицы, "
        f"{len(cj.stage_metrics)} метрик"
    )
