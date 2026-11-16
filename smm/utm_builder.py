"""UTM builder — campaign URL generator with structured parameters.

Generates structured UTM configs:
- Base URL templates per product
- Campaign naming conventions
- Pre-built UTM links per pillar x platform x format
- Short URL mapping rules
- QR code generation specs
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode

BASE_URLS: list[dict[str, str]] = [
    {
        "pillar": "Cyber Security & Ethical Hacking",
        "url": "https://shadowrigs.com/courses/cybersecurity",
        "short_alias": "cyber",
    },
    {
        "pillar": "Blue Team / Defensive Security",
        "url": "https://shadowrigs.com/courses/blue-team",
        "short_alias": "blue",
    },
    {
        "pillar": "Red Team / Offensive Security",
        "url": "https://shadowrigs.com/courses/red-team",
        "short_alias": "red",
    },
    {
        "pillar": "Machine Learning & AI",
        "url": "https://shadowrigs.com/courses/machine-learning",
        "short_alias": "ml",
    },
    {
        "pillar": "AliExpress — Гаджеты",
        "url": "https://aliexpress.com/store/shadowrigs",
        "short_alias": "gadgets",
    },
]

PLATFORMS: list[str] = ["instagram", "tiktok", "youtube", "telegram", "email"]

CAMPAIGN_TYPES: list[dict[str, str]] = [
    {
        "type": "organic",
        "medium": "social",
        "description": "Органические посты в соцсетях",
    },
    {
        "type": "paid",
        "medium": "cpc",
        "description": "Платная реклама (CPC/CPM)",
    },
    {
        "type": "email",
        "medium": "email",
        "description": "Email-рассылки и цепочки",
    },
    {
        "type": "partner",
        "medium": "affiliate",
        "description": "Партнёрский/реферальный трафик",
    },
    {
        "type": "influencer",
        "medium": "influencer",
        "description": "Инфлюенсер-коллаборации",
    },
]

NAMING_RULES: dict[str, str] = {
    "utm_source": "{platform} — источник трафика",
    "utm_medium": "{campaign_type.medium} — тип трафика",
    "utm_campaign": "{pillar_alias}_{campaign_type}_{YYYYMM} — кампания",
    "utm_content": "{format}_{variant} — вариант контента",
    "utm_term": "{keyword} — ключевое слово (для PPC)",
}


@dataclass(frozen=True, slots=True)
class BaseURL:
    pillar: str
    url: str
    short_alias: str


@dataclass(frozen=True, slots=True)
class CampaignType:
    type: str
    medium: str
    description: str


@dataclass(frozen=True, slots=True)
class UTMLink:
    pillar: str
    platform: str
    campaign_type: str
    full_url: str
    utm_source: str
    utm_medium: str
    utm_campaign: str


@dataclass(frozen=True, slots=True)
class UTMBuilder:
    base_urls: tuple[BaseURL, ...]
    campaign_types: tuple[CampaignType, ...]
    platforms: tuple[str, ...]
    naming_rules: dict[str, str]
    sample_links: tuple[UTMLink, ...]
    total_combinations: int


def _build_utm_url(
    base_url: str,
    source: str,
    medium: str,
    campaign: str,
) -> str:
    params = {
        "utm_source": source,
        "utm_medium": medium,
        "utm_campaign": campaign,
    }
    return f"{base_url}?{urlencode(params)}"


def generate_utm_builder() -> UTMBuilder:
    base_urls = tuple(
        BaseURL(pillar=b["pillar"], url=b["url"], short_alias=b["short_alias"])
        for b in BASE_URLS
    )
    campaign_types = tuple(
        CampaignType(type=c["type"], medium=c["medium"], description=c["description"])
        for c in CAMPAIGN_TYPES
    )
    platforms = tuple(PLATFORMS)

    sample_links: list[UTMLink] = []
    for b in base_urls:
        for ct in campaign_types[:2]:
            for plat in platforms[:3]:
                campaign_name = f"{b.short_alias}_{ct.type}_202611"
                full_url = _build_utm_url(b.url, plat, ct.medium, campaign_name)
                sample_links.append(
                    UTMLink(
                        pillar=b.pillar,
                        platform=plat,
                        campaign_type=ct.type,
                        full_url=full_url,
                        utm_source=plat,
                        utm_medium=ct.medium,
                        utm_campaign=campaign_name,
                    )
                )

    total = len(base_urls) * len(campaign_types) * len(platforms)

    return UTMBuilder(
        base_urls=base_urls,
        campaign_types=campaign_types,
        platforms=platforms,
        naming_rules=dict(NAMING_RULES),
        sample_links=tuple(sample_links),
        total_combinations=total,
    )


def export_utm_json(ub: UTMBuilder, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "base_urls": [
            {"pillar": b.pillar, "url": b.url, "short_alias": b.short_alias}
            for b in ub.base_urls
        ],
        "campaign_types": [
            {"type": c.type, "medium": c.medium, "description": c.description}
            for c in ub.campaign_types
        ],
        "platforms": list(ub.platforms),
        "naming_rules": ub.naming_rules,
        "sample_links": [
            {
                "pillar": link.pillar,
                "platform": link.platform,
                "campaign_type": link.campaign_type,
                "full_url": link.full_url,
                "utm_source": link.utm_source,
                "utm_medium": link.utm_medium,
                "utm_campaign": link.utm_campaign,
            }
            for link in ub.sample_links
        ],
        "total_combinations": ub.total_combinations,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_utm_txt(ub: UTMBuilder, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "UTM-БИЛДЕР — ГЕНЕРАТОР КАМПАНЕЙНЫХ ССЫЛОК",
        "=" * 60,
        "\n🔗 БАЗОВЫЕ URL",
        "━" * 50,
    ]
    lines.extend(f"  [{b.short_alias}] {b.pillar}\n    {b.url}" for b in ub.base_urls)

    lines.append(f"\n{'━' * 50}")
    lines.append("📊 ТИПЫ КАМПАНИЙ")
    lines.append("━" * 50)
    lines.extend(
        f"  {c.type} (medium={c.medium}) — {c.description}" for c in ub.campaign_types
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("📐 ПРАВИЛА ИМЕНОВАНИЯ")
    lines.append("━" * 50)
    for key, desc in ub.naming_rules.items():
        lines.append(f"  {key}: {desc}")

    lines.append(f"\n{'━' * 50}")
    lines.append(
        f"🔗 ПРИМЕРЫ ССЫЛОК ({len(ub.sample_links)} из {ub.total_combinations})"
    )
    lines.append("━" * 50)
    for link in ub.sample_links[:10]:
        lines.append(f"\n  [{link.pillar} | {link.platform} | {link.campaign_type}]")
        lines.append(f"    {link.full_url}")

    if len(ub.sample_links) > 10:
        lines.append(f"\n  ... и ещё {len(ub.sample_links) - 10} ссылок")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def utm_summary(ub: UTMBuilder) -> str:
    return (
        f"UTM-билдер: "
        f"{len(ub.base_urls)} базовых URL, "
        f"{len(ub.campaign_types)} типов кампаний, "
        f"{len(ub.platforms)} платформ, "
        f"{len(ub.sample_links)} примеров ссылок "
        f"({ub.total_combinations} комбинаций)"
    )
