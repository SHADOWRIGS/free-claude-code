"""Affiliate dashboard — partner program analytics and management.

Generates structured configs for:
- Affiliate tiers and commission structure
- Performance KPIs per affiliate
- Payout rules and schedules
- Promotional materials catalog
- Dashboard widgets and reports
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

AFFILIATE_TIERS: list[dict[str, str | int | float]] = [
    {
        "tier": "Bronze",
        "min_referrals": 0,
        "commission_pct": 15.0,
        "bonus_per_sale": 0.0,
        "payout_min_usd": 50,
        "perks": "Базовые промо-материалы, реферальная ссылка",
    },
    {
        "tier": "Silver",
        "min_referrals": 10,
        "commission_pct": 20.0,
        "bonus_per_sale": 5.0,
        "payout_min_usd": 25,
        "perks": "Кастомный лендинг, приоритетная поддержка",
    },
    {
        "tier": "Gold",
        "min_referrals": 50,
        "commission_pct": 25.0,
        "bonus_per_sale": 10.0,
        "payout_min_usd": 10,
        "perks": "Бесплатный курс, совместный вебинар, ранний доступ",
    },
    {
        "tier": "Platinum",
        "min_referrals": 100,
        "commission_pct": 30.0,
        "bonus_per_sale": 15.0,
        "payout_min_usd": 0,
        "perks": "Все курсы бесплатно, эксклюзивные офферы, менторство",
    },
]

PERFORMANCE_KPIS: list[dict[str, str]] = [
    {
        "kpi": "Клики",
        "description": "Количество кликов по реферальной ссылке",
        "formula": "Уникальные клики за период",
        "target_monthly": "500+",
    },
    {
        "kpi": "Регистрации",
        "description": "Новые пользователи через реферальную ссылку",
        "formula": "Регистрации / Клики",
        "target_monthly": "50+",
    },
    {
        "kpi": "Конверсия в покупку",
        "description": "Процент регистраций, ставших покупками",
        "formula": "Покупки / Регистрации * 100",
        "target_monthly": "10%+",
    },
    {
        "kpi": "Доход",
        "description": "Общий доход от рефералов за период",
        "formula": "Сумма всех покупок рефералов",
        "target_monthly": "$500+",
    },
    {
        "kpi": "EPC (Earning Per Click)",
        "description": "Средний доход на клик",
        "formula": "Доход / Клики",
        "target_monthly": "$0.50+",
    },
    {
        "kpi": "Средний чек",
        "description": "Средняя сумма покупки от рефералов",
        "formula": "Доход / Количество покупок",
        "target_monthly": "$150+",
    },
]

PAYOUT_RULES: list[dict[str, str]] = [
    {
        "rule": "Период начисления",
        "value": "30 дней cookie window",
        "note": "Комиссия начисляется, если покупка в течение 30 дней после клика",
    },
    {
        "rule": "Выплата",
        "value": "1 раз в месяц, 15 числа",
        "note": "PayPal, банковский перевод или криптовалюта",
    },
    {
        "rule": "Минимум для выплаты",
        "value": "Зависит от тира (0-50 USD)",
        "note": "Невыплаченное переносится на следующий месяц",
    },
    {
        "rule": "Возвраты",
        "value": "Комиссия сторнируется при возврате",
        "note": "Холд 14 дней перед начислением",
    },
    {
        "rule": "Самореферал",
        "value": "Запрещён",
        "note": "Автоматическое отклонение совпадений email/IP",
    },
]

PROMO_MATERIALS: list[dict[str, str | int]] = [
    {
        "material": "Баннеры",
        "formats": "728x90, 300x250, 1080x1080, 1080x1920",
        "count": 20,
        "description": "Набор баннеров для каждого курса и сезона",
    },
    {
        "material": "Email-шаблоны",
        "formats": "HTML, текст",
        "count": 10,
        "description": "Готовые письма для рассылки подписчикам",
    },
    {
        "material": "Посты для соцсетей",
        "formats": "Текст + визуал (IG, TT, YT)",
        "count": 30,
        "description": "Готовые посты с UTM-ссылками партнёра",
    },
    {
        "material": "Видео-обзоры",
        "formats": "MP4 15s, 30s, 60s",
        "count": 5,
        "description": "Промо-ролики для использования в рекламе",
    },
    {
        "material": "Лендинг-конструктор",
        "formats": "HTML-шаблон",
        "count": 3,
        "description": "Настраиваемый лендинг с реферальной ссылкой",
    },
]

DASHBOARD_WIDGETS: list[dict[str, str]] = [
    {
        "widget": "Сводка доходов",
        "type": "stat_card",
        "data": "Доход сегодня / неделя / месяц / всё время",
    },
    {
        "widget": "График кликов и конверсий",
        "type": "line_chart",
        "data": "Клики, регистрации, покупки по дням",
    },
    {
        "widget": "Топ-партнёры",
        "type": "table",
        "data": "Имя, тир, клики, конверсии, доход, EPC",
    },
    {
        "widget": "Распределение по курсам",
        "type": "pie_chart",
        "data": "Доля продаж каждого курса от рефералов",
    },
    {
        "widget": "Выплаты",
        "type": "table",
        "data": "Дата, партнёр, сумма, статус (ожидание/выплачено)",
    },
    {
        "widget": "Активность партнёров",
        "type": "heatmap",
        "data": "Активные / неактивные / потерянные партнёры",
    },
]


@dataclass(frozen=True, slots=True)
class AffiliateTier:
    tier: str
    min_referrals: int
    commission_pct: float
    bonus_per_sale: float
    payout_min_usd: int
    perks: str


@dataclass(frozen=True, slots=True)
class PerformanceKPI:
    kpi: str
    description: str
    formula: str
    target_monthly: str


@dataclass(frozen=True, slots=True)
class PayoutRule:
    rule: str
    value: str
    note: str


@dataclass(frozen=True, slots=True)
class PromoMaterial:
    material: str
    formats: str
    count: int
    description: str


@dataclass(frozen=True, slots=True)
class DashboardWidget:
    widget: str
    type: str
    data: str


@dataclass(frozen=True, slots=True)
class AffiliateDashboard:
    tiers: tuple[AffiliateTier, ...]
    kpis: tuple[PerformanceKPI, ...]
    payout_rules: tuple[PayoutRule, ...]
    promo_materials: tuple[PromoMaterial, ...]
    widgets: tuple[DashboardWidget, ...]


def generate_affiliate_dashboard() -> AffiliateDashboard:
    return AffiliateDashboard(
        tiers=tuple(
            AffiliateTier(
                tier=t["tier"],
                min_referrals=int(t["min_referrals"]),
                commission_pct=float(t["commission_pct"]),
                bonus_per_sale=float(t["bonus_per_sale"]),
                payout_min_usd=int(t["payout_min_usd"]),
                perks=t["perks"],
            )
            for t in AFFILIATE_TIERS
        ),
        kpis=tuple(
            PerformanceKPI(
                kpi=k["kpi"],
                description=k["description"],
                formula=k["formula"],
                target_monthly=k["target_monthly"],
            )
            for k in PERFORMANCE_KPIS
        ),
        payout_rules=tuple(
            PayoutRule(
                rule=pr["rule"],
                value=pr["value"],
                note=pr["note"],
            )
            for pr in PAYOUT_RULES
        ),
        promo_materials=tuple(
            PromoMaterial(
                material=pm["material"],
                formats=pm["formats"],
                count=int(pm["count"]),
                description=pm["description"],
            )
            for pm in PROMO_MATERIALS
        ),
        widgets=tuple(
            DashboardWidget(
                widget=dw["widget"],
                type=dw["type"],
                data=dw["data"],
            )
            for dw in DASHBOARD_WIDGETS
        ),
    )


def export_affiliate_json(ad: AffiliateDashboard, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "tiers": [
            {
                "tier": t.tier,
                "min_referrals": t.min_referrals,
                "commission_pct": t.commission_pct,
                "bonus_per_sale": t.bonus_per_sale,
                "payout_min_usd": t.payout_min_usd,
                "perks": t.perks,
            }
            for t in ad.tiers
        ],
        "kpis": [
            {
                "kpi": k.kpi,
                "description": k.description,
                "formula": k.formula,
                "target_monthly": k.target_monthly,
            }
            for k in ad.kpis
        ],
        "payout_rules": [
            {"rule": pr.rule, "value": pr.value, "note": pr.note}
            for pr in ad.payout_rules
        ],
        "promo_materials": [
            {
                "material": pm.material,
                "formats": pm.formats,
                "count": pm.count,
                "description": pm.description,
            }
            for pm in ad.promo_materials
        ],
        "widgets": [
            {"widget": dw.widget, "type": dw.type, "data": dw.data} for dw in ad.widgets
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_affiliate_txt(ad: AffiliateDashboard, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "ДАШБОРД ПАРТНЁРСКОЙ ПРОГРАММЫ",
        "=" * 60,
        "\n🏅 УРОВНИ ПАРТНЁРОВ",
        "━" * 50,
    ]
    for t in ad.tiers:
        lines.append(
            f"\n  [{t.tier}] от {t.min_referrals} рефералов | "
            f"{t.commission_pct:.0f}% + ${t.bonus_per_sale:.0f}/продажу"
        )
        lines.append(f"    Мин. выплата: ${t.payout_min_usd}")
        lines.append(f"    Привилегии: {t.perks}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📊 KPI ПАРТНЁРОВ")
    lines.append("━" * 50)
    for k in ad.kpis:
        lines.append(f"\n  [{k.kpi}] цель: {k.target_monthly}")
        lines.append(f"    {k.description}")
        lines.append(f"    Формула: {k.formula}")

    lines.append(f"\n{'━' * 50}")
    lines.append("💰 ПРАВИЛА ВЫПЛАТ")
    lines.append("━" * 50)
    for pr in ad.payout_rules:
        lines.append(f"\n  [{pr.rule}] {pr.value}")
        lines.append(f"    {pr.note}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📦 ПРОМО-МАТЕРИАЛЫ")
    lines.append("━" * 50)
    lines.extend(
        f"  [{pm.material}] {pm.count} шт. ({pm.formats})" for pm in ad.promo_materials
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("🖥 ВИДЖЕТЫ ДАШБОРДА")
    lines.append("━" * 50)
    lines.extend(f"  [{dw.widget}] тип: {dw.type} | {dw.data}" for dw in ad.widgets)

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def affiliate_summary(ad: AffiliateDashboard) -> str:
    return (
        f"Партнёрский дашборд: "
        f"{len(ad.tiers)} уровней, "
        f"{len(ad.kpis)} KPI, "
        f"{len(ad.payout_rules)} правил выплат, "
        f"{len(ad.promo_materials)} типов промо, "
        f"{len(ad.widgets)} виджетов"
    )
