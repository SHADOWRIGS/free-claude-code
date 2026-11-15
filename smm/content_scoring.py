"""Content scoring — predict post performance for priority ordering.

Scores each post 0-100 based on hook strength, format fit,
platform match, timing, and pillar engagement multiplier.
Use to prioritize which posts to publish first when capacity
is limited or to identify weak spots for improvement.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from smm.content_pillars import PILLARS

HOOK_KEYWORDS_SCORE: dict[str, int] = {
    "бесплатн": 12,
    "секрет": 10,
    "ошибк": 10,
    "топ-": 8,
    "взлом": 9,
    "хакер": 8,
    "скидк": 11,
    "за 5 минут": 9,
    "за 10 минут": 8,
    "пошагов": 7,
    "чеклист": 7,
    "гайд": 6,
    "новинк": 6,
    "распаковка": 8,
    "AI": 7,
    "нейросет": 8,
    "CTF": 6,
    "OSINT": 7,
    "Kali": 6,
}

FORMAT_SCORES: dict[str, int] = {
    "reel": 15,
    "carousel": 12,
    "story": 10,
    "static_post": 6,
    "video": 14,
    "shorts": 15,
    "live": 8,
}

PLATFORM_ENGAGEMENT: dict[str, float] = {
    "tiktok": 1.15,
    "instagram": 1.0,
    "youtube": 0.95,
}

PILLAR_MULTIPLIER: dict[str, float] = {
    "Cyber Security & Ethical Hacking": 1.1,
    "Blue Team / Defensive Security": 0.95,
    "Red Team / Offensive Security": 1.15,
    "Machine Learning & AI": 1.2,
    "AliExpress - Гаджеты": 1.05,
}

OPTIMAL_HOURS = {9, 12, 13, 18, 19, 20, 21}


@dataclass(frozen=True, slots=True)
class ScoredPost:
    title: str
    pillar: str
    platform: str
    format_type: str
    hour: int
    hook_score: int
    format_score: int
    timing_score: int
    total_score: int
    grade: str


def _hook_score(text: str) -> int:
    text_lower = text.lower()
    score = 0
    for keyword, points in HOOK_KEYWORDS_SCORE.items():
        if keyword.lower() in text_lower:
            score += points
    return min(score, 30)


def _format_score(fmt: str) -> int:
    return FORMAT_SCORES.get(fmt.lower(), 5)


def _timing_score(hour: int) -> int:
    return 15 if hour in OPTIMAL_HOURS else 5


def _grade(score: int) -> str:
    if score >= 80:
        return "A"
    if score >= 65:
        return "B"
    if score >= 50:
        return "C"
    if score >= 35:
        return "D"
    return "F"


def score_post(
    title: str,
    pillar: str,
    platform: str,
    format_type: str = "static_post",
    hour: int = 12,
) -> ScoredPost:
    hook = _hook_score(title)
    fmt = _format_score(format_type)
    timing = _timing_score(hour)

    raw = hook + fmt + timing
    plat_mult = PLATFORM_ENGAGEMENT.get(platform.lower(), 1.0)
    pillar_mult = PILLAR_MULTIPLIER.get(pillar, 1.0)
    total = min(int(raw * plat_mult * pillar_mult), 100)

    return ScoredPost(
        title=title,
        pillar=pillar,
        platform=platform,
        format_type=format_type,
        hour=hour,
        hook_score=hook,
        format_score=fmt,
        timing_score=timing,
        total_score=total,
        grade=_grade(total),
    )


def generate_scored_batch(
    count: int = 30,
    seed: int | None = None,
) -> list[ScoredPost]:
    rng = random.Random(seed)
    platforms = ["instagram", "tiktok", "youtube"]
    formats = list(FORMAT_SCORES.keys())
    hours = list(range(8, 23))

    sample_titles = [
        "Бесплатный чеклист: настрой безопасность за 10 минут",
        "Топ-5 хакерских гаджетов до $20",
        "Секрет: как хакеры обходят антивирусы",
        "Пошаговый гайд по Kali Linux для новичков",
        "Распаковка: 10 устройств с AliExpress",
        "AI заменит программистов? Разбираемся",
        "Как настроить SIEM за 1 час (бесплатно)",
        "CTF для новичков: первая задача за 5 минут",
        "Ошибка, которую делают 90% новичков",
        "Нейросеть написала код лучше меня",
        "OSINT: что можно узнать о тебе за 5 минут",
        "Скидка 30% на курс по пентесту",
        "Новинка с AliExpress: ESP32 для хакеров",
        "Взлом WiFi за 3 минуты (легально)",
        "Гайд: первый багбаунти за месяц",
    ]

    scored: list[ScoredPost] = []
    for _ in range(count):
        title = rng.choice(sample_titles)
        pillar = rng.choice(PILLARS).name
        platform = rng.choice(platforms)
        fmt = rng.choice(formats)
        hour = rng.choice(hours)
        scored.append(score_post(title, pillar, platform, fmt, hour))

    scored.sort(key=lambda s: s.total_score, reverse=True)
    return scored


def export_scores_json(scored: list[ScoredPost], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "title": s.title,
            "pillar": s.pillar,
            "platform": s.platform,
            "format": s.format_type,
            "hour": s.hour,
            "hook_score": s.hook_score,
            "format_score": s.format_score,
            "timing_score": s.timing_score,
            "total": s.total_score,
            "grade": s.grade,
        }
        for s in scored
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_scores_txt(scored: list[ScoredPost], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "СКОРИНГ КОНТЕНТА — ПРИОРИТИЗАЦИЯ ПОСТОВ",
        "=" * 60,
    ]

    for s in scored:
        lines.append(f"\n[{s.grade}] {s.total_score}/100 — {s.title}")
        lines.append(f"  Направление: {s.pillar}")
        lines.append(
            f"  Платформа: {s.platform} | Формат: {s.format_type} | Час: {s.hour}:00"
        )
        lines.append(
            f"  Хук: {s.hook_score} | Формат: {s.format_score} | Время: {s.timing_score}"
        )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def scoring_summary(scored: list[ScoredPost]) -> str:
    if not scored:
        return "Скоринг: 0 постов"

    by_grade: dict[str, int] = {}
    total = 0
    for s in scored:
        by_grade[s.grade] = by_grade.get(s.grade, 0) + 1
        total += s.total_score

    avg = total / len(scored)
    lines: list[str] = [
        f"Скоринг контента: {len(scored)} постов",
        f"Средний балл: {avg:.1f}/100",
        "\nПо грейдам:",
    ]
    for grade in ("A", "B", "C", "D", "F"):
        count = by_grade.get(grade, 0)
        if count:
            lines.append(f"  {grade}: {count}")

    return "\n".join(lines)
