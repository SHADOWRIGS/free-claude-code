"""Pricing and ROI calculator for SMM service packages.

Generates pricing breakdowns, ROI projections, and comparison tables
for the three service tiers (Starter, Growth, Pro).
Helps potential clients understand value vs. cost.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

TIERS: list[dict[str, str | int | float]] = [
    {
        "id": "starter",
        "name": "Starter",
        "price_usd": 97,
        "posts_per_week": 21,
        "platforms": 1,
        "features": (
            "21 пост/нед на 1 платформу",
            "Подписи + хештеги",
            "Визуальные брифы",
            "Контент-календарь",
            "Еженедельный отчёт",
        ),
        "best_for": "Начинающие блогеры, фрилансеры",
    },
    {
        "id": "growth",
        "name": "Growth",
        "price_usd": 197,
        "posts_per_week": 42,
        "platforms": 2,
        "features": (
            "42 поста/нед на 2 платформы",
            "Подписи + хештеги + CTA",
            "Визуальные брифы + видео-скрипты",
            "A/B тестирование",
            "Контент-календарь + серии",
            "Еженедельный отчёт + аналитика",
        ),
        "best_for": "Растущие бренды, малый бизнес",
    },
    {
        "id": "pro",
        "name": "Pro",
        "price_usd": 397,
        "posts_per_week": 63,
        "platforms": 3,
        "features": (
            "63 поста/нед на 3 платформы",
            "Полный набор контента (подписи, скрипты, карусели, сторис)",
            "A/B тестирование + скоринг",
            "Конверсионная воронка (TOFU/MOFU/BOFU)",
            "Email-последовательности",
            "Лид-магниты + социальное доказательство",
            "Ретаргетинг-гайд",
            "Приоритетная поддержка",
        ),
        "best_for": "Агентства, средний бизнес, инфобизнес",
    },
]

INDUSTRY_BENCHMARKS: dict[str, float] = {
    "avg_cost_per_post_agency": 25.0,
    "avg_cost_per_post_freelancer": 12.0,
    "avg_engagement_rate": 0.03,
    "avg_click_rate": 0.015,
    "avg_conversion_rate": 0.02,
    "avg_customer_value_usd": 150.0,
}


@dataclass(frozen=True, slots=True)
class TierBreakdown:
    tier_id: str
    name: str
    price_usd: int
    posts_per_week: int
    platforms: int
    features: tuple[str, ...]
    best_for: str
    cost_per_post: float
    monthly_posts: int
    savings_vs_agency: float
    savings_vs_freelancer: float


@dataclass(frozen=True, slots=True)
class ROIProjection:
    tier_id: str
    monthly_impressions: int
    monthly_clicks: int
    monthly_conversions: int
    monthly_revenue: float
    monthly_cost: int
    monthly_profit: float
    roi_percent: float
    payback_days: int


def generate_tier_breakdowns() -> list[TierBreakdown]:
    results: list[TierBreakdown] = []
    for t in TIERS:
        price = int(t["price_usd"])
        ppw = int(t["posts_per_week"])
        monthly = ppw * 4
        cpp = price / monthly if monthly else 0
        agency_cost = monthly * INDUSTRY_BENCHMARKS["avg_cost_per_post_agency"]
        freelancer_cost = monthly * INDUSTRY_BENCHMARKS["avg_cost_per_post_freelancer"]

        results.append(
            TierBreakdown(
                tier_id=str(t["id"]),
                name=str(t["name"]),
                price_usd=price,
                posts_per_week=ppw,
                platforms=int(t["platforms"]),
                features=tuple(t["features"]),  # type: ignore[arg-type]
                best_for=str(t["best_for"]),
                cost_per_post=round(cpp, 2),
                monthly_posts=monthly,
                savings_vs_agency=round(agency_cost - price, 2),
                savings_vs_freelancer=round(freelancer_cost - price, 2),
            )
        )
    return results


def generate_roi_projections(
    impressions_per_post: int = 500,
) -> list[ROIProjection]:
    results: list[ROIProjection] = []
    bench = INDUSTRY_BENCHMARKS
    for t in TIERS:
        price = int(t["price_usd"])
        ppw = int(t["posts_per_week"])
        monthly_posts = ppw * 4
        impressions = monthly_posts * impressions_per_post
        clicks = int(impressions * bench["avg_click_rate"])
        conversions = int(clicks * bench["avg_conversion_rate"])
        revenue = conversions * bench["avg_customer_value_usd"]
        profit = revenue - price
        roi = (profit / price * 100) if price else 0
        payback = int(30 * price / revenue) if revenue > 0 else 999

        results.append(
            ROIProjection(
                tier_id=str(t["id"]),
                monthly_impressions=impressions,
                monthly_clicks=clicks,
                monthly_conversions=conversions,
                monthly_revenue=round(revenue, 2),
                monthly_cost=price,
                monthly_profit=round(profit, 2),
                roi_percent=round(roi, 1),
                payback_days=payback,
            )
        )
    return results


def export_pricing_json(
    tiers: list[TierBreakdown],
    roi: list[ROIProjection],
    path: Path,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "tiers": [
            {
                "id": t.tier_id,
                "name": t.name,
                "price_usd": t.price_usd,
                "posts_per_week": t.posts_per_week,
                "platforms": t.platforms,
                "features": list(t.features),
                "best_for": t.best_for,
                "cost_per_post": t.cost_per_post,
                "monthly_posts": t.monthly_posts,
                "savings_vs_agency": t.savings_vs_agency,
                "savings_vs_freelancer": t.savings_vs_freelancer,
            }
            for t in tiers
        ],
        "roi_projections": [
            {
                "tier_id": r.tier_id,
                "monthly_impressions": r.monthly_impressions,
                "monthly_clicks": r.monthly_clicks,
                "monthly_conversions": r.monthly_conversions,
                "monthly_revenue": r.monthly_revenue,
                "monthly_cost": r.monthly_cost,
                "monthly_profit": r.monthly_profit,
                "roi_percent": r.roi_percent,
                "payback_days": r.payback_days,
            }
            for r in roi
        ],
        "benchmarks": INDUSTRY_BENCHMARKS,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_pricing_txt(
    tiers: list[TierBreakdown],
    roi: list[ROIProjection],
    path: Path,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "КАЛЬКУЛЯТОР СТОИМОСТИ И ROI",
        "=" * 60,
    ]

    for t in tiers:
        lines.append(f"\n{'━' * 50}")
        lines.append(f"💰 {t.name} — ${t.price_usd}/мес")
        lines.append("━" * 50)
        lines.append(f"  Постов/нед: {t.posts_per_week}")
        lines.append(f"  Платформ: {t.platforms}")
        lines.append(f"  Стоимость за пост: ${t.cost_per_post}")
        lines.append(f"  Постов/мес: {t.monthly_posts}")
        lines.append(f"  Экономия vs агентство: ${t.savings_vs_agency}")
        lines.append(f"  Экономия vs фрилансер: ${t.savings_vs_freelancer}")
        lines.append(f"  Для кого: {t.best_for}")
        lines.append("\n  Включено:")
        lines.extend(f"    ✅ {f}" for f in t.features)

    lines.append(f"\n{'━' * 50}")
    lines.append("📈 ROI-ПРОЕКЦИЯ (при 500 показов/пост)")
    lines.append("━" * 50)

    roi_map = {r.tier_id: r for r in roi}
    for t in tiers:
        r = roi_map.get(t.tier_id)
        if r:
            lines.append(f"\n  {t.name}:")
            lines.append(f"    Показов/мес: {r.monthly_impressions:,}")
            lines.append(f"    Кликов/мес: {r.monthly_clicks:,}")
            lines.append(f"    Конверсий/мес: {r.monthly_conversions}")
            lines.append(f"    Выручка/мес: ${r.monthly_revenue:,.0f}")
            lines.append(f"    Прибыль/мес: ${r.monthly_profit:,.0f}")
            lines.append(f"    ROI: {r.roi_percent}%")
            lines.append(f"    Окупаемость: {r.payback_days} дней")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def pricing_summary(tiers: list[TierBreakdown], roi: list[ROIProjection]) -> str:
    tier_names = ", ".join(f"{t.name} (${t.price_usd})" for t in tiers)
    best_roi = max(roi, key=lambda r: r.roi_percent) if roi else None
    roi_info = (
        f", лучший ROI: {best_roi.tier_id} ({best_roi.roi_percent}%)"
        if best_roi
        else ""
    )
    return f"Тарифы: {tier_names}{roi_info}"
