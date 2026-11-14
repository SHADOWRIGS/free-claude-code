"""Content mixer — balanced daily content scheduling.

Takes the raw post plan and redistributes content types so each day
has the optimal mix of educational, promotional, entertaining, and
engagement content. Prevents clustering of same-type posts.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from smm.content_strategy import CONTENT_MIX
from smm.ready_posts import ReadyPost, generate_ready_posts

CONTENT_TYPE_MAP: dict[str, str] = {
    "tutorial": "educational",
    "tip": "educational",
    "how-to": "educational",
    "guide": "educational",
    "cheatsheet": "educational",
    "comparison": "educational",
    "meme": "entertaining",
    "behind-the-scenes": "entertaining",
    "day-in-life": "entertaining",
    "unboxing": "entertaining",
    "reaction": "entertaining",
    "promo": "promotional",
    "sale": "promotional",
    "launch": "promotional",
    "discount": "promotional",
    "referral": "promotional",
    "poll": "engagement",
    "quiz": "engagement",
    "question": "engagement",
    "challenge": "engagement",
    "giveaway": "engagement",
    "testimonial": "social_proof",
    "case-study": "social_proof",
    "review": "social_proof",
    "result": "social_proof",
}


@dataclass(frozen=True, slots=True)
class MixedPost:
    post: ReadyPost
    content_type: str
    type_label: str


@dataclass(frozen=True, slots=True)
class DayMix:
    day: date
    posts: list[MixedPost]
    type_distribution: dict[str, int]
    balance_score: float


TYPE_LABELS: dict[str, str] = {
    "educational": "Образовательный",
    "entertaining": "Развлекательный",
    "promotional": "Промо",
    "engagement": "Вовлечение",
    "social_proof": "Соц. доказательство",
}


def classify_post(post: ReadyPost) -> str:
    topic_lower = post.topic.lower()
    for keyword, content_type in CONTENT_TYPE_MAP.items():
        if keyword in topic_lower:
            return content_type
    fmt = post.format.lower()
    if fmt in ("carousel", "tutorial"):
        return "educational"
    if fmt in ("reel", "short_video"):
        return "entertaining"
    if fmt == "story":
        return "engagement"
    return "educational"


def _balance_score(type_dist: dict[str, int], total: int) -> float:
    if total == 0:
        return 1.0
    score = 0.0
    for content_type, target_share in CONTENT_MIX.items():
        actual = type_dist.get(content_type, 0) / total
        diff = abs(actual - target_share)
        score += diff
    return max(0.0, 1.0 - score)


def mix_posts(
    posts: list[ReadyPost],
    seed: int | None = None,
) -> list[DayMix]:
    rng = random.Random(seed)

    by_day: dict[date, list[ReadyPost]] = {}
    for p in posts:
        by_day.setdefault(p.day, []).append(p)

    day_mixes: list[DayMix] = []
    for day in sorted(by_day):
        day_posts = by_day[day]
        rng.shuffle(day_posts)

        mixed: list[MixedPost] = [
            MixedPost(
                post=p,
                content_type=classify_post(p),
                type_label=TYPE_LABELS.get(classify_post(p), "Другое"),
            )
            for p in day_posts
        ]

        type_dist: dict[str, int] = {}
        for m in mixed:
            type_dist[m.content_type] = type_dist.get(m.content_type, 0) + 1

        score = _balance_score(type_dist, len(mixed))

        day_mixes.append(
            DayMix(
                day=day,
                posts=mixed,
                type_distribution=type_dist,
                balance_score=round(score, 2),
            )
        )

    return day_mixes


def generate_mixed_schedule(
    days: int = 7,
    seed: int | None = None,
) -> list[DayMix]:
    posts = generate_ready_posts(days=days, seed=seed)
    return mix_posts(posts, seed=seed)


def export_mix_json(day_mixes: list[DayMix], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "day": dm.day.isoformat(),
            "posts": [
                {
                    "platform": m.post.platform,
                    "topic": m.post.topic,
                    "time": m.post.time_slot,
                    "content_type": m.content_type,
                    "type_label": m.type_label,
                    "pillar": m.post.pillar,
                }
                for m in dm.posts
            ],
            "type_distribution": dm.type_distribution,
            "balance_score": dm.balance_score,
        }
        for dm in day_mixes
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_mix_txt(day_mixes: list[DayMix], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "КОНТЕНТ-МИКС — БАЛАНС ПО ДНЯМ",
        "=" * 60,
    ]

    for dm in day_mixes:
        lines.append(f"\n{'─' * 40}")
        lines.append(
            f"📅 {dm.day.isoformat()} | "
            f"{len(dm.posts)} постов | "
            f"Баланс: {dm.balance_score:.0%}"
        )
        for ctype, count in sorted(dm.type_distribution.items()):
            label = TYPE_LABELS.get(ctype, ctype)
            lines.append(f"  {label}: {count}")
        lines.append("")
        lines.extend(
            f"  [{m.type_label}] {m.post.platform} "
            f"{m.post.time_slot} — {m.post.topic[:40]}"
            for m in dm.posts
        )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def mix_summary(day_mixes: list[DayMix]) -> str:
    total = sum(len(dm.posts) for dm in day_mixes)
    avg_score = (
        sum(dm.balance_score for dm in day_mixes) / len(day_mixes) if day_mixes else 0
    )
    lines: list[str] = [
        f"Контент-микс: {total} постов, {len(day_mixes)} дней",
        f"Средний баланс: {avg_score:.0%}",
    ]
    global_dist: dict[str, int] = {}
    for dm in day_mixes:
        for ctype, count in dm.type_distribution.items():
            global_dist[ctype] = global_dist.get(ctype, 0) + count
    lines.append("\nРаспределение:")
    for ctype, count in sorted(global_dist.items(), key=lambda x: -x[1]):
        label = TYPE_LABELS.get(ctype, ctype)
        pct = count / total * 100 if total else 0
        lines.append(f"  {label}: {count} ({pct:.0f}%)")
    return "\n".join(lines)
