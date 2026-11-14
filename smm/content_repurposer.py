"""Content repurposer — adapt one piece of content across platforms.

Takes a single source post (ReadyPost) and generates platform-adapted
versions with appropriate caption length, hashtag count, format, and
visual brief adjustments for each target platform.

Enables creating once → publishing everywhere with platform-native feel.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from smm.platforms import PLATFORM_SPECS, Platform
from smm.ready_posts import ReadyPost


@dataclass(frozen=True, slots=True)
class RepurposedPost:
    original_platform: str
    target_platform: str
    original_caption: str
    adapted_caption: str
    adapted_hashtags: list[str]
    adapted_format: str
    visual_note: str
    video_note: str


def _trim_caption(caption: str, max_len: int) -> str:
    if len(caption) <= max_len:
        return caption
    trimmed = caption[: max_len - 3].rsplit(" ", 1)[0]
    return trimmed + "..."


def _adapt_hashtags(hashtags: list[str], target: Platform) -> list[str]:
    spec = PLATFORM_SPECS[target]
    max_tags = spec.hashtag_range[1]
    return hashtags[:max_tags]


FORMAT_MAP: dict[str, dict[str, str]] = {
    "instagram": {
        "static_post": "static_post",
        "reels": "reels",
        "carousel": "carousel",
        "story": "story",
        "short_video": "reels",
        "shorts": "reels",
        "full_video": "reels",
        "duet": "reels",
    },
    "tiktok": {
        "static_post": "short_video",
        "reels": "short_video",
        "carousel": "short_video",
        "story": "short_video",
        "short_video": "short_video",
        "shorts": "short_video",
        "full_video": "short_video",
        "duet": "duet",
    },
    "youtube": {
        "static_post": "shorts",
        "reels": "shorts",
        "carousel": "shorts",
        "story": "shorts",
        "short_video": "shorts",
        "shorts": "shorts",
        "full_video": "full_video",
        "duet": "shorts",
    },
}


def _adapt_format(original_format: str, target: Platform) -> str:
    mapping = FORMAT_MAP.get(target.value, {})
    return mapping.get(original_format, original_format)


VISUAL_ADAPTATIONS: dict[str, str] = {
    "instagram": "Квадрат 1:1 или 4:5, яркие цвета, минималистичный текст на изображении",
    "tiktok": "Вертикаль 9:16, динамичный монтаж, субтитры крупным шрифтом",
    "youtube": "Горизонталь 16:9 для видео, вертикаль 9:16 для Shorts, превью с крупным текстом",
}

VIDEO_ADAPTATIONS: dict[str, str] = {
    "instagram": "Reels 15-60 сек, хук в первые 3 секунды, музыка из библиотеки IG",
    "tiktok": "15-60 сек, trending звук, текст на экране, быстрый темп",
    "youtube": "Shorts до 60 сек или полное видео 8-15 мин с таймкодами",
}


def repurpose_post(
    post: ReadyPost,
    target: Platform,
) -> RepurposedPost:
    spec = PLATFORM_SPECS[target]
    adapted_caption = _trim_caption(post.caption, spec.max_caption_length)
    adapted_hashtags = _adapt_hashtags(post.hashtags, target)
    adapted_format = _adapt_format(post.format, target)
    visual_note = VISUAL_ADAPTATIONS.get(target.value, "")
    video_note = VIDEO_ADAPTATIONS.get(target.value, "")

    return RepurposedPost(
        original_platform=post.platform,
        target_platform=target.value,
        original_caption=post.caption,
        adapted_caption=adapted_caption,
        adapted_hashtags=adapted_hashtags,
        adapted_format=adapted_format,
        visual_note=visual_note,
        video_note=video_note,
    )


def repurpose_batch(
    posts: list[ReadyPost],
    targets: list[Platform] | None = None,
) -> list[RepurposedPost]:
    if targets is None:
        targets = list(Platform)

    results: list[RepurposedPost] = []
    for post in posts:
        original_platform = None
        for p in Platform:
            if p.value == post.platform:
                original_platform = p
                break
        for target in targets:
            if original_platform and target == original_platform:
                continue
            results.append(repurpose_post(post, target))
    return results


def export_repurposed_json(posts: list[RepurposedPost], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "original_platform": p.original_platform,
            "target_platform": p.target_platform,
            "adapted_caption": p.adapted_caption,
            "adapted_hashtags": p.adapted_hashtags,
            "adapted_format": p.adapted_format,
            "visual_note": p.visual_note,
            "video_note": p.video_note,
        }
        for p in posts
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def repurpose_summary(posts: list[RepurposedPost]) -> str:
    by_target: dict[str, int] = {}
    by_source: dict[str, int] = {}
    for p in posts:
        by_target[p.target_platform] = by_target.get(p.target_platform, 0) + 1
        by_source[p.original_platform] = by_source.get(p.original_platform, 0) + 1

    lines = [
        f"Репёрпоз: {len(posts)} адаптаций",
        "\nИз платформ:",
    ]
    for name, count in sorted(by_source.items()):
        lines.append(f"  {name}: {count} оригиналов")
    lines.append("\nВ платформы:")
    for name, count in sorted(by_target.items()):
        lines.append(f"  {name}: {count} адаптаций")
    return "\n".join(lines)
