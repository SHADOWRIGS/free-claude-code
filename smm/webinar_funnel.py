"""Webinar funnel content generator.

Produces a complete set of messages for a webinar-based sales funnel:
invite sequence, reminder emails, replay sequence, and post-webinar sales.
Each pillar gets its own webinar topic and full message set.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

WEBINAR_TOPICS: dict[str, dict[str, str]] = {
    "Cyber Security & Ethical Hacking": {
        "title": "Как найти первый Bug Bounty за 30 дней",
        "hook": "90% начинающих делают одну и ту же ошибку. Я покажу, как её избежать.",
        "promise": "Получите пошаговый план + 3 инструмента для старта",
    },
    "Blue Team / Defensive Security": {
        "title": "SOC за 60 минут: автоматизация реагирования",
        "hook": "Ваша команда тратит 80% времени на ложные срабатывания? Есть способ лучше.",
        "promise": "Шаблон SOAR-плейбука + чеклист настройки SIEM",
    },
    "Red Team / Offensive Security": {
        "title": "Active Directory: 5 атак, которые проходят на 90% сетей",
        "hook": "Пентестеры зарабатывают $150/час. Покажу, какие навыки окупаются быстрее всего.",
        "promise": "Лаба с 5 готовыми сценариями атак + отчёт-шаблон",
    },
    "Machine Learning & AI": {
        "title": "Первая ML-модель за 45 минут (без математики)",
        "hook": "AI-инженеры — самые востребованные специалисты 2025 года. Вот с чего начать.",
        "promise": "Jupyter-ноутбук + датасет + видеоразбор решения",
    },
    "AliExpress — Гаджеты": {
        "title": "Домашняя хакерская лаба за $50: что купить на AliExpress",
        "hook": "Не переплачивайте за оборудование. Покажу проверенных продавцов.",
        "promise": "Список 10 гаджетов с прямыми ссылками + скидки",
    },
}

FUNNEL_STAGES = ("invite", "reminder", "last_chance", "replay", "sales")

STAGE_LABELS: dict[str, str] = {
    "invite": "Приглашение на вебинар",
    "reminder": "Напоминание (за 1 час)",
    "last_chance": "Последний шанс (за 10 мин)",
    "replay": "Запись вебинара",
    "sales": "Продажа после вебинара",
}

MESSAGE_TEMPLATES: dict[str, dict[str, str]] = {
    "invite": {
        "subject": "🎓 Бесплатный вебинар: {title}",
        "body": (
            "Привет!\n\n"
            "{hook}\n\n"
            "Приглашаю на бесплатный вебинар «{title}».\n\n"
            "Что вы получите:\n"
            "✅ {promise}\n"
            "✅ Ответы на ваши вопросы в прямом эфире\n"
            "✅ Бонус для участников\n\n"
            "📅 Дата: [ДАТА]\n"
            "⏰ Время: [ВРЕМЯ]\n\n"
            "👉 Записаться: [ССЫЛКА]\n\n"
            "Мест ограничено — бронируйте сейчас!"
        ),
    },
    "reminder": {
        "subject": "⏰ Через 1 час — вебинар «{title}»",
        "body": (
            "Напоминаю: через 1 час начнётся вебинар «{title}».\n\n"
            "{hook}\n\n"
            "Не забудьте:\n"
            "📌 Ссылка на трансляцию: [ССЫЛКА]\n"
            "📌 Подготовьте вопросы заранее\n\n"
            "До встречи через час! 🚀"
        ),
    },
    "last_chance": {
        "subject": "🔴 Начинаем через 10 минут!",
        "body": (
            "Вебинар «{title}» начинается через 10 минут!\n\n"
            "Подключайтесь сейчас: [ССЫЛКА]\n\n"
            "Не пропустите — {promise}"
        ),
    },
    "replay": {
        "subject": "📹 Запись вебинара «{title}» (доступ 48 часов)",
        "body": (
            "Не успели на вебинар? Запись доступна 48 часов.\n\n"
            "Что было на вебинаре:\n"
            "✅ {promise}\n"
            "✅ Разбор реальных кейсов\n"
            "✅ Ответы на вопросы участников\n\n"
            "📹 Смотреть запись: [ССЫЛКА]\n\n"
            "⚠️ Ссылка активна до [ДАТА+2]. Не откладывайте!"
        ),
    },
    "sales": {
        "subject": "🎯 Специальное предложение для участников вебинара",
        "body": (
            "Спасибо, что были на вебинаре «{title}»!\n\n"
            "Как и обещал — специальное предложение только для участников:\n\n"
            "🔥 Скидка 30% на полный курс — только 48 часов\n"
            "🎁 Бонус: {promise}\n\n"
            "Что входит в курс:\n"
            "📚 [ОПИСАНИЕ КУРСА]\n\n"
            "💰 Обычная цена: [ЦЕНА]\n"
            "💰 Ваша цена: [ЦЕНА СО СКИДКОЙ]\n\n"
            "👉 Записаться со скидкой: [ССЫЛКА]\n\n"
            "Предложение действует до [ДАТА+2]. Не упустите!"
        ),
    },
}


@dataclass(frozen=True, slots=True)
class WebinarMessage:
    pillar: str
    stage: str
    stage_label: str
    webinar_title: str
    subject: str
    body: str


def generate_webinar_funnel(
    pillar: str | None = None,
) -> list[WebinarMessage]:
    topics = (
        {pillar: WEBINAR_TOPICS[pillar]}
        if pillar and pillar in WEBINAR_TOPICS
        else WEBINAR_TOPICS
    )

    messages: list[WebinarMessage] = []
    for pil, topic in topics.items():
        for stage in FUNNEL_STAGES:
            tmpl = MESSAGE_TEMPLATES[stage]
            subject = tmpl["subject"].format(**topic)
            body = tmpl["body"].format(**topic)
            messages.append(
                WebinarMessage(
                    pillar=pil,
                    stage=stage,
                    stage_label=STAGE_LABELS[stage],
                    webinar_title=topic["title"],
                    subject=subject,
                    body=body,
                )
            )
    return messages


def export_webinar_json(messages: list[WebinarMessage], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "pillar": m.pillar,
            "stage": m.stage,
            "stage_label": m.stage_label,
            "webinar_title": m.webinar_title,
            "subject": m.subject,
            "body": m.body,
        }
        for m in messages
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_webinar_txt(messages: list[WebinarMessage], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "ВЕБИНАРНАЯ ВОРОНКА",
        "=" * 60,
    ]

    current_pillar = ""
    for m in messages:
        if m.pillar != current_pillar:
            current_pillar = m.pillar
            lines.append(f"\n{'━' * 50}")
            lines.append(f"📡 {current_pillar}")
            lines.append(f"   Вебинар: «{m.webinar_title}»")
            lines.append("━" * 50)

        lines.append(f"\n  [{m.stage_label}]")
        lines.append(f"  Тема: {m.subject}")
        lines.append("  ---")
        lines.extend(f"  {body_line}" for body_line in m.body.split("\n"))

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def webinar_summary(messages: list[WebinarMessage]) -> str:
    pillars = {m.pillar for m in messages}
    stages = {m.stage for m in messages}
    return (
        f"Вебинарная воронка: {len(messages)} писем, "
        f"{len(pillars)} направлений, {len(stages)} этапов"
    )
