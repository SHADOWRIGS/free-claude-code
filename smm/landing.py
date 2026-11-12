"""Landing page generator for the SMM automation service.

Produces a self-contained HTML sales page that can be:
- Sent to potential clients as a commercial proposal
- Hosted on any static server
- Used as a template for a real landing page

The page showcases service tiers, deliverables, and sample content.
"""

from __future__ import annotations

import html as html_mod
from pathlib import Path

from smm.service_spec import DELIVERABLES, TIERS


def _esc(text: str) -> str:
    return html_mod.escape(text, quote=True)


def generate_landing(
    brand: str = "ShadowRigs SMM",
    tagline: str = "Автоматизация контента для кибербезопасности и технологий",
    contact_cta: str = "Написать в Telegram",
    contact_url: str = "https://t.me/shadowrigs",
) -> str:
    tiers_html = ""
    for tier in TIERS:
        platforms_list = ", ".join(p.title() for p in tier.platforms)
        features = [
            f"{tier.posts_per_week} постов/нед",
            f"Платформы: {platforms_list}",
            "Контент-план" if tier.posts_per_week >= 21 else "",
            "AI-копирайтинг" if tier.posts_per_week >= 42 else "",
            "Видео-скрипты" if tier.posts_per_week >= 63 else "",
            "Аналитика" if tier.posts_per_week >= 63 else "",
        ]
        features = [f for f in features if f]
        features_li = "\n".join(f"        <li>{_esc(f)}</li>" for f in features)
        is_popular = tier.name == "Growth"
        badge = '<span class="popular-badge">Popular</span>' if is_popular else ""
        highlight = (
            ' class="tier-card highlight"' if is_popular else ' class="tier-card"'
        )
        tiers_html += f"""
    <div{highlight}>
      {badge}
      <h3>{_esc(tier.name)}</h3>
      <div class="price">${tier.price_monthly_usd}<span>/мес</span></div>
      <ul>
{features_li}
      </ul>
      <a href="{_esc(contact_url)}" class="tier-cta">{_esc(contact_cta)}</a>
    </div>"""

    deliverables_html = ""
    for d in DELIVERABLES:
        deliverables_html += f"""
    <div class="deliverable">
      <h4>{_esc(d.name)}</h4>
      <p>{_esc(d.description)}</p>
    </div>"""

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(brand)}</title>
<style>
:root {{
  --bg: #0b0e14;
  --surface: #141820;
  --text: #e4e8f0;
  --text-muted: #7a8194;
  --accent: #6366f1;
  --accent-glow: rgba(99, 102, 241, 0.2);
  --border: #1e2430;
  --success: #10b981;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}}
.container {{ max-width: 1100px; margin: 0 auto; padding: 0 20px; }}
.hero {{
  text-align: center;
  padding: 80px 20px 60px;
  background: linear-gradient(180deg, rgba(99, 102, 241, 0.08) 0%, transparent 100%);
}}
.hero h1 {{
  font-size: 2.4rem;
  font-weight: 800;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #6366f1, #818cf8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}}
.hero .tagline {{
  font-size: 1.15rem;
  color: var(--text-muted);
  max-width: 600px;
  margin: 0 auto 32px;
}}
.hero-stats {{
  display: flex;
  justify-content: center;
  gap: 32px;
  flex-wrap: wrap;
}}
.hero-stat {{
  text-align: center;
}}
.hero-stat .num {{
  font-size: 2rem;
  font-weight: 700;
  color: var(--accent);
  display: block;
}}
.hero-stat .label {{
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}}
section {{
  padding: 60px 0;
}}
section h2 {{
  font-size: 1.5rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 40px;
}}
.tiers {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  padding: 0 20px;
}}
.tier-card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 28px 24px;
  position: relative;
  transition: transform 0.15s;
}}
.tier-card:hover {{ transform: translateY(-3px); }}
.tier-card.highlight {{
  border-color: var(--accent);
  box-shadow: 0 0 30px var(--accent-glow);
}}
.popular-badge {{
  position: absolute;
  top: -10px;
  right: 20px;
  background: var(--accent);
  color: #fff;
  padding: 3px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}}
.tier-card h3 {{
  font-size: 1.2rem;
  margin-bottom: 8px;
}}
.price {{
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--accent);
  margin-bottom: 16px;
}}
.price span {{
  font-size: 0.9rem;
  font-weight: 400;
  color: var(--text-muted);
}}
.tier-card ul {{
  list-style: none;
  margin-bottom: 20px;
}}
.tier-card li {{
  padding: 6px 0;
  font-size: 0.9rem;
  color: var(--text-muted);
}}
.tier-card li::before {{
  content: "✓ ";
  color: var(--success);
  font-weight: 700;
}}
.tier-cta {{
  display: block;
  text-align: center;
  padding: 10px;
  background: var(--accent);
  color: #fff;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  transition: opacity 0.15s;
}}
.tier-cta:hover {{ opacity: 0.9; }}
.deliverables {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
  padding: 0 20px;
}}
.deliverable {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px;
}}
.deliverable h4 {{
  font-size: 0.95rem;
  margin-bottom: 6px;
  color: var(--accent);
}}
.deliverable p {{
  font-size: 0.85rem;
  color: var(--text-muted);
}}
.footer {{
  text-align: center;
  padding: 40px 20px;
  color: var(--text-muted);
  font-size: 0.8rem;
  border-top: 1px solid var(--border);
}}
@media (max-width: 600px) {{
  .hero h1 {{ font-size: 1.6rem; }}
  .hero {{ padding: 48px 16px 40px; }}
  .tiers {{ grid-template-columns: 1fr; }}
  .deliverables {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>
<div class="hero">
  <div class="container">
    <h1>{_esc(brand)}</h1>
    <p class="tagline">{_esc(tagline)}</p>
    <div class="hero-stats">
      <div class="hero-stat"><span class="num">63</span><span class="label">постов/нед</span></div>
      <div class="hero-stat"><span class="num">3</span><span class="label">платформы</span></div>
      <div class="hero-stat"><span class="num">5</span><span class="label">направлений</span></div>
      <div class="hero-stat"><span class="num">AI</span><span class="label">генерация</span></div>
    </div>
  </div>
</div>

<section>
  <div class="container">
    <h2>Тарифы</h2>
    <div class="tiers">{tiers_html}
    </div>
  </div>
</section>

<section>
  <div class="container">
    <h2>Что входит</h2>
    <div class="deliverables">{deliverables_html}
    </div>
  </div>
</section>

<div class="footer">
  <div class="container">
    <p>{_esc(brand)} &mdash; AI-автоматизация SMM для кибербезопасности и технологий</p>
  </div>
</div>
</body>
</html>"""


def generate_landing_file(
    output: Path | None = None,
    **kwargs: str,
) -> Path:
    html_content = generate_landing(**kwargs)
    if output is None:
        output = Path("smm_data") / "landing.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html_content, encoding="utf-8")
    return output
