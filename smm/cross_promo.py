"""Cross-platform promotion — drive traffic between platforms.

Generates posts specifically designed to funnel followers from one
platform to another and ultimately to course landing pages and
referral links. Each promo type has platform-specific variants.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from smm.content_pillars import PILLARS

PROMO_ROUTES = (
    ("instagram", "youtube"),
    ("tiktok", "youtube"),
    ("instagram", "tiktok"),
    ("tiktok", "instagram"),
    ("youtube", "instagram"),
    ("instagram", "course"),
    ("tiktok", "course"),
    ("youtube", "course"),
    ("instagram", "referral"),
    ("tiktok", "referral"),
)


@dataclass(frozen=True, slots=True)
class CrossPromoPost:
    pillar: str
    source_platform: str
    target: str
    hook: str
    caption: str
    cta: str


ROUTE_TEMPLATES: dict[tuple[str, str], dict[str, str]] = {
    ("instagram", "youtube"): {
        "hook": "Полный разбор — на YouTube",
        "caption_tpl": "Это было краткое превью! Полный {duration}-минутный "
        "разбор с практикой уже на YouTube.\n\n"
        "Тема: {topic}\n\n"
        "Переходи по ссылке в био — канал ShadowRigs",
        "cta": "Ссылка на видео в био!",
    },
    ("tiktok", "youtube"): {
        "hook": "Это только верхушка — полная версия на YouTube",
        "caption_tpl": "В 60 секунд всё не уместить!\n\n"
        "На YouTube — полный гайд по {topic}: "
        "{duration} минут практики и разборов.\n\n"
        "Ник в профиле — подписывайся там тоже",
        "cta": "YouTube — ссылка в профиле",
    },
    ("instagram", "tiktok"): {
        "hook": "Больше таких видео — в TikTok",
        "caption_tpl": "Залетай в мой TikTok — там ещё больше "
        "коротких разборов по {topic}.\n\n"
        "Новые видео каждый день!",
        "cta": "TikTok: @shadowrigs",
    },
    ("tiktok", "instagram"): {
        "hook": "Карусель с деталями — в Instagram",
        "caption_tpl": "Хочешь сохранить? В Instagram выложил карусель "
        "с пошаговым разбором {topic}.\n\n"
        "Там же — PDF и чеклисты в сторис",
        "cta": "Instagram: @shadowrigs",
    },
    ("youtube", "instagram"): {
        "hook": "Ежедневные советы — в Instagram",
        "caption_tpl": "Пока я монтирую следующее видео — заходи в Instagram.\n\n"
        "Каждый день: карусели, Reels и сторис по {topic}.\n\n"
        "Подписывайся: @shadowrigs",
        "cta": "Instagram в описании под видео",
    },
    ("instagram", "course"): {
        "hook": "Хочешь разобраться глубже? Есть курс",
        "caption_tpl": "Этот пост — 1% того, что ты узнаешь на курсе.\n\n"
        "Полная программа по {topic}:\n"
        "- Теория + практика\n"
        "- Менторство\n"
        "- Сертификат\n\n"
        "Ссылка на курс — в био",
        "cta": "Записаться на курс — ссылка в био",
    },
    ("tiktok", "course"): {
        "hook": "Из TikTok — в профессию",
        "caption_tpl": "Нравятся мои видео по {topic}? "
        "Представь, что ты умеешь это сам.\n\n"
        "Курс: от нуля до {level} за 3 месяца.\n\n"
        "Ссылка в профиле",
        "cta": "Курс — ссылка в профиле",
    },
    ("youtube", "course"): {
        "hook": "Хочешь такие же навыки? Записывайся на курс",
        "caption_tpl": "Всё, что я показал в этом видео — "
        "часть программы моего курса по {topic}.\n\n"
        "Студенты получают:\n"
        "- Доступ к закрытым материалам\n"
        "- Практические задания\n"
        "- Поддержку ментора\n\n"
        "Ссылка под видео в описании",
        "cta": "Ссылка на курс в описании",
    },
    ("instagram", "referral"): {
        "hook": "Гаджет из поста — по ссылке со скидкой",
        "caption_tpl": "Спрашивали, где купить {gadget}?\n\n"
        "Ссылка в био — AliExpress со скидкой для подписчиков.\n\n"
        "Проверено лично, работает отлично!",
        "cta": "Купить — ссылка в био",
    },
    ("tiktok", "referral"): {
        "hook": "Ссылка на этот гаджет — в профиле",
        "caption_tpl": "Этот {gadget} стоит копейки, а работает как оригинал.\n\n"
        "AliExpress, проверенный продавец.\n\n"
        "Ссылка в профиле",
        "cta": "Ссылка в профиле — покупай!",
    },
}

PILLAR_VARS: dict[str, dict[str, str]] = {
    "Cyber Security & Ethical Hacking": {
        "topic": "кибербезопасности и пентесту",
        "duration": "20",
        "level": "пентестера",
        "gadget": "WiFi-адаптер для Kali",
    },
    "Blue Team / Defensive Security": {
        "topic": "защите и мониторингу сетей",
        "duration": "25",
        "level": "SOC-аналитика",
        "gadget": "сетевой TAP-адаптер",
    },
    "Red Team / Offensive Security": {
        "topic": "пентесту и наступательной безопасности",
        "duration": "30",
        "level": "пентестера",
        "gadget": "USB Rubber Ducky аналог",
    },
    "Machine Learning & AI": {
        "topic": "машинному обучению и AI",
        "duration": "20",
        "level": "ML-инженера",
        "gadget": "Jetson Nano для ML",
    },
    "AliExpress - Гаджеты": {
        "topic": "хакерским гаджетам",
        "duration": "15",
        "level": "эксперта по гаджетам",
        "gadget": "ESP32 для пентеста",
    },
}


def generate_cross_promos(
    pillar_name: str | None = None,
    seed: int | None = None,
) -> list[CrossPromoPost]:
    rng = random.Random(seed)
    pillars = [p for p in PILLARS if p.name == pillar_name] if pillar_name else PILLARS

    promos: list[CrossPromoPost] = []
    for pillar in pillars:
        variables = PILLAR_VARS.get(pillar.name, {})
        for source, target in PROMO_ROUTES:
            template = ROUTE_TEMPLATES.get((source, target))
            if template is None:
                continue

            caption = template["caption_tpl"].format(
                topic=variables.get("topic", "теме"),
                duration=variables.get("duration", "15"),
                level=variables.get("level", "профи"),
                gadget=variables.get("gadget", "гаджет"),
            )

            promos.append(
                CrossPromoPost(
                    pillar=pillar.name,
                    source_platform=source,
                    target=target,
                    hook=template["hook"],
                    caption=caption,
                    cta=template["cta"],
                )
            )

    rng.shuffle(promos)
    return promos


def export_promos_json(promos: list[CrossPromoPost], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "pillar": p.pillar,
            "source": p.source_platform,
            "target": p.target,
            "hook": p.hook,
            "caption": p.caption,
            "cta": p.cta,
        }
        for p in promos
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_promos_txt(promos: list[CrossPromoPost], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "КРОСС-ПРОМО — ПЕРЕГОНКА ТРАФИКА",
        "=" * 60,
    ]

    for p in promos:
        target_label = {
            "course": "Курс",
            "referral": "Реферал",
        }.get(p.target, p.target.upper())

        lines.append(f"\n{'─' * 40}")
        lines.append(f"[{p.source_platform.upper()} → {target_label}] {p.pillar}")
        lines.append(f"Хук: {p.hook}")
        lines.append(f"Текст:\n{p.caption}")
        lines.append(f"CTA: {p.cta}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def promos_summary(promos: list[CrossPromoPost]) -> str:
    by_route: dict[str, int] = {}
    for p in promos:
        route = f"{p.source_platform} -> {p.target}"
        by_route[route] = by_route.get(route, 0) + 1

    lines: list[str] = [
        f"Кросс-промо: {len(promos)} постов",
    ]
    lines.append("\nМаршруты:")
    lines.extend(f"  {route}: {count}" for route, count in sorted(by_route.items()))
    return "\n".join(lines)
