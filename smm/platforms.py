"""Platform definitions and formatting constraints."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field


class Platform(enum.StrEnum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"


@dataclass(frozen=True, slots=True)
class PlatformSpec:
    name: str
    max_caption_length: int
    hashtag_range: tuple[int, int]
    posting_times: list[str] = field(default_factory=list)
    formats: list[str] = field(default_factory=list)


PLATFORM_SPECS: dict[Platform, PlatformSpec] = {
    Platform.INSTAGRAM: PlatformSpec(
        name="Instagram",
        max_caption_length=2200,
        hashtag_range=(20, 30),
        posting_times=["09:00", "14:00", "20:00"],
        formats=["reels", "carousel", "stories", "static_post"],
    ),
    Platform.TIKTOK: PlatformSpec(
        name="TikTok",
        max_caption_length=4000,
        hashtag_range=(5, 10),
        posting_times=["10:00", "15:00", "21:00"],
        formats=["short_video", "duet", "stitch", "live"],
    ),
    Platform.YOUTUBE: PlatformSpec(
        name="YouTube",
        max_caption_length=5000,
        hashtag_range=(3, 15),
        posting_times=["11:00", "16:00", "22:00"],
        formats=["shorts", "full_video", "community_post"],
    ),
}
