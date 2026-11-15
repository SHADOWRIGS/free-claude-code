"""Audience personas — target audience profiles for content personalization.

Defines buyer personas for each pillar so content is tailored to the right
audience segment. Each persona has demographics, pain points, goals,
preferred platforms, and content preferences.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

PERSONAS_DATA: list[dict[str, object]] = [
    {
        "id": "junior-pentester",
        "name": "Алексей — начинающий пентестер",
        "pillar": "Cyber Security & Ethical Hacking",
        "age_range": "18-25",
        "role": "Студент / Junior в IT",
        "pain_points": [
            "Не знает, с чего начать в кибербезопасности",
            "Нет практического опыта",
            "Курсы слишком дорогие",
        ],
        "goals": [
            "Получить первую работу в InfoSec",
            "Научиться пентесту на практике",
            "Заработать на Bug Bounty",
        ],
        "platforms": ["tiktok", "instagram"],
        "content_prefs": ["короткие видео", "чеклисты", "реальные кейсы"],
        "buying_triggers": [
            "бесплатный пробный урок",
            "скидка для студентов",
            "отзывы выпускников",
        ],
    },
    {
        "id": "soc-analyst",
        "name": "Мария — SOC-аналитик",
        "pillar": "Blue Team / Defensive Security",
        "age_range": "25-35",
        "role": "SOC-аналитик / Security Engineer",
        "pain_points": [
            "Перегрузка алертами и ложные срабатывания",
            "Нет времени на обучение новым инструментам",
            "Сложно убедить руководство в бюджете на безопасность",
        ],
        "goals": [
            "Автоматизировать рутинные задачи",
            "Повысить квалификацию до Senior",
            "Внедрить SOAR в команде",
        ],
        "platforms": ["youtube", "instagram"],
        "content_prefs": ["подробные гайды", "карусели с шагами", "вебинары"],
        "buying_triggers": [
            "сертификация включена",
            "гарантия результата",
            "корпоративная лицензия",
        ],
    },
    {
        "id": "red-teamer",
        "name": "Дмитрий — Red Team специалист",
        "pillar": "Red Team / Offensive Security",
        "age_range": "25-40",
        "role": "Пентестер / Red Team Lead",
        "pain_points": [
            "Нужны новые техники для обхода защиты",
            "Клиенты не понимают ценность пентеста",
            "Сложно найти качественные лабы для практики",
        ],
        "goals": [
            "Освоить новые эксплойты и техники",
            "Развить свою команду",
            "Увеличить доход от Bug Bounty",
        ],
        "platforms": ["youtube", "tiktok"],
        "content_prefs": ["технические deep-dive", "live-хакинг", "writeups"],
        "buying_triggers": [
            "эксклюзивные лабы",
            "менторство от практика",
            "доступ к закрытому сообществу",
        ],
    },
    {
        "id": "ml-beginner",
        "name": "Анна — начинающий ML-инженер",
        "pillar": "Machine Learning & AI",
        "age_range": "20-30",
        "role": "Data Analyst / Junior ML Engineer",
        "pain_points": [
            "Теория без практики — не понимает, как применять",
            "Слишком много фреймворков, не знает какой учить",
            "Нет портфолио для трудоустройства",
        ],
        "goals": [
            "Построить ML-модель от начала до конца",
            "Получить работу ML-инженера",
            "Разобраться в LLM и prompt engineering",
        ],
        "platforms": ["youtube", "instagram"],
        "content_prefs": [
            "пошаговые туториалы",
            "code-along видео",
            "карусели с концепциями",
        ],
        "buying_triggers": [
            "проекты для портфолио",
            "помощь с трудоустройством",
            "живые Q&A",
        ],
    },
    {
        "id": "gadget-hunter",
        "name": "Игорь — охотник за гаджетами",
        "pillar": "AliExpress — Гаджеты",
        "age_range": "18-35",
        "role": "IT-энтузиаст / Хобби-хакер",
        "pain_points": [
            "Много подделок и некачественных товаров",
            "Не знает, какой гаджет реально работает",
            "Бюджет ограничен",
        ],
        "goals": [
            "Собрать домашнюю хакерскую лабораторию",
            "Найти качественные гаджеты за минимум денег",
            "Быть в курсе новинок",
        ],
        "platforms": ["tiktok", "instagram"],
        "content_prefs": ["обзоры с распаковкой", "сравнения", "топ-списки"],
        "buying_triggers": [
            "реферальная скидка",
            "проверено лично",
            "ограниченное предложение",
        ],
    },
]


@dataclass(frozen=True, slots=True)
class Persona:
    id: str
    name: str
    pillar: str
    age_range: str
    role: str
    pain_points: tuple[str, ...]
    goals: tuple[str, ...]
    platforms: tuple[str, ...]
    content_prefs: tuple[str, ...]
    buying_triggers: tuple[str, ...]


def _to_persona(data: dict[str, object]) -> Persona:
    return Persona(
        id=str(data["id"]),
        name=str(data["name"]),
        pillar=str(data["pillar"]),
        age_range=str(data["age_range"]),
        role=str(data["role"]),
        pain_points=tuple(str(x) for x in data["pain_points"]),  # type: ignore[arg-type]
        goals=tuple(str(x) for x in data["goals"]),  # type: ignore[arg-type]
        platforms=tuple(str(x) for x in data["platforms"]),  # type: ignore[arg-type]
        content_prefs=tuple(str(x) for x in data["content_prefs"]),  # type: ignore[arg-type]
        buying_triggers=tuple(str(x) for x in data["buying_triggers"]),  # type: ignore[arg-type]
    )


def generate_personas(
    pillar: str | None = None,
) -> list[Persona]:
    result: list[Persona] = []
    for data in PERSONAS_DATA:
        if pillar and str(data["pillar"]) != pillar:
            continue
        result.append(_to_persona(data))
    return result


def pick_persona(pillar: str, seed: int | None = None) -> Persona:
    rng = random.Random(seed)
    pool = generate_personas(pillar=pillar)
    if not pool:
        pool = generate_personas()
    return rng.choice(pool)


def generate_content_brief(persona: Persona) -> str:
    lines = [
        f"Бриф для: {persona.name}",
        f"Направление: {persona.pillar}",
        f"Возраст: {persona.age_range} | Роль: {persona.role}",
        "",
        "Боли аудитории (использовать в хуках):",
    ]
    lines.extend(f"  - {p}" for p in persona.pain_points)
    lines.append("\nЦели (использовать в CTA):")
    lines.extend(f"  - {g}" for g in persona.goals)
    lines.append(f"\nПлатформы: {', '.join(persona.platforms)}")
    lines.append(f"Предпочтения: {', '.join(persona.content_prefs)}")
    lines.append("\nТриггеры покупки:")
    lines.extend(f"  - {t}" for t in persona.buying_triggers)
    return "\n".join(lines)


def export_personas_json(personas: list[Persona], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "id": p.id,
            "name": p.name,
            "pillar": p.pillar,
            "age_range": p.age_range,
            "role": p.role,
            "pain_points": list(p.pain_points),
            "goals": list(p.goals),
            "platforms": list(p.platforms),
            "content_prefs": list(p.content_prefs),
            "buying_triggers": list(p.buying_triggers),
        }
        for p in personas
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_personas_txt(personas: list[Persona], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "ПРОФИЛИ ЦЕЛЕВОЙ АУДИТОРИИ",
        "=" * 60,
    ]

    for p in personas:
        lines.append(f"\n{'━' * 50}")
        lines.append(f"👤 {p.name}")
        lines.append(f"{'━' * 50}")
        lines.append(f"  Направление: {p.pillar}")
        lines.append(f"  Возраст: {p.age_range}")
        lines.append(f"  Роль: {p.role}")
        lines.append("  Боли:")
        lines.extend(f"    - {pain}" for pain in p.pain_points)
        lines.append("  Цели:")
        lines.extend(f"    - {goal}" for goal in p.goals)
        lines.append(f"  Платформы: {', '.join(p.platforms)}")
        lines.append(f"  Контент: {', '.join(p.content_prefs)}")
        lines.append("  Триггеры покупки:")
        lines.extend(f"    - {t}" for t in p.buying_triggers)

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def personas_summary(personas: list[Persona]) -> str:
    if not personas:
        return "Персоны: 0 профилей"

    lines: list[str] = [
        f"Персоны: {len(personas)} профилей",
        "\nПо направлениям:",
    ]
    lines.extend(f"  {p.pillar}: {p.name}" for p in personas)
    return "\n".join(lines)
