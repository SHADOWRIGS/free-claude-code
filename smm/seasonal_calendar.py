"""Seasonal calendar — holiday and event-driven content planning.

Generates structured seasonal configs:
- Key dates and holidays for content campaigns
- Seasonal themes per pillar
- Campaign templates tied to events
- Black Friday / Cyber Monday special plans
- Content adjustment rules by season
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

KEY_DATES: list[dict[str, str]] = [
    {
        "date": "01-01",
        "name": "Новый год",
        "type": "holiday",
        "content_angle": "Итоги года, цели на новый год, скидки",
        "pillars": "all",
    },
    {
        "date": "02-14",
        "name": "День влюблённых",
        "type": "holiday",
        "content_angle": "Влюбись в кибербезопасность, подарок-курс",
        "pillars": "all",
    },
    {
        "date": "03-08",
        "name": "8 Марта",
        "type": "holiday",
        "content_angle": "Женщины в IT/кибербезе, скидки",
        "pillars": "all",
    },
    {
        "date": "03-14",
        "name": "День числа Пи",
        "type": "tech_event",
        "content_angle": "ML/AI контент, математика в безопасности",
        "pillars": "Machine Learning & AI",
    },
    {
        "date": "05-04",
        "name": "Star Wars Day",
        "type": "pop_culture",
        "content_angle": "Тёмная/светлая сторона = Red/Blue Team",
        "pillars": "Red Team, Blue Team",
    },
    {
        "date": "05-25",
        "name": "GDPR Day",
        "type": "tech_event",
        "content_angle": "Защита данных, комплаенс, приватность",
        "pillars": "Blue Team / Defensive Security",
    },
    {
        "date": "09-01",
        "name": "День знаний",
        "type": "holiday",
        "content_angle": "Старт учебного сезона, промо курсов",
        "pillars": "all",
    },
    {
        "date": "10-31",
        "name": "Хэллоуин",
        "type": "holiday",
        "content_angle": "Страшные уязвимости, хакерские истории",
        "pillars": "Cyber Security & Ethical Hacking",
    },
    {
        "date": "11-11",
        "name": "11.11 AliExpress",
        "type": "sales",
        "content_angle": "Мега-распродажа гаджетов, подборки",
        "pillars": "AliExpress",
    },
    {
        "date": "11-29",
        "name": "Black Friday",
        "type": "sales",
        "content_angle": "Максимальные скидки на курсы и гаджеты",
        "pillars": "all",
    },
    {
        "date": "12-02",
        "name": "Cyber Monday",
        "type": "sales",
        "content_angle": "Кибер-скидки, тематический контент",
        "pillars": "all",
    },
    {
        "date": "12-31",
        "name": "Новогодняя ночь",
        "type": "holiday",
        "content_angle": "Итоги, подведение результатов, планы",
        "pillars": "all",
    },
]

SEASONAL_THEMES: list[dict[str, str | list[str]]] = [
    {
        "season": "Зима (декабрь-февраль)",
        "mood": "Уютное обучение, новогодние цели",
        "colors": ["#1a1a2e", "#16213e", "#0f3460"],
        "content_focus": "Итоги года, планирование, зимние распродажи",
        "best_formats": "Карусели с итогами, видео-обзоры года",
    },
    {
        "season": "Весна (март-май)",
        "mood": "Новый старт, энергия, обновление",
        "colors": ["#00b4d8", "#0077b6", "#023e8a"],
        "content_focus": "Старт обучения, весенние вебинары, 8 Марта",
        "best_formats": "Челленджи, стримы, интерактив",
    },
    {
        "season": "Лето (июнь-август)",
        "mood": "Лёгкий контент, летняя практика",
        "colors": ["#f77f00", "#fcbf49", "#eae2b7"],
        "content_focus": "Летние интенсивы, CTF-соревнования, практика",
        "best_formats": "Короткие видео, мемы, лайт-контент",
    },
    {
        "season": "Осень (сентябрь-ноябрь)",
        "mood": "Серьёзное обучение, карьерный рост",
        "colors": ["#d62828", "#f77f00", "#003049"],
        "content_focus": "День знаний, Black Friday, карьерные треки",
        "best_formats": "Длинные видео, курсы, кейсы успеха",
    },
]

CAMPAIGN_TEMPLATES: list[dict[str, str | int]] = [
    {
        "name": "Предпраздничный прогрев",
        "days_before": 7,
        "posts_count": 5,
        "structure": "тизер → польза → социальное доказательство → оффер → напоминание",
        "goal": "Подготовить аудиторию к акции",
    },
    {
        "name": "Flash Sale (1 день)",
        "days_before": 0,
        "posts_count": 3,
        "structure": "утро: анонс → день: таймер → вечер: последний шанс",
        "goal": "Максимум конверсий за 24 часа",
    },
    {
        "name": "Пост-акция (отработка)",
        "days_before": -1,
        "posts_count": 2,
        "structure": "итоги акции → благодарность + следующий шаг",
        "goal": "Удержание новых подписчиков",
    },
    {
        "name": "Сезонный контент-блок",
        "days_before": 14,
        "posts_count": 10,
        "structure": "5 образовательных + 3 вовлекающих + 2 продающих",
        "goal": "Поддержание активности в тематический период",
    },
]

BF_CM_PLAN: dict[str, list[dict[str, str]]] = {
    "black_friday": [
        {"day": "Пн (за 4 дня)", "action": "Тизер: скоро что-то огромное"},
        {"day": "Вт (за 3 дня)", "action": "Превью скидок, wishlist"},
        {"day": "Ср (за 2 дня)", "action": "Ранний доступ для подписчиков"},
        {"day": "Чт (за 1 день)", "action": "Обратный отсчёт, сторис-напоминания"},
        {"day": "Пт (Black Friday)", "action": "СТАРТ! Все каналы, максимум постов"},
        {"day": "Сб", "action": "Продление, отзывы покупателей"},
        {"day": "Вс", "action": "Последний день, дефицит"},
        {"day": "Пн (Cyber Monday)", "action": "Кибер-скидки, новый оффер"},
    ],
    "eleven_eleven": [
        {"day": "За 3 дня", "action": "Подборка лучших гаджетов со скидкой"},
        {"day": "За 1 день", "action": "Корзина-гайд: что положить"},
        {"day": "11.11", "action": "Максимум постов + стримы с распаковкой"},
        {"day": "После", "action": "Отзывы и что купили подписчики"},
    ],
}


@dataclass(frozen=True, slots=True)
class KeyDate:
    date: str
    name: str
    type: str
    content_angle: str
    pillars: str


@dataclass(frozen=True, slots=True)
class SeasonalTheme:
    season: str
    mood: str
    colors: tuple[str, ...]
    content_focus: str
    best_formats: str


@dataclass(frozen=True, slots=True)
class CampaignTemplate:
    name: str
    days_before: int
    posts_count: int
    structure: str
    goal: str


@dataclass(frozen=True, slots=True)
class BFDay:
    day: str
    action: str


@dataclass(frozen=True, slots=True)
class SeasonalCalendar:
    key_dates: tuple[KeyDate, ...]
    themes: tuple[SeasonalTheme, ...]
    campaign_templates: tuple[CampaignTemplate, ...]
    bf_plan: tuple[BFDay, ...]
    eleven_plan: tuple[BFDay, ...]


def generate_seasonal_calendar() -> SeasonalCalendar:
    return SeasonalCalendar(
        key_dates=tuple(
            KeyDate(
                date=d["date"],
                name=d["name"],
                type=d["type"],
                content_angle=d["content_angle"],
                pillars=d["pillars"],
            )
            for d in KEY_DATES
        ),
        themes=tuple(
            SeasonalTheme(
                season=t["season"],
                mood=t["mood"],
                colors=tuple(t["colors"]),
                content_focus=t["content_focus"],
                best_formats=t["best_formats"],
            )
            for t in SEASONAL_THEMES
        ),
        campaign_templates=tuple(
            CampaignTemplate(
                name=c["name"],
                days_before=int(c["days_before"]),
                posts_count=int(c["posts_count"]),
                structure=c["structure"],
                goal=c["goal"],
            )
            for c in CAMPAIGN_TEMPLATES
        ),
        bf_plan=tuple(
            BFDay(day=d["day"], action=d["action"]) for d in BF_CM_PLAN["black_friday"]
        ),
        eleven_plan=tuple(
            BFDay(day=d["day"], action=d["action"]) for d in BF_CM_PLAN["eleven_eleven"]
        ),
    )


def export_seasonal_json(sc: SeasonalCalendar, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "key_dates": [
            {
                "date": d.date,
                "name": d.name,
                "type": d.type,
                "content_angle": d.content_angle,
                "pillars": d.pillars,
            }
            for d in sc.key_dates
        ],
        "themes": [
            {
                "season": t.season,
                "mood": t.mood,
                "colors": list(t.colors),
                "content_focus": t.content_focus,
                "best_formats": t.best_formats,
            }
            for t in sc.themes
        ],
        "campaign_templates": [
            {
                "name": c.name,
                "days_before": c.days_before,
                "posts_count": c.posts_count,
                "structure": c.structure,
                "goal": c.goal,
            }
            for c in sc.campaign_templates
        ],
        "bf_plan": [{"day": d.day, "action": d.action} for d in sc.bf_plan],
        "eleven_plan": [{"day": d.day, "action": d.action} for d in sc.eleven_plan],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_seasonal_txt(sc: SeasonalCalendar, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "СЕЗОННЫЙ КАЛЕНДАРЬ — ПРАЗДНИКИ И СОБЫТИЯ",
        "=" * 60,
        "\n📅 КЛЮЧЕВЫЕ ДАТЫ",
        "━" * 50,
    ]
    for d in sc.key_dates:
        lines.append(f"\n  [{d.date}] {d.name} ({d.type})")
        lines.append(f"    Контент: {d.content_angle}")
        lines.append(f"    Для: {d.pillars}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🌦 СЕЗОННЫЕ ТЕМЫ")
    lines.append("━" * 50)
    for t in sc.themes:
        lines.append(f"\n  [{t.season}]")
        lines.append(f"    Настроение: {t.mood}")
        lines.append(f"    Фокус: {t.content_focus}")
        lines.append(f"    Форматы: {t.best_formats}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📋 ШАБЛОНЫ КАМПАНИЙ")
    lines.append("━" * 50)
    for c in sc.campaign_templates:
        lines.append(f"\n  [{c.name}] ({c.posts_count} постов)")
        lines.append(f"    Старт: за {c.days_before} дней")
        lines.append(f"    Структура: {c.structure}")
        lines.append(f"    Цель: {c.goal}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🛒 BLACK FRIDAY / CYBER MONDAY ПЛАН")
    lines.append("━" * 50)
    lines.extend(f"  {d.day}: {d.action}" for d in sc.bf_plan)

    lines.append(f"\n{'━' * 50}")
    lines.append("🛍 11.11 ALIEXPRESS ПЛАН")
    lines.append("━" * 50)
    lines.extend(f"  {d.day}: {d.action}" for d in sc.eleven_plan)

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def seasonal_summary(sc: SeasonalCalendar) -> str:
    return (
        f"Сезонный календарь: "
        f"{len(sc.key_dates)} ключевых дат, "
        f"{len(sc.themes)} сезонных тем, "
        f"{len(sc.campaign_templates)} шаблонов кампаний, "
        f"BF-план на {len(sc.bf_plan)} дней, "
        f"11.11-план на {len(sc.eleven_plan)} дней"
    )
