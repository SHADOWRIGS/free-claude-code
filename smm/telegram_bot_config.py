"""Telegram sales bot configuration and message templates.

Generates structured config for a Telegram bot that handles:
- Welcome messages for new subscribers
- Lead magnet delivery
- Course info on demand
- FAQ auto-replies
- Notification templates for new leads / purchases
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

BOT_COMMANDS: list[dict[str, str]] = [
    {"command": "/start", "description": "Начать — получить приветствие и меню"},
    {"command": "/courses", "description": "Список курсов и цены"},
    {"command": "/free", "description": "Бесплатные материалы (лид-магниты)"},
    {"command": "/gadgets", "description": "Подборка гаджетов с AliExpress"},
    {"command": "/faq", "description": "Часто задаваемые вопросы"},
    {"command": "/contact", "description": "Связаться с менторами"},
]

WELCOME_MESSAGE = (
    "Привет! 👋\n\n"
    "Я бот ShadowRigs — помогу выбрать курс и получить бесплатные материалы.\n\n"
    "Вот что я умею:\n"
    "📚 /courses — посмотреть курсы\n"
    "🎁 /free — скачать бесплатные материалы\n"
    "🔧 /gadgets — гаджеты с AliExpress\n"
    "❓ /faq — частые вопросы\n"
    "📩 /contact — написать ментору\n\n"
    "Выбери команду или задай вопрос!"
)

COURSE_MESSAGES: dict[str, str] = {
    "Cyber Security & Ethical Hacking": (
        "🔒 *Cyber Security & Ethical Hacking*\n\n"
        "Научись находить уязвимости и зарабатывать на Bug Bounty.\n\n"
        "✅ От нуля до первого баг-баунти\n"
        "✅ Практика на реальных лабах\n"
        "✅ Менторская поддержка\n\n"
        "💰 Цена: [ЦЕНА]\n"
        "👉 Подробнее: [ССЫЛКА]"
    ),
    "Blue Team / Defensive Security": (
        "🛡 *Blue Team / Defensive Security*\n\n"
        "Строй защиту: SIEM, SOAR, Incident Response.\n\n"
        "✅ Настройка SOC с нуля\n"
        "✅ Автоматизация реагирования\n"
        "✅ Реальные кейсы инцидентов\n\n"
        "💰 Цена: [ЦЕНА]\n"
        "👉 Подробнее: [ССЫЛКА]"
    ),
    "Red Team / Offensive Security": (
        "⚔️ *Red Team / Offensive Security*\n\n"
        "Атакуй как профи: AD, pivoting, evasion.\n\n"
        "✅ Реальные сценарии пентеста\n"
        "✅ Подготовка к OSCP\n"
        "✅ Лабы Active Directory\n\n"
        "💰 Цена: [ЦЕНА]\n"
        "👉 Подробнее: [ССЫЛКА]"
    ),
    "Machine Learning & AI": (
        "🤖 *Machine Learning & AI*\n\n"
        "Первая ML-модель за 45 минут, портфолио за месяц.\n\n"
        "✅ Python + библиотеки ML\n"
        "✅ 8 проектов для портфолио\n"
        "✅ Помощь с трудоустройством\n\n"
        "💰 Цена: [ЦЕНА]\n"
        "👉 Подробнее: [ССЫЛКА]"
    ),
}

GADGETS_MESSAGE = (
    "🔧 *Гаджеты для хакеров с AliExpress*\n\n"
    "Проверенные продавцы, честные обзоры:\n\n"
    "📡 WiFi-адаптеры для пентеста\n"
    "🔌 USB Rubber Ducky аналоги\n"
    "📻 SDR-приёмники\n"
    "🖥 Мини-серверы для лабораторий\n"
    "🔋 Powerbank'и и кабели\n\n"
    "👉 Полный каталог: [ССЫЛКА]"
)

FAQ_ITEMS: list[dict[str, str]] = [
    {
        "question": "Сколько времени занимает курс?",
        "answer": "В среднем 2-3 месяца при занятиях 1-2 часа в день. Доступ пожизненный.",
    },
    {
        "question": "Нужен ли опыт?",
        "answer": "Нет! Курсы рассчитаны на новичков. Начинаем с самых основ.",
    },
    {
        "question": "Есть ли гарантия?",
        "answer": "Да, 30-дневная гарантия возврата. Если не подойдёт — вернём деньги.",
    },
    {
        "question": "Как проходят занятия?",
        "answer": "Видеоуроки + практические задания + лабораторные работы. Всё онлайн.",
    },
    {
        "question": "Будет ли сертификат?",
        "answer": "Да, после прохождения курса выдаётся сертификат.",
    },
    {
        "question": "Можно ли оплатить частями?",
        "answer": "Да, доступна рассрочка на 3 и 6 месяцев.",
    },
]

NOTIFICATION_TEMPLATES: dict[str, str] = {
    "new_lead": (
        "🔔 Новый лид!\n"
        "Имя: {name}\n"
        "Источник: {source}\n"
        "Интерес: {interest}\n"
        "Время: {timestamp}"
    ),
    "new_purchase": (
        "💰 Новая покупка!\n"
        "Курс: {course}\n"
        "Сумма: ${amount}\n"
        "Email: {email}\n"
        "Время: {timestamp}"
    ),
    "lead_magnet_download": (
        "📥 Скачан лид-магнит\n"
        "Материал: {magnet_name}\n"
        "Email: {email}\n"
        "Источник: {source}"
    ),
}


@dataclass(frozen=True, slots=True)
class BotCommand:
    command: str
    description: str


@dataclass(frozen=True, slots=True)
class FAQItem:
    question: str
    answer: str


@dataclass(frozen=True, slots=True)
class TelegramBotConfig:
    commands: tuple[BotCommand, ...]
    welcome_message: str
    course_messages: dict[str, str]
    gadgets_message: str
    faq_items: tuple[FAQItem, ...]
    notification_templates: dict[str, str]


def generate_bot_config() -> TelegramBotConfig:
    return TelegramBotConfig(
        commands=tuple(
            BotCommand(command=c["command"], description=c["description"])
            for c in BOT_COMMANDS
        ),
        welcome_message=WELCOME_MESSAGE,
        course_messages=dict(COURSE_MESSAGES),
        gadgets_message=GADGETS_MESSAGE,
        faq_items=tuple(
            FAQItem(question=f["question"], answer=f["answer"]) for f in FAQ_ITEMS
        ),
        notification_templates=dict(NOTIFICATION_TEMPLATES),
    )


def export_bot_config_json(config: TelegramBotConfig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "commands": [
            {"command": c.command, "description": c.description}
            for c in config.commands
        ],
        "welcome_message": config.welcome_message,
        "course_messages": config.course_messages,
        "gadgets_message": config.gadgets_message,
        "faq": [{"question": f.question, "answer": f.answer} for f in config.faq_items],
        "notification_templates": config.notification_templates,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_bot_config_txt(config: TelegramBotConfig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "TELEGRAM-БОТ — КОНФИГУРАЦИЯ",
        "=" * 60,
        "\n📋 КОМАНДЫ БОТА",
        "━" * 50,
    ]
    lines.extend(f"  {c.command} — {c.description}" for c in config.commands)

    lines.append(f"\n{'━' * 50}")
    lines.append("👋 ПРИВЕТСТВИЕ")
    lines.append("━" * 50)
    lines.append(config.welcome_message)

    lines.append(f"\n{'━' * 50}")
    lines.append("📚 СООБЩЕНИЯ КУРСОВ")
    lines.append("━" * 50)
    for pillar, msg in config.course_messages.items():
        lines.append(f"\n  [{pillar}]")
        lines.append(msg)

    lines.append(f"\n{'━' * 50}")
    lines.append("❓ FAQ")
    lines.append("━" * 50)
    for f in config.faq_items:
        lines.append(f"\n  В: {f.question}")
        lines.append(f"  О: {f.answer}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def bot_config_summary(config: TelegramBotConfig) -> str:
    return (
        f"Telegram-бот: {len(config.commands)} команд, "
        f"{len(config.course_messages)} курсов, "
        f"{len(config.faq_items)} FAQ, "
        f"{len(config.notification_templates)} уведомлений"
    )
