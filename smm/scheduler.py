"""Content calendar and scheduling logic.

Manages a local JSON-based content calendar. Posts can be queued, listed,
and exported for Buffer / Make.com / Zapier integration.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any

from smm.platforms import PLATFORM_SPECS, Platform


@dataclass(slots=True)
class ScheduledPost:
    id: str
    platform: Platform
    format: str
    topic: str
    publish_at: datetime
    content: dict[str, Any] = field(default_factory=dict)
    status: str = "draft"
    referral_url: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "platform": self.platform.value,
            "format": self.format,
            "topic": self.topic,
            "publish_at": self.publish_at.isoformat(),
            "content": self.content,
            "status": self.status,
            "referral_url": self.referral_url,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScheduledPost:
        return cls(
            id=data["id"],
            platform=Platform(data["platform"]),
            format=data["format"],
            topic=data["topic"],
            publish_at=datetime.fromisoformat(data["publish_at"]),
            content=data.get("content", {}),
            status=data.get("status", "draft"),
            referral_url=data.get("referral_url", ""),
        )


@dataclass(slots=True)
class ContentCalendar:
    posts: list[ScheduledPost] = field(default_factory=list)
    _path: Path | None = None

    @classmethod
    def load(cls, path: Path) -> ContentCalendar:
        cal = cls(_path=path)
        if path.exists():
            data = json.loads(path.read_text())
            cal.posts = [ScheduledPost.from_dict(p) for p in data]
        return cal

    def save(self) -> None:
        if self._path is None:
            return
        self._path.write_text(
            json.dumps(
                [p.to_dict() for p in self.posts],
                ensure_ascii=False,
                indent=2,
            )
        )

    def add(self, post: ScheduledPost) -> None:
        self.posts.append(post)

    def upcoming(self, days: int = 7) -> list[ScheduledPost]:
        now = datetime.now()
        cutoff = now + timedelta(days=days)
        return sorted(
            [p for p in self.posts if now <= p.publish_at <= cutoff],
            key=lambda p: p.publish_at,
        )

    def by_platform(self, platform: Platform) -> list[ScheduledPost]:
        return [p for p in self.posts if p.platform == platform]

    def by_date(self, target: date) -> list[ScheduledPost]:
        return sorted(
            [p for p in self.posts if p.publish_at.date() == target],
            key=lambda p: p.publish_at,
        )

    def fill_week(
        self,
        start: date | None = None,
        days: int = 7,
        topics: list[dict[str, str]] | None = None,
    ) -> list[ScheduledPost]:
        start = start or date.today()
        created: list[ScheduledPost] = []
        topic_idx = 0
        default_topics = topics or []

        for day_offset in range(days):
            current_date = start + timedelta(days=day_offset)
            for platform in Platform:
                spec = PLATFORM_SPECS[platform]
                for slot_time in spec.posting_times:
                    hour, minute = (int(x) for x in slot_time.split(":"))
                    publish_dt = datetime.combine(current_date, time(hour, minute))

                    topic_data = (
                        default_topics[topic_idx % len(default_topics)]
                        if default_topics
                        else {
                            "topic": f"AI content #{topic_idx + 1}",
                            "format": spec.formats[0],
                        }
                    )
                    topic_idx += 1

                    post = ScheduledPost(
                        id=uuid.uuid4().hex[:12],
                        platform=platform,
                        format=topic_data.get("format", spec.formats[0]),
                        topic=topic_data.get("topic", ""),
                        publish_at=publish_dt,
                    )
                    self.add(post)
                    created.append(post)
        return created

    def export_csv(self, path: Path) -> None:
        lines = [
            "id,platform,format,topic,publish_at,status,referral_url,body,hashtags"
        ]
        for p in sorted(self.posts, key=lambda x: x.publish_at):
            body = p.content.get("body", "").replace('"', '""')
            hashtags = " ".join(p.content.get("hashtags", []))
            lines.append(
                f'"{p.id}","{p.platform.value}","{p.format}","{p.topic}",'
                f'"{p.publish_at.isoformat()}","{p.status}","{p.referral_url}",'
                f'"{body}","{hashtags}"'
            )
        path.write_text("\n".join(lines), encoding="utf-8")

    def export_buffer_json(self, path: Path) -> None:
        entries = [
            {
                "text": p.content.get("body", p.topic),
                "scheduled_at": p.publish_at.isoformat(),
                "profile_type": p.platform.value,
                "media": p.content.get("media", []),
            }
            for p in sorted(self.posts, key=lambda x: x.publish_at)
        ]
        path.write_text(json.dumps(entries, ensure_ascii=False, indent=2))
