"""Export content plans to scheduling tool formats.

Supported formats:
- Buffer CSV (direct import)
- Later CSV (direct import)
- Meta Business Suite bulk upload
- Generic iCal (.ics) for calendar integration
- Notion database JSON
"""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path

from smm.ready_posts import ReadyPost


def export_later_csv(posts: list[ReadyPost], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Caption",
                "Date",
                "Time",
                "Platform",
                "Media Type",
                "Hashtags",
                "Link",
            ]
        )
        for p in posts:
            media = "Video" if p.video_script else "Image"
            writer.writerow(
                [
                    p.caption,
                    p.day.isoformat(),
                    p.time_slot,
                    p.platform.title(),
                    media,
                    " ".join(p.hashtags),
                    p.referral_url,
                ]
            )
    return path


def export_meta_json(posts: list[ReadyPost], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    ig_posts = [p for p in posts if p.platform == "instagram"]
    entries = []
    for p in ig_posts:
        pub_dt = datetime.combine(p.day, datetime.min.time(), tzinfo=UTC)
        parts = p.time_slot.split(":")
        if len(parts) == 2:
            pub_dt = pub_dt.replace(hour=int(parts[0]), minute=int(parts[1]))
        entries.append(
            {
                "message": p.caption,
                "scheduled_publish_time": int(pub_dt.timestamp()),
                "media_type": "VIDEO" if p.video_script else "IMAGE",
                "visual_brief": p.visual_brief,
                "link": p.referral_url,
            }
        )
    data = {
        "platform": "instagram",
        "posts": entries,
        "total": len(entries),
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_ical(posts: list[ReadyPost], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//ShadowRigs SMM//EN",
        "CALSCALE:GREGORIAN",
    ]
    for i, p in enumerate(posts):
        pub_dt = datetime.combine(p.day, datetime.min.time())
        parts = p.time_slot.split(":")
        if len(parts) == 2:
            pub_dt = pub_dt.replace(hour=int(parts[0]), minute=int(parts[1]))
        dt_str = pub_dt.strftime("%Y%m%dT%H%M%S")
        summary = f"[{p.platform.upper()}] {p.topic[:60]}"
        desc = p.caption.replace("\n", "\\n").replace(",", "\\,")
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:smm-{p.day.isoformat()}-{i}@shadowrigs",
                f"DTSTART:{dt_str}",
                f"SUMMARY:{summary}",
                f"DESCRIPTION:{desc}",
                f"CATEGORIES:{p.pillar}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    path.write_text("\r\n".join(lines), encoding="utf-8")
    return path


def export_notion_json(posts: list[ReadyPost], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "properties": {
                "Name": {"title": [{"text": {"content": p.topic}}]},
                "Platform": {"select": {"name": p.platform.title()}},
                "Date": {"date": {"start": p.day.isoformat()}},
                "Time": {"rich_text": [{"text": {"content": p.time_slot}}]},
                "Pillar": {"select": {"name": p.pillar}},
                "Format": {"select": {"name": p.format}},
                "Status": {"select": {"name": "Draft"}},
                "Caption": {"rich_text": [{"text": {"content": p.caption[:2000]}}]},
            }
        }
        for p in posts
    ]
    data = {"database_rows": rows, "total": len(rows)}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_all_formats(
    posts: list[ReadyPost],
    out_dir: Path,
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    paths["later_csv"] = export_later_csv(posts, out_dir / "later_import.csv")
    paths["meta_json"] = export_meta_json(posts, out_dir / "meta_business.json")
    paths["ical"] = export_ical(posts, out_dir / "smm_calendar.ics")
    paths["notion"] = export_notion_json(posts, out_dir / "notion_import.json")
    return paths
