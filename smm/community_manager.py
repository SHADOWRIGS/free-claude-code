"""Community management templates — reply scripts and engagement rules.

Generates structured response templates for:
- Comment replies (positive, negative, questions, spam)
- DM auto-responses
- Engagement scripts for live streams
- Moderation rules
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

REPLY_CATEGORIES: tuple[str, ...] = (
    "positive",
    "question",
    "negative",
    "spam",
    "purchase_intent",
)

REPLY_TEMPLATES: dict[str, list[str]] = {
    "positive": [
        "Спасибо за тёплые слова! 🙏 Рады, что полезно!",
        "Круто, что тебе зашло! Поделись с друзьями — будем признательны 🔥",
        "Спасибо! Если есть вопросы — пиши, поможем 💪",
    ],
    "question": [
        "Отличный вопрос! Ответ: {answer}. Подробнее в нашем курсе 👉 /courses",
        "Привет! По этой теме у нас есть бесплатный материал — напиши /free 📥",
        "Хороший вопрос! Мы разобрали это в последнем видео — ссылка в био 🔗",
    ],
    "negative": [
        "Спасибо за обратную связь! Подскажи, что именно можно улучшить? 🤔",
        "Жаль, что не оправдали ожиданий. Напиши в ЛС — разберёмся вместе 🤝",
        "Учтём! Мы постоянно улучшаем контент. Конструктив всегда приветствуется 👍",
    ],
    "spam": [
        "[Скрыть комментарий — нарушение правил сообщества]",
        "[Заблокировать пользователя — повторный спам]",
    ],
    "purchase_intent": [
        "Рады интересу! Все детали здесь 👉 /courses. Если нужна помощь — пиши! 🎯",
        "Отличный выбор! Сейчас действует скидка для подписчиков 💰 Подробнее в ЛС",
        "Готов начать? Напиши /start в нашем боте — поможем с выбором курса 🤖",
    ],
}

DM_AUTO_RESPONSES: dict[str, str] = {
    "greeting": (
        "Привет! 👋 Спасибо, что написал(а)!\n"
        "Я автоматический ассистент ShadowRigs.\n\n"
        "Чем могу помочь?\n"
        "📚 Курсы — напиши «курсы»\n"
        "🎁 Бесплатные материалы — «бесплатно»\n"
        "🔧 Гаджеты — «гаджеты»\n"
        "💬 Связь с ментором — «ментор»"
    ),
    "courses": (
        "Наши курсы:\n\n"
        "🔒 Cyber Security & Ethical Hacking\n"
        "🛡 Blue Team / Defensive Security\n"
        "⚔️ Red Team / Offensive Security\n"
        "🤖 Machine Learning & AI\n\n"
        "Напиши название курса для подробностей!"
    ),
    "free": (
        "Бесплатные материалы:\n\n"
        "📖 Чеклист кибербезопасности\n"
        "🗺 Roadmap пентестера\n"
        "🧠 Шпаргалка ML-алгоритмов\n\n"
        "Какой материал отправить?"
    ),
    "mentor": (
        "Свяжись с нашими менторами:\n\n"
        "📩 Telegram: [ССЫЛКА]\n"
        "📧 Email: support@shadowrigs.com\n\n"
        "Ответим в течение 24 часов!"
    ),
}

LIVE_STREAM_SCRIPTS: list[dict[str, str]] = [
    {
        "moment": "Начало стрима",
        "script": (
            "Привет всем! 🔴 Мы в эфире!\n"
            "Подпишись и нажми колокольчик, чтобы не пропустить.\n"
            "Сегодня разбираем: {topic}\n"
            "Задавайте вопросы в чате — ответим на все!"
        ),
    },
    {
        "moment": "Середина стрима",
        "script": (
            "Напоминание: если полезно — ставьте 👍 и делитесь ссылкой!\n"
            "Бесплатные материалы по теме — ссылка в описании 📥\n"
            "Вопросы? Пишите в чат!"
        ),
    },
    {
        "moment": "Конец стрима",
        "script": (
            "Спасибо, что были с нами! 🙏\n"
            "Подводим итоги:\n"
            "1. {takeaway_1}\n"
            "2. {takeaway_2}\n"
            "3. {takeaway_3}\n\n"
            "Подпишись, чтобы не пропустить следующий эфир!\n"
            "Курсы и бесплатные материалы — ссылки в описании 🔗"
        ),
    },
]

MODERATION_RULES: list[dict[str, str]] = [
    {
        "rule": "Спам-фильтр",
        "action": "Скрыть комментарий",
        "trigger": "3+ ссылки, промо чужих продуктов",
    },
    {
        "rule": "Оскорбления",
        "action": "Предупреждение → бан",
        "trigger": "Нецензурная лексика, личные атаки",
    },
    {
        "rule": "Накрутка",
        "action": "Скрыть и пометить",
        "trigger": "Массовые однотипные комментарии",
    },
    {
        "rule": "Фишинг",
        "action": "Немедленный бан",
        "trigger": "Ссылки на подозрительные сайты",
    },
    {"rule": "Off-topic", "action": "Скрыть", "trigger": "Не связано с темой поста"},
]


@dataclass(frozen=True, slots=True)
class ReplyTemplate:
    category: str
    templates: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DMResponse:
    trigger: str
    message: str


@dataclass(frozen=True, slots=True)
class LiveScript:
    moment: str
    script: str


@dataclass(frozen=True, slots=True)
class ModerationRule:
    rule: str
    action: str
    trigger: str


@dataclass(frozen=True, slots=True)
class CommunityConfig:
    reply_templates: tuple[ReplyTemplate, ...]
    dm_responses: tuple[DMResponse, ...]
    live_scripts: tuple[LiveScript, ...]
    moderation_rules: tuple[ModerationRule, ...]


def generate_community_config() -> CommunityConfig:
    return CommunityConfig(
        reply_templates=tuple(
            ReplyTemplate(category=cat, templates=tuple(tmpls))
            for cat, tmpls in REPLY_TEMPLATES.items()
        ),
        dm_responses=tuple(
            DMResponse(trigger=k, message=v) for k, v in DM_AUTO_RESPONSES.items()
        ),
        live_scripts=tuple(
            LiveScript(moment=s["moment"], script=s["script"])
            for s in LIVE_STREAM_SCRIPTS
        ),
        moderation_rules=tuple(
            ModerationRule(rule=r["rule"], action=r["action"], trigger=r["trigger"])
            for r in MODERATION_RULES
        ),
    )


def export_community_json(config: CommunityConfig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "reply_templates": [
            {"category": r.category, "templates": list(r.templates)}
            for r in config.reply_templates
        ],
        "dm_responses": [
            {"trigger": d.trigger, "message": d.message} for d in config.dm_responses
        ],
        "live_scripts": [
            {"moment": s.moment, "script": s.script} for s in config.live_scripts
        ],
        "moderation_rules": [
            {"rule": m.rule, "action": m.action, "trigger": m.trigger}
            for m in config.moderation_rules
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_community_txt(config: CommunityConfig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "КОММЬЮНИТИ-МЕНЕДЖМЕНТ — ШАБЛОНЫ И ПРАВИЛА",
        "=" * 60,
        "\n💬 ШАБЛОНЫ ОТВЕТОВ",
        "━" * 50,
    ]
    for r in config.reply_templates:
        lines.append(f"\n  [{r.category}]")
        for i, t in enumerate(r.templates, 1):
            lines.append(f"    {i}. {t}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📩 АВТО-ОТВЕТЫ В ЛС")
    lines.append("━" * 50)
    for d in config.dm_responses:
        lines.append(f"\n  Триггер: «{d.trigger}»")
        lines.extend(f"  {line}" for line in d.message.split("\n"))

    lines.append(f"\n{'━' * 50}")
    lines.append("🔴 СКРИПТЫ ДЛЯ СТРИМОВ")
    lines.append("━" * 50)
    for s in config.live_scripts:
        lines.append(f"\n  [{s.moment}]")
        lines.extend(f"  {line}" for line in s.script.split("\n"))

    lines.append(f"\n{'━' * 50}")
    lines.append("🛡 ПРАВИЛА МОДЕРАЦИИ")
    lines.append("━" * 50)
    for m in config.moderation_rules:
        lines.append(f"\n  Правило: {m.rule}")
        lines.append(f"  Действие: {m.action}")
        lines.append(f"  Триггер: {m.trigger}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def community_summary(config: CommunityConfig) -> str:
    total_templates = sum(len(r.templates) for r in config.reply_templates)
    return (
        f"Коммьюнити: {len(config.reply_templates)} категорий ответов "
        f"({total_templates} шаблонов), "
        f"{len(config.dm_responses)} авто-ответов, "
        f"{len(config.live_scripts)} скриптов стримов, "
        f"{len(config.moderation_rules)} правил модерации"
    )
