"""ROI tracker — return on investment tracking per channel and campaign.

Generates structured ROI configs:
- Revenue streams per product
- Cost categories (content, ads, tools)
- ROI formulas and targets
- Monthly projection templates
- Break-even analysis per channel
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

REVENUE_STREAMS: list[dict[str, str | float]] = [
    {
        "id": "cyber_course",
        "name": "Курс Cyber Security & Ethical Hacking",
        "type": "course",
        "avg_price_usd": 197.0,
        "margin_pct": 85.0,
    },
    {
        "id": "blue_course",
        "name": "Курс Blue Team / Defensive Security",
        "type": "course",
        "avg_price_usd": 197.0,
        "margin_pct": 85.0,
    },
    {
        "id": "red_course",
        "name": "Курс Red Team / Offensive Security",
        "type": "course",
        "avg_price_usd": 197.0,
        "margin_pct": 85.0,
    },
    {
        "id": "ml_course",
        "name": "Курс Machine Learning & AI",
        "type": "course",
        "avg_price_usd": 197.0,
        "margin_pct": 85.0,
    },
    {
        "id": "ali_referral",
        "name": "Реферальные комиссии AliExpress",
        "type": "affiliate",
        "avg_price_usd": 8.5,
        "margin_pct": 100.0,
    },
    {
        "id": "smm_service",
        "name": "SMM-услуга (подписка)",
        "type": "service",
        "avg_price_usd": 197.0,
        "margin_pct": 70.0,
    },
]

COST_CATEGORIES: list[dict[str, str | float]] = [
    {
        "id": "content_production",
        "name": "Создание контента",
        "type": "fixed",
        "monthly_usd": 200.0,
        "description": "AI-генерация, Canva Pro, стоки",
    },
    {
        "id": "paid_ads",
        "name": "Платная реклама",
        "type": "variable",
        "monthly_usd": 500.0,
        "description": "Meta Ads, TikTok Ads, YouTube Ads",
    },
    {
        "id": "tools",
        "name": "Инструменты и сервисы",
        "type": "fixed",
        "monthly_usd": 100.0,
        "description": "Buffer, аналитика, хостинг",
    },
    {
        "id": "influencer",
        "name": "Инфлюенсер-коллаборации",
        "type": "variable",
        "monthly_usd": 300.0,
        "description": "Оплата блогерам и рекламным интеграциям",
    },
    {
        "id": "team",
        "name": "Команда (если есть)",
        "type": "fixed",
        "monthly_usd": 0.0,
        "description": "Контент-мейкер, дизайнер, менеджер",
    },
]

CHANNEL_ROI: list[dict[str, str | float]] = [
    {
        "channel": "Instagram",
        "monthly_reach": 50000,
        "conversion_rate_pct": 1.5,
        "avg_cac_usd": 12.0,
        "target_roas": 3.0,
    },
    {
        "channel": "TikTok",
        "monthly_reach": 100000,
        "conversion_rate_pct": 0.8,
        "avg_cac_usd": 8.0,
        "target_roas": 4.0,
    },
    {
        "channel": "YouTube",
        "monthly_reach": 20000,
        "conversion_rate_pct": 3.0,
        "avg_cac_usd": 25.0,
        "target_roas": 5.0,
    },
    {
        "channel": "Telegram",
        "monthly_reach": 10000,
        "conversion_rate_pct": 5.0,
        "avg_cac_usd": 5.0,
        "target_roas": 8.0,
    },
    {
        "channel": "Email",
        "monthly_reach": 5000,
        "conversion_rate_pct": 4.0,
        "avg_cac_usd": 2.0,
        "target_roas": 10.0,
    },
]

MONTHLY_PROJECTIONS: list[dict[str, str | float]] = [
    {
        "month": "Месяц 1",
        "subscribers": 500,
        "leads": 50,
        "sales": 3,
        "revenue_usd": 591.0,
    },
    {
        "month": "Месяц 2",
        "subscribers": 1500,
        "leads": 150,
        "sales": 10,
        "revenue_usd": 1970.0,
    },
    {
        "month": "Месяц 3",
        "subscribers": 3000,
        "leads": 300,
        "sales": 25,
        "revenue_usd": 4925.0,
    },
    {
        "month": "Месяц 6",
        "subscribers": 10000,
        "leads": 1000,
        "sales": 80,
        "revenue_usd": 15760.0,
    },
    {
        "month": "Месяц 12",
        "subscribers": 30000,
        "leads": 3000,
        "sales": 250,
        "revenue_usd": 49250.0,
    },
]

ROI_FORMULAS: dict[str, str] = {
    "ROI": "(Revenue - Cost) / Cost x 100%",
    "ROAS": "Revenue / Ad Spend",
    "CAC": "Total Marketing Cost / New Customers",
    "LTV": "Avg Order Value x Purchase Frequency x Customer Lifespan",
    "LTV:CAC": "LTV / CAC (target: > 3:1)",
    "Break-even": "Fixed Costs / (Avg Price - Variable Cost per Sale)",
}


@dataclass(frozen=True, slots=True)
class RevenueStream:
    id: str
    name: str
    type: str
    avg_price_usd: float
    margin_pct: float


@dataclass(frozen=True, slots=True)
class CostCategory:
    id: str
    name: str
    type: str
    monthly_usd: float
    description: str


@dataclass(frozen=True, slots=True)
class ChannelROI:
    channel: str
    monthly_reach: int
    conversion_rate_pct: float
    avg_cac_usd: float
    target_roas: float


@dataclass(frozen=True, slots=True)
class MonthlyProjection:
    month: str
    subscribers: int
    leads: int
    sales: int
    revenue_usd: float


@dataclass(frozen=True, slots=True)
class ROITracker:
    revenue_streams: tuple[RevenueStream, ...]
    cost_categories: tuple[CostCategory, ...]
    channel_roi: tuple[ChannelROI, ...]
    projections: tuple[MonthlyProjection, ...]
    formulas: dict[str, str]
    total_monthly_cost: float
    break_even_sales: int


def generate_roi_tracker() -> ROITracker:
    costs = tuple(
        CostCategory(
            id=c["id"],
            name=c["name"],
            type=c["type"],
            monthly_usd=float(c["monthly_usd"]),
            description=c["description"],
        )
        for c in COST_CATEGORIES
    )
    total_cost = sum(c.monthly_usd for c in costs)
    avg_price = 197.0
    break_even = int(total_cost / avg_price) + 1 if avg_price > 0 else 0

    return ROITracker(
        revenue_streams=tuple(
            RevenueStream(
                id=r["id"],
                name=r["name"],
                type=r["type"],
                avg_price_usd=float(r["avg_price_usd"]),
                margin_pct=float(r["margin_pct"]),
            )
            for r in REVENUE_STREAMS
        ),
        cost_categories=costs,
        channel_roi=tuple(
            ChannelROI(
                channel=ch["channel"],
                monthly_reach=int(ch["monthly_reach"]),
                conversion_rate_pct=float(ch["conversion_rate_pct"]),
                avg_cac_usd=float(ch["avg_cac_usd"]),
                target_roas=float(ch["target_roas"]),
            )
            for ch in CHANNEL_ROI
        ),
        projections=tuple(
            MonthlyProjection(
                month=p["month"],
                subscribers=int(p["subscribers"]),
                leads=int(p["leads"]),
                sales=int(p["sales"]),
                revenue_usd=float(p["revenue_usd"]),
            )
            for p in MONTHLY_PROJECTIONS
        ),
        formulas=dict(ROI_FORMULAS),
        total_monthly_cost=total_cost,
        break_even_sales=break_even,
    )


def export_roi_json(rt: ROITracker, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "revenue_streams": [
            {
                "id": r.id,
                "name": r.name,
                "type": r.type,
                "avg_price_usd": r.avg_price_usd,
                "margin_pct": r.margin_pct,
            }
            for r in rt.revenue_streams
        ],
        "cost_categories": [
            {
                "id": c.id,
                "name": c.name,
                "type": c.type,
                "monthly_usd": c.monthly_usd,
                "description": c.description,
            }
            for c in rt.cost_categories
        ],
        "channel_roi": [
            {
                "channel": ch.channel,
                "monthly_reach": ch.monthly_reach,
                "conversion_rate_pct": ch.conversion_rate_pct,
                "avg_cac_usd": ch.avg_cac_usd,
                "target_roas": ch.target_roas,
            }
            for ch in rt.channel_roi
        ],
        "projections": [
            {
                "month": p.month,
                "subscribers": p.subscribers,
                "leads": p.leads,
                "sales": p.sales,
                "revenue_usd": p.revenue_usd,
            }
            for p in rt.projections
        ],
        "formulas": rt.formulas,
        "total_monthly_cost": rt.total_monthly_cost,
        "break_even_sales": rt.break_even_sales,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_roi_txt(rt: ROITracker, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "ROI-ТРЕКЕР — ОТСЛЕЖИВАНИЕ ВОЗВРАТА ИНВЕСТИЦИЙ",
        "=" * 60,
        "\n💰 ПОТОКИ ДОХОДА",
        "━" * 50,
    ]
    for r in rt.revenue_streams:
        lines.append(f"\n  [{r.id}] {r.name}")
        lines.append(
            f"    Средняя цена: ${r.avg_price_usd:.0f} | Маржа: {r.margin_pct:.0f}%"
        )

    lines.append(f"\n{'━' * 50}")
    lines.append("📊 КАТЕГОРИИ РАСХОДОВ")
    lines.append("━" * 50)
    for c in rt.cost_categories:
        lines.append(f"\n  [{c.id}] {c.name} ({c.type})")
        lines.append(f"    ${c.monthly_usd:.0f}/мес — {c.description}")
    lines.append(f"\n  ИТОГО: ${rt.total_monthly_cost:.0f}/мес")

    lines.append(f"\n{'━' * 50}")
    lines.append("📈 ROI ПО КАНАЛАМ")
    lines.append("━" * 50)
    for ch in rt.channel_roi:
        lines.append(f"\n  [{ch.channel}]")
        lines.append(f"    Охват: {ch.monthly_reach:,} | CR: {ch.conversion_rate_pct}%")
        lines.append(
            f"    CAC: ${ch.avg_cac_usd:.0f} | Целевой ROAS: {ch.target_roas}x"
        )

    lines.append(f"\n{'━' * 50}")
    lines.append("📅 ПРОГНОЗЫ")
    lines.append("━" * 50)
    lines.extend(
        f"  {p.month}: {p.subscribers:,} подп. | "
        f"{p.leads} лидов | {p.sales} продаж | ${p.revenue_usd:,.0f}"
        for p in rt.projections
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("🧮 ФОРМУЛЫ")
    lines.append("━" * 50)
    for name, formula in rt.formulas.items():
        lines.append(f"  {name} = {formula}")
    lines.append(f"\n  Точка безубыточности: {rt.break_even_sales} продаж/мес")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def roi_summary(rt: ROITracker) -> str:
    return (
        f"ROI-трекер: "
        f"{len(rt.revenue_streams)} потоков дохода, "
        f"{len(rt.cost_categories)} категорий расходов "
        f"(${rt.total_monthly_cost:.0f}/мес), "
        f"{len(rt.channel_roi)} каналов, "
        f"безубыточность: {rt.break_even_sales} продаж/мес"
    )
