"""Visual content calendar — weekly grid view as HTML.

Renders a colour-coded weekly calendar where each cell is a
scheduled post slot.  Rows are time slots, columns are days,
and posts are colour-coded by pillar.  Hovering a cell shows
the full caption preview.
"""

from __future__ import annotations

import html
from datetime import date
from pathlib import Path

from smm.ready_posts import ReadyPost

PILLAR_COLORS: dict[str, str] = {
    "Cyber Security & Ethical Hacking": "#00ff41",
    "Blue Team / Defensive Security": "#00bfff",
    "Red Team / Offensive Security": "#ff4444",
    "Machine Learning & AI": "#a855f7",
    "AliExpress - Гаджеты": "#ff6600",
}

PLATFORM_ICONS: dict[str, str] = {
    "instagram": "IG",
    "tiktok": "TT",
    "youtube": "YT",
}

WEEKDAYS_RU = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье",
]


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def generate_calendar_html(posts: list[ReadyPost]) -> str:
    days = sorted({p.day for p in posts})
    time_slots = sorted({p.time_slot for p in posts})

    grid: dict[tuple[str, date], list[ReadyPost]] = {}
    for p in posts:
        grid.setdefault((p.time_slot, p.day), []).append(p)

    header_cells = ""
    for d in days:
        wd = WEEKDAYS_RU[d.weekday()]
        header_cells += f"<th>{wd}<br><small>{d.isoformat()}</small></th>\n"

    rows_html = ""
    for ts in time_slots:
        cells = f"<td class='time-cell'>{_esc(ts)}</td>\n"
        for d in days:
            cell_posts = grid.get((ts, d), [])
            inner = ""
            for p in cell_posts:
                color = PILLAR_COLORS.get(p.pillar, "#888")
                icon = PLATFORM_ICONS.get(p.platform, p.platform[:2].upper())
                preview = _esc(p.caption[:120])
                topic = _esc(p.topic[:50])
                inner += (
                    f"<div class='post-chip' style='border-left:3px solid {color}'"
                    f" title='{preview}'>"
                    f"<span class='platform-badge'>{icon}</span> "
                    f"<span class='topic-text'>{topic}</span>"
                    f"</div>\n"
                )
            cells += f"<td class='day-cell'>{inner}</td>\n"
        rows_html += f"<tr>{cells}</tr>\n"

    stats_by_pillar = ""
    pillar_counts: dict[str, int] = {}
    for p in posts:
        pillar_counts[p.pillar] = pillar_counts.get(p.pillar, 0) + 1
    for name, count in sorted(pillar_counts.items()):
        color = PILLAR_COLORS.get(name, "#888")
        stats_by_pillar += (
            f"<span class='legend-item'>"
            f"<span class='legend-dot' style='background:{color}'></span>"
            f"{_esc(name)}: {count}"
            f"</span>\n"
        )

    platform_counts: dict[str, int] = {}
    for p in posts:
        platform_counts[p.platform] = platform_counts.get(p.platform, 0) + 1
    stats_by_platform = " | ".join(
        f"{PLATFORM_ICONS.get(pl, pl)}: {c}"
        for pl, c in sorted(platform_counts.items())
    )

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Контент-календарь</title>
<style>
:root {{
  --bg: #0d1117;
  --card-bg: #161b22;
  --text: #e6edf3;
  --text-muted: #8b949e;
  --border: #30363d;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg);
  color: var(--text);
  padding: 16px;
}}
h1 {{ font-size: 1.4rem; margin-bottom: 8px; }}
.stats {{ color: var(--text-muted); font-size: 0.85rem; margin-bottom: 16px; }}
.legend {{
  display: flex; flex-wrap: wrap; gap: 12px;
  margin-bottom: 16px; font-size: 0.8rem;
}}
.legend-item {{ display: flex; align-items: center; gap: 4px; }}
.legend-dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
.calendar-wrap {{ overflow-x: auto; }}
table {{
  border-collapse: collapse; width: 100%; min-width: 700px;
  font-size: 0.8rem;
}}
th {{
  background: var(--card-bg); padding: 8px; border: 1px solid var(--border);
  text-align: center; font-weight: 600;
}}
td {{ border: 1px solid var(--border); padding: 4px; vertical-align: top; }}
.time-cell {{
  background: var(--card-bg); font-weight: 600; text-align: center;
  width: 60px; white-space: nowrap;
}}
.day-cell {{ min-width: 120px; }}
.post-chip {{
  background: var(--card-bg); border-radius: 4px; padding: 4px 6px;
  margin-bottom: 3px; cursor: default; font-size: 0.75rem;
}}
.platform-badge {{
  font-weight: 700; font-size: 0.65rem;
  padding: 1px 4px; border-radius: 3px;
  background: rgba(255,255,255,0.1);
}}
.topic-text {{ color: var(--text-muted); }}
</style>
</head>
<body>
<h1>Контент-календарь — {len(posts)} постов</h1>
<div class="stats">{_esc(stats_by_platform)}</div>
<div class="legend">{stats_by_pillar}</div>
<div class="calendar-wrap">
<table>
<thead><tr><th>Время</th>{header_cells}</tr></thead>
<tbody>{rows_html}</tbody>
</table>
</div>
</body>
</html>"""


def generate_calendar_file(
    posts: list[ReadyPost],
    output: Path | None = None,
) -> Path:
    if output is None:
        output = Path("smm_data") / "calendar.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(generate_calendar_html(posts), encoding="utf-8")
    return output
