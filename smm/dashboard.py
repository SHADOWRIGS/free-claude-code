"""SMM Dashboard — unified HTML overview of the entire system.

Generates a single-page interactive dashboard that shows:
- Weekly content calendar with posts per platform
- Strategy overview with pillar priorities
- Competitor positioning map
- Content mix and format distribution
- Growth targets and KPIs
- Quick-access links to all CLI commands

Designed as both a management tool and a sales demo.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from smm.competitor_analysis import analyze_all_niches
from smm.content_strategy import (
    CONTENT_MIX,
    GROWTH_TARGETS,
    generate_pillar_strategies,
)
from smm.ready_posts import generate_ready_posts


def _pillar_color(pillar_name: str) -> str:
    colors = {
        "Cyber Security & Ethical Hacking": "#00d4ff",
        "Blue Team / Defensive Security": "#4a90d9",
        "Red Team / Offensive Security": "#ff4757",
        "Machine Learning & AI": "#7c3aed",
        "AliExpress - Гаджеты": "#ffa502",
    }
    return colors.get(pillar_name, "#888888")


def _platform_icon(platform: str) -> str:
    icons = {
        "instagram": "IG",
        "tiktok": "TT",
        "youtube": "YT",
    }
    return icons.get(platform, platform[:2].upper())


def generate_dashboard(
    days: int = 7,
    seed: int | None = None,
    output: Path | None = None,
) -> Path:
    if output is None:
        output = Path("smm_data") / "dashboard.html"
    output.parent.mkdir(parents=True, exist_ok=True)

    posts = generate_ready_posts(days=days, seed=seed)
    strategies = generate_pillar_strategies()
    analyses = analyze_all_niches()
    by_day: dict[str, list[dict[str, str]]] = {}
    for p in posts:
        day_key = p.day.isoformat()
        by_day.setdefault(day_key, []).append(
            {
                "platform": p.platform,
                "topic": p.topic,
                "time": p.time_slot,
                "format": p.format,
                "pillar": p.pillar,
            }
        )

    calendar_json = json.dumps(by_day, ensure_ascii=False)

    strategy_rows = ""
    for s in strategies:
        color = _pillar_color(s.pillar)
        strategy_rows += f"""
        <tr>
          <td><span class="dot" style="background:{color}"></span> {s.pillar}</td>
          <td>#{s.priority}</td>
          <td>{s.content_share:.0%}</td>
          <td class="small">{s.growth_lever}</td>
        </tr>"""

    competitor_cards = ""
    for a in analyses:
        color = _pillar_color(a.pillar)
        comps_html = "".join(
            f'<div class="comp-item">{c.name} <span class="comp-plat">{c.platform}</span></div>'
            for c in a.competitors[:3]
        )
        gaps_html = "".join(f"<li>{g}</li>" for g in a.gaps[:3])
        competitor_cards += f"""
        <div class="card">
          <h4 style="border-left:3px solid {color}; padding-left:8px">{a.pillar}</h4>
          <div class="comp-list">{comps_html}</div>
          <p class="label">Гэпы:</p>
          <ul class="gaps">{gaps_html}</ul>
        </div>"""

    mix_items = ""
    for content_type, share in CONTENT_MIX.items():
        label = {
            "educational": "Образовательный",
            "entertaining": "Развлекательный",
            "promotional": "Промо",
            "engagement": "Вовлечение",
            "social_proof": "Соц. доказательство",
        }.get(content_type, content_type)
        pct = int(share * 100)
        mix_items += f"""
          <div class="mix-bar">
            <span class="mix-label">{label}</span>
            <div class="bar-track"><div class="bar-fill" style="width:{pct}%"></div></div>
            <span class="mix-pct">{pct}%</span>
          </div>"""

    growth_rows = ""
    for period, targets in GROWTH_TARGETS.items():
        label = {
            "month_1": "1 месяц",
            "month_3": "3 месяца",
            "month_6": "6 месяцев",
        }.get(period, period)
        growth_rows += f"""
        <tr>
          <td>{label}</td>
          <td>+{targets["followers_growth_pct"]}%</td>
          <td>{targets["engagement_rate_target"]}%</td>
          <td>{targets["video_views_target_pct"]}%</td>
        </tr>"""

    total_posts = len(posts)
    platforms_count = len({p.platform for p in posts})
    pillars_count = len({p.pillar for p in posts})

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SMM Dashboard</title>
<style>
:root {{
  --bg: #0f0f1a;
  --surface: #1a1a2e;
  --border: #2a2a40;
  --text: #e0e0e0;
  --text-dim: #8888aa;
  --accent: #00d4ff;
  --success: #00c853;
  --warn: #ffa502;
  --danger: #ff4757;
}}
@media (prefers-color-scheme: light) {{
  :root:not([data-theme="dark"]) {{
    --bg: #f5f5f8;
    --surface: #ffffff;
    --border: #e0e0e8;
    --text: #1a1a2e;
    --text-dim: #666680;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #0f0f1a;
  --surface: #1a1a2e;
  --border: #2a2a40;
  --text: #e0e0e0;
  --text-dim: #8888aa;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  padding: 16px;
  max-width: 1200px;
  margin: 0 auto;
}}
h1 {{ font-size:1.8rem; margin-bottom:4px; }}
h2 {{ font-size:1.2rem; margin:24px 0 12px; color:var(--accent); }}
h3 {{ font-size:1rem; margin:16px 0 8px; }}
h4 {{ font-size:0.9rem; margin-bottom:8px; }}
.subtitle {{ color:var(--text-dim); font-size:0.85rem; margin-bottom:20px; }}
.stats {{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
  gap:12px;
  margin-bottom:20px;
}}
.stat {{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:8px;
  padding:16px;
  text-align:center;
}}
.stat .num {{ font-size:2rem; font-weight:700; color:var(--accent); }}
.stat .label {{ font-size:0.75rem; color:var(--text-dim); margin-top:4px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:16px; }}
.card {{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:8px;
  padding:16px;
}}
table {{
  width:100%;
  border-collapse:collapse;
  font-size:0.85rem;
}}
th, td {{
  padding:8px 12px;
  text-align:left;
  border-bottom:1px solid var(--border);
}}
th {{ color:var(--text-dim); font-weight:500; font-size:0.75rem; text-transform:uppercase; }}
.dot {{
  display:inline-block;
  width:10px;
  height:10px;
  border-radius:50%;
  margin-right:6px;
  vertical-align:middle;
}}
.small {{ font-size:0.75rem; color:var(--text-dim); max-width:200px; }}
.comp-item {{ padding:4px 0; font-size:0.85rem; }}
.comp-plat {{ font-size:0.7rem; color:var(--text-dim); }}
.gaps {{ font-size:0.8rem; padding-left:16px; color:var(--text-dim); }}
.gaps li {{ margin:4px 0; }}
.label {{ font-size:0.75rem; color:var(--text-dim); margin-top:8px; }}
.mix-bar {{ display:flex; align-items:center; gap:8px; margin:6px 0; }}
.mix-label {{ font-size:0.8rem; min-width:140px; }}
.bar-track {{ flex:1; height:8px; background:var(--border); border-radius:4px; overflow:hidden; }}
.bar-fill {{ height:100%; background:var(--accent); border-radius:4px; }}
.mix-pct {{ font-size:0.8rem; color:var(--text-dim); min-width:30px; }}
.cal-grid {{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
  gap:8px;
  margin-top:8px;
}}
.cal-day {{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:6px;
  padding:10px;
  font-size:0.8rem;
}}
.cal-day .date {{ font-weight:600; margin-bottom:6px; color:var(--accent); }}
.cal-post {{
  display:flex;
  align-items:center;
  gap:4px;
  padding:2px 0;
  font-size:0.75rem;
}}
.plat-badge {{
  display:inline-block;
  padding:1px 5px;
  border-radius:3px;
  font-size:0.65rem;
  font-weight:600;
  color:#fff;
}}
.plat-ig {{ background:#e1306c; }}
.plat-tt {{ background:#000; }}
.plat-yt {{ background:#ff0000; }}
.cmd-grid {{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
  gap:8px;
}}
.cmd {{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:6px;
  padding:10px;
  font-size:0.8rem;
}}
.cmd code {{ color:var(--accent); font-size:0.75rem; }}
</style>
</head>
<body>
<h1>SMM Dashboard</h1>
<p class="subtitle">ShadowRigs — автоматизация контент-маркетинга | {date.today().isoformat()}</p>

<div class="stats">
  <div class="stat"><div class="num">{total_posts}</div><div class="label">Постов / неделю</div></div>
  <div class="stat"><div class="num">{platforms_count}</div><div class="label">Платформы</div></div>
  <div class="stat"><div class="num">{pillars_count}</div><div class="label">Направлений</div></div>
  <div class="stat"><div class="num">{len(strategies)}</div><div class="label">Стратегий</div></div>
  <div class="stat"><div class="num">{sum(len(a.competitors) for a in analyses)}</div><div class="label">Конкурентов</div></div>
  <div class="stat"><div class="num">34</div><div class="label">CLI команд</div></div>
</div>

<h2>Стратегия по направлениям</h2>
<div class="card">
<table>
  <tr><th>Направление</th><th>Приоритет</th><th>Доля</th><th>Рычаг роста</th></tr>
  {strategy_rows}
</table>
</div>

<h2>Контент-микс</h2>
<div class="card">
  {mix_items}
</div>

<h2>Цели роста</h2>
<div class="card">
<table>
  <tr><th>Период</th><th>Подписчики</th><th>Engagement</th><th>Видео-просмотры</th></tr>
  {growth_rows}
</table>
</div>

<h2>Конкуренты и гэпы</h2>
<div class="grid">
  {competitor_cards}
</div>

<h2>Контент-календарь</h2>
<div class="cal-grid" id="calendar"></div>

<h2>CLI-команды</h2>
<div class="cmd-grid">
  <div class="cmd"><code>uv run -m smm.cli generate</code><br>Генерация плана</div>
  <div class="cmd"><code>uv run -m smm.cli batch</code><br>Готовые посты</div>
  <div class="cmd"><code>uv run -m smm.cli week-pack</code><br>Полный пакет</div>
  <div class="cmd"><code>uv run -m smm.cli series</code><br>Контент-серии</div>
  <div class="cmd"><code>uv run -m smm.cli carousel</code><br>Карусели</div>
  <div class="cmd"><code>uv run -m smm.cli stories</code><br>Сторис-пакеты</div>
  <div class="cmd"><code>uv run -m smm.cli strategy</code><br>Стратегия</div>
  <div class="cmd"><code>uv run -m smm.cli competitors</code><br>Анализ конкурентов</div>
  <div class="cmd"><code>uv run -m smm.cli optimize</code><br>Оптимизация расписания</div>
  <div class="cmd"><code>uv run -m smm.cli dashboard</code><br>Этот дашборд</div>
  <div class="cmd"><code>uv run -m smm.cli scheduler-export</code><br>Экспорт в Buffer/Later</div>
  <div class="cmd"><code>uv run -m smm.cli ab-test</code><br>A/B тесты</div>
</div>

<script>
const cal = {calendar_json};
const container = document.getElementById('calendar');
const platClass = {{"instagram":"plat-ig","tiktok":"plat-tt","youtube":"plat-yt"}};
const platIcon = {{"instagram":"IG","tiktok":"TT","youtube":"YT"}};
Object.keys(cal).sort().forEach(day => {{
  const div = document.createElement('div');
  div.className = 'cal-day';
  const posts = cal[day];
  let html = '<div class="date">' + day + ' (' + posts.length + ')</div>';
  posts.slice(0, 9).forEach(p => {{
    const cls = platClass[p.platform] || '';
    const icon = platIcon[p.platform] || p.platform;
    html += '<div class="cal-post"><span class="plat-badge ' + cls + '">' + icon + '</span> ' + p.time + ' ' + p.topic.slice(0, 30) + '</div>';
  }});
  if (posts.length > 9) html += '<div class="cal-post" style="color:var(--text-dim)">+' + (posts.length - 9) + ' ещё</div>';
  div.innerHTML = html;
  container.appendChild(div);
}});
</script>
</body>
</html>"""

    output.write_text(html, encoding="utf-8")
    return output


def dashboard_summary(path: Path) -> str:
    return f"SMM-дашборд сгенерирован: {path}"
