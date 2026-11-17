"""Analytics report generator — structured configs for periodic reports.

Generates:
- Report sections (KPI, trends, comparisons)
- Metric definitions with targets
- Chart specifications
- Automated insight rules
- Distribution schedule
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

REPORT_SECTIONS: list[dict[str, str | int]] = [
    {
        "section": "Обзор KPI",
        "description": "Ключевые метрики за период с динамикой",
        "order": 1,
        "data_source": "analytics_dashboard + platform APIs",
        "visualization": "Карточки с трендовыми стрелками",
    },
    {
        "section": "Охват и рост аудитории",
        "description": "Подписчики, охват, показы по платформам",
        "order": 2,
        "data_source": "Instagram Insights, TikTok Analytics, YouTube Studio",
        "visualization": "Линейные графики, столбчатая диаграмма",
    },
    {
        "section": "Вовлечённость",
        "description": "ER, лайки, комментарии, сохранения, репосты",
        "order": 3,
        "data_source": "Platform APIs",
        "visualization": "Тепловая карта по дням/часам",
    },
    {
        "section": "Контент-перформанс",
        "description": "Топ-5 постов, худшие 5, по типам контента",
        "order": 4,
        "data_source": "content_scoring + platform APIs",
        "visualization": "Таблица с превью, горизонтальные бары",
    },
    {
        "section": "Конверсии и трафик",
        "description": "Клики, CTR, переходы на лендинг, регистрации",
        "order": 5,
        "data_source": "UTM-трекинг, Google Analytics, referral_analytics",
        "visualization": "Воронка, диаграмма Санки",
    },
    {
        "section": "Доход и ROI",
        "description": "Выручка, ROAS, стоимость привлечения, LTV",
        "order": 6,
        "data_source": "roi_tracker, payment gateway",
        "visualization": "Круговая диаграмма, стековый бар",
    },
    {
        "section": "Рекомендации",
        "description": "Автоматические инсайты и план действий",
        "order": 7,
        "data_source": "Правила на основе метрик",
        "visualization": "Чеклист с приоритетами",
    },
]

METRIC_DEFINITIONS: list[dict[str, str | float]] = [
    {
        "metric": "Followers Growth Rate",
        "formula": "(new_followers - unfollows) / total_followers * 100",
        "target_weekly": 2.0,
        "unit": "%",
        "direction": "up",
    },
    {
        "metric": "Engagement Rate",
        "formula": "(likes + comments + saves + shares) / reach * 100",
        "target_weekly": 5.0,
        "unit": "%",
        "direction": "up",
    },
    {
        "metric": "Click-Through Rate",
        "formula": "link_clicks / impressions * 100",
        "target_weekly": 3.0,
        "unit": "%",
        "direction": "up",
    },
    {
        "metric": "Conversion Rate",
        "formula": "purchases / link_clicks * 100",
        "target_weekly": 2.5,
        "unit": "%",
        "direction": "up",
    },
    {
        "metric": "Cost Per Acquisition",
        "formula": "total_ad_spend / new_customers",
        "target_weekly": 15.0,
        "unit": "$",
        "direction": "down",
    },
    {
        "metric": "Return on Ad Spend",
        "formula": "revenue / ad_spend",
        "target_weekly": 4.0,
        "unit": "x",
        "direction": "up",
    },
    {
        "metric": "Content Efficiency Score",
        "formula": "weighted_sum(reach, engagement, conversions) / posts_published",
        "target_weekly": 70.0,
        "unit": "pts",
        "direction": "up",
    },
    {
        "metric": "Audience Sentiment",
        "formula": "positive_mentions / (positive + negative) * 100",
        "target_weekly": 80.0,
        "unit": "%",
        "direction": "up",
    },
]

CHART_SPECS: list[dict[str, str]] = [
    {
        "chart": "KPI Dashboard Cards",
        "type": "stat_cards",
        "metrics": "Followers, ER, CTR, CR, Revenue",
        "comparison": "vs. prev week, % change",
    },
    {
        "chart": "Audience Growth",
        "type": "line",
        "metrics": "Followers by platform (IG, TT, YT)",
        "comparison": "7-day rolling average",
    },
    {
        "chart": "Engagement Heatmap",
        "type": "heatmap",
        "metrics": "ER by day of week and hour",
        "comparison": "Best vs worst slots",
    },
    {
        "chart": "Content Type Performance",
        "type": "horizontal_bar",
        "metrics": "ER by type (Reels, Carousel, Post, Story, Video)",
        "comparison": "Average ER per type",
    },
    {
        "chart": "Conversion Funnel",
        "type": "funnel",
        "metrics": "Impressions --> Clicks --> Registrations --> Purchases",
        "comparison": "Drop-off rates between stages",
    },
    {
        "chart": "Revenue by Channel",
        "type": "pie",
        "metrics": "Revenue split: IG, TT, YT, Email, Direct",
        "comparison": "vs. previous period",
    },
]

INSIGHT_RULES: list[dict[str, str]] = [
    {
        "rule": "ER Drop Alert",
        "condition": "ER < target * 0.8 for 3+ consecutive days",
        "insight": "Вовлечённость упала ниже порога. Проверьте контент-микс и время публикации.",
        "action": "Увеличить долю Reels/видео, протестировать новые хуки",
    },
    {
        "rule": "Top Performer",
        "condition": "Post ER > 2x average ER",
        "insight": "Пост значительно превысил средний ER. Проанализируйте формат и тему.",
        "action": "Создать серию аналогичного контента, репёрпозить на другие платформы",
    },
    {
        "rule": "Conversion Spike",
        "condition": "CR > target * 1.5 on specific day",
        "insight": "Конверсия резко выросла. Определите источник трафика.",
        "action": "Масштабировать рекламу на этот источник, повторить оффер",
    },
    {
        "rule": "Audience Shift",
        "condition": "New follower demographics changed > 10%",
        "insight": "Демография новых подписчиков изменилась. Контент привлекает новую аудиторию.",
        "action": "Пересмотреть персоны, адаптировать контент или отсечь нецелевых",
    },
    {
        "rule": "Budget Efficiency",
        "condition": "CPA > target * 1.3 for 7+ days",
        "insight": "Стоимость привлечения превышает норму. Рекламные кампании неэффективны.",
        "action": "Пересмотреть таргетинг, обновить креативы, перераспределить бюджет",
    },
]

DISTRIBUTION_SCHEDULE: list[dict[str, str]] = [
    {
        "report": "Ежедневный дайджест",
        "frequency": "Каждый день в 09:00",
        "recipients": "Владелец",
        "channel": "Telegram-бот",
        "content": "KPI карточки + топ-пост + алерты",
    },
    {
        "report": "Недельный отчёт",
        "frequency": "Понедельник 10:00",
        "recipients": "Владелец, команда",
        "channel": "Email + PDF",
        "content": "Полный отчёт: все 7 секций",
    },
    {
        "report": "Месячный обзор",
        "frequency": "1-е число месяца",
        "recipients": "Владелец, инвесторы, партнёры",
        "channel": "Email + PDF + Dashboard link",
        "content": "Итоги месяца, тренды, ROI, план на следующий месяц",
    },
    {
        "report": "Алерт (по событию)",
        "frequency": "Real-time",
        "recipients": "Владелец",
        "channel": "Telegram push",
        "content": "Критические алерты: ER drop, negative spike, budget overrun",
    },
]


@dataclass(frozen=True, slots=True)
class ReportSection:
    section: str
    description: str
    order: int
    data_source: str
    visualization: str


@dataclass(frozen=True, slots=True)
class MetricDefinition:
    metric: str
    formula: str
    target_weekly: float
    unit: str
    direction: str


@dataclass(frozen=True, slots=True)
class ChartSpec:
    chart: str
    type: str
    metrics: str
    comparison: str


@dataclass(frozen=True, slots=True)
class InsightRule:
    rule: str
    condition: str
    insight: str
    action: str


@dataclass(frozen=True, slots=True)
class DistributionEntry:
    report: str
    frequency: str
    recipients: str
    channel: str
    content: str


@dataclass(frozen=True, slots=True)
class AnalyticsReportGen:
    sections: tuple[ReportSection, ...]
    metric_definitions: tuple[MetricDefinition, ...]
    chart_specs: tuple[ChartSpec, ...]
    insight_rules: tuple[InsightRule, ...]
    distribution_schedule: tuple[DistributionEntry, ...]


def generate_analytics_report_gen() -> AnalyticsReportGen:
    return AnalyticsReportGen(
        sections=tuple(
            ReportSection(
                section=rs["section"],
                description=rs["description"],
                order=int(rs["order"]),
                data_source=rs["data_source"],
                visualization=rs["visualization"],
            )
            for rs in REPORT_SECTIONS
        ),
        metric_definitions=tuple(
            MetricDefinition(
                metric=md["metric"],
                formula=md["formula"],
                target_weekly=float(md["target_weekly"]),
                unit=md["unit"],
                direction=md["direction"],
            )
            for md in METRIC_DEFINITIONS
        ),
        chart_specs=tuple(
            ChartSpec(
                chart=cs["chart"],
                type=cs["type"],
                metrics=cs["metrics"],
                comparison=cs["comparison"],
            )
            for cs in CHART_SPECS
        ),
        insight_rules=tuple(
            InsightRule(
                rule=ir["rule"],
                condition=ir["condition"],
                insight=ir["insight"],
                action=ir["action"],
            )
            for ir in INSIGHT_RULES
        ),
        distribution_schedule=tuple(
            DistributionEntry(
                report=de["report"],
                frequency=de["frequency"],
                recipients=de["recipients"],
                channel=de["channel"],
                content=de["content"],
            )
            for de in DISTRIBUTION_SCHEDULE
        ),
    )


def export_report_gen_json(ar: AnalyticsReportGen, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "sections": [
            {
                "section": rs.section,
                "description": rs.description,
                "order": rs.order,
                "data_source": rs.data_source,
                "visualization": rs.visualization,
            }
            for rs in ar.sections
        ],
        "metric_definitions": [
            {
                "metric": md.metric,
                "formula": md.formula,
                "target_weekly": md.target_weekly,
                "unit": md.unit,
                "direction": md.direction,
            }
            for md in ar.metric_definitions
        ],
        "chart_specs": [
            {
                "chart": cs.chart,
                "type": cs.type,
                "metrics": cs.metrics,
                "comparison": cs.comparison,
            }
            for cs in ar.chart_specs
        ],
        "insight_rules": [
            {
                "rule": ir.rule,
                "condition": ir.condition,
                "insight": ir.insight,
                "action": ir.action,
            }
            for ir in ar.insight_rules
        ],
        "distribution_schedule": [
            {
                "report": de.report,
                "frequency": de.frequency,
                "recipients": de.recipients,
                "channel": de.channel,
                "content": de.content,
            }
            for de in ar.distribution_schedule
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_report_gen_txt(ar: AnalyticsReportGen, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "ГЕНЕРАТОР АНАЛИТИЧЕСКИХ ОТЧЁТОВ",
        "=" * 60,
        "\n📊 СЕКЦИИ ОТЧЁТА",
        "━" * 50,
    ]
    for rs in ar.sections:
        lines.append(f"\n  {rs.order}. [{rs.section}]")
        lines.append(f"     {rs.description}")
        lines.append(f"     Визуализация: {rs.visualization}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📈 МЕТРИКИ")
    lines.append("━" * 50)
    for md in ar.metric_definitions:
        arrow = "↑" if md.direction == "up" else "↓"
        lines.append(f"  [{md.metric}] цель: {md.target_weekly}{md.unit} {arrow}")
        lines.append(f"    Формула: {md.formula}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📉 ГРАФИКИ")
    lines.append("━" * 50)
    lines.extend(
        f"  [{cs.chart}] тип: {cs.type} | {cs.comparison}" for cs in ar.chart_specs
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("💡 ПРАВИЛА ИНСАЙТОВ")
    lines.append("━" * 50)
    for ir in ar.insight_rules:
        lines.append(f"\n  [{ir.rule}]")
        lines.append(f"    Условие: {ir.condition}")
        lines.append(f"    Действие: {ir.action}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📬 РАСПИСАНИЕ РАССЫЛКИ")
    lines.append("━" * 50)
    lines.extend(
        f"  [{de.report}] {de.frequency} | {de.channel}"
        for de in ar.distribution_schedule
    )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def report_gen_summary(ar: AnalyticsReportGen) -> str:
    return (
        f"Аналитические отчёты: "
        f"{len(ar.sections)} секций, "
        f"{len(ar.metric_definitions)} метрик, "
        f"{len(ar.chart_specs)} графиков, "
        f"{len(ar.insight_rules)} правил инсайтов, "
        f"{len(ar.distribution_schedule)} каналов доставки"
    )
