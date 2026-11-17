"""Content recycler — reuse and refresh evergreen content.

Generates structured recycling configs:
- Evergreen content identification rules
- Refresh strategies per content type
- Recycling schedule (when to repost/update)
- Performance-based recycling triggers
- Format transformation rules (post to reel, etc.)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

EVERGREEN_RULES: list[dict[str, str]] = [
    {
        "id": "how_to",
        "name": "Гайды и туториалы",
        "criteria": "Обучающий контент без привязки к дате",
        "shelf_life": "12 месяцев",
        "example": "Как настроить VPN за 5 минут",
    },
    {
        "id": "tool_review",
        "name": "Обзоры инструментов",
        "criteria": "Описание инструмента/гаджета с практической ценностью",
        "shelf_life": "6 месяцев",
        "example": "Топ-5 инструментов для пентеста",
    },
    {
        "id": "concept_explainer",
        "name": "Объяснение концепций",
        "criteria": "Фундаментальные темы кибербезопасности/ML",
        "shelf_life": "18 месяцев",
        "example": "Что такое Zero Trust и зачем он нужен",
    },
    {
        "id": "case_study",
        "name": "Кейсы и истории",
        "criteria": "Разбор реальных инцидентов/проектов",
        "shelf_life": "12 месяцев",
        "example": "Как мы остановили DDoS-атаку за 20 минут",
    },
    {
        "id": "checklist",
        "name": "Чеклисты и шпаргалки",
        "criteria": "Компактные справочные материалы",
        "shelf_life": "12 месяцев",
        "example": "Чеклист безопасности домашней сети",
    },
]

REFRESH_STRATEGIES: list[dict[str, str]] = [
    {
        "id": "visual_refresh",
        "name": "Обновление визуала",
        "description": "Новый дизайн, другой шаблон, свежие скриншоты",
        "effort": "Низкий",
        "best_for": "Посты с устаревшим визуалом",
    },
    {
        "id": "data_update",
        "name": "Обновление данных",
        "description": "Свежая статистика, новые цифры, актуальные ссылки",
        "effort": "Средний",
        "best_for": "Инфографика, обзоры, рейтинги",
    },
    {
        "id": "format_change",
        "name": "Смена формата",
        "description": "Пост в карусель, текст в видео, сторис в рилс",
        "effort": "Средний",
        "best_for": "Успешный контент для новой платформы",
    },
    {
        "id": "deep_dive",
        "name": "Углубление темы",
        "description": "Расширить короткий пост в серию или длинное видео",
        "effort": "Высокий",
        "best_for": "Топ-контент с высоким сохранением",
    },
    {
        "id": "audience_adapt",
        "name": "Адаптация под аудиторию",
        "description": "Версия для новичков / продвинутых / бизнеса",
        "effort": "Средний",
        "best_for": "Универсальные темы",
    },
]

RECYCLE_SCHEDULE: list[dict[str, str | int]] = [
    {
        "interval_days": 30,
        "action": "Репост в сторис с новым комментарием",
        "platform": "instagram",
        "condition": "Пост набрал ER > среднего",
    },
    {
        "interval_days": 60,
        "action": "Визуальное обновление + новый caption",
        "platform": "instagram",
        "condition": "Evergreen-контент",
    },
    {
        "interval_days": 14,
        "action": "Репост с другим хештег-пулом",
        "platform": "tiktok",
        "condition": "Видео набрало > 5000 просмотров",
    },
    {
        "interval_days": 90,
        "action": "Обновлённая версия (data refresh)",
        "platform": "youtube",
        "condition": "Видео в топ-10 по просмотрам",
    },
    {
        "interval_days": 7,
        "action": "Кросс-пост на другую платформу",
        "platform": "all",
        "condition": "Контент ещё не был на целевой платформе",
    },
]

PERFORMANCE_TRIGGERS: list[dict[str, str]] = [
    {
        "metric": "saves",
        "threshold": "Топ-10% по сохранениям",
        "action": "Создать серию из этой темы",
        "priority": "Высокий",
    },
    {
        "metric": "shares",
        "threshold": "Больше 50 репостов",
        "action": "Превратить в рилс/шортс",
        "priority": "Высокий",
    },
    {
        "metric": "comments",
        "threshold": "Больше 20 комментариев",
        "action": "Создать Q&A пост по вопросам",
        "priority": "Средний",
    },
    {
        "metric": "click_rate",
        "threshold": "CTR > 5%",
        "action": "Повторить с A/B вариантом caption",
        "priority": "Средний",
    },
    {
        "metric": "conversion",
        "threshold": "Привёл > 3 покупки",
        "action": "Масштабировать в рекламу",
        "priority": "Высокий",
    },
]

FORMAT_TRANSFORMS: list[dict[str, str]] = [
    {
        "from_format": "Пост (текст + изображение)",
        "to_format": "Карусель (5 слайдов)",
        "how": "Разбить текст на ключевые тезисы, по 1 на слайд",
    },
    {
        "from_format": "Пост (текст + изображение)",
        "to_format": "Рилс/Шортс (30 сек)",
        "how": "Озвучить ключевые факты с визуальным рядом",
    },
    {
        "from_format": "Длинное видео (YouTube)",
        "to_format": "5 коротких клипов (Reels/TT)",
        "how": "Нарезать ключевые моменты с хуками",
    },
    {
        "from_format": "Карусель",
        "to_format": "Thread (Telegram/X)",
        "how": "Каждый слайд = 1 сообщение треда",
    },
    {
        "from_format": "Сторис (серия)",
        "to_format": "Гайд-пост",
        "how": "Объединить слайды в один длинный пост",
    },
    {
        "from_format": "Email-рассылка",
        "to_format": "Серия постов (3 шт.)",
        "how": "Каждый блок письма = отдельный пост",
    },
]


@dataclass(frozen=True, slots=True)
class EvergreenRule:
    id: str
    name: str
    criteria: str
    shelf_life: str
    example: str


@dataclass(frozen=True, slots=True)
class RefreshStrategy:
    id: str
    name: str
    description: str
    effort: str
    best_for: str


@dataclass(frozen=True, slots=True)
class RecycleSlot:
    interval_days: int
    action: str
    platform: str
    condition: str


@dataclass(frozen=True, slots=True)
class PerformanceTrigger:
    metric: str
    threshold: str
    action: str
    priority: str


@dataclass(frozen=True, slots=True)
class FormatTransform:
    from_format: str
    to_format: str
    how: str


@dataclass(frozen=True, slots=True)
class ContentRecycler:
    evergreen_rules: tuple[EvergreenRule, ...]
    refresh_strategies: tuple[RefreshStrategy, ...]
    schedule: tuple[RecycleSlot, ...]
    performance_triggers: tuple[PerformanceTrigger, ...]
    format_transforms: tuple[FormatTransform, ...]


def generate_content_recycler() -> ContentRecycler:
    return ContentRecycler(
        evergreen_rules=tuple(
            EvergreenRule(
                id=r["id"],
                name=r["name"],
                criteria=r["criteria"],
                shelf_life=r["shelf_life"],
                example=r["example"],
            )
            for r in EVERGREEN_RULES
        ),
        refresh_strategies=tuple(
            RefreshStrategy(
                id=s["id"],
                name=s["name"],
                description=s["description"],
                effort=s["effort"],
                best_for=s["best_for"],
            )
            for s in REFRESH_STRATEGIES
        ),
        schedule=tuple(
            RecycleSlot(
                interval_days=int(sl["interval_days"]),
                action=sl["action"],
                platform=sl["platform"],
                condition=sl["condition"],
            )
            for sl in RECYCLE_SCHEDULE
        ),
        performance_triggers=tuple(
            PerformanceTrigger(
                metric=t["metric"],
                threshold=t["threshold"],
                action=t["action"],
                priority=t["priority"],
            )
            for t in PERFORMANCE_TRIGGERS
        ),
        format_transforms=tuple(
            FormatTransform(
                from_format=ft["from_format"],
                to_format=ft["to_format"],
                how=ft["how"],
            )
            for ft in FORMAT_TRANSFORMS
        ),
    )


def export_recycler_json(cr: ContentRecycler, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "evergreen_rules": [
            {
                "id": r.id,
                "name": r.name,
                "criteria": r.criteria,
                "shelf_life": r.shelf_life,
                "example": r.example,
            }
            for r in cr.evergreen_rules
        ],
        "refresh_strategies": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "effort": s.effort,
                "best_for": s.best_for,
            }
            for s in cr.refresh_strategies
        ],
        "schedule": [
            {
                "interval_days": sl.interval_days,
                "action": sl.action,
                "platform": sl.platform,
                "condition": sl.condition,
            }
            for sl in cr.schedule
        ],
        "performance_triggers": [
            {
                "metric": t.metric,
                "threshold": t.threshold,
                "action": t.action,
                "priority": t.priority,
            }
            for t in cr.performance_triggers
        ],
        "format_transforms": [
            {
                "from_format": ft.from_format,
                "to_format": ft.to_format,
                "how": ft.how,
            }
            for ft in cr.format_transforms
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_recycler_txt(cr: ContentRecycler, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "КОНТЕНТ-РЕЦИКЛЕР — ПОВТОРНОЕ ИСПОЛЬЗОВАНИЕ КОНТЕНТА",
        "=" * 60,
        "\n♻ ПРАВИЛА EVERGREEN-КОНТЕНТА",
        "━" * 50,
    ]
    for r in cr.evergreen_rules:
        lines.append(f"\n  [{r.id}] {r.name} (срок: {r.shelf_life})")
        lines.append(f"    Критерий: {r.criteria}")
        lines.append(f"    Пример: {r.example}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🔄 СТРАТЕГИИ ОБНОВЛЕНИЯ")
    lines.append("━" * 50)
    for s in cr.refresh_strategies:
        lines.append(f"\n  [{s.id}] {s.name} (усилие: {s.effort})")
        lines.append(f"    {s.description}")
        lines.append(f"    Лучше для: {s.best_for}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📅 РАСПИСАНИЕ РЕЦИКЛИНГА")
    lines.append("━" * 50)
    for sl in cr.schedule:
        lines.append(f"\n  Каждые {sl.interval_days} дней [{sl.platform}]")
        lines.append(f"    {sl.action}")
        lines.append(f"    Условие: {sl.condition}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📈 ТРИГГЕРЫ ПО МЕТРИКАМ")
    lines.append("━" * 50)
    for t in cr.performance_triggers:
        lines.append(f"\n  [{t.metric}] {t.threshold} (приоритет: {t.priority})")
        lines.append(f"    Действие: {t.action}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🔀 ТРАНСФОРМАЦИЯ ФОРМАТОВ")
    lines.append("━" * 50)
    for ft in cr.format_transforms:
        lines.append(f"\n  {ft.from_format} -> {ft.to_format}")
        lines.append(f"    Как: {ft.how}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def recycler_summary(cr: ContentRecycler) -> str:
    return (
        f"Контент-рециклер: "
        f"{len(cr.evergreen_rules)} правил evergreen, "
        f"{len(cr.refresh_strategies)} стратегий обновления, "
        f"{len(cr.schedule)} слотов расписания, "
        f"{len(cr.performance_triggers)} триггеров, "
        f"{len(cr.format_transforms)} трансформаций"
    )
