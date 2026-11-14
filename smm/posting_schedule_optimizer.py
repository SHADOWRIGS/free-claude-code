"""Posting schedule optimizer — maximize reach through smart timing.

Analyzes platform-specific optimal posting times, day-of-week patterns,
and content type distribution to recommend the best posting schedule.

Uses research-backed engagement data to score time slots and
distribute content types for maximum algorithm-friendly consistency.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time, timedelta

from smm.platforms import Platform
from smm.ready_posts import ReadyPost

ENGAGEMENT_SCORES: dict[str, dict[int, float]] = {
    "instagram": {
        8: 0.85,
        9: 0.90,
        10: 0.75,
        11: 0.80,
        12: 0.95,
        13: 0.85,
        14: 0.70,
        15: 0.65,
        16: 0.60,
        17: 0.80,
        18: 0.90,
        19: 0.95,
        20: 0.85,
        21: 0.80,
        22: 0.60,
    },
    "tiktok": {
        7: 0.70,
        8: 0.75,
        9: 0.80,
        10: 0.85,
        11: 0.90,
        12: 0.95,
        13: 0.85,
        14: 0.80,
        15: 0.75,
        16: 0.70,
        17: 0.80,
        18: 0.85,
        19: 0.95,
        20: 0.90,
        21: 0.85,
        22: 0.80,
        23: 0.70,
    },
    "youtube": {
        9: 0.70,
        10: 0.75,
        11: 0.80,
        12: 0.85,
        13: 0.80,
        14: 0.90,
        15: 0.95,
        16: 0.90,
        17: 0.85,
        18: 0.80,
        19: 0.75,
        20: 0.70,
    },
}

WEEKDAY_MULTIPLIERS: dict[str, dict[int, float]] = {
    "instagram": {
        0: 0.95,
        1: 1.00,
        2: 1.05,
        3: 1.00,
        4: 0.95,
        5: 0.85,
        6: 0.90,
    },
    "tiktok": {
        0: 0.90,
        1: 1.00,
        2: 1.00,
        3: 1.05,
        4: 1.00,
        5: 0.95,
        6: 0.90,
    },
    "youtube": {
        0: 0.90,
        1: 0.95,
        2: 1.00,
        3: 1.00,
        4: 1.05,
        5: 1.00,
        6: 0.95,
    },
}


@dataclass(frozen=True, slots=True)
class TimeSlotScore:
    platform: str
    hour: int
    weekday: int
    base_score: float
    weekday_multiplier: float
    final_score: float


@dataclass(frozen=True, slots=True)
class ScheduleRecommendation:
    platform: str
    day: date
    recommended_times: list[time]
    scores: list[float]


def score_time_slot(platform: Platform, hour: int, weekday: int) -> TimeSlotScore:
    platform_scores = ENGAGEMENT_SCORES.get(platform.value, {})
    base = platform_scores.get(hour, 0.50)
    weekday_mults = WEEKDAY_MULTIPLIERS.get(platform.value, {})
    mult = weekday_mults.get(weekday, 1.0)
    final = round(base * mult, 3)
    return TimeSlotScore(
        platform=platform.value,
        hour=hour,
        weekday=weekday,
        base_score=base,
        weekday_multiplier=mult,
        final_score=final,
    )


def best_times(
    platform: Platform,
    weekday: int,
    count: int = 3,
) -> list[TimeSlotScore]:
    scores = [score_time_slot(platform, hour, weekday) for hour in range(6, 24)]
    scores.sort(key=lambda s: s.final_score, reverse=True)
    return scores[:count]


def recommend_schedule(
    start: date | None = None,
    days: int = 7,
    posts_per_platform: int = 3,
) -> list[ScheduleRecommendation]:
    if start is None:
        start = date.today()

    recommendations: list[ScheduleRecommendation] = []
    for day_offset in range(days):
        current = start + timedelta(days=day_offset)
        weekday = current.weekday()
        for platform in Platform:
            tops = best_times(platform, weekday, count=posts_per_platform)
            rec = ScheduleRecommendation(
                platform=platform.value,
                day=current,
                recommended_times=[time(t.hour, 0) for t in tops],
                scores=[t.final_score for t in tops],
            )
            recommendations.append(rec)
    return recommendations


def optimize_existing_posts(
    posts: list[ReadyPost],
) -> list[dict[str, object]]:
    suggestions: list[dict[str, object]] = []
    for i, post in enumerate(posts):
        platform = None
        for p in Platform:
            if p.value == post.platform:
                platform = p
                break
        if platform is None:
            continue

        weekday = post.day.weekday()
        tops = best_times(platform, weekday, count=1)
        best_hour = tops[0].hour if tops else 12
        current_hour = (
            int(post.time_slot.split(":")[0]) if ":" in post.time_slot else 12
        )

        score_current = score_time_slot(platform, current_hour, weekday).final_score
        score_best = tops[0].final_score if tops else score_current

        if score_best > score_current * 1.1:
            suggestions.append(
                {
                    "post_index": i,
                    "platform": post.platform,
                    "day": post.day.isoformat(),
                    "current_time": post.time_slot,
                    "suggested_time": f"{best_hour:02d}:00",
                    "current_score": score_current,
                    "suggested_score": score_best,
                    "improvement": f"+{round((score_best / score_current - 1) * 100)}%",
                }
            )
    return suggestions


def schedule_heatmap(platform: Platform) -> str:
    weekday_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    lines: list[str] = [f"Тепловая карта: {platform.value}\n"]
    header = "Час  " + "  ".join(f"{d:>4}" for d in weekday_names)
    lines.append(header)
    lines.append("-" * len(header))

    for hour in range(6, 24):
        row = f"{hour:02d}:00"
        for wd in range(7):
            score = score_time_slot(platform, hour, wd).final_score
            if score >= 0.90:
                marker = " ███"
            elif score >= 0.80:
                marker = " ▓▓▓"
            elif score >= 0.70:
                marker = " ▒▒▒"
            else:
                marker = " ░░░"
            row += marker
        lines.append(row)

    lines.append("\nЛегенда: ███ >0.90  ▓▓▓ >0.80  ▒▒▒ >0.70  ░░░ <0.70")
    return "\n".join(lines)


def optimizer_summary(
    recommendations: list[ScheduleRecommendation],
) -> str:
    by_platform: dict[str, list[float]] = {}
    for rec in recommendations:
        by_platform.setdefault(rec.platform, []).extend(rec.scores)

    lines = [
        f"Оптимизация расписания: {len(recommendations)} рекомендаций",
        f"Дней: {len({r.day for r in recommendations})}",
        "\nСредний скор вовлечённости:",
    ]
    for platform, scores in sorted(by_platform.items()):
        avg = sum(scores) / len(scores) if scores else 0
        lines.append(f"  {platform}: {avg:.3f}")
    return "\n".join(lines)
