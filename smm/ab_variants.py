"""A/B caption variant generator for split-testing.

Produces two distinct caption variants for each post so the user
can test which hook/CTA combination performs better. Each variant
uses a different hook, CTA, and caption template to maximize
the difference between A and B.
"""

from __future__ import annotations

import csv
import json
import random
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from smm.content_bank import (
    CTA_COURSE_EXTENDED,
    CTA_ENGAGE_EXTENDED,
    CTA_REFERRAL_EXTENDED,
    HOOKS_EXTENDED,
)
from smm.post_generator import PostSlot, generate_week_plan
from smm.ready_posts import (
    CAPTION_TEMPLATES_COURSE,
    CAPTION_TEMPLATES_REFERRAL,
    _pillar_short,
)


@dataclass(frozen=True, slots=True)
class ABVariant:
    variant: str
    hook: str
    cta: str
    caption: str


@dataclass(frozen=True, slots=True)
class ABPost:
    day: date
    time_slot: str
    platform: str
    pillar: str
    topic: str
    format: str
    variant_a: ABVariant
    variant_b: ABVariant
    hashtags: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "day": self.day.isoformat(),
            "time": self.time_slot,
            "platform": self.platform,
            "pillar": self.pillar,
            "topic": self.topic,
            "format": self.format,
            "variant_a": {
                "hook": self.variant_a.hook,
                "cta": self.variant_a.cta,
                "caption": self.variant_a.caption,
            },
            "variant_b": {
                "hook": self.variant_b.hook,
                "cta": self.variant_b.cta,
                "caption": self.variant_b.caption,
            },
            "hashtags": self.hashtags,
        }


def _pick_two_hooks(slot: PostSlot) -> tuple[str, str]:
    keyword = _pillar_short(slot.pillar)
    extended = [
        h.format(keyword=keyword) if "{keyword}" in h else h for h in HOOKS_EXTENDED
    ]
    pool = [slot.hook, *extended[:15]]
    chosen = random.sample(pool, min(2, len(pool)))
    if len(chosen) < 2:
        chosen.append(slot.hook)
    return chosen[0], chosen[1]


def _pick_two_ctas(is_referral: bool) -> tuple[str, str]:
    if is_referral:
        pool = list(CTA_REFERRAL_EXTENDED) + list(CTA_ENGAGE_EXTENDED[:3])
    else:
        pool = list(CTA_COURSE_EXTENDED) + list(CTA_ENGAGE_EXTENDED[:3])
    chosen = random.sample(pool, min(2, len(pool)))
    return chosen[0], chosen[1]


def _pick_two_templates(is_referral: bool) -> tuple[str, str]:
    templates = CAPTION_TEMPLATES_REFERRAL if is_referral else CAPTION_TEMPLATES_COURSE
    chosen = random.sample(templates, min(2, len(templates)))
    return chosen[0], chosen[1]


def _render_caption(tpl: str, slot: PostSlot, hook: str, cta: str) -> str:
    hashtags_str = " ".join(slot.hashtags)
    return tpl.format(
        hook=hook,
        topic=slot.topic,
        topic_lower=slot.topic.lower() if slot.topic[0].isupper() else slot.topic,
        pillar_short=_pillar_short(slot.pillar),
        cta=cta,
        hashtags=hashtags_str,
    )


def generate_ab_posts(
    days: int = 7,
    seed: int | None = None,
    start: date | None = None,
) -> list[ABPost]:
    plan = generate_week_plan(start=start, days=days, seed=seed)
    if seed is not None:
        random.seed(seed + 2000)

    result: list[ABPost] = []
    for slot in plan:
        is_referral = slot.pillar.product == "referral"
        hook_a, hook_b = _pick_two_hooks(slot)
        cta_a, cta_b = _pick_two_ctas(is_referral)
        tpl_a, tpl_b = _pick_two_templates(is_referral)

        variant_a = ABVariant(
            variant="A",
            hook=hook_a,
            cta=cta_a,
            caption=_render_caption(tpl_a, slot, hook_a, cta_a),
        )
        variant_b = ABVariant(
            variant="B",
            hook=hook_b,
            cta=cta_b,
            caption=_render_caption(tpl_b, slot, hook_b, cta_b),
        )
        result.append(
            ABPost(
                day=slot.day,
                time_slot=slot.time_slot,
                platform=slot.platform.value,
                pillar=slot.pillar.name,
                topic=slot.topic,
                format=slot.format,
                variant_a=variant_a,
                variant_b=variant_b,
                hashtags=slot.hashtags,
            )
        )
    return result


def export_ab_json(posts: list[ABPost], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [p.to_dict() for p in posts]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_ab_csv(posts: list[ABPost], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Day",
                "Time",
                "Platform",
                "Topic",
                "Hook_A",
                "Caption_A",
                "Hook_B",
                "Caption_B",
                "Winner",
            ]
        )
        for p in posts:
            writer.writerow(
                [
                    p.day.isoformat(),
                    p.time_slot,
                    p.platform,
                    p.topic,
                    p.variant_a.hook,
                    p.variant_a.caption,
                    p.variant_b.hook,
                    p.variant_b.caption,
                    "",
                ]
            )
    return path


def export_ab_markdown(posts: list[ABPost], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = ["# A/B Test — Caption Variants\n"]
    for i, p in enumerate(posts, 1):
        lines.append(f"## Post {i} | {p.day.isoformat()} {p.time_slot} | {p.platform}")
        lines.append(f"**Topic:** {p.topic}\n")
        lines.append("### Variant A")
        lines.append(f"**Hook:** {p.variant_a.hook}")
        lines.append(f"```\n{p.variant_a.caption}\n```\n")
        lines.append("### Variant B")
        lines.append(f"**Hook:** {p.variant_b.hook}")
        lines.append(f"```\n{p.variant_b.caption}\n```\n")
        lines.append("**Winner:** ___\n")
        lines.append("---\n")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def ab_summary(posts: list[ABPost]) -> str:
    return (
        f"A/B тест: {len(posts)} постов, {len(posts) * 2} вариантов подписей.\n"
        f"Платформы: {', '.join(sorted({p.platform for p in posts}))}\n"
        f"Колонка «Winner» — для записи результатов тестирования."
    )
