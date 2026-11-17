"""Content audit — evaluates existing content quality and gaps.

Generates structured audit configs:
- Quality scoring criteria per content type
- Gap analysis dimensions
- Audit checklist items
- Performance benchmarks
- Improvement recommendations
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

QUALITY_CRITERIA: list[dict[str, str | int]] = [
    {
        "criterion": "Релевантность теме",
        "weight": 25,
        "description": "Контент соответствует столпу и целевой аудитории",
        "scoring": "1-5: 1=офтопик, 3=частично, 5=точно в цель",
    },
    {
        "criterion": "Вовлечённость",
        "weight": 20,
        "description": "Хуки, вопросы, CTA стимулируют реакцию",
        "scoring": "1-5: 1=нет CTA, 3=есть CTA, 5=сильный хук+CTA",
    },
    {
        "criterion": "Визуальное качество",
        "weight": 20,
        "description": "Графика, видео, карусели соответствуют бренд-киту",
        "scoring": "1-5: 1=нет визуала, 3=шаблон, 5=уникальный дизайн",
    },
    {
        "criterion": "SEO и хештеги",
        "weight": 15,
        "description": "Ключевые слова, хештеги, alt-тексты оптимизированы",
        "scoring": "1-5: 1=нет SEO, 3=базовый, 5=полная оптимизация",
    },
    {
        "criterion": "Конверсионный путь",
        "weight": 20,
        "description": "Контент ведёт к целевому действию (покупка, подписка)",
        "scoring": "1-5: 1=тупик, 3=ссылка в био, 5=прямой путь к конверсии",
    },
]

GAP_ANALYSIS: list[dict[str, str]] = [
    {
        "dimension": "Частота публикаций",
        "ideal": "3 поста/день на платформу",
        "gap_signal": "Менее 2 постов/день в любом канале",
        "fix": "Использовать контент-рециклер и батч-генератор",
    },
    {
        "dimension": "Баланс столпов",
        "ideal": "20% на каждый из 5 столпов",
        "gap_signal": "Любой столп < 10% или > 35%",
        "fix": "Контент-миксер: перебалансировать недельный план",
    },
    {
        "dimension": "Формат-микс",
        "ideal": "Reels 40%, Карусели 25%, Посты 20%, Сторис 15%",
        "gap_signal": "Один формат > 60% или отсутствует",
        "fix": "Добавить недостающие форматы через репёрпозер",
    },
    {
        "dimension": "Воронка покрытия",
        "ideal": "TOFU 40%, MOFU 35%, BOFU 25%",
        "gap_signal": "BOFU < 15% или TOFU < 25%",
        "fix": "Генерировать контент для слабого этапа воронки",
    },
    {
        "dimension": "Вовлечённость аудитории",
        "ideal": "ER > 3% Instagram, > 5% TikTok",
        "gap_signal": "ER падает 2 недели подряд",
        "fix": "Engagement-хуки, опросы, квизы, UGC",
    },
    {
        "dimension": "Реферальный контент",
        "ideal": "15-20% постов с реферальной ссылкой",
        "gap_signal": "Менее 10% или более 30% реферальных",
        "fix": "Контент-скоринг: приоритизировать посты с UTM",
    },
]

AUDIT_CHECKLIST: list[dict[str, str]] = [
    {
        "item": "Все посты имеют CTA",
        "category": "engagement",
        "priority": "high",
    },
    {
        "item": "Хештеги соответствуют пулу (не забанены)",
        "category": "seo",
        "priority": "high",
    },
    {
        "item": "Визуалы в бренд-ките (цвета, шрифты)",
        "category": "branding",
        "priority": "medium",
    },
    {
        "item": "UTM-метки на всех ссылках",
        "category": "tracking",
        "priority": "high",
    },
    {
        "item": "Disclosure на партнёрских постах",
        "category": "compliance",
        "priority": "high",
    },
    {
        "item": "Alt-текст на изображениях",
        "category": "accessibility",
        "priority": "medium",
    },
    {
        "item": "Подписи в рамках лимита платформы",
        "category": "platform",
        "priority": "medium",
    },
    {
        "item": "Серии контента завершены (нет обрывов)",
        "category": "content",
        "priority": "low",
    },
]

BENCHMARKS: list[dict[str, str | float]] = [
    {
        "metric": "Engagement Rate (Instagram)",
        "target": 3.0,
        "good": 5.0,
        "excellent": 8.0,
        "unit": "%",
    },
    {
        "metric": "Engagement Rate (TikTok)",
        "target": 5.0,
        "good": 8.0,
        "excellent": 12.0,
        "unit": "%",
    },
    {
        "metric": "Click-Through Rate",
        "target": 1.5,
        "good": 3.0,
        "excellent": 5.0,
        "unit": "%",
    },
    {
        "metric": "Conversion Rate",
        "target": 1.0,
        "good": 2.5,
        "excellent": 5.0,
        "unit": "%",
    },
    {
        "metric": "Saves per Post",
        "target": 50.0,
        "good": 150.0,
        "excellent": 500.0,
        "unit": "saves",
    },
]

RECOMMENDATIONS: list[dict[str, str]] = [
    {
        "area": "Низкий ER",
        "action": "Добавить опросы и квизы в сторис, задавать вопросы в подписях",
        "expected_impact": "ER +30-50% за 2 недели",
        "tools": "engagement_hooks, story_generator",
    },
    {
        "area": "Слабая конверсия",
        "action": "Усилить BOFU-контент: кейсы, отзывы, сравнения, дедлайны",
        "expected_impact": "CR +20-40% за месяц",
        "tools": "social_proof, cta_library, conversion_funnel",
    },
    {
        "area": "Дисбаланс столпов",
        "action": "Перебалансировать недельный план через content_mixer",
        "expected_impact": "Охват новых сегментов аудитории",
        "tools": "content_mixer, content_strategy",
    },
    {
        "area": "Устаревший контент",
        "action": "Обновить evergreen-контент, обновить данные и визуалы",
        "expected_impact": "Второй пик трафика на обновлённый контент",
        "tools": "content_recycler",
    },
    {
        "area": "Нет UGC",
        "action": "Запустить челлендж, запросить отзывы, репост историй клиентов",
        "expected_impact": "Доверие аудитории +40%, экономия на контенте",
        "tools": "ugc_templates, gamification",
    },
]


@dataclass(frozen=True, slots=True)
class QualityCriterion:
    criterion: str
    weight: int
    description: str
    scoring: str


@dataclass(frozen=True, slots=True)
class GapDimension:
    dimension: str
    ideal: str
    gap_signal: str
    fix: str


@dataclass(frozen=True, slots=True)
class AuditCheckItem:
    item: str
    category: str
    priority: str


@dataclass(frozen=True, slots=True)
class Benchmark:
    metric: str
    target: float
    good: float
    excellent: float
    unit: str


@dataclass(frozen=True, slots=True)
class Recommendation:
    area: str
    action: str
    expected_impact: str
    tools: str


@dataclass(frozen=True, slots=True)
class ContentAudit:
    quality_criteria: tuple[QualityCriterion, ...]
    gap_analysis: tuple[GapDimension, ...]
    checklist: tuple[AuditCheckItem, ...]
    benchmarks: tuple[Benchmark, ...]
    recommendations: tuple[Recommendation, ...]


def generate_content_audit() -> ContentAudit:
    return ContentAudit(
        quality_criteria=tuple(
            QualityCriterion(
                criterion=q["criterion"],
                weight=int(q["weight"]),
                description=q["description"],
                scoring=q["scoring"],
            )
            for q in QUALITY_CRITERIA
        ),
        gap_analysis=tuple(
            GapDimension(
                dimension=g["dimension"],
                ideal=g["ideal"],
                gap_signal=g["gap_signal"],
                fix=g["fix"],
            )
            for g in GAP_ANALYSIS
        ),
        checklist=tuple(
            AuditCheckItem(
                item=c["item"],
                category=c["category"],
                priority=c["priority"],
            )
            for c in AUDIT_CHECKLIST
        ),
        benchmarks=tuple(
            Benchmark(
                metric=b["metric"],
                target=float(b["target"]),
                good=float(b["good"]),
                excellent=float(b["excellent"]),
                unit=b["unit"],
            )
            for b in BENCHMARKS
        ),
        recommendations=tuple(
            Recommendation(
                area=r["area"],
                action=r["action"],
                expected_impact=r["expected_impact"],
                tools=r["tools"],
            )
            for r in RECOMMENDATIONS
        ),
    )


def export_audit_json(audit: ContentAudit, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "quality_criteria": [
            {
                "criterion": q.criterion,
                "weight": q.weight,
                "description": q.description,
                "scoring": q.scoring,
            }
            for q in audit.quality_criteria
        ],
        "gap_analysis": [
            {
                "dimension": g.dimension,
                "ideal": g.ideal,
                "gap_signal": g.gap_signal,
                "fix": g.fix,
            }
            for g in audit.gap_analysis
        ],
        "checklist": [
            {
                "item": c.item,
                "category": c.category,
                "priority": c.priority,
            }
            for c in audit.checklist
        ],
        "benchmarks": [
            {
                "metric": b.metric,
                "target": b.target,
                "good": b.good,
                "excellent": b.excellent,
                "unit": b.unit,
            }
            for b in audit.benchmarks
        ],
        "recommendations": [
            {
                "area": r.area,
                "action": r.action,
                "expected_impact": r.expected_impact,
                "tools": r.tools,
            }
            for r in audit.recommendations
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_audit_txt(audit: ContentAudit, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "АУДИТ КОНТЕНТА",
        "=" * 60,
        "\n📋 КРИТЕРИИ КАЧЕСТВА",
        "━" * 50,
    ]
    total_weight = sum(q.weight for q in audit.quality_criteria)
    for q in audit.quality_criteria:
        lines.append(f"\n  [{q.criterion}] вес: {q.weight}/{total_weight}")
        lines.append(f"    {q.description}")
        lines.append(f"    Оценка: {q.scoring}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🔍 ГЭП-АНАЛИЗ")
    lines.append("━" * 50)
    for g in audit.gap_analysis:
        lines.append(f"\n  [{g.dimension}]")
        lines.append(f"    Идеал: {g.ideal}")
        lines.append(f"    Сигнал: {g.gap_signal}")
        lines.append(f"    Решение: {g.fix}")

    lines.append(f"\n{'━' * 50}")
    lines.append("✅ ЧЕКЛИСТ АУДИТА")
    lines.append("━" * 50)
    for c in audit.checklist:
        prio = {"high": "!!!", "medium": "!!", "low": "!"}[c.priority]
        lines.append(f"  [{prio}] {c.item} ({c.category})")

    lines.append(f"\n{'━' * 50}")
    lines.append("📊 БЕНЧМАРКИ")
    lines.append("━" * 50)
    lines.extend(
        f"  {b.metric}: цель {b.target}{b.unit} | "
        f"хорошо {b.good}{b.unit} | отлично {b.excellent}{b.unit}"
        for b in audit.benchmarks
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("💡 РЕКОМЕНДАЦИИ")
    lines.append("━" * 50)
    for r in audit.recommendations:
        lines.append(f"\n  [{r.area}]")
        lines.append(f"    Действие: {r.action}")
        lines.append(f"    Эффект: {r.expected_impact}")
        lines.append(f"    Инструменты: {r.tools}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def audit_summary(audit: ContentAudit) -> str:
    return (
        f"Аудит контента: "
        f"{len(audit.quality_criteria)} критериев качества, "
        f"{len(audit.gap_analysis)} измерений гэпа, "
        f"{len(audit.checklist)} пунктов чеклиста, "
        f"{len(audit.benchmarks)} бенчмарков, "
        f"{len(audit.recommendations)} рекомендаций"
    )
