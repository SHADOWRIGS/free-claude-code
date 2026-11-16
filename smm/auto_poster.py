"""Auto-posting configuration and queue manager.

Defines posting profiles for each platform (Instagram, TikTok, YouTube),
queue management for scheduled posts, and retry/error handling config.
Generates ready-to-use posting configs that plug into Buffer, Later,
or direct platform APIs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import time
from pathlib import Path

PLATFORMS: tuple[str, ...] = ("instagram", "tiktok", "youtube")

POSTING_WINDOWS: dict[str, list[dict[str, str]]] = {
    "instagram": [
        {"slot": "morning", "time": "09:00", "label": "Утро — высокая активность"},
        {"slot": "afternoon", "time": "13:00", "label": "Обед — пик охвата"},
        {"slot": "evening", "time": "19:00", "label": "Вечер — максимум вовлечённости"},
    ],
    "tiktok": [
        {"slot": "morning", "time": "08:00", "label": "Утро — FYP активен"},
        {"slot": "afternoon", "time": "12:00", "label": "Обед — вирусный потенциал"},
        {"slot": "evening", "time": "20:00", "label": "Вечер — пиковый скроллинг"},
    ],
    "youtube": [
        {"slot": "morning", "time": "10:00", "label": "Утро — подписчики онлайн"},
        {"slot": "afternoon", "time": "14:00", "label": "День — алгоритм активен"},
        {"slot": "evening", "time": "18:00", "label": "Вечер — прайм-тайм"},
    ],
}

API_PROFILES: dict[str, dict[str, str]] = {
    "buffer": {
        "name": "Buffer",
        "api_base": "https://api.bufferapp.com/1",
        "auth_type": "oauth2",
        "docs_url": "https://buffer.com/developers/api",
        "env_var": "BUFFER_ACCESS_TOKEN",
        "description": "Кросс-платформенный планировщик. Поддерживает IG, TikTok, YouTube.",
    },
    "later": {
        "name": "Later",
        "api_base": "https://api.later.com/v1",
        "auth_type": "oauth2",
        "docs_url": "https://later.com/developers",
        "env_var": "LATER_ACCESS_TOKEN",
        "description": "Визуальный планировщик. Лучший для Instagram.",
    },
    "meta_business": {
        "name": "Meta Business Suite",
        "api_base": "https://graph.facebook.com/v18.0",
        "auth_type": "page_token",
        "docs_url": "https://developers.facebook.com/docs/instagram-api",
        "env_var": "META_PAGE_TOKEN",
        "description": "Прямой постинг в Instagram через Meta API.",
    },
    "tiktok_creator": {
        "name": "TikTok Creator Tools",
        "api_base": "https://open.tiktokapis.com/v2",
        "auth_type": "oauth2",
        "docs_url": "https://developers.tiktok.com/doc",
        "env_var": "TIKTOK_ACCESS_TOKEN",
        "description": "Прямая публикация видео в TikTok.",
    },
    "youtube_data": {
        "name": "YouTube Data API",
        "api_base": "https://www.googleapis.com/youtube/v3",
        "auth_type": "oauth2",
        "docs_url": "https://developers.google.com/youtube/v3",
        "env_var": "YOUTUBE_API_KEY",
        "description": "Загрузка видео и управление каналом.",
    },
}

RETRY_POLICY: dict[str, int | float] = {
    "max_retries": 3,
    "backoff_base_seconds": 60,
    "backoff_multiplier": 2.0,
    "timeout_seconds": 30,
}

RATE_LIMITS: dict[str, dict[str, int]] = {
    "instagram": {"posts_per_day": 25, "stories_per_day": 100, "reels_per_day": 10},
    "tiktok": {"posts_per_day": 50, "max_video_length_sec": 600},
    "youtube": {"uploads_per_day": 50, "max_video_length_sec": 43200},
}


@dataclass(frozen=True, slots=True)
class PostingSlot:
    platform: str
    slot: str
    post_time: time
    label: str


@dataclass(frozen=True, slots=True)
class APIProfile:
    key: str
    name: str
    api_base: str
    auth_type: str
    docs_url: str
    env_var: str
    description: str


@dataclass(frozen=True, slots=True)
class QueueItem:
    platform: str
    slot: str
    caption: str
    hashtags: str
    media_brief: str
    status: str


@dataclass(frozen=True, slots=True)
class AutoPosterConfig:
    profiles: tuple[APIProfile, ...]
    slots: tuple[PostingSlot, ...]
    queue_size: int
    retry_policy: dict[str, int | float]
    rate_limits: dict[str, dict[str, int]]


def generate_posting_slots() -> tuple[PostingSlot, ...]:
    slots: list[PostingSlot] = []
    for platform in PLATFORMS:
        for window in POSTING_WINDOWS[platform]:
            h, m = window["time"].split(":")
            slots.append(
                PostingSlot(
                    platform=platform,
                    slot=window["slot"],
                    post_time=time(int(h), int(m)),
                    label=window["label"],
                )
            )
    return tuple(slots)


def generate_api_profiles() -> tuple[APIProfile, ...]:
    return tuple(
        APIProfile(
            key=k,
            name=v["name"],
            api_base=v["api_base"],
            auth_type=v["auth_type"],
            docs_url=v["docs_url"],
            env_var=v["env_var"],
            description=v["description"],
        )
        for k, v in API_PROFILES.items()
    )


def generate_auto_poster_config() -> AutoPosterConfig:
    return AutoPosterConfig(
        profiles=generate_api_profiles(),
        slots=generate_posting_slots(),
        queue_size=63,
        retry_policy=dict(RETRY_POLICY),
        rate_limits={k: dict(v) for k, v in RATE_LIMITS.items()},
    )


def export_auto_poster_json(config: AutoPosterConfig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "profiles": [
            {
                "key": p.key,
                "name": p.name,
                "api_base": p.api_base,
                "auth_type": p.auth_type,
                "docs_url": p.docs_url,
                "env_var": p.env_var,
                "description": p.description,
            }
            for p in config.profiles
        ],
        "posting_slots": [
            {
                "platform": s.platform,
                "slot": s.slot,
                "time": s.post_time.strftime("%H:%M"),
                "label": s.label,
            }
            for s in config.slots
        ],
        "queue_size": config.queue_size,
        "retry_policy": config.retry_policy,
        "rate_limits": config.rate_limits,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_auto_poster_txt(config: AutoPosterConfig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "АВТО-ПОСТИНГ — КОНФИГУРАЦИЯ",
        "=" * 60,
        "\n📡 API-ПРОФИЛИ",
        "━" * 50,
    ]
    for p in config.profiles:
        lines.append(f"\n  [{p.name}]")
        lines.append(f"  API: {p.api_base}")
        lines.append(f"  Авторизация: {p.auth_type}")
        lines.append(f"  Env: {p.env_var}")
        lines.append(f"  Описание: {p.description}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🕐 РАСПИСАНИЕ ПУБЛИКАЦИЙ")
    lines.append("━" * 50)
    lines.extend(
        f"  {s.platform:<12} {s.slot:<12} "
        f"{s.post_time.strftime('%H:%M')}  {s.label}"
        for s in config.slots
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("🔄 ПОЛИТИКА ПОВТОРОВ")
    lines.append("━" * 50)
    for k, v in config.retry_policy.items():
        lines.append(f"  {k}: {v}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📊 ЛИМИТЫ ПЛАТФОРМ")
    lines.append("━" * 50)
    for platform, limits in config.rate_limits.items():
        lines.append(f"\n  [{platform}]")
        for lk, lv in limits.items():
            lines.append(f"    {lk}: {lv}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def auto_poster_summary(config: AutoPosterConfig) -> str:
    return (
        f"Авто-постинг: {len(config.profiles)} API-профилей, "
        f"{len(config.slots)} слотов публикации, "
        f"очередь {config.queue_size} постов, "
        f"{len(config.rate_limits)} платформ с лимитами"
    )
