"""Testimonial collector — structured configs for gathering and displaying reviews.

Generates:
- Review request templates per stage
- Testimonial categories and formats
- Display widgets for landing/social
- Incentive programs for reviews
- Moderation rules
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

REQUEST_TEMPLATES: list[dict[str, str | int]] = [
    {
        "stage": "После завершения модуля",
        "trigger_day": 7,
        "channel": "Email",
        "subject": "Как вам модуль? 1 минута на отзыв",
        "body": "Вы завершили модуль «{module_name}»! "
        "Расскажите в 2-3 предложениях: что было самым полезным?",
        "incentive": "Бонусный чеклист по теме модуля",
    },
    {
        "stage": "После завершения курса",
        "trigger_day": 0,
        "channel": "Email + In-app",
        "subject": "Поздравляем! Поделитесь впечатлениями",
        "body": "Вы прошли весь курс {course_name}! "
        "Ваш отзыв поможет другим студентам принять решение.",
        "incentive": "Скидка 15% на следующий курс",
    },
    {
        "stage": "Через 30 дней после покупки",
        "trigger_day": 30,
        "channel": "Telegram",
        "subject": "Месяц с нами! Как результаты?",
        "body": "Прошёл месяц с начала обучения. "
        "Какой навык вы применили на практике? Поделитесь историей!",
        "incentive": "Доступ к закрытому вебинару",
    },
    {
        "stage": "После получения сертификата",
        "trigger_day": 0,
        "channel": "Email",
        "subject": "Ваш сертификат готов! Покажите миру",
        "body": "Сертификат «{cert_name}» ваш! "
        "Опубликуйте в LinkedIn с отметкой и получите бонус.",
        "incentive": "Бейдж амбассадора + промокод для друзей",
    },
    {
        "stage": "NPS > 8",
        "trigger_day": 1,
        "channel": "Email персональный",
        "subject": "Спасибо за высокую оценку! Просьба",
        "body": "Вы оценили нас на {score}/10. "
        "Не могли бы вы написать короткий отзыв для нашего сайта?",
        "incentive": "Персональная скидка 20%",
    },
]

TESTIMONIAL_CATEGORIES: list[dict[str, str]] = [
    {
        "category": "Карьерный результат",
        "description": "Студент получил работу, повышение, новый проект",
        "example_prompt": "Опишите, как курс повлиял на вашу карьеру",
        "display_priority": "high",
    },
    {
        "category": "Навык на практике",
        "description": "Студент применил знания в реальной задаче",
        "example_prompt": "Какой навык из курса вы используете каждый день?",
        "display_priority": "high",
    },
    {
        "category": "До/После",
        "description": "Трансформация: что было и что стало",
        "example_prompt": "Опишите ваш уровень до курса и сейчас",
        "display_priority": "high",
    },
    {
        "category": "Качество обучения",
        "description": "Оценка материалов, подачи, поддержки",
        "example_prompt": "Что вам больше всего понравилось в процессе обучения?",
        "display_priority": "medium",
    },
    {
        "category": "Соотношение цена/качество",
        "description": "Стоило ли вложение, ROI обучения",
        "example_prompt": "Оправдали ли инвестиции в курс ваши ожидания?",
        "display_priority": "medium",
    },
    {
        "category": "Рекомендация",
        "description": "Кому и почему студент рекомендует курс",
        "example_prompt": "Кому бы вы порекомендовали этот курс и почему?",
        "display_priority": "low",
    },
]

DISPLAY_FORMATS: list[dict[str, str | int]] = [
    {
        "format": "Карточка отзыва (сайт)",
        "elements": "Фото, имя, должность, текст, рейтинг (звёзды)",
        "max_text_length": 280,
        "platform": "Landing page",
    },
    {
        "format": "Карусель отзывов (Instagram)",
        "elements": "Фото студента, цитата, курс, результат",
        "max_text_length": 150,
        "platform": "Instagram",
    },
    {
        "format": "Видео-отзыв (TikTok/YouTube)",
        "elements": "Видео 30-60 сек, субтитры, CTA",
        "max_text_length": 0,
        "platform": "TikTok, YouTube",
    },
    {
        "format": "Скриншот переписки",
        "elements": "Скриншот DM/чата с благодарностью (с разрешения)",
        "max_text_length": 0,
        "platform": "Instagram Stories",
    },
    {
        "format": "Кейс-стади (лонгрид)",
        "elements": "Проблема, решение, результат, цифры, цитаты",
        "max_text_length": 2000,
        "platform": "Blog, YouTube описание",
    },
]

INCENTIVE_PROGRAMS: list[dict[str, str | int]] = [
    {
        "program": "Быстрый отзыв",
        "condition": "Отзыв в течение 48 часов после запроса",
        "reward": "Бонусный PDF-гайд",
        "cost": 0,
    },
    {
        "program": "Видео-отзыв",
        "condition": "Видео от 30 секунд с лицом и голосом",
        "reward": "Скидка 25% на следующий курс",
        "cost": 0,
    },
    {
        "program": "Развёрнутый кейс",
        "condition": "Текст от 300 слов с конкретными цифрами",
        "reward": "Бесплатный модуль продвинутого курса",
        "cost": 0,
    },
    {
        "program": "LinkedIn-публикация",
        "condition": "Пост в LinkedIn с отметкой аккаунта и хештегом",
        "reward": "Промокод 15% для 3 друзей + 15% себе",
        "cost": 0,
    },
    {
        "program": "Амбассадор месяца",
        "condition": "Лучший отзыв месяца (голосование)",
        "reward": "Бесплатный курс на выбор",
        "cost": 197,
    },
]

MODERATION_RULES: list[dict[str, str]] = [
    {
        "rule": "Проверка подлинности",
        "description": "Отзыв только от верифицированных студентов (есть покупка)",
        "action": "Автоматическая проверка по email/ID",
    },
    {
        "rule": "Минимальная длина",
        "description": "Текстовый отзыв от 50 символов",
        "action": "Запрос дополнить, если короче",
    },
    {
        "rule": "Запрет спойлеров",
        "description": "Не раскрывать ключевые решения задач курса",
        "action": "Редактирование перед публикацией",
    },
    {
        "rule": "Персональные данные",
        "description": "Не публиковать контакты, email, телефоны третьих лиц",
        "action": "Автоматическое маскирование",
    },
    {
        "rule": "Негативные отзывы",
        "description": "Негатив публикуется, но с ответом команды",
        "action": "Эскалация в поддержку, ответ в течение 24 часов",
    },
]


@dataclass(frozen=True, slots=True)
class RequestTemplate:
    stage: str
    trigger_day: int
    channel: str
    subject: str
    body: str
    incentive: str


@dataclass(frozen=True, slots=True)
class TestimonialCategory:
    category: str
    description: str
    example_prompt: str
    display_priority: str


@dataclass(frozen=True, slots=True)
class DisplayFormat:
    format: str
    elements: str
    max_text_length: int
    platform: str


@dataclass(frozen=True, slots=True)
class IncentiveProgram:
    program: str
    condition: str
    reward: str
    cost: int


@dataclass(frozen=True, slots=True)
class ModerationRule:
    rule: str
    description: str
    action: str


@dataclass(frozen=True, slots=True)
class TestimonialCollector:
    request_templates: tuple[RequestTemplate, ...]
    categories: tuple[TestimonialCategory, ...]
    display_formats: tuple[DisplayFormat, ...]
    incentive_programs: tuple[IncentiveProgram, ...]
    moderation_rules: tuple[ModerationRule, ...]


def generate_testimonial_collector() -> TestimonialCollector:
    return TestimonialCollector(
        request_templates=tuple(
            RequestTemplate(
                stage=rt["stage"],
                trigger_day=int(rt["trigger_day"]),
                channel=rt["channel"],
                subject=rt["subject"],
                body=rt["body"],
                incentive=rt["incentive"],
            )
            for rt in REQUEST_TEMPLATES
        ),
        categories=tuple(
            TestimonialCategory(
                category=tc["category"],
                description=tc["description"],
                example_prompt=tc["example_prompt"],
                display_priority=tc["display_priority"],
            )
            for tc in TESTIMONIAL_CATEGORIES
        ),
        display_formats=tuple(
            DisplayFormat(
                format=df["format"],
                elements=df["elements"],
                max_text_length=int(df["max_text_length"]),
                platform=df["platform"],
            )
            for df in DISPLAY_FORMATS
        ),
        incentive_programs=tuple(
            IncentiveProgram(
                program=ip["program"],
                condition=ip["condition"],
                reward=ip["reward"],
                cost=int(ip["cost"]),
            )
            for ip in INCENTIVE_PROGRAMS
        ),
        moderation_rules=tuple(
            ModerationRule(
                rule=mr["rule"],
                description=mr["description"],
                action=mr["action"],
            )
            for mr in MODERATION_RULES
        ),
    )


def export_testimonial_json(tc: TestimonialCollector, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "request_templates": [
            {
                "stage": rt.stage,
                "trigger_day": rt.trigger_day,
                "channel": rt.channel,
                "subject": rt.subject,
                "body": rt.body,
                "incentive": rt.incentive,
            }
            for rt in tc.request_templates
        ],
        "categories": [
            {
                "category": cat.category,
                "description": cat.description,
                "example_prompt": cat.example_prompt,
                "display_priority": cat.display_priority,
            }
            for cat in tc.categories
        ],
        "display_formats": [
            {
                "format": df.format,
                "elements": df.elements,
                "max_text_length": df.max_text_length,
                "platform": df.platform,
            }
            for df in tc.display_formats
        ],
        "incentive_programs": [
            {
                "program": ip.program,
                "condition": ip.condition,
                "reward": ip.reward,
                "cost": ip.cost,
            }
            for ip in tc.incentive_programs
        ],
        "moderation_rules": [
            {
                "rule": mr.rule,
                "description": mr.description,
                "action": mr.action,
            }
            for mr in tc.moderation_rules
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_testimonial_txt(tc: TestimonialCollector, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "КОЛЛЕКТОР ОТЗЫВОВ",
        "=" * 60,
        "\n📧 ШАБЛОНЫ ЗАПРОСОВ ОТЗЫВОВ",
        "━" * 50,
    ]
    for rt in tc.request_templates:
        lines.append(f"\n  [{rt.stage}] канал: {rt.channel}")
        lines.append(f"    Тема: {rt.subject}")
        lines.append(f"    Стимул: {rt.incentive}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📂 КАТЕГОРИИ ОТЗЫВОВ")
    lines.append("━" * 50)
    for cat in tc.categories:
        lines.append(f"\n  [{cat.category}] приоритет: {cat.display_priority}")
        lines.append(f"    Промпт: {cat.example_prompt}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🖼 ФОРМАТЫ ОТОБРАЖЕНИЯ")
    lines.append("━" * 50)
    lines.extend(
        f"  [{df.format}] {df.platform} | макс. {df.max_text_length} симв."
        for df in tc.display_formats
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("🎁 ПРОГРАММЫ СТИМУЛИРОВАНИЯ")
    lines.append("━" * 50)
    for ip in tc.incentive_programs:
        lines.append(f"\n  [{ip.program}] стоимость: ${ip.cost}")
        lines.append(f"    Условие: {ip.condition}")
        lines.append(f"    Награда: {ip.reward}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🛡 ПРАВИЛА МОДЕРАЦИИ")
    lines.append("━" * 50)
    lines.extend(f"  [{mr.rule}] {mr.action}" for mr in tc.moderation_rules)

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def testimonial_summary(tc: TestimonialCollector) -> str:
    return (
        f"Отзывы: "
        f"{len(tc.request_templates)} шаблонов запроса, "
        f"{len(tc.categories)} категорий, "
        f"{len(tc.display_formats)} форматов, "
        f"{len(tc.incentive_programs)} программ стимулирования, "
        f"{len(tc.moderation_rules)} правил модерации"
    )
