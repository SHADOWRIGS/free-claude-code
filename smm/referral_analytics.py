"""Referral analytics — simulated UTM performance reports.

Generates campaign-level analytics for each product vertical
(courses + AliExpress gadgets) across all platforms. Reports
include clicks, conversions, revenue, and ROI by UTM source.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

PRODUCTS: list[dict[str, str]] = [
    {
        "id": "cyber-security",
        "name": "Cyber Security & Ethical Hacking",
        "type": "course",
        "price": "297",
    },
    {
        "id": "blue-team",
        "name": "Blue Team / Defensive Security",
        "type": "course",
        "price": "247",
    },
    {
        "id": "red-team",
        "name": "Red Team / Offensive Security",
        "type": "course",
        "price": "347",
    },
    {
        "id": "ml-ai",
        "name": "Machine Learning & AI",
        "type": "course",
        "price": "197",
    },
    {
        "id": "aliexpress-gadgets",
        "name": "AliExpress — Гаджеты",
        "type": "referral",
        "price": "35",
    },
]

PLATFORMS = ("instagram", "tiktok", "youtube")

UTM_CAMPAIGNS = ("organic", "stories", "reels", "bio_link", "cross_promo", "email")


@dataclass(frozen=True, slots=True)
class CampaignMetric:
    product_id: str
    product_name: str
    product_type: str
    platform: str
    utm_campaign: str
    impressions: int
    clicks: int
    conversions: int
    revenue: float
    cost: float
    ctr: float
    conversion_rate: float
    roas: float


def generate_campaign_metrics(
    seed: int | None = None,
) -> list[CampaignMetric]:
    rng = random.Random(seed)
    metrics: list[CampaignMetric] = []

    for product in PRODUCTS:
        for platform in PLATFORMS:
            for campaign in UTM_CAMPAIGNS:
                impressions = rng.randint(500, 15000)
                ctr_base = {
                    "instagram": 0.035,
                    "tiktok": 0.045,
                    "youtube": 0.025,
                }[platform]
                ctr = ctr_base * rng.uniform(0.6, 1.8)
                clicks = max(1, int(impressions * ctr))

                conv_base = 0.03 if product["type"] == "course" else 0.06
                conv_rate = conv_base * rng.uniform(0.4, 2.2)
                conversions = max(0, int(clicks * conv_rate))

                price = float(product["price"])
                commission = price if product["type"] == "course" else price * 0.08
                revenue = round(conversions * commission, 2)

                cost = round(clicks * rng.uniform(0.15, 0.80), 2)
                roas = round(revenue / cost, 2) if cost > 0 else 0.0

                metrics.append(
                    CampaignMetric(
                        product_id=product["id"],
                        product_name=product["name"],
                        product_type=product["type"],
                        platform=platform,
                        utm_campaign=campaign,
                        impressions=impressions,
                        clicks=clicks,
                        conversions=conversions,
                        revenue=revenue,
                        cost=cost,
                        ctr=round(ctr * 100, 2),
                        conversion_rate=round(conv_rate * 100, 2),
                        roas=roas,
                    )
                )

    return metrics


@dataclass(frozen=True, slots=True)
class ProductSummary:
    product_id: str
    product_name: str
    total_impressions: int
    total_clicks: int
    total_conversions: int
    total_revenue: float
    total_cost: float
    avg_ctr: float
    avg_conversion_rate: float
    roas: float
    best_platform: str
    best_campaign: str


def summarize_by_product(
    metrics: list[CampaignMetric],
) -> list[ProductSummary]:
    grouped: dict[str, list[CampaignMetric]] = {}
    for m in metrics:
        grouped.setdefault(m.product_id, []).append(m)

    summaries: list[ProductSummary] = []
    for pid, items in grouped.items():
        total_imp = sum(m.impressions for m in items)
        total_clicks = sum(m.clicks for m in items)
        total_conv = sum(m.conversions for m in items)
        total_rev = round(sum(m.revenue for m in items), 2)
        total_cost = round(sum(m.cost for m in items), 2)
        avg_ctr = round(total_clicks / total_imp * 100, 2) if total_imp else 0.0
        avg_cr = round(total_conv / total_clicks * 100, 2) if total_clicks else 0.0
        roas = round(total_rev / total_cost, 2) if total_cost > 0 else 0.0

        by_platform: dict[str, float] = {}
        by_campaign: dict[str, float] = {}
        for m in items:
            by_platform[m.platform] = by_platform.get(m.platform, 0) + m.revenue
            by_campaign[m.utm_campaign] = by_campaign.get(m.utm_campaign, 0) + m.revenue

        best_plat = max(by_platform, key=lambda k: by_platform[k])
        best_camp = max(by_campaign, key=lambda k: by_campaign[k])

        summaries.append(
            ProductSummary(
                product_id=pid,
                product_name=items[0].product_name,
                total_impressions=total_imp,
                total_clicks=total_clicks,
                total_conversions=total_conv,
                total_revenue=total_rev,
                total_cost=total_cost,
                avg_ctr=avg_ctr,
                avg_conversion_rate=avg_cr,
                roas=roas,
                best_platform=best_plat,
                best_campaign=best_camp,
            )
        )

    return summaries


def export_analytics_json(metrics: list[CampaignMetric], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "product_id": m.product_id,
            "product_name": m.product_name,
            "product_type": m.product_type,
            "platform": m.platform,
            "utm_campaign": m.utm_campaign,
            "impressions": m.impressions,
            "clicks": m.clicks,
            "conversions": m.conversions,
            "revenue": m.revenue,
            "cost": m.cost,
            "ctr": m.ctr,
            "conversion_rate": m.conversion_rate,
            "roas": m.roas,
        }
        for m in metrics
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_analytics_txt(metrics: list[CampaignMetric], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    summaries = summarize_by_product(metrics)

    lines: list[str] = [
        "=" * 60,
        "АНАЛИТИКА РЕФЕРАЛЬНЫХ КАМПАНИЙ",
        "=" * 60,
    ]

    for s in summaries:
        lines.append(f"\n{'━' * 50}")
        lines.append(f"📊 {s.product_name}")
        lines.append(f"{'━' * 50}")
        lines.append(f"  Показы: {s.total_impressions:,}")
        lines.append(f"  Клики: {s.total_clicks:,}")
        lines.append(f"  Конверсии: {s.total_conversions:,}")
        lines.append(f"  Выручка: ${s.total_revenue:,.2f}")
        lines.append(f"  Затраты: ${s.total_cost:,.2f}")
        lines.append(f"  CTR: {s.avg_ctr}%")
        lines.append(f"  Конверсия: {s.avg_conversion_rate}%")
        lines.append(f"  ROAS: {s.roas}x")
        lines.append(f"  Лучшая платформа: {s.best_platform}")
        lines.append(f"  Лучшая кампания: {s.best_campaign}")

    total_rev = sum(s.total_revenue for s in summaries)
    total_cost = sum(s.total_cost for s in summaries)
    total_roas = round(total_rev / total_cost, 2) if total_cost > 0 else 0.0
    lines.append(f"\n{'=' * 60}")
    lines.append(
        f"ИТОГО: ${total_rev:,.2f} выручка | ${total_cost:,.2f} затраты | ROAS {total_roas}x"
    )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def analytics_summary(metrics: list[CampaignMetric]) -> str:
    if not metrics:
        return "Аналитика: 0 кампаний"

    summaries = summarize_by_product(metrics)
    total_rev = sum(s.total_revenue for s in summaries)
    total_cost = sum(s.total_cost for s in summaries)
    total_conv = sum(s.total_conversions for s in summaries)
    roas = round(total_rev / total_cost, 2) if total_cost > 0 else 0.0

    lines: list[str] = [
        f"Аналитика: {len(metrics)} кампаний, {len(summaries)} продуктов",
        f"Общая выручка: ${total_rev:,.2f}",
        f"Общие затраты: ${total_cost:,.2f}",
        f"Конверсии: {total_conv:,}",
        f"ROAS: {roas}x",
        "\nПо продуктам:",
    ]
    lines.extend(
        f"  {s.product_name}: ${s.total_revenue:,.2f} (ROAS {s.roas}x, лучшая: {s.best_platform})"
        for s in summaries
    )
    return "\n".join(lines)
