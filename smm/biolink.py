"""Bio link page generator — a Linktree-style page for social media profiles.

Every caption says "ссылка в био" — this page IS that link.
Aggregates all course URLs, referral links, and social profiles
into a single mobile-first page that can be hosted anywhere.
"""

from __future__ import annotations

import html as html_mod
from dataclasses import dataclass, field
from pathlib import Path


def _esc(text: str) -> str:
    return html_mod.escape(text, quote=True)


@dataclass(frozen=True, slots=True)
class BioLink:
    label: str
    url: str
    emoji: str = ""
    category: str = "general"


@dataclass(slots=True)
class BioLinkPage:
    brand: str = "ShadowRigs"
    tagline: str = "Cybersecurity | AI | Гаджеты"
    avatar_emoji: str = ""
    links: list[BioLink] = field(default_factory=list)
    telegram: str = "https://t.me/shadowrigs"
    theme_accent: str = "#6366f1"

    def add(
        self, label: str, url: str, emoji: str = "", category: str = "general"
    ) -> None:
        self.links.append(BioLink(label=label, url=url, emoji=emoji, category=category))


DEFAULT_LINKS: list[BioLink] = [
    BioLink(
        label="Cyber Security & Ethical Hacking",
        url="https://shadowrigs.com/courses/cybersecurity",
        emoji="",
        category="course",
    ),
    BioLink(
        label="Blue Team / Defensive Security",
        url="https://shadowrigs.com/courses/blue-team",
        emoji="",
        category="course",
    ),
    BioLink(
        label="Red Team / Offensive Security",
        url="https://shadowrigs.com/courses/red-team",
        emoji="",
        category="course",
    ),
    BioLink(
        label="Machine Learning & AI",
        url="https://shadowrigs.com/courses/machine-learning",
        emoji="",
        category="course",
    ),
    BioLink(
        label="Гаджеты для хакера — AliExpress",
        url="https://aliexpress.com/store/shadowrigs",
        emoji="",
        category="referral",
    ),
    BioLink(
        label="Сетевое оборудование — AliExpress",
        url="https://aliexpress.com/store/shadowrigs-network",
        emoji="",
        category="referral",
    ),
]


def generate_biolink_html(page: BioLinkPage | None = None) -> str:
    if page is None:
        page = BioLinkPage(links=list(DEFAULT_LINKS))

    links_html = ""
    current_cat = ""
    cat_labels = {"course": "Курсы", "referral": "Гаджеты", "general": ""}

    for link in page.links:
        if link.category != current_cat:
            current_cat = link.category
            cat_label = cat_labels.get(current_cat, current_cat)
            if cat_label:
                links_html += f'    <div class="cat">{_esc(cat_label)}</div>\n'

        emoji_span = (
            f'<span class="emoji">{_esc(link.emoji)}</span> ' if link.emoji else ""
        )
        links_html += (
            f'    <a class="link-btn" href="{_esc(link.url)}" '
            f'target="_blank" rel="noopener">'
            f"{emoji_span}{_esc(link.label)}</a>\n"
        )

    accent = _esc(page.theme_accent)

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(page.brand)} — Links</title>
<style>
:root {{
  --bg: #0c0e14;
  --surface: #161a24;
  --text: #e5e7ef;
  --text-muted: #8890a4;
  --accent: {accent};
  --accent-glow: {accent}33;
  --border: #252a38;
}}
@media (prefers-color-scheme: light) {{
  :root:not([data-theme="dark"]) {{
    --bg: #f5f5f7;
    --surface: #ffffff;
    --text: #1a1d23;
    --text-muted: #6b7280;
    --accent-glow: {accent}1a;
    --border: #e5e7eb;
  }}
}}
:root[data-theme="light"] {{
  --bg: #f5f5f7;
  --surface: #ffffff;
  --text: #1a1d23;
  --text-muted: #6b7280;
  --accent-glow: {accent}1a;
  --border: #e5e7eb;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100dvh;
  display: flex;
  justify-content: center;
  padding: 40px 16px 60px;
}}
.container {{
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}}
.avatar {{
  width: 88px;
  height: 88px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--accent-glow));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.4rem;
  border: 3px solid var(--accent);
  margin-bottom: 4px;
}}
.brand {{
  font-size: 1.3rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}}
.tagline {{
  font-size: 0.82rem;
  color: var(--text-muted);
  margin-bottom: 16px;
  text-align: center;
}}
.cat {{
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  margin-top: 12px;
  margin-bottom: 2px;
  align-self: flex-start;
  padding-left: 4px;
}}
.link-btn {{
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 14px 20px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  color: var(--text);
  text-decoration: none;
  font-size: 0.88rem;
  font-weight: 500;
  transition: all 0.2s ease;
  gap: 8px;
}}
.link-btn:hover {{
  border-color: var(--accent);
  box-shadow: 0 0 20px var(--accent-glow);
  transform: translateY(-1px);
}}
.link-btn:active {{
  transform: scale(0.98);
}}
.emoji {{ font-size: 1.1rem; }}
.tg-btn {{
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
  padding: 14px 20px;
  width: 100%;
  background: var(--accent);
  color: #fff;
  text-decoration: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.9rem;
}}
.footer {{
  margin-top: 32px;
  font-size: 0.68rem;
  color: var(--text-muted);
  text-align: center;
}}
</style>
</head>
<body>
  <div class="container">
    <div class="avatar">{_esc(page.avatar_emoji) if page.avatar_emoji else "SR"}</div>
    <div class="brand">{_esc(page.brand)}</div>
    <div class="tagline">{_esc(page.tagline)}</div>

{links_html}
    <a class="tg-btn" href="{_esc(page.telegram)}" target="_blank" rel="noopener">
      Написать в Telegram
    </a>

    <div class="footer">{_esc(page.brand)} &copy; 2024</div>
  </div>
</body>
</html>"""


def generate_biolink_file(
    page: BioLinkPage | None = None,
    output: Path | None = None,
) -> Path:
    html_content = generate_biolink_html(page)
    if output is None:
        output = Path("smm_data") / "biolink.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html_content, encoding="utf-8")
    return output
