"""Brand kit — visual identity and tone-of-voice guidelines.

Generates structured brand assets:
- Color palette (primary, secondary, accent, neutral)
- Typography stack (headings, body, code)
- Logo usage rules
- Tone-of-voice matrix per platform
- Visual style templates for posts
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

BRAND_COLORS: list[dict[str, str]] = [
    {
        "role": "primary",
        "hex": "#0D1117",
        "name": "Shadow Black",
        "usage": "Фон, основные элементы",
    },
    {
        "role": "secondary",
        "hex": "#21262D",
        "name": "Dark Steel",
        "usage": "Карточки, контейнеры",
    },
    {
        "role": "accent",
        "hex": "#58A6FF",
        "name": "Cyber Blue",
        "usage": "Ссылки, CTA, акценты",
    },
    {
        "role": "accent_alt",
        "hex": "#F78166",
        "name": "Alert Orange",
        "usage": "Предупреждения, промо-цены",
    },
    {
        "role": "success",
        "hex": "#3FB950",
        "name": "Terminal Green",
        "usage": "Успех, подтверждения, хакерский стиль",
    },
    {
        "role": "neutral",
        "hex": "#C9D1D9",
        "name": "Light Gray",
        "usage": "Текст на тёмном фоне",
    },
]

TYPOGRAPHY: list[dict[str, str]] = [
    {
        "role": "heading",
        "family": "JetBrains Mono",
        "weight": "700",
        "usage": "Заголовки, акцентный текст",
    },
    {
        "role": "body",
        "family": "Inter",
        "weight": "400",
        "usage": "Основной текст постов и лендингов",
    },
    {
        "role": "code",
        "family": "Fira Code",
        "weight": "400",
        "usage": "Код-сниппеты, терминальные скриншоты",
    },
]

LOGO_RULES: list[dict[str, str]] = [
    {
        "rule": "Минимальный размер",
        "detail": "32px высота для цифровых носителей",
    },
    {
        "rule": "Защитное поле",
        "detail": "Минимум 1× высота логотипа со всех сторон",
    },
    {
        "rule": "Фон",
        "detail": "Только на тёмном (#0D1117) или прозрачном фоне",
    },
    {
        "rule": "Запрещено",
        "detail": "Не растягивать, не менять цвета, не добавлять эффекты",
    },
    {
        "rule": "Форматы",
        "detail": "SVG (web), PNG (соцсети), favicon.ico (сайт)",
    },
]

TONE_OF_VOICE: list[dict[str, str]] = [
    {
        "platform": "Instagram",
        "tone": "Экспертный, но дружелюбный",
        "style": "Короткие абзацы, эмодзи умеренно, CTA в конце",
        "avoid": "Канцеляризмы, длинные предложения",
    },
    {
        "platform": "TikTok",
        "tone": "Дерзкий, энергичный",
        "style": "Хуки в первые 3 секунды, сленг уместен, провокации",
        "avoid": "Формальность, длинные пояснения",
    },
    {
        "platform": "YouTube",
        "tone": "Преподаватель-практик",
        "style": "Структурированные объяснения, примеры из практики",
        "avoid": "Поверхностность, кликбейт без содержания",
    },
    {
        "platform": "Telegram",
        "tone": "Свой человек в чате",
        "style": "Прямое обращение, быстрые ответы, мемы допустимы",
        "avoid": "Официоз, рекламные штампы",
    },
]

VISUAL_STYLES: list[dict[str, str]] = [
    {
        "name": "Terminal",
        "description": "Тёмный фон + зелёный текст (хакерская эстетика)",
        "best_for": "Cyber Security, Red Team",
        "bg": "#0D1117",
        "text": "#3FB950",
    },
    {
        "name": "Blueprint",
        "description": "Тёмно-синий фон + светлые схемы (защита/архитектура)",
        "best_for": "Blue Team",
        "bg": "#161B22",
        "text": "#58A6FF",
    },
    {
        "name": "Neural",
        "description": "Градиент фиолетовый → синий (AI/ML)",
        "best_for": "Machine Learning & AI",
        "bg": "#1A1032",
        "text": "#D2A8FF",
    },
    {
        "name": "Gadget",
        "description": "Оранжевые акценты на тёмном (товары/обзоры)",
        "best_for": "AliExpress — Гаджеты",
        "bg": "#0D1117",
        "text": "#F78166",
    },
]


@dataclass(frozen=True, slots=True)
class BrandColor:
    role: str
    hex: str
    name: str
    usage: str


@dataclass(frozen=True, slots=True)
class TypographyEntry:
    role: str
    family: str
    weight: str
    usage: str


@dataclass(frozen=True, slots=True)
class LogoRule:
    rule: str
    detail: str


@dataclass(frozen=True, slots=True)
class ToneOfVoice:
    platform: str
    tone: str
    style: str
    avoid: str


@dataclass(frozen=True, slots=True)
class VisualStyle:
    name: str
    description: str
    best_for: str
    bg: str
    text: str


@dataclass(frozen=True, slots=True)
class BrandKit:
    colors: tuple[BrandColor, ...]
    typography: tuple[TypographyEntry, ...]
    logo_rules: tuple[LogoRule, ...]
    tone_of_voice: tuple[ToneOfVoice, ...]
    visual_styles: tuple[VisualStyle, ...]
    brand_name: str
    tagline: str


def generate_brand_kit() -> BrandKit:
    return BrandKit(
        colors=tuple(
            BrandColor(role=c["role"], hex=c["hex"], name=c["name"], usage=c["usage"])
            for c in BRAND_COLORS
        ),
        typography=tuple(
            TypographyEntry(
                role=t["role"],
                family=t["family"],
                weight=t["weight"],
                usage=t["usage"],
            )
            for t in TYPOGRAPHY
        ),
        logo_rules=tuple(
            LogoRule(rule=r["rule"], detail=r["detail"]) for r in LOGO_RULES
        ),
        tone_of_voice=tuple(
            ToneOfVoice(
                platform=v["platform"],
                tone=v["tone"],
                style=v["style"],
                avoid=v["avoid"],
            )
            for v in TONE_OF_VOICE
        ),
        visual_styles=tuple(
            VisualStyle(
                name=s["name"],
                description=s["description"],
                best_for=s["best_for"],
                bg=s["bg"],
                text=s["text"],
            )
            for s in VISUAL_STYLES
        ),
        brand_name="ShadowRigs",
        tagline="Кибербезопасность. Обучение. Инструменты.",
    )


def export_brand_kit_json(kit: BrandKit, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "brand_name": kit.brand_name,
        "tagline": kit.tagline,
        "colors": [
            {"role": c.role, "hex": c.hex, "name": c.name, "usage": c.usage}
            for c in kit.colors
        ],
        "typography": [
            {
                "role": t.role,
                "family": t.family,
                "weight": t.weight,
                "usage": t.usage,
            }
            for t in kit.typography
        ],
        "logo_rules": [{"rule": r.rule, "detail": r.detail} for r in kit.logo_rules],
        "tone_of_voice": [
            {
                "platform": v.platform,
                "tone": v.tone,
                "style": v.style,
                "avoid": v.avoid,
            }
            for v in kit.tone_of_voice
        ],
        "visual_styles": [
            {
                "name": s.name,
                "description": s.description,
                "best_for": s.best_for,
                "bg": s.bg,
                "text": s.text,
            }
            for s in kit.visual_styles
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_brand_kit_txt(kit: BrandKit, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        f"БРЕНД-КИТ — {kit.brand_name}",
        f'"{kit.tagline}"',
        "=" * 60,
        "\n🎨 ЦВЕТОВАЯ ПАЛИТРА",
        "━" * 50,
    ]
    lines.extend(f"  {c.role}: {c.hex} ({c.name}) — {c.usage}" for c in kit.colors)

    lines.append(f"\n{'━' * 50}")
    lines.append("🔤 ТИПОГРАФИКА")
    lines.append("━" * 50)
    lines.extend(
        f"  {t.role}: {t.family} (w{t.weight}) — {t.usage}" for t in kit.typography
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("📐 ПРАВИЛА ЛОГОТИПА")
    lines.append("━" * 50)
    lines.extend(f"  • {r.rule}: {r.detail}" for r in kit.logo_rules)

    lines.append(f"\n{'━' * 50}")
    lines.append("🗣 ТОНАЛЬНОСТЬ ПО ПЛАТФОРМАМ")
    lines.append("━" * 50)
    for v in kit.tone_of_voice:
        lines.append(f"\n  [{v.platform}]")
        lines.append(f"    Тон: {v.tone}")
        lines.append(f"    Стиль: {v.style}")
        lines.append(f"    Избегать: {v.avoid}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🎭 ВИЗУАЛЬНЫЕ СТИЛИ")
    lines.append("━" * 50)
    for s in kit.visual_styles:
        lines.append(f"\n  [{s.name}] — {s.description}")
        lines.append(f"    Для: {s.best_for}")
        lines.append(f"    Фон: {s.bg} | Текст: {s.text}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def brand_kit_summary(kit: BrandKit) -> str:
    return (
        f"Бренд-кит «{kit.brand_name}»: "
        f"{len(kit.colors)} цветов, "
        f"{len(kit.typography)} шрифта, "
        f"{len(kit.logo_rules)} правил лого, "
        f"{len(kit.tone_of_voice)} тональностей, "
        f"{len(kit.visual_styles)} визуальных стилей"
    )
