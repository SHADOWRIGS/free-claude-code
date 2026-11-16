"""Analytics dashboard data — KPI tracking, ROI reports, growth metrics.

Generates structured analytics data for:
- Weekly/monthly KPI snapshots (followers, engagement, conversions)
- ROI per pillar and per platform
- Growth rate projections
- Funnel conversion metrics
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

PLATFORMS: tuple[str, ...] = ("instagram", "tiktok", "youtube")
PILLARS: tuple[str, ...] = (
    "Cyber Security & Ethical Hacking",
    "Blue Team / Defensive Security",
    "Red Team / Offensive Security",
    "Machine Learning & AI",
    "AliExpress — Гаджеты",
)

KPI_NAMES: tuple[str, ...] = (
    "followers",
    "impressions",
    "reach",
    "engagement_rate",
    "clicks",
    "conversions",
    "revenue_usd",
    "cost_per_lead",
    "customer_acquisition_cost",
    "lifetime_value",
)

KPI_LABELS: dict[str, str] = {
    "followers": "Подписчики",
    "impressions": "Показы",
    "reach": "Охват",
    "engagement_rate": "Вовлечённость (%)",
    "clicks": "Клики",
    "conversions": "Конверсии",
    "revenue_usd": "Доход ($)",
    "cost_per_lead": "Цена лида ($)",
    "customer_acquisition_cost": "CAC ($)",
    "lifetime_value": "LTV ($)",
}


@dataclass(frozen=True, slots=True)
class KPISnapshot:
    platform: str
    period: str
    followers: int
    impressions: int
    reach: int
    engagement_rate: float
    clicks: int
    conversions: int
    revenue_usd: float
    cost_per_lead: float
    cac: float
    ltv: float


@dataclass(frozen=True, slots=True)
class PillarROI:
    pillar: str
    total_posts: int
    total_impressions: int
    total_clicks: int
    total_conversions: int
    revenue_usd: float
    cost_usd: float
    roi_percent: float
    top_format: str


@dataclass(frozen=True, slots=True)
class GrowthProjection:
    platform: str
    current_followers: int
    monthly_growth_rate: float
    projected_3m: int
    projected_6m: int
    projected_12m: int


@dataclass(frozen=True, slots=True)
class AnalyticsDashboard:
    kpis: tuple[KPISnapshot, ...]
    pillar_roi: tuple[PillarROI, ...]
    growth: tuple[GrowthProjection, ...]


def generate_kpi_snapshots(
    seed: int | None = None,
) -> tuple[KPISnapshot, ...]:
    rng = random.Random(seed)
    snapshots: list[KPISnapshot] = []
    for platform in PLATFORMS:
        base_followers = rng.randint(1000, 15000)
        base_impressions = base_followers * rng.randint(5, 15)
        for period in ("week_1", "week_2", "week_3", "week_4"):
            growth = 1.0 + rng.uniform(0.02, 0.08)
            followers = int(base_followers * growth)
            impressions = int(base_impressions * growth)
            reach = int(impressions * rng.uniform(0.6, 0.85))
            eng_rate = round(rng.uniform(1.5, 8.0), 2)
            clicks = int(impressions * rng.uniform(0.01, 0.05))
            conversions = int(clicks * rng.uniform(0.02, 0.10))
            revenue = round(conversions * rng.uniform(47.0, 197.0), 2)
            cpl = round(rng.uniform(2.0, 15.0), 2)
            cac = round(cpl * rng.uniform(3.0, 8.0), 2)
            ltv = round(rng.uniform(150.0, 600.0), 2)

            snapshots.append(
                KPISnapshot(
                    platform=platform,
                    period=period,
                    followers=followers,
                    impressions=impressions,
                    reach=reach,
                    engagement_rate=eng_rate,
                    clicks=clicks,
                    conversions=conversions,
                    revenue_usd=revenue,
                    cost_per_lead=cpl,
                    cac=cac,
                    ltv=ltv,
                )
            )
            base_followers = followers
            base_impressions = impressions
    return tuple(snapshots)


def generate_pillar_roi(seed: int | None = None) -> tuple[PillarROI, ...]:
    rng = random.Random(seed)
    formats = ("карусель", "рилс", "сторис", "видео", "пост")
    results: list[PillarROI] = []
    for pillar in PILLARS:
        posts = rng.randint(30, 70)
        impressions = posts * rng.randint(500, 3000)
        clicks = int(impressions * rng.uniform(0.015, 0.045))
        conversions = int(clicks * rng.uniform(0.03, 0.12))
        revenue = round(conversions * rng.uniform(47.0, 397.0), 2)
        cost = round(posts * rng.uniform(2.0, 8.0), 2)
        roi = round(((revenue - cost) / cost) * 100, 1) if cost > 0 else 0.0
        results.append(
            PillarROI(
                pillar=pillar,
                total_posts=posts,
                total_impressions=impressions,
                total_clicks=clicks,
                total_conversions=conversions,
                revenue_usd=revenue,
                cost_usd=cost,
                roi_percent=roi,
                top_format=rng.choice(formats),
            )
        )
    return tuple(results)


def generate_growth_projections(
    seed: int | None = None,
) -> tuple[GrowthProjection, ...]:
    rng = random.Random(seed)
    projections: list[GrowthProjection] = []
    for platform in PLATFORMS:
        current = rng.randint(2000, 20000)
        rate = round(rng.uniform(0.05, 0.20), 3)
        proj_3 = int(current * (1 + rate) ** 3)
        proj_6 = int(current * (1 + rate) ** 6)
        proj_12 = int(current * (1 + rate) ** 12)
        projections.append(
            GrowthProjection(
                platform=platform,
                current_followers=current,
                monthly_growth_rate=rate,
                projected_3m=proj_3,
                projected_6m=proj_6,
                projected_12m=proj_12,
            )
        )
    return tuple(projections)


def generate_analytics_dashboard(
    seed: int | None = None,
) -> AnalyticsDashboard:
    return AnalyticsDashboard(
        kpis=generate_kpi_snapshots(seed),
        pillar_roi=generate_pillar_roi(seed),
        growth=generate_growth_projections(seed),
    )


def export_analytics_dashboard_json(dashboard: AnalyticsDashboard, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "kpis": [
            {
                "platform": k.platform,
                "period": k.period,
                "followers": k.followers,
                "impressions": k.impressions,
                "reach": k.reach,
                "engagement_rate": k.engagement_rate,
                "clicks": k.clicks,
                "conversions": k.conversions,
                "revenue_usd": k.revenue_usd,
                "cost_per_lead": k.cost_per_lead,
                "cac": k.cac,
                "ltv": k.ltv,
            }
            for k in dashboard.kpis
        ],
        "pillar_roi": [
            {
                "pillar": r.pillar,
                "total_posts": r.total_posts,
                "total_impressions": r.total_impressions,
                "total_clicks": r.total_clicks,
                "total_conversions": r.total_conversions,
                "revenue_usd": r.revenue_usd,
                "cost_usd": r.cost_usd,
                "roi_percent": r.roi_percent,
                "top_format": r.top_format,
            }
            for r in dashboard.pillar_roi
        ],
        "growth_projections": [
            {
                "platform": g.platform,
                "current_followers": g.current_followers,
                "monthly_growth_rate": g.monthly_growth_rate,
                "projected_3m": g.projected_3m,
                "projected_6m": g.projected_6m,
                "projected_12m": g.projected_12m,
            }
            for g in dashboard.growth
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_analytics_dashboard_txt(dashboard: AnalyticsDashboard, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "АНАЛИТИЧЕСКИЙ ДАШБОРД — KPI И ROI",
        "=" * 60,
        "\n📊 KPI ПО ПЛАТФОРМАМ (НЕДЕЛЬНЫЕ)",
        "━" * 50,
    ]
    lines.extend(
        f"  {k.platform:<12} {k.period:<8} "
        f"👥{k.followers:>6}  👁{k.impressions:>7}  "
        f"📈{k.engagement_rate:.1f}%  💰${k.revenue_usd:.0f}"
        for k in dashboard.kpis
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("💰 ROI ПО НАПРАВЛЕНИЯМ")
    lines.append("━" * 50)
    for r in dashboard.pillar_roi:
        lines.append(f"\n  [{r.pillar}]")
        lines.append(f"    Постов: {r.total_posts} | Показы: {r.total_impressions:,}")
        lines.append(f"    Клики: {r.total_clicks} → Конверсии: {r.total_conversions}")
        lines.append(
            f"    Доход: ${r.revenue_usd:.0f} | Расход: ${r.cost_usd:.0f} | "
            f"ROI: {r.roi_percent:.0f}%"
        )
        lines.append(f"    Лучший формат: {r.top_format}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📈 ПРОГНОЗ РОСТА")
    lines.append("━" * 50)
    for g in dashboard.growth:
        lines.append(f"\n  [{g.platform}]")
        lines.append(
            f"    Сейчас: {g.current_followers:,} | "
            f"Рост: {g.monthly_growth_rate:.1%}/мес"
        )
        lines.append(
            f"    3 мес: {g.projected_3m:,} | "
            f"6 мес: {g.projected_6m:,} | "
            f"12 мес: {g.projected_12m:,}"
        )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def analytics_dashboard_summary(dashboard: AnalyticsDashboard) -> str:
    total_revenue = sum(k.revenue_usd for k in dashboard.kpis)
    total_conversions = sum(k.conversions for k in dashboard.kpis)
    avg_roi = (
        sum(r.roi_percent for r in dashboard.pillar_roi) / len(dashboard.pillar_roi)
        if dashboard.pillar_roi
        else 0
    )
    return (
        f"Дашборд: {len(dashboard.kpis)} KPI-снимков, "
        f"{len(dashboard.pillar_roi)} направлений ROI, "
        f"{total_conversions} конверсий, "
        f"${total_revenue:.0f} дохода, "
        f"средний ROI {avg_roi:.0f}%"
    )
