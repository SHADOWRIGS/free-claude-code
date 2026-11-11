"""SMM automation service specification.

Defines the service offering, pricing tiers, and deliverables
for packaging SMM automation as a sellable product/service.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ServiceTier:
    name: str
    price_monthly_usd: int
    posts_per_week: int
    platforms: list[str]
    includes_ai_captions: bool
    includes_video_scripts: bool
    includes_visual_briefs: bool
    includes_analytics: bool
    includes_trend_reports: bool
    description: str


TIERS: list[ServiceTier] = [
    ServiceTier(
        name="Starter",
        price_monthly_usd=97,
        posts_per_week=21,
        platforms=["Instagram"],
        includes_ai_captions=True,
        includes_video_scripts=False,
        includes_visual_briefs=True,
        includes_analytics=False,
        includes_trend_reports=False,
        description=(
            "21 post/week for one platform. "
            "AI-generated captions, hashtags, visual briefs. "
            "Weekly content calendar in JSON/Markdown."
        ),
    ),
    ServiceTier(
        name="Growth",
        price_monthly_usd=197,
        posts_per_week=42,
        platforms=["Instagram", "TikTok"],
        includes_ai_captions=True,
        includes_video_scripts=True,
        includes_visual_briefs=True,
        includes_analytics=False,
        includes_trend_reports=True,
        description=(
            "42 posts/week across Instagram + TikTok. "
            "AI captions, video scripts, visual briefs, trend reports. "
            "Platform-specific formatting and scheduling."
        ),
    ),
    ServiceTier(
        name="Pro",
        price_monthly_usd=397,
        posts_per_week=63,
        platforms=["Instagram", "TikTok", "YouTube"],
        includes_ai_captions=True,
        includes_video_scripts=True,
        includes_visual_briefs=True,
        includes_analytics=True,
        includes_trend_reports=True,
        description=(
            "63 posts/week across all 3 platforms. "
            "Full AI content generation pipeline: captions, scripts, "
            "visual briefs, thumbnails, analytics, trend reports. "
            "Ready-to-post packages per platform."
        ),
    ),
]


@dataclass(frozen=True, slots=True)
class TargetAudience:
    segment: str
    pain_points: list[str]
    value_proposition: str


TARGET_AUDIENCES: list[TargetAudience] = [
    TargetAudience(
        segment="Solo creators / infopreneurs",
        pain_points=[
            "No time to create consistent content",
            "Don't know what to post",
            "Can't afford a social media manager",
        ],
        value_proposition=(
            "AI generates a full week of content in minutes, "
            "ready to copy-paste into scheduling tools."
        ),
    ),
    TargetAudience(
        segment="Small cybersecurity training companies",
        pain_points=[
            "Need to market courses but staff are technical, not marketers",
            "Inconsistent social media presence",
            "Low engagement on educational content",
        ],
        value_proposition=(
            "Pre-built content pillars for cybersec niches. "
            "Hook-driven posts that convert followers to course buyers."
        ),
    ),
    TargetAudience(
        segment="Affiliate marketers (tech gadgets)",
        pain_points=[
            "Need high volume of product-adjacent content",
            "Referral links must be woven in naturally",
            "Platform-specific formatting is tedious",
        ],
        value_proposition=(
            "UTM-tracked referral links baked into every post. "
            "Platform-specific packages ready for scheduling."
        ),
    ),
]


@dataclass(frozen=True, slots=True)
class Deliverable:
    name: str
    format: str
    frequency: str
    description: str


DELIVERABLES: list[Deliverable] = [
    Deliverable(
        name="Weekly content calendar",
        format="JSON + Markdown",
        frequency="Weekly",
        description="63 posts with topics, hooks, CTAs, hashtags, referral URLs",
    ),
    Deliverable(
        name="Instagram posting package",
        format="JSON",
        frequency="Weekly",
        description="21 ready-to-post Instagram entries with captions, hashtags, visual briefs",
    ),
    Deliverable(
        name="TikTok posting package",
        format="JSON",
        frequency="Weekly",
        description="21 TikTok entries with scripts, hooks, captions, sound suggestions",
    ),
    Deliverable(
        name="YouTube posting package",
        format="JSON",
        frequency="Weekly",
        description="21 YouTube entries with titles, descriptions, tags, scripts, thumbnail briefs",
    ),
    Deliverable(
        name="AI-generated full captions",
        format="JSON",
        frequency="On demand",
        description="Full post text generated via AI with multiple hook variants",
    ),
    Deliverable(
        name="Trend analysis report",
        format="JSON",
        frequency="Weekly",
        description="Trending topics, hashtags, and content angles per niche",
    ),
]


@dataclass(slots=True)
class ServiceSpec:
    tiers: list[ServiceTier] = field(default_factory=lambda: list(TIERS))
    audiences: list[TargetAudience] = field(
        default_factory=lambda: list(TARGET_AUDIENCES)
    )
    deliverables: list[Deliverable] = field(default_factory=lambda: list(DELIVERABLES))

    def pricing_table(self) -> str:
        lines = [
            "Tier         | Price/mo | Posts/wk | Platforms",
            "-------------|----------|----------|----------",
            *[
                f"{t.name:<13}| ${t.price_monthly_usd:<7} | {t.posts_per_week:<8} | "
                f"{', '.join(t.platforms)}"
                for t in self.tiers
            ],
        ]
        return "\n".join(lines)

    def full_spec(self) -> str:
        sections = [
            "# SMM Automation Service",
            "",
            "## What We Sell",
            "AI-powered content generation and distribution pipeline for social media.",
            "The system generates ready-to-post content packages for Instagram, TikTok,",
            "and YouTube, with built-in referral tracking and platform-specific formatting.",
            "",
            "## Pricing",
            self.pricing_table(),
            "",
            "## Target Audience",
        ]
        for a in self.audiences:
            sections.append(f"\n### {a.segment}")
            sections.append(f"Value: {a.value_proposition}")
            sections.append("Pain points:")
            sections.extend(f"  - {p}" for p in a.pain_points)

        sections.append("\n## Deliverables")
        for d in self.deliverables:
            sections.append(f"\n### {d.name}")
            sections.append(f"Format: {d.format} | Frequency: {d.frequency}")
            sections.append(d.description)

        sections.append("\n## Tech Stack")
        sections.append("- Python 3.14 + uv")
        sections.append("- Anthropic API (via free-claude-code proxy)")
        sections.append("- Platform-specific content formatters")
        sections.append("- UTM referral tracking")
        sections.append("- JSON/Markdown export for any scheduling tool")

        return "\n".join(sections)
