"""Onboarding flow — new customer welcome and activation sequence.

Generates structured onboarding configs:
- Welcome sequence (messages per day)
- Activation milestones
- Onboarding checklist per product
- FAQ auto-responses
- Success metrics for onboarding
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

WELCOME_MESSAGES: list[dict[str, str | int]] = [
    {
        "day": 0,
        "channel": "email",
        "subject": "Добро пожаловать в ShadowRigs!",
        "body": "Привет, {name}! Ты получил доступ к {course_name}. Начни с первого модуля: {access_url}",
        "goal": "Первый вход в систему",
    },
    {
        "day": 0,
        "channel": "telegram",
        "subject": "",
        "body": "Добро пожаловать! Присоединяйся к чату учеников: {chat_url}",
        "goal": "Присоединение к сообществу",
    },
    {
        "day": 1,
        "channel": "email",
        "subject": "Как получить максимум от курса",
        "body": "3 совета для быстрого старта: 1) Пройди первый урок 2) Задай вопрос в чате 3) Скачай материалы",
        "goal": "Завершение первого урока",
    },
    {
        "day": 3,
        "channel": "email",
        "subject": "Как дела с обучением?",
        "body": "Ты уже прошёл {progress}% курса. Вот что тебя ждёт дальше: {next_module}",
        "goal": "Прогресс 10%+",
    },
    {
        "day": 7,
        "channel": "telegram",
        "subject": "",
        "body": "Прошла неделя! Если есть вопросы, пиши прямо мне. Также рекомендую посмотреть: {recommended_url}",
        "goal": "Удержание на 7 день",
    },
    {
        "day": 14,
        "channel": "email",
        "subject": "Ты в середине пути!",
        "body": "Уже {progress}% позади. Вот бонусные материалы для тебя: {bonus_url}",
        "goal": "Прогресс 50%+",
    },
    {
        "day": 30,
        "channel": "email",
        "subject": "Поздравляю с месяцем обучения!",
        "body": "Ты многого достиг! Вот твой сертификат прогресса. Также посмотри другие курсы: {upsell_url}",
        "goal": "Апсейл или сертификат",
    },
]

ACTIVATION_MILESTONES: list[dict[str, str | int]] = [
    {
        "id": "first_login",
        "name": "Первый вход",
        "target_hours": 1,
        "reward": "Приветственный бейдж",
        "critical": "yes",
    },
    {
        "id": "first_lesson",
        "name": "Первый урок пройден",
        "target_hours": 24,
        "reward": "Прогресс-бейдж 'Старт'",
        "critical": "yes",
    },
    {
        "id": "community_join",
        "name": "Присоединение к чату",
        "target_hours": 48,
        "reward": "Доступ к эксклюзивным материалам",
        "critical": "no",
    },
    {
        "id": "first_practice",
        "name": "Первое практическое задание",
        "target_hours": 72,
        "reward": "Бейдж 'Практик'",
        "critical": "yes",
    },
    {
        "id": "week_active",
        "name": "Активность 7 дней подряд",
        "target_hours": 168,
        "reward": "Скидка 10% на следующий курс",
        "critical": "no",
    },
]

PRODUCT_CHECKLISTS: list[dict[str, str | list[str]]] = [
    {
        "product": "Курсы кибербезопасности",
        "steps": [
            "Получить доступ к платформе",
            "Скачать VPN и настроить лабораторию",
            "Пройти вводный модуль",
            "Присоединиться к Telegram-чату",
            "Выполнить первое практическое задание",
            "Пройти промежуточный тест",
        ],
    },
    {
        "product": "Курс Machine Learning & AI",
        "steps": [
            "Получить доступ к платформе",
            "Установить Python + Jupyter",
            "Скачать датасеты для практики",
            "Пройти вводный модуль",
            "Запустить первый ноутбук",
            "Загрузить результат в чат",
        ],
    },
    {
        "product": "Гаджеты AliExpress",
        "steps": [
            "Перейти по реферальной ссылке",
            "Выбрать товар из подборки",
            "Оформить заказ с промокодом",
            "Поделиться распаковкой в сторис",
            "Оставить отзыв",
        ],
    },
]

FAQ_RESPONSES: list[dict[str, str]] = [
    {
        "question": "Как получить доступ к курсу?",
        "answer": "После оплаты ссылка придёт на email. Также проверь папку Спам.",
        "category": "access",
    },
    {
        "question": "Можно ли вернуть деньги?",
        "answer": "Да, в течение 14 дней с момента покупки. Напиши нам в Telegram.",
        "category": "billing",
    },
    {
        "question": "Какие системные требования?",
        "answer": "ПК с 8GB RAM, стабильный интернет. Для практики — VirtualBox или Docker.",
        "category": "technical",
    },
    {
        "question": "Есть ли сертификат?",
        "answer": "Да, после прохождения 80%+ курса выдаётся электронный сертификат.",
        "category": "certificate",
    },
    {
        "question": "Сколько времени нужно на курс?",
        "answer": "В среднем 2-3 часа в неделю. Доступ бессрочный, учись в своём темпе.",
        "category": "schedule",
    },
    {
        "question": "Как связаться с поддержкой?",
        "answer": "Telegram: {support_url}, email: support@shadowrigs.com, ответ в течение 24ч.",
        "category": "support",
    },
]

ONBOARDING_METRICS: list[dict[str, str | float]] = [
    {
        "metric": "Активация (день 1)",
        "target_pct": 70.0,
        "description": "Процент новых клиентов, вошедших в первый день",
    },
    {
        "metric": "Первый урок (день 3)",
        "target_pct": 50.0,
        "description": "Процент прошедших первый урок за 3 дня",
    },
    {
        "metric": "Удержание (день 7)",
        "target_pct": 40.0,
        "description": "Процент активных на 7 день",
    },
    {
        "metric": "Удержание (день 30)",
        "target_pct": 25.0,
        "description": "Процент активных на 30 день",
    },
    {
        "metric": "NPS (день 14)",
        "target_pct": 50.0,
        "description": "Net Promoter Score на 2 неделе",
    },
]


@dataclass(frozen=True, slots=True)
class WelcomeMessage:
    day: int
    channel: str
    subject: str
    body: str
    goal: str


@dataclass(frozen=True, slots=True)
class ActivationMilestone:
    id: str
    name: str
    target_hours: int
    reward: str
    critical: str


@dataclass(frozen=True, slots=True)
class ProductChecklist:
    product: str
    steps: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FAQResponse:
    question: str
    answer: str
    category: str


@dataclass(frozen=True, slots=True)
class OnboardingMetric:
    metric: str
    target_pct: float
    description: str


@dataclass(frozen=True, slots=True)
class OnboardingFlow:
    welcome_messages: tuple[WelcomeMessage, ...]
    milestones: tuple[ActivationMilestone, ...]
    checklists: tuple[ProductChecklist, ...]
    faq: tuple[FAQResponse, ...]
    metrics: tuple[OnboardingMetric, ...]


def generate_onboarding_flow() -> OnboardingFlow:
    return OnboardingFlow(
        welcome_messages=tuple(
            WelcomeMessage(
                day=int(m["day"]),
                channel=m["channel"],
                subject=m["subject"],
                body=m["body"],
                goal=m["goal"],
            )
            for m in WELCOME_MESSAGES
        ),
        milestones=tuple(
            ActivationMilestone(
                id=ml["id"],
                name=ml["name"],
                target_hours=int(ml["target_hours"]),
                reward=ml["reward"],
                critical=ml["critical"],
            )
            for ml in ACTIVATION_MILESTONES
        ),
        checklists=tuple(
            ProductChecklist(
                product=cl["product"],
                steps=tuple(cl["steps"]),
            )
            for cl in PRODUCT_CHECKLISTS
        ),
        faq=tuple(
            FAQResponse(
                question=f["question"],
                answer=f["answer"],
                category=f["category"],
            )
            for f in FAQ_RESPONSES
        ),
        metrics=tuple(
            OnboardingMetric(
                metric=om["metric"],
                target_pct=float(om["target_pct"]),
                description=om["description"],
            )
            for om in ONBOARDING_METRICS
        ),
    )


def export_onboarding_json(ob: OnboardingFlow, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "welcome_messages": [
            {
                "day": m.day,
                "channel": m.channel,
                "subject": m.subject,
                "body": m.body,
                "goal": m.goal,
            }
            for m in ob.welcome_messages
        ],
        "milestones": [
            {
                "id": ml.id,
                "name": ml.name,
                "target_hours": ml.target_hours,
                "reward": ml.reward,
                "critical": ml.critical,
            }
            for ml in ob.milestones
        ],
        "checklists": [
            {"product": cl.product, "steps": list(cl.steps)} for cl in ob.checklists
        ],
        "faq": [
            {
                "question": f.question,
                "answer": f.answer,
                "category": f.category,
            }
            for f in ob.faq
        ],
        "metrics": [
            {
                "metric": om.metric,
                "target_pct": om.target_pct,
                "description": om.description,
            }
            for om in ob.metrics
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_onboarding_txt(ob: OnboardingFlow, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "ОНБОРДИНГ — АКТИВАЦИЯ НОВОГО КЛИЕНТА",
        "=" * 60,
        "\n📨 ПРИВЕТСТВЕННАЯ СЕРИЯ",
        "━" * 50,
    ]
    for m in ob.welcome_messages:
        lines.append(f"\n  День {m.day} [{m.channel}]")
        if m.subject:
            lines.append(f"    Тема: {m.subject}")
        lines.append(f"    {m.body}")
        lines.append(f"    Цель: {m.goal}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🎯 ВЕХИ АКТИВАЦИИ")
    lines.append("━" * 50)
    for ml in ob.milestones:
        crit = " [КРИТИЧНО]" if ml.critical == "yes" else ""
        lines.append(f"\n  [{ml.id}] {ml.name} (до {ml.target_hours}ч){crit}")
        lines.append(f"    Награда: {ml.reward}")

    lines.append(f"\n{'━' * 50}")
    lines.append("✅ ЧЕКЛИСТЫ ПО ПРОДУКТАМ")
    lines.append("━" * 50)
    for cl in ob.checklists:
        lines.append(f"\n  [{cl.product}]")
        for i, step in enumerate(cl.steps, 1):
            lines.append(f"    {i}. {step}")

    lines.append(f"\n{'━' * 50}")
    lines.append("❓ FAQ")
    lines.append("━" * 50)
    for fq in ob.faq:
        lines.append(f"\n  В: {fq.question}")
        lines.append(f"  О: {fq.answer}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📊 МЕТРИКИ ОНБОРДИНГА")
    lines.append("━" * 50)
    lines.extend(
        f"  {om.metric}: цель {om.target_pct}% — {om.description}"
        for om in ob.metrics
    )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def onboarding_summary(ob: OnboardingFlow) -> str:
    return (
        f"Онбординг: "
        f"{len(ob.welcome_messages)} сообщений, "
        f"{len(ob.milestones)} вех активации, "
        f"{len(ob.checklists)} чеклистов, "
        f"{len(ob.faq)} FAQ, "
        f"{len(ob.metrics)} метрик"
    )
