"""Content strategy planner — unified weekly/monthly strategy.

Combines competitor analysis, posting schedule optimization,
content series, and engagement data into a cohesive strategy
document with priorities, content mix, and KPI targets.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from smm.competitor_analysis import (
    analyze_all_niches,
)
from smm.content_pillars import PILLARS, ContentPillar

CONTENT_MIX: dict[str, float] = {
    "educational": 0.40,
    "entertaining": 0.20,
    "promotional": 0.15,
    "engagement": 0.15,
    "social_proof": 0.10,
}

FORMAT_DISTRIBUTION: dict[str, dict[str, float]] = {
    "instagram": {
        "carousel": 0.30,
        "reel": 0.30,
        "static_post": 0.15,
        "story": 0.25,
    },
    "tiktok": {
        "short_video": 0.50,
        "duet": 0.15,
        "tutorial": 0.20,
        "trending": 0.15,
    },
    "youtube": {
        "long_video": 0.30,
        "shorts": 0.40,
        "tutorial": 0.20,
        "livestream": 0.10,
    },
}

GROWTH_TARGETS: dict[str, dict[str, float]] = {
    "month_1": {
        "followers_growth_pct": 5.0,
        "engagement_rate_target": 3.0,
        "posts_per_week": 63,
        "video_views_target_pct": 10.0,
    },
    "month_3": {
        "followers_growth_pct": 15.0,
        "engagement_rate_target": 4.0,
        "posts_per_week": 63,
        "video_views_target_pct": 15.0,
    },
    "month_6": {
        "followers_growth_pct": 40.0,
        "engagement_rate_target": 5.0,
        "posts_per_week": 63,
        "video_views_target_pct": 20.0,
    },
}


@dataclass(frozen=True, slots=True)
class PillarStrategy:
    pillar: str
    priority: int
    content_share: float
    key_topics: list[str]
    content_types: list[str]
    growth_lever: str
    competitive_advantage: str


@dataclass(frozen=True, slots=True)
class WeeklyStrategy:
    pillars: list[PillarStrategy]
    content_mix: dict[str, float]
    format_distribution: dict[str, dict[str, float]]
    growth_targets: dict[str, dict[str, float]]
    total_posts_per_week: int
    priority_actions: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "pillars": [
                {
                    "pillar": p.pillar,
                    "priority": p.priority,
                    "content_share": p.content_share,
                    "key_topics": p.key_topics,
                    "content_types": p.content_types,
                    "growth_lever": p.growth_lever,
                    "competitive_advantage": p.competitive_advantage,
                }
                for p in self.pillars
            ],
            "content_mix": self.content_mix,
            "format_distribution": self.format_distribution,
            "growth_targets": self.growth_targets,
            "total_posts_per_week": self.total_posts_per_week,
            "priority_actions": self.priority_actions,
        }


def _pillar_priority(pillar: ContentPillar) -> int:
    priorities = {
        "Cyber Security & Ethical Hacking": 1,
        "Red Team / Offensive Security": 2,
        "AliExpress - Гаджеты": 3,
        "Machine Learning & AI": 4,
        "Blue Team / Defensive Security": 5,
    }
    return priorities.get(pillar.name, 5)


def _content_share(priority: int) -> float:
    shares = {1: 0.30, 2: 0.25, 3: 0.20, 4: 0.15, 5: 0.10}
    return shares.get(priority, 0.10)


def _growth_lever(pillar: ContentPillar) -> str:
    levers = {
        "Cyber Security & Ethical Hacking": "Короткие Reels с быстрыми хаками + карусели-гайды",
        "Blue Team / Defensive Security": "Инфографики и чеклисты для SOC-аналитиков",
        "Red Team / Offensive Security": "CTF-разборы и серии «взломай за 5 минут»",
        "Machine Learning & AI": "Демо AI-проектов за 15 минут + тренды",
        "AliExpress - Гаджеты": "Распаковки бюджетных гаджетов + тесты «работает или нет»",
    }
    return levers.get(pillar.name, "Регулярный постинг с высоким engagement")


def _competitive_advantage(pillar: ContentPillar) -> str:
    advantages = {
        "Cyber Security & Ethical Hacking": "Русскоязычный контент в нише, где доминирует EN; короткий формат",
        "Blue Team / Defensive Security": "Практические чеклисты вместо сухой теории конкурентов",
        "Red Team / Offensive Security": "Юмор + практика, без занудства IppSec и LiveOverflow",
        "Machine Learning & AI": "Актуальные LLM-темы на русском, пока конкуренты на EN",
        "AliExpress - Гаджеты": "Бюджетный сегмент против дорогих Hak5 и оригиналов",
    }
    return advantages.get(pillar.name, "Уникальный стиль подачи контента")


def generate_pillar_strategies() -> list[PillarStrategy]:
    strategies: list[PillarStrategy] = []
    for pillar in PILLARS:
        priority = _pillar_priority(pillar)
        share = _content_share(priority)
        key_topics = pillar.topics[:5] if pillar.topics else []
        content_types = ["carousel", "reel", "static_post", "story", "video"]
        growth_lever = _growth_lever(pillar)
        advantage = _competitive_advantage(pillar)

        strategies.append(
            PillarStrategy(
                pillar=pillar.name,
                priority=priority,
                content_share=share,
                key_topics=key_topics,
                content_types=content_types,
                growth_lever=growth_lever,
                competitive_advantage=advantage,
            )
        )

    strategies.sort(key=lambda s: s.priority)
    return strategies


def generate_priority_actions() -> list[str]:
    analyses = analyze_all_niches()
    actions: list[str] = [
        "Настроить автопостинг через Buffer/Later (команда `scheduler-export`)",
        "Запустить контент-серии для удержания аудитории (команда `series`)",
        "Создать карусели-шпаргалки для каждого направления (команда `carousel`)",
    ]

    actions.extend(f"Закрыть гэп в {a.pillar}: {a.gaps[0]}" for a in analyses if a.gaps)

    actions.extend(
        [
            "Настроить A/B тестирование подписей (команда `ab-test`)",
            "Оптимизировать время публикации по тепловой карте (команда `optimize`)",
            "Подготовить сторис-пакеты с интерактивами (команда `stories`)",
        ]
    )

    return actions


def generate_strategy() -> WeeklyStrategy:
    pillar_strategies = generate_pillar_strategies()
    priority_actions = generate_priority_actions()

    return WeeklyStrategy(
        pillars=pillar_strategies,
        content_mix=dict(CONTENT_MIX),
        format_distribution={k: dict(v) for k, v in FORMAT_DISTRIBUTION.items()},
        growth_targets={k: dict(v) for k, v in GROWTH_TARGETS.items()},
        total_posts_per_week=63,
        priority_actions=priority_actions,
    )


def export_strategy_json(strategy: WeeklyStrategy, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(strategy.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def export_strategy_txt(strategy: WeeklyStrategy, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "КОНТЕНТ-СТРАТЕГИЯ SMM",
        "=" * 60,
        f"\nВсего постов в неделю: {strategy.total_posts_per_week}",
        "\n--- ПРИОРИТЕТЫ ПО НАПРАВЛЕНИЯМ ---",
    ]

    for ps in strategy.pillars:
        lines.append(
            f"\n  #{ps.priority} {ps.pillar} ({ps.content_share:.0%} контента)"
        )
        lines.append(f"    Рычаг роста: {ps.growth_lever}")
        lines.append(f"    Конкурентное преимущество: {ps.competitive_advantage}")
        lines.append(f"    Ключевые темы: {', '.join(ps.key_topics[:3])}")

    lines.append("\n--- КОНТЕНТ-МИКС ---")
    for content_type, share in strategy.content_mix.items():
        lines.append(f"  {content_type}: {share:.0%}")

    lines.append("\n--- ФОРМАТЫ ПО ПЛАТФОРМАМ ---")
    for platform, formats in strategy.format_distribution.items():
        lines.append(f"\n  {platform}:")
        for fmt, share in formats.items():
            lines.append(f"    {fmt}: {share:.0%}")

    lines.append("\n--- ЦЕЛИ РОСТА ---")
    for period, targets in strategy.growth_targets.items():
        lines.append(f"\n  {period}:")
        for metric, value in targets.items():
            lines.append(f"    {metric}: {value}")

    lines.append("\n--- ПРИОРИТЕТНЫЕ ДЕЙСТВИЯ ---")
    for i, action in enumerate(strategy.priority_actions, 1):
        lines.append(f"  {i}. {action}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def strategy_summary(strategy: WeeklyStrategy) -> str:
    lines: list[str] = [
        f"Контент-стратегия: {strategy.total_posts_per_week} постов/нед",
        f"Направлений: {len(strategy.pillars)}",
        f"Приоритетных действий: {len(strategy.priority_actions)}",
        "\nТоп-направления:",
    ]
    lines.extend(
        f"  #{ps.priority} {ps.pillar} ({ps.content_share:.0%})"
        for ps in strategy.pillars[:3]
    )
    lines.append("\nБлижайшие действия:")
    lines.extend(f"  -> {a}" for a in strategy.priority_actions[:3])
    return "\n".join(lines)
