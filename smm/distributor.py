"""Distribution-ready content packages per platform.

Takes generated PostSlots and exports platform-specific posting packages:
- Instagram: caption + hashtags + visual brief + carousel slides outline
- TikTok: script + hook + caption + hashtags
- YouTube: title + description + tags + script + thumbnail brief

Each package is a self-contained JSON ready to hand to a posting tool
or a human social media manager.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

from smm.platforms import Platform
from smm.post_generator import PostSlot, generate_week_plan


@dataclass(frozen=True, slots=True)
class InstagramPackage:
    date: str
    time: str
    format: str
    pillar: str
    topic: str
    caption: str
    hashtags: str
    visual_brief: str
    referral_url: str
    carousel_slides: list[str]


@dataclass(frozen=True, slots=True)
class TikTokPackage:
    date: str
    time: str
    format: str
    pillar: str
    topic: str
    hook: str
    script: str
    caption: str
    hashtags: str
    referral_url: str
    sounds_suggestion: str


@dataclass(frozen=True, slots=True)
class YouTubePackage:
    date: str
    time: str
    format: str
    pillar: str
    topic: str
    title: str
    description: str
    tags: list[str]
    script: str
    thumbnail_brief: str
    referral_url: str
    end_screen_cta: str


def _build_instagram_caption(slot: PostSlot) -> str:
    lines = [
        slot.hook,
        "",
        slot.body.strip(),
        "",
        slot.cta,
        "",
        " ".join(slot.hashtags),
    ]
    return "\n".join(lines)


def _build_carousel_slides(slot: PostSlot) -> list[str]:
    return [
        f"Slide 1 (Cover): {slot.hook}",
        f"Slide 2: {slot.topic} - intro",
        "Slide 3: Key points / steps",
        "Slide 4: Tools / resources",
        f"Slide 5 (CTA): {slot.cta}",
    ]


def _build_tiktok_script(slot: PostSlot) -> str:
    return (
        f"[0-3s] Hook: {slot.hook}\n"
        f"[3-20s] Main: {slot.topic}\n"
        f"[20-25s] Key takeaway\n"
        f"[25-30s] CTA: {slot.cta}"
    )


def _build_youtube_description(slot: PostSlot) -> str:
    lines = [
        slot.body.strip(),
        "",
        slot.cta,
        "",
    ]
    if slot.referral_url:
        lines.append(f"Link: {slot.referral_url}")
        lines.append("")
    lines.append(" ".join(slot.hashtags))
    return "\n".join(lines)


def package_instagram(slot: PostSlot) -> InstagramPackage:
    return InstagramPackage(
        date=slot.day.isoformat(),
        time=slot.time_slot,
        format=slot.format,
        pillar=slot.pillar.name,
        topic=slot.topic,
        caption=_build_instagram_caption(slot),
        hashtags=" ".join(slot.hashtags),
        visual_brief=f"Create {slot.format} visual for: {slot.topic}. "
        f"Style: modern, dark tech aesthetic. Include text overlay with hook.",
        referral_url=slot.referral_url,
        carousel_slides=_build_carousel_slides(slot)
        if slot.format == "carousel"
        else [],
    )


def package_tiktok(slot: PostSlot) -> TikTokPackage:
    return TikTokPackage(
        date=slot.day.isoformat(),
        time=slot.time_slot,
        format=slot.format,
        pillar=slot.pillar.name,
        topic=slot.topic,
        hook=slot.hook,
        script=_build_tiktok_script(slot),
        caption=f"{slot.hook}\n\n{slot.cta}\n\n{' '.join(slot.hashtags)}",
        hashtags=" ".join(slot.hashtags),
        referral_url=slot.referral_url,
        sounds_suggestion="trending tech/hacker ambient or dramatic reveal sound",
    )


def package_youtube(slot: PostSlot) -> YouTubePackage:
    is_short = slot.format in ("shorts",)
    return YouTubePackage(
        date=slot.day.isoformat(),
        time=slot.time_slot,
        format=slot.format,
        pillar=slot.pillar.name,
        topic=slot.topic,
        title=slot.hook[:70] if is_short else f"{slot.topic} | ShadowRigs",
        description=_build_youtube_description(slot),
        tags=[h.lstrip("#") for h in slot.hashtags],
        script=_build_tiktok_script(slot)
        if is_short
        else (
            f"[Intro 0-15s] {slot.hook}\n"
            f"[Main 15s-8min] Deep dive: {slot.topic}\n"
            f"[Demo 8-12min] Practical examples\n"
            f"[CTA 12-13min] {slot.cta}"
        ),
        thumbnail_brief=f"Bold text: '{slot.topic[:40]}'. "
        "Dark background, neon accent, face or screen capture.",
        referral_url=slot.referral_url,
        end_screen_cta=slot.cta,
    )


PACKAGERS = {
    Platform.INSTAGRAM: package_instagram,
    Platform.TIKTOK: package_tiktok,
    Platform.YOUTUBE: package_youtube,
}


@dataclass(slots=True)
class WeeklyDistribution:
    week_start: date
    instagram: list[InstagramPackage] = field(default_factory=list)
    tiktok: list[TikTokPackage] = field(default_factory=list)
    youtube: list[YouTubePackage] = field(default_factory=list)

    @classmethod
    def from_plan(cls, slots: list[PostSlot]) -> WeeklyDistribution:
        dist = cls(week_start=slots[0].day if slots else date.today())
        for slot in slots:
            pkg = PACKAGERS[slot.platform](slot)
            if slot.platform == Platform.INSTAGRAM:
                dist.instagram.append(pkg)
            elif slot.platform == Platform.TIKTOK:
                dist.tiktok.append(pkg)
            else:
                dist.youtube.append(pkg)
        return dist

    def export_all(self, out_dir: Path) -> dict[str, Path]:
        out_dir.mkdir(parents=True, exist_ok=True)
        paths: dict[str, Path] = {}
        for name, data in [
            ("instagram", self.instagram),
            ("tiktok", self.tiktok),
            ("youtube", self.youtube),
        ]:
            p = out_dir / f"{name}_package.json"
            p.write_text(
                json.dumps(
                    [asdict(pkg) for pkg in data],
                    ensure_ascii=False,
                    indent=2,
                )
            )
            paths[name] = p
        return paths

    def summary(self) -> str:
        lines = [
            f"Weekly distribution starting {self.week_start.isoformat()}:",
            f"  Instagram: {len(self.instagram)} posts",
            f"  TikTok: {len(self.tiktok)} posts",
            f"  YouTube: {len(self.youtube)} posts",
            f"  Total: {len(self.instagram) + len(self.tiktok) + len(self.youtube)} posts",
        ]
        return "\n".join(lines)


def build_distribution(days: int = 7, seed: int | None = None) -> WeeklyDistribution:
    plan = generate_week_plan(days=days, seed=seed)
    return WeeklyDistribution.from_plan(plan)
