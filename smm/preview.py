"""Visual preview renderer for SMM posts.

Generates a self-contained HTML file with styled post cards
for each platform. Cards can be screenshotted and posted manually,
or used as visual references for a social media manager.
"""

from __future__ import annotations

import html
from datetime import date
from pathlib import Path

from smm.platforms import Platform
from smm.post_generator import PostSlot, generate_week_plan

PLATFORM_COLORS = {
    Platform.INSTAGRAM: ("#E1306C", "#833AB4", "#F77737"),
    Platform.TIKTOK: ("#00F2EA", "#FF0050", "#000000"),
    Platform.YOUTUBE: ("#FF0000", "#282828", "#FFFFFF"),
}

PLATFORM_ICONS = {
    Platform.INSTAGRAM: "IG",
    Platform.TIKTOK: "TT",
    Platform.YOUTUBE: "YT",
}


def _escape(text: str) -> str:
    return html.escape(text, quote=True)


def _render_card(slot: PostSlot) -> str:
    colors = PLATFORM_COLORS[slot.platform]
    icon = PLATFORM_ICONS[slot.platform]
    accent = colors[0]
    bg = colors[1] if slot.platform == Platform.TIKTOK else "#1a1a2e"

    hashtags_html = " ".join(
        f'<span class="tag">{_escape(h)}</span>' for h in slot.hashtags[:8]
    )

    ref_line = ""
    if slot.referral_url:
        ref_line = (
            f'<div class="ref-link">'
            f'<span class="ref-icon">&#128279;</span> '
            f"{_escape(slot.referral_url[:60])}...</div>"
        )

    return f"""<div class="card" style="--accent: {accent}; --card-bg: {bg}">
  <div class="card-header">
    <span class="platform-badge" style="background: {accent}">{icon}</span>
    <span class="platform-name">{_escape(slot.platform.value.title())}</span>
    <span class="card-date">{slot.day.isoformat()} {_escape(slot.time_slot)}</span>
    <span class="card-format">{_escape(slot.format)}</span>
  </div>
  <div class="card-pillar">{_escape(slot.pillar.name)}</div>
  <div class="card-topic">{_escape(slot.topic)}</div>
  <div class="card-hook">{_escape(slot.hook)}</div>
  <div class="card-body">{_escape(slot.body)}</div>
  <div class="card-cta">{_escape(slot.cta)}</div>
  <div class="card-hashtags">{hashtags_html}</div>
  {ref_line}
</div>"""


def render_preview(
    slots: list[PostSlot],
    title: str = "SMM Content Preview",
) -> str:
    cards_by_day: dict[date, list[str]] = {}
    for slot in slots:
        cards_by_day.setdefault(slot.day, []).append(_render_card(slot))

    day_sections = []
    for day in sorted(cards_by_day):
        cards_html = "\n".join(cards_by_day[day])
        weekday_names = [
            "Пн",
            "Вт",
            "Ср",
            "Чт",
            "Пт",
            "Сб",
            "Вс",
        ]
        wd = weekday_names[day.weekday()]
        day_sections.append(
            f'<div class="day-section">'
            f'<h2 class="day-title">{day.isoformat()} ({wd})</h2>'
            f'<div class="day-cards">{cards_html}</div>'
            f"</div>"
        )

    sections_html = "\n".join(day_sections)

    stats_ig = sum(1 for s in slots if s.platform == Platform.INSTAGRAM)
    stats_tt = sum(1 for s in slots if s.platform == Platform.TIKTOK)
    stats_yt = sum(1 for s in slots if s.platform == Platform.YOUTUBE)
    pillars = {}
    for s in slots:
        pillars[s.pillar.name] = pillars.get(s.pillar.name, 0) + 1
    pillar_stats = " | ".join(f"{n}: {c}" for n, c in sorted(pillars.items()))

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_escape(title)}</title>
<style>
:root {{
  --bg: #0d1117;
  --surface: #161b22;
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
  max-width: 1400px;
  margin: 0 auto;
}}
.header {{
  text-align: center;
  padding: 24px 16px;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border);
}}
.header h1 {{ font-size: 1.8rem; margin-bottom: 8px; }}
.stats {{
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 12px;
}}
.stat {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 0.85rem;
}}
.stat strong {{ color: #58a6ff; }}
.day-section {{ margin-bottom: 32px; }}
.day-title {{
  font-size: 1.2rem;
  color: #58a6ff;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}}
.day-cards {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}}
.card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  border-top: 3px solid var(--accent);
  transition: transform 0.15s;
}}
.card:hover {{ transform: translateY(-2px); }}
.card-header {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}}
.platform-badge {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.7rem;
  color: #fff;
}}
.platform-name {{ font-weight: 600; font-size: 0.9rem; }}
.card-date {{ color: var(--text-muted); font-size: 0.8rem; margin-left: auto; }}
.card-format {{
  background: rgba(88, 166, 255, 0.15);
  color: #58a6ff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
}}
.card-pillar {{
  color: var(--text-muted);
  font-size: 0.8rem;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}}
.card-topic {{
  font-size: 1.05rem;
  font-weight: 600;
  margin-bottom: 8px;
  line-height: 1.3;
}}
.card-hook {{
  background: rgba(255, 255, 255, 0.05);
  border-left: 3px solid var(--accent);
  padding: 8px 12px;
  margin-bottom: 10px;
  font-style: italic;
  font-size: 0.9rem;
  border-radius: 0 6px 6px 0;
}}
.card-body {{
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 10px;
  line-height: 1.5;
}}
.card-cta {{
  background: linear-gradient(135deg, var(--accent), rgba(88, 166, 255, 0.3));
  color: #fff;
  padding: 8px 12px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.85rem;
  text-align: center;
  margin-bottom: 10px;
}}
.card-hashtags {{
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
}}
.tag {{
  background: rgba(88, 166, 255, 0.1);
  color: #58a6ff;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
}}
.ref-link {{
  font-size: 0.75rem;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}}
.ref-icon {{ font-size: 0.85rem; }}
@media (max-width: 600px) {{
  .day-cards {{ grid-template-columns: 1fr; }}
  body {{ padding: 8px; }}
}}
</style>
</head>
<body>
<div class="header">
  <h1>{_escape(title)}</h1>
  <p style="color: var(--text-muted)">
    {len(slots)} постов на {len(cards_by_day)} дней
  </p>
  <div class="stats">
    <div class="stat"><strong>{stats_ig}</strong> Instagram</div>
    <div class="stat"><strong>{stats_tt}</strong> TikTok</div>
    <div class="stat"><strong>{stats_yt}</strong> YouTube</div>
  </div>
  <p style="color: var(--text-muted); font-size: 0.8rem; margin-top: 8px">
    {_escape(pillar_stats)}
  </p>
</div>
{sections_html}
</body>
</html>"""


def render_preview_file(
    days: int = 7,
    seed: int | None = None,
    output: Path | None = None,
) -> Path:
    plan = generate_week_plan(days=days, seed=seed)
    html_content = render_preview(plan)
    if output is None:
        output = Path("smm_data") / "preview.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html_content, encoding="utf-8")
    return output
