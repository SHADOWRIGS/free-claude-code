"""Performance benchmark — industry benchmarks for cybersecurity niche SMM.

Generates:
- Platform benchmarks (ER, growth, reach by platform)
- Niche benchmarks (cybersecurity vs general)
- Growth milestones and timelines
- Competitive positioning scores
- Performance grading rules
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

PLATFORM_BENCHMARKS: list[dict[str, str | float]] = [
    {
        "platform": "Instagram",
        "metric": "Engagement Rate",
        "poor": 1.0,
        "average": 3.0,
        "good": 5.0,
        "excellent": 8.0,
        "unit": "%",
    },
    {
        "platform": "Instagram",
        "metric": "Follower Growth Rate (weekly)",
        "poor": 0.5,
        "average": 1.5,
        "good": 3.0,
        "excellent": 5.0,
        "unit": "%",
    },
    {
        "platform": "Instagram",
        "metric": "Reach Rate",
        "poor": 10.0,
        "average": 25.0,
        "good": 40.0,
        "excellent": 60.0,
        "unit": "%",
    },
    {
        "platform": "TikTok",
        "metric": "Engagement Rate",
        "poor": 2.0,
        "average": 5.0,
        "good": 8.0,
        "excellent": 12.0,
        "unit": "%",
    },
    {
        "platform": "TikTok",
        "metric": "Follower Growth Rate (weekly)",
        "poor": 1.0,
        "average": 3.0,
        "good": 7.0,
        "excellent": 15.0,
        "unit": "%",
    },
    {
        "platform": "TikTok",
        "metric": "Video Completion Rate",
        "poor": 15.0,
        "average": 30.0,
        "good": 50.0,
        "excellent": 70.0,
        "unit": "%",
    },
    {
        "platform": "YouTube",
        "metric": "CTR (Click-Through Rate)",
        "poor": 2.0,
        "average": 5.0,
        "good": 8.0,
        "excellent": 12.0,
        "unit": "%",
    },
    {
        "platform": "YouTube",
        "metric": "Average View Duration",
        "poor": 20.0,
        "average": 40.0,
        "good": 55.0,
        "excellent": 70.0,
        "unit": "% of video",
    },
    {
        "platform": "YouTube",
        "metric": "Subscriber Conversion Rate",
        "poor": 0.5,
        "average": 2.0,
        "good": 4.0,
        "excellent": 7.0,
        "unit": "%",
    },
]

NICHE_BENCHMARKS: list[dict[str, str | float]] = [
    {
        "niche": "Cybersecurity Education",
        "metric": "Average ER (Instagram)",
        "value": 4.2,
        "general_average": 3.0,
        "advantage": "Высокая вовлечённость из-за нишевой аудитории",
    },
    {
        "niche": "Cybersecurity Education",
        "metric": "CTR to Landing",
        "value": 3.5,
        "general_average": 1.5,
        "advantage": "Целевая аудитория активно кликает на обучающий контент",
    },
    {
        "niche": "Cybersecurity Education",
        "metric": "Course Conversion Rate",
        "value": 2.8,
        "general_average": 1.0,
        "advantage": "Высокий intent: аудитория ищет конкретные навыки",
    },
    {
        "niche": "Tech Gadgets (AliExpress)",
        "metric": "Referral CTR",
        "value": 4.0,
        "general_average": 2.0,
        "advantage": "Визуальный контент гаджетов хорошо конвертирует",
    },
    {
        "niche": "Tech Gadgets (AliExpress)",
        "metric": "Average Order Value",
        "value": 35.0,
        "general_average": 25.0,
        "advantage": "Аудитория готова покупать специализированное оборудование",
    },
    {
        "niche": "Online Education (general)",
        "metric": "Email Open Rate",
        "value": 35.0,
        "general_average": 22.0,
        "advantage": "Образовательный контент хорошо открывается в email",
    },
]

GROWTH_MILESTONES: list[dict[str, str | int]] = [
    {
        "milestone": "Запуск (месяц 1-2)",
        "followers_target": 1000,
        "monthly_revenue_target": 500,
        "posts_per_week": 63,
        "focus": "Контент-машина: ежедневный постинг, тестирование форматов",
    },
    {
        "milestone": "Рост (месяц 3-4)",
        "followers_target": 5000,
        "monthly_revenue_target": 2000,
        "posts_per_week": 63,
        "focus": "Вовлечение: коллаборации, UGC, челленджи",
    },
    {
        "milestone": "Масштабирование (месяц 5-6)",
        "followers_target": 15000,
        "monthly_revenue_target": 5000,
        "posts_per_week": 63,
        "focus": "Конверсия: воронки, ретаргетинг, платная реклама",
    },
    {
        "milestone": "Оптимизация (месяц 7-9)",
        "followers_target": 30000,
        "monthly_revenue_target": 10000,
        "posts_per_week": 63,
        "focus": "ROI: аналитика, A/B тесты, апсейл, партнёрская программа",
    },
    {
        "milestone": "Лидерство (месяц 10-12)",
        "followers_target": 50000,
        "monthly_revenue_target": 20000,
        "posts_per_week": 63,
        "focus": "Автономность: команда, автоматизация, новые каналы",
    },
]

COMPETITIVE_SCORES: list[dict[str, str | int]] = [
    {
        "competitor": "HackerU",
        "content_quality": 7,
        "posting_frequency": 5,
        "engagement": 6,
        "conversion": 7,
        "brand_strength": 8,
        "total": 33,
        "weakness": "Низкая частота публикаций, мало видео",
    },
    {
        "competitor": "OffSec (Offensive Security)",
        "content_quality": 9,
        "posting_frequency": 4,
        "engagement": 5,
        "conversion": 8,
        "brand_strength": 9,
        "total": 35,
        "weakness": "Элитарность, мало контента для начинающих",
    },
    {
        "competitor": "TryHackMe",
        "content_quality": 8,
        "posting_frequency": 7,
        "engagement": 8,
        "conversion": 7,
        "brand_strength": 8,
        "total": 38,
        "weakness": "Фокус на платформе, мало персонального бренда",
    },
    {
        "competitor": "HackTheBox",
        "content_quality": 8,
        "posting_frequency": 6,
        "engagement": 7,
        "conversion": 7,
        "brand_strength": 9,
        "total": 37,
        "weakness": "Сложный контент, высокий порог входа",
    },
    {
        "competitor": "ShadowRigs (цель)",
        "content_quality": 8,
        "posting_frequency": 10,
        "engagement": 8,
        "conversion": 8,
        "brand_strength": 7,
        "total": 41,
        "weakness": "Молодой бренд, нужно время на узнаваемость",
    },
]

GRADING_RULES: list[dict[str, str | float]] = [
    {
        "grade": "A+ (выдающийся)",
        "min_score_pct": 90.0,
        "description": "Все метрики в зоне excellent, лидер ниши",
        "action": "Масштабировать успешные стратегии, выходить на новые рынки",
    },
    {
        "grade": "A (отличный)",
        "min_score_pct": 80.0,
        "description": "Большинство метрик в good/excellent",
        "action": "Оптимизировать слабые метрики, тестировать новые форматы",
    },
    {
        "grade": "B (хороший)",
        "min_score_pct": 65.0,
        "description": "Метрики на уровне average-good",
        "action": "Увеличить частоту и качество контента, работать над вовлечением",
    },
    {
        "grade": "C (средний)",
        "min_score_pct": 50.0,
        "description": "Метрики на уровне average, есть проблемные зоны",
        "action": "Пересмотреть контент-стратегию, изучить успешных конкурентов",
    },
    {
        "grade": "D (требует внимания)",
        "min_score_pct": 0.0,
        "description": "Метрики ниже average, требуется перезапуск",
        "action": "Аудит всех процессов, возможно смена стратегии",
    },
]


@dataclass(frozen=True, slots=True)
class PlatformBenchmark:
    platform: str
    metric: str
    poor: float
    average: float
    good: float
    excellent: float
    unit: str


@dataclass(frozen=True, slots=True)
class NicheBenchmark:
    niche: str
    metric: str
    value: float
    general_average: float
    advantage: str


@dataclass(frozen=True, slots=True)
class GrowthMilestone:
    milestone: str
    followers_target: int
    monthly_revenue_target: int
    posts_per_week: int
    focus: str


@dataclass(frozen=True, slots=True)
class CompetitiveScore:
    competitor: str
    content_quality: int
    posting_frequency: int
    engagement: int
    conversion: int
    brand_strength: int
    total: int
    weakness: str


@dataclass(frozen=True, slots=True)
class GradingRule:
    grade: str
    min_score_pct: float
    description: str
    action: str


@dataclass(frozen=True, slots=True)
class PerformanceBenchmark:
    platform_benchmarks: tuple[PlatformBenchmark, ...]
    niche_benchmarks: tuple[NicheBenchmark, ...]
    growth_milestones: tuple[GrowthMilestone, ...]
    competitive_scores: tuple[CompetitiveScore, ...]
    grading_rules: tuple[GradingRule, ...]


def generate_performance_benchmark() -> PerformanceBenchmark:
    return PerformanceBenchmark(
        platform_benchmarks=tuple(
            PlatformBenchmark(
                platform=pb["platform"],
                metric=pb["metric"],
                poor=float(pb["poor"]),
                average=float(pb["average"]),
                good=float(pb["good"]),
                excellent=float(pb["excellent"]),
                unit=pb["unit"],
            )
            for pb in PLATFORM_BENCHMARKS
        ),
        niche_benchmarks=tuple(
            NicheBenchmark(
                niche=nb["niche"],
                metric=nb["metric"],
                value=float(nb["value"]),
                general_average=float(nb["general_average"]),
                advantage=nb["advantage"],
            )
            for nb in NICHE_BENCHMARKS
        ),
        growth_milestones=tuple(
            GrowthMilestone(
                milestone=gm["milestone"],
                followers_target=int(gm["followers_target"]),
                monthly_revenue_target=int(gm["monthly_revenue_target"]),
                posts_per_week=int(gm["posts_per_week"]),
                focus=gm["focus"],
            )
            for gm in GROWTH_MILESTONES
        ),
        competitive_scores=tuple(
            CompetitiveScore(
                competitor=cs["competitor"],
                content_quality=int(cs["content_quality"]),
                posting_frequency=int(cs["posting_frequency"]),
                engagement=int(cs["engagement"]),
                conversion=int(cs["conversion"]),
                brand_strength=int(cs["brand_strength"]),
                total=int(cs["total"]),
                weakness=cs["weakness"],
            )
            for cs in COMPETITIVE_SCORES
        ),
        grading_rules=tuple(
            GradingRule(
                grade=gr["grade"],
                min_score_pct=float(gr["min_score_pct"]),
                description=gr["description"],
                action=gr["action"],
            )
            for gr in GRADING_RULES
        ),
    )


def export_benchmark_json(pb: PerformanceBenchmark, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "platform_benchmarks": [
            {
                "platform": b.platform,
                "metric": b.metric,
                "poor": b.poor,
                "average": b.average,
                "good": b.good,
                "excellent": b.excellent,
                "unit": b.unit,
            }
            for b in pb.platform_benchmarks
        ],
        "niche_benchmarks": [
            {
                "niche": nb.niche,
                "metric": nb.metric,
                "value": nb.value,
                "general_average": nb.general_average,
                "advantage": nb.advantage,
            }
            for nb in pb.niche_benchmarks
        ],
        "growth_milestones": [
            {
                "milestone": gm.milestone,
                "followers_target": gm.followers_target,
                "monthly_revenue_target": gm.monthly_revenue_target,
                "posts_per_week": gm.posts_per_week,
                "focus": gm.focus,
            }
            for gm in pb.growth_milestones
        ],
        "competitive_scores": [
            {
                "competitor": cs.competitor,
                "content_quality": cs.content_quality,
                "posting_frequency": cs.posting_frequency,
                "engagement": cs.engagement,
                "conversion": cs.conversion,
                "brand_strength": cs.brand_strength,
                "total": cs.total,
                "weakness": cs.weakness,
            }
            for cs in pb.competitive_scores
        ],
        "grading_rules": [
            {
                "grade": gr.grade,
                "min_score_pct": gr.min_score_pct,
                "description": gr.description,
                "action": gr.action,
            }
            for gr in pb.grading_rules
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_benchmark_txt(pb: PerformanceBenchmark, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "БЕНЧМАРКИ ПРОИЗВОДИТЕЛЬНОСТИ",
        "=" * 60,
        "\n📊 БЕНЧМАРКИ ПО ПЛАТФОРМАМ",
        "━" * 50,
    ]
    lines.extend(
        f"  [{b.platform}] {b.metric}: "
        f"poor <{b.poor} | avg {b.average} | good {b.good} | "
        f"excellent >{b.excellent} {b.unit}"
        for b in pb.platform_benchmarks
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("🎯 НИШЕВЫЕ БЕНЧМАРКИ")
    lines.append("━" * 50)
    for nb in pb.niche_benchmarks:
        lines.append(
            f"  [{nb.niche}] {nb.metric}: {nb.value} "
            f"(среднее по рынку: {nb.general_average})"
        )
        lines.append(f"    Преимущество: {nb.advantage}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📈 ВЕХИ РОСТА")
    lines.append("━" * 50)
    for gm in pb.growth_milestones:
        lines.append(
            f"\n  [{gm.milestone}] {gm.followers_target} подписчиков, "
            f"${gm.monthly_revenue_target}/мес"
        )
        lines.append(f"    Фокус: {gm.focus}")

    lines.append(f"\n{'━' * 50}")
    lines.append("⚔ КОНКУРЕНТНЫЕ ОЦЕНКИ")
    lines.append("━" * 50)
    for cs in pb.competitive_scores:
        lines.append(f"\n  [{cs.competitor}] итого: {cs.total}/50")
        lines.append(
            f"    Контент:{cs.content_quality} Частота:{cs.posting_frequency} "
            f"Вовлечение:{cs.engagement} Конверсия:{cs.conversion} "
            f"Бренд:{cs.brand_strength}"
        )
        lines.append(f"    Слабость: {cs.weakness}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🏆 СИСТЕМА ОЦЕНОК")
    lines.append("━" * 50)
    lines.extend(
        f"  [{gr.grade}] от {gr.min_score_pct}% | {gr.action}"
        for gr in pb.grading_rules
    )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def benchmark_summary(pb: PerformanceBenchmark) -> str:
    return (
        f"Бенчмарки: "
        f"{len(pb.platform_benchmarks)} платформенных метрик, "
        f"{len(pb.niche_benchmarks)} нишевых, "
        f"{len(pb.growth_milestones)} вех роста, "
        f"{len(pb.competitive_scores)} конкурентных оценок, "
        f"{len(pb.grading_rules)} правил грейдинга"
    )
