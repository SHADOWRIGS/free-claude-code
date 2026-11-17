"""A/B price testing — price and offer variant experiments.

Generates structured pricing experiment configs:
- Price variants per product
- Offer bundles to test
- Discount strategies
- Test duration and sample size rules
- Statistical significance thresholds
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

PRICE_VARIANTS: list[dict[str, str | float]] = [
    {
        "product": "Cyber Security & Ethical Hacking",
        "variant_a": 197.0,
        "variant_b": 149.0,
        "variant_c": 247.0,
        "currency": "USD",
        "hypothesis": "Снижение цены увеличит конверсию на 30%+",
    },
    {
        "product": "Blue Team / Defensive Security",
        "variant_a": 197.0,
        "variant_b": 179.0,
        "variant_c": 229.0,
        "currency": "USD",
        "hypothesis": "Премиальная цена повысит воспринимаемую ценность",
    },
    {
        "product": "Red Team / Offensive Security",
        "variant_a": 197.0,
        "variant_b": 167.0,
        "variant_c": 297.0,
        "currency": "USD",
        "hypothesis": "Red Team аудитория готова платить больше",
    },
    {
        "product": "Machine Learning & AI",
        "variant_a": 197.0,
        "variant_b": 127.0,
        "variant_c": 197.0,
        "currency": "USD",
        "hypothesis": "ML-аудитория чувствительна к цене",
    },
    {
        "product": "SMM-услуга (Growth)",
        "variant_a": 197.0,
        "variant_b": 147.0,
        "variant_c": 247.0,
        "currency": "USD",
        "hypothesis": "Средний тариф оптимален для конверсии",
    },
]

OFFER_BUNDLES: list[dict[str, str | float]] = [
    {
        "name": "Starter Bundle",
        "products": "1 курс + гайд PDF",
        "price_usd": 197.0,
        "savings_pct": 0.0,
        "target": "Новички, первая покупка",
    },
    {
        "name": "Dual Bundle",
        "products": "2 курса на выбор",
        "price_usd": 347.0,
        "savings_pct": 12.0,
        "target": "Переход между направлениями",
    },
    {
        "name": "Full Stack Security",
        "products": "Red + Blue + Cyber (3 курса)",
        "price_usd": 497.0,
        "savings_pct": 16.0,
        "target": "Карьеристы, полный стек",
    },
    {
        "name": "All Access",
        "products": "Все 4 курса + годовые обновления",
        "price_usd": 697.0,
        "savings_pct": 11.0,
        "target": "Максимальная ценность, VIP",
    },
]

DISCOUNT_STRATEGIES: list[dict[str, str | int]] = [
    {
        "name": "Early Bird",
        "discount_pct": 20,
        "duration_days": 7,
        "condition": "Первые 50 покупателей",
        "best_for": "Запуск нового курса",
    },
    {
        "name": "Flash Sale",
        "discount_pct": 30,
        "duration_days": 1,
        "condition": "Только 24 часа",
        "best_for": "Импульсные покупки, дефицит",
    },
    {
        "name": "Loyalty Reward",
        "discount_pct": 15,
        "duration_days": 30,
        "condition": "Для существующих клиентов",
        "best_for": "Апсейл и повторные покупки",
    },
    {
        "name": "Referral Bonus",
        "discount_pct": 25,
        "duration_days": 14,
        "condition": "Пришёл по реферальной ссылке",
        "best_for": "Рост через сарафанное радио",
    },
    {
        "name": "Seasonal",
        "discount_pct": 35,
        "duration_days": 3,
        "condition": "Black Friday / Cyber Monday / 11.11",
        "best_for": "Массовые распродажи",
    },
]

TEST_RULES: dict[str, str | int] = {
    "min_sample_size": 100,
    "confidence_level": "95%",
    "min_duration_days": 7,
    "max_duration_days": 30,
    "traffic_split": "50/50 (равный сплит)",
    "primary_metric": "Конверсия в покупку",
    "secondary_metrics": "ARPU, LTV, отказы",
    "stop_rule": "Статистическая значимость или конец периода",
}

SIGNIFICANCE_THRESHOLDS: list[dict[str, str | float]] = [
    {
        "metric": "Конверсия (CR)",
        "min_lift_pct": 10.0,
        "p_value": 0.05,
        "action_on_win": "Применить победителя ко всему трафику",
    },
    {
        "metric": "Средний чек (AOV)",
        "min_lift_pct": 5.0,
        "p_value": 0.05,
        "action_on_win": "Обновить цену на лендинге",
    },
    {
        "metric": "Revenue per visitor",
        "min_lift_pct": 15.0,
        "p_value": 0.01,
        "action_on_win": "Масштабировать рекламу на победителя",
    },
    {
        "metric": "Refund rate",
        "min_lift_pct": -5.0,
        "p_value": 0.05,
        "action_on_win": "Убрать вариант с высоким возвратом",
    },
]


@dataclass(frozen=True, slots=True)
class PriceVariant:
    product: str
    variant_a: float
    variant_b: float
    variant_c: float
    currency: str
    hypothesis: str


@dataclass(frozen=True, slots=True)
class OfferBundle:
    name: str
    products: str
    price_usd: float
    savings_pct: float
    target: str


@dataclass(frozen=True, slots=True)
class DiscountStrategy:
    name: str
    discount_pct: int
    duration_days: int
    condition: str
    best_for: str


@dataclass(frozen=True, slots=True)
class SignificanceThreshold:
    metric: str
    min_lift_pct: float
    p_value: float
    action_on_win: str


@dataclass(frozen=True, slots=True)
class ABPriceTest:
    price_variants: tuple[PriceVariant, ...]
    bundles: tuple[OfferBundle, ...]
    discount_strategies: tuple[DiscountStrategy, ...]
    test_rules: dict[str, str | int]
    thresholds: tuple[SignificanceThreshold, ...]


def generate_ab_price_test() -> ABPriceTest:
    return ABPriceTest(
        price_variants=tuple(
            PriceVariant(
                product=pv["product"],
                variant_a=float(pv["variant_a"]),
                variant_b=float(pv["variant_b"]),
                variant_c=float(pv["variant_c"]),
                currency=pv["currency"],
                hypothesis=pv["hypothesis"],
            )
            for pv in PRICE_VARIANTS
        ),
        bundles=tuple(
            OfferBundle(
                name=b["name"],
                products=b["products"],
                price_usd=float(b["price_usd"]),
                savings_pct=float(b["savings_pct"]),
                target=b["target"],
            )
            for b in OFFER_BUNDLES
        ),
        discount_strategies=tuple(
            DiscountStrategy(
                name=ds["name"],
                discount_pct=int(ds["discount_pct"]),
                duration_days=int(ds["duration_days"]),
                condition=ds["condition"],
                best_for=ds["best_for"],
            )
            for ds in DISCOUNT_STRATEGIES
        ),
        test_rules=dict(TEST_RULES),
        thresholds=tuple(
            SignificanceThreshold(
                metric=t["metric"],
                min_lift_pct=float(t["min_lift_pct"]),
                p_value=float(t["p_value"]),
                action_on_win=t["action_on_win"],
            )
            for t in SIGNIFICANCE_THRESHOLDS
        ),
    )


def export_ab_price_json(ab: ABPriceTest, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "price_variants": [
            {
                "product": pv.product,
                "variant_a": pv.variant_a,
                "variant_b": pv.variant_b,
                "variant_c": pv.variant_c,
                "currency": pv.currency,
                "hypothesis": pv.hypothesis,
            }
            for pv in ab.price_variants
        ],
        "bundles": [
            {
                "name": b.name,
                "products": b.products,
                "price_usd": b.price_usd,
                "savings_pct": b.savings_pct,
                "target": b.target,
            }
            for b in ab.bundles
        ],
        "discount_strategies": [
            {
                "name": ds.name,
                "discount_pct": ds.discount_pct,
                "duration_days": ds.duration_days,
                "condition": ds.condition,
                "best_for": ds.best_for,
            }
            for ds in ab.discount_strategies
        ],
        "test_rules": ab.test_rules,
        "thresholds": [
            {
                "metric": t.metric,
                "min_lift_pct": t.min_lift_pct,
                "p_value": t.p_value,
                "action_on_win": t.action_on_win,
            }
            for t in ab.thresholds
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_ab_price_txt(ab: ABPriceTest, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "A/B ТЕСТИРОВАНИЕ ЦЕН И ОФФЕРОВ",
        "=" * 60,
        "\n💲 ЦЕНОВЫЕ ВАРИАНТЫ",
        "━" * 50,
    ]
    for pv in ab.price_variants:
        lines.append(f"\n  [{pv.product}]")
        lines.append(
            f"    A: ${pv.variant_a:.0f} | B: ${pv.variant_b:.0f} | "
            f"C: ${pv.variant_c:.0f} ({pv.currency})"
        )
        lines.append(f"    Гипотеза: {pv.hypothesis}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📦 БАНДЛЫ (ПАКЕТНЫЕ ПРЕДЛОЖЕНИЯ)")
    lines.append("━" * 50)
    for b in ab.bundles:
        lines.append(f"\n  [{b.name}] ${b.price_usd:.0f}")
        lines.append(f"    {b.products}")
        savings = f" (экономия {b.savings_pct:.0f}%)" if b.savings_pct > 0 else ""
        lines.append(f"    Цель: {b.target}{savings}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🏷 СТРАТЕГИИ СКИДОК")
    lines.append("━" * 50)
    for ds in ab.discount_strategies:
        lines.append(f"\n  [{ds.name}] -{ds.discount_pct}% ({ds.duration_days} дней)")
        lines.append(f"    Условие: {ds.condition}")
        lines.append(f"    Лучше для: {ds.best_for}")

    lines.append(f"\n{'━' * 50}")
    lines.append("⚙ ПРАВИЛА ТЕСТИРОВАНИЯ")
    lines.append("━" * 50)
    for key, val in ab.test_rules.items():
        lines.append(f"  {key}: {val}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📊 ПОРОГИ ЗНАЧИМОСТИ")
    lines.append("━" * 50)
    for t in ab.thresholds:
        lines.append(
            f"\n  [{t.metric}] min lift: {t.min_lift_pct:+.0f}% | p < {t.p_value}"
        )
        lines.append(f"    При победе: {t.action_on_win}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def ab_price_summary(ab: ABPriceTest) -> str:
    return (
        f"A/B цены: "
        f"{len(ab.price_variants)} ценовых вариантов, "
        f"{len(ab.bundles)} бандлов, "
        f"{len(ab.discount_strategies)} стратегий скидок, "
        f"{len(ab.thresholds)} порогов значимости"
    )
