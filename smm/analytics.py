"""Analytics and weekly reporting for SMM automation.

Tracks planned content metrics and generates weekly performance
report templates. Actual engagement data is filled in manually
or via platform APIs when available.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

from smm.post_generator import generate_week_plan


@dataclass(slots=True)
class PostMetrics:
    date: str
    platform: str
    topic: str
    pillar: str
    format: str
    impressions: int = 0
    reach: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    link_clicks: int = 0
    profile_visits: int = 0

    @property
    def engagement_rate(self) -> float:
        if self.impressions == 0:
            return 0.0
        total = self.likes + self.comments + self.shares + self.saves
        return round(total / self.impressions * 100, 2)

    @property
    def click_through_rate(self) -> float:
        if self.impressions == 0:
            return 0.0
        return round(self.link_clicks / self.impressions * 100, 2)


@dataclass(slots=True)
class WeeklyReport:
    week_start: date
    week_end: date
    posts: list[PostMetrics] = field(default_factory=list)

    @property
    def total_posts(self) -> int:
        return len(self.posts)

    @property
    def total_impressions(self) -> int:
        return sum(p.impressions for p in self.posts)

    @property
    def total_engagement(self) -> int:
        return sum(p.likes + p.comments + p.shares + p.saves for p in self.posts)

    @property
    def total_clicks(self) -> int:
        return sum(p.link_clicks for p in self.posts)

    @property
    def avg_engagement_rate(self) -> float:
        rates = [p.engagement_rate for p in self.posts if p.impressions > 0]
        if not rates:
            return 0.0
        return round(sum(rates) / len(rates), 2)

    def by_platform(self) -> dict[str, list[PostMetrics]]:
        result: dict[str, list[PostMetrics]] = {}
        for p in self.posts:
            result.setdefault(p.platform, []).append(p)
        return result

    def by_pillar(self) -> dict[str, list[PostMetrics]]:
        result: dict[str, list[PostMetrics]] = {}
        for p in self.posts:
            result.setdefault(p.pillar, []).append(p)
        return result

    def top_posts(self, n: int = 5) -> list[PostMetrics]:
        return sorted(self.posts, key=lambda p: p.engagement_rate, reverse=True)[:n]

    def summary(self) -> str:
        lines = [
            "# Недельный отчёт SMM",
            f"Период: {self.week_start.isoformat()} — {self.week_end.isoformat()}",
            "",
            "## Общие метрики",
            f"- Всего постов: {self.total_posts}",
            f"- Охват: {self.total_impressions:,}",
            f"- Вовлеченность: {self.total_engagement:,}",
            f"- Клики по ссылкам: {self.total_clicks:,}",
            f"- Средний ER: {self.avg_engagement_rate}%",
            "",
            "## По платформам",
        ]
        for platform, posts in sorted(self.by_platform().items()):
            total_eng = sum(p.likes + p.comments + p.shares + p.saves for p in posts)
            total_imp = sum(p.impressions for p in posts)
            er = round(total_eng / total_imp * 100, 2) if total_imp > 0 else 0.0
            lines.append(f"- **{platform.title()}**: {len(posts)} постов, ER {er}%")

        lines.append("")
        lines.append("## По направлениям")
        for pillar, posts in sorted(self.by_pillar().items()):
            total_clicks = sum(p.link_clicks for p in posts)
            lines.append(f"- **{pillar}**: {len(posts)} постов, {total_clicks} кликов")

        top = self.top_posts(3)
        if top and any(p.impressions > 0 for p in top):
            lines.append("")
            lines.append("## Топ-3 поста")
            for i, p in enumerate(top, 1):
                if p.impressions > 0:
                    lines.append(
                        f"{i}. [{p.platform}] {p.topic} — ER {p.engagement_rate}%"
                    )

        return "\n".join(lines)

    def export_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "week_start": self.week_start.isoformat(),
            "week_end": self.week_end.isoformat(),
            "summary": {
                "total_posts": self.total_posts,
                "total_impressions": self.total_impressions,
                "total_engagement": self.total_engagement,
                "total_clicks": self.total_clicks,
                "avg_engagement_rate": self.avg_engagement_rate,
            },
            "posts": [asdict(p) for p in self.posts],
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def export_markdown(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.summary(), encoding="utf-8")


def create_tracking_template(days: int = 7, seed: int | None = None) -> WeeklyReport:
    from datetime import timedelta

    plan = generate_week_plan(days=days, seed=seed)
    start = plan[0].day if plan else date.today()
    end = start + timedelta(days=days - 1)

    posts = [
        PostMetrics(
            date=slot.day.isoformat(),
            platform=slot.platform.value,
            topic=slot.topic,
            pillar=slot.pillar.name,
            format=slot.format,
        )
        for slot in plan
    ]
    return WeeklyReport(week_start=start, week_end=end, posts=posts)


def load_report(path: Path) -> WeeklyReport:
    if not path.exists():
        return create_tracking_template()
    data = json.loads(path.read_text())
    posts = [PostMetrics(**p) for p in data["posts"]]
    return WeeklyReport(
        week_start=date.fromisoformat(data["week_start"]),
        week_end=date.fromisoformat(data["week_end"]),
        posts=posts,
    )
