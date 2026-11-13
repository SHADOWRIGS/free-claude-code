"""Commercial proposal generator for SMM automation service.

Produces personalized HTML proposals that can be sent to potential clients.
Each proposal includes:
- Client-specific greeting and needs analysis
- Service tier recommendation based on client profile
- Sample content preview for their niche
- Pricing breakdown with ROI estimates
- Call to action
"""

from __future__ import annotations

import html as html_mod
from dataclasses import dataclass
from pathlib import Path

from smm.service_spec import DELIVERABLES, TIERS, ServiceTier


def _esc(text: str) -> str:
    return html_mod.escape(text, quote=True)


@dataclass(frozen=True, slots=True)
class ClientProfile:
    name: str
    business: str
    niche: str
    current_platforms: list[str]
    posts_per_week_goal: int
    main_goal: str

    @property
    def recommended_tier(self) -> ServiceTier:
        for tier in reversed(TIERS):
            if self.posts_per_week_goal >= tier.posts_per_week:
                return tier
        return TIERS[0]


NICHE_SAMPLES: dict[str, list[str]] = {
    "cybersecurity": [
        "5 инструментов для пентеста, которые должен знать каждый",
        "Как хакеры взламывают Wi-Fi за 5 минут (и как защититься)",
        "Топ-10 уязвимостей OWASP: разбор с примерами",
    ],
    "ai": [
        "Нейросети за 10 минут: как это работает",
        "ChatGPT vs Claude vs Gemini: большое сравнение",
        "RAG: как сделать AI, который знает ваши документы",
    ],
    "gadgets": [
        "Топ-5 гаджетов для хакера с AliExpress до $20",
        "Flipper Zero vs дешевые аналоги: стоит ли?",
        "Лучшие WiFi-адаптеры для Kali Linux",
    ],
    "default": [
        "Контент-план на неделю за 5 минут с AI",
        "Как увеличить охваты в Instagram на 300%",
        "Формула идеального хука для Reels и TikTok",
    ],
}


def _get_niche_samples(niche: str) -> list[str]:
    niche_lower = niche.lower()
    for key, samples in NICHE_SAMPLES.items():
        if key in niche_lower:
            return samples
    return NICHE_SAMPLES["default"]


def generate_proposal(client: ClientProfile) -> str:
    tier = client.recommended_tier
    samples = _get_niche_samples(client.niche)
    samples_html = "\n".join(
        f'      <div class="sample-topic">{_esc(s)}</div>' for s in samples
    )

    other_tiers_html = ""
    for t in TIERS:
        if t.name == tier.name:
            continue
        platforms_str = ", ".join(t.platforms)
        other_tiers_html += f"""
    <div class="alt-tier">
      <strong>{_esc(t.name)}</strong> &mdash; ${t.price_monthly_usd}/мес
      ({t.posts_per_week} постов/нед, {_esc(platforms_str)})
    </div>"""

    deliverables_html = "\n".join(
        f"      <li>{_esc(d.name)} ({_esc(d.frequency.lower())})</li>"
        for d in DELIVERABLES
    )

    platforms_str = ", ".join(tier.platforms)
    monthly_posts = tier.posts_per_week * 4
    cost_per_post = round(tier.price_monthly_usd / monthly_posts, 2)

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Предложение для {_esc(client.name)}</title>
<style>
:root {{
  --bg: #ffffff;
  --surface: #f8f9fb;
  --text: #1a1d23;
  --text-muted: #6b7280;
  --accent: #6366f1;
  --accent-soft: rgba(99, 102, 241, 0.06);
  --border: #e5e7eb;
  --green: #059669;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #0c0e14;
    --surface: #161a24;
    --text: #e5e7ef;
    --text-muted: #8890a4;
    --accent: #818cf8;
    --accent-soft: rgba(129, 140, 248, 0.08);
    --border: #252a38;
    --green: #34d399;
    color-scheme: dark;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #0c0e14;
  --surface: #161a24;
  --text: #e5e7ef;
  --text-muted: #8890a4;
  --accent: #818cf8;
  --accent-soft: rgba(129, 140, 248, 0.08);
  --border: #252a38;
  --green: #34d399;
  color-scheme: dark;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.65;
  max-width: 720px;
  margin: 0 auto;
  padding: 40px 24px;
}}
h1 {{ font-size: 1.6rem; font-weight: 700; margin-bottom: 8px; }}
h2 {{ font-size: 1.15rem; font-weight: 600; margin: 32px 0 12px; color: var(--accent); }}
p {{ margin-bottom: 12px; }}
.subtitle {{ color: var(--text-muted); font-size: 0.9rem; margin-bottom: 32px; }}
.highlight-box {{
  background: var(--accent-soft);
  border: 1px solid var(--accent);
  border-radius: 10px;
  padding: 20px 24px;
  margin: 20px 0;
}}
.highlight-box .tier-name {{ font-size: 1.3rem; font-weight: 700; color: var(--accent); }}
.highlight-box .price {{ font-size: 1.8rem; font-weight: 800; color: var(--accent); margin: 8px 0; }}
.highlight-box .price span {{ font-size: 0.9rem; font-weight: 400; color: var(--text-muted); }}
.highlight-box .details {{ font-size: 0.85rem; color: var(--text-muted); }}
.sample-topic {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  margin: 6px 0;
  font-size: 0.88rem;
}}
.sample-topic::before {{ content: "\\25B6 "; color: var(--accent); }}
.roi-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin: 16px 0;
}}
.roi-item {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}}
.roi-item .val {{ font-size: 1.4rem; font-weight: 700; color: var(--green); }}
.roi-item .lbl {{ font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; margin-top: 4px; }}
ul {{ padding-left: 20px; margin: 8px 0 16px; }}
li {{ font-size: 0.88rem; margin: 4px 0; color: var(--text-muted); }}
.alt-tier {{
  font-size: 0.85rem;
  color: var(--text-muted);
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
}}
.cta {{
  display: block;
  text-align: center;
  padding: 14px;
  background: var(--accent);
  color: #fff;
  text-decoration: none;
  border-radius: 10px;
  font-weight: 600;
  margin: 24px 0;
  font-size: 0.95rem;
}}
.footer {{ text-align: center; color: var(--text-muted); font-size: 0.75rem; margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--border); }}
</style>
</head>
<body>

<h1>Коммерческое предложение</h1>
<p class="subtitle">Подготовлено для {_esc(client.name)} &mdash; {_esc(client.business)}</p>

<h2>Ваша задача</h2>
<p>
  Вы хотите {_esc(client.main_goal.lower())} в нише <strong>{_esc(client.niche)}</strong>.
  Для этого нужен стабильный поток контента на {_esc(", ".join(client.current_platforms))}.
</p>
<p>
  Мы предлагаем полностью автоматизированную систему генерации контента,
  которая создаёт готовые к публикации посты каждую неделю.
</p>

<h2>Рекомендуемый тариф</h2>
<div class="highlight-box">
  <div class="tier-name">{_esc(tier.name)}</div>
  <div class="price">${tier.price_monthly_usd}<span>/мес</span></div>
  <div class="details">
    {tier.posts_per_week} постов/нед &bull; {_esc(platforms_str)} &bull;
    AI-генерация &bull; готовые пакеты
  </div>
</div>

<h2>Примеры контента для вашей ниши</h2>
<div class="samples">
{samples_html}
</div>

<h2>ROI-расчёт</h2>
<div class="roi-grid">
  <div class="roi-item">
    <div class="val">{monthly_posts}</div>
    <div class="lbl">постов/мес</div>
  </div>
  <div class="roi-item">
    <div class="val">${cost_per_post}</div>
    <div class="lbl">за пост</div>
  </div>
  <div class="roi-item">
    <div class="val">~40ч</div>
    <div class="lbl">экономия/мес</div>
  </div>
</div>

<h2>Что входит</h2>
<ul>
{deliverables_html}
</ul>

<h2>Другие тарифы</h2>
{other_tiers_html}

<a class="cta" href="https://t.me/shadowrigs">Обсудить запуск</a>

<div class="footer">
  ShadowRigs SMM &mdash; AI-автоматизация контента для бизнеса
</div>

</body>
</html>"""


def generate_proposal_file(
    client: ClientProfile,
    output: Path | None = None,
) -> Path:
    html_content = generate_proposal(client)
    if output is None:
        safe_name = client.name.lower().replace(" ", "_")[:30]
        output = Path("smm_data") / "proposals" / f"proposal_{safe_name}.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html_content, encoding="utf-8")
    return output
