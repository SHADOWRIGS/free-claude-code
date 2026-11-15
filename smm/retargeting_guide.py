"""Retargeting pixel and audience setup guide generator.

Produces structured guides for setting up retargeting across
Meta Pixel, TikTok Pixel, and YouTube remarketing lists.
Includes audience segments, event triggers, and lookalike specs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

PLATFORMS = ("meta", "tiktok", "youtube")

EVENTS: dict[str, list[dict[str, str]]] = {
    "meta": [
        {"name": "PageView", "trigger": "Посещение лендинга курса", "priority": "high"},
        {
            "name": "ViewContent",
            "trigger": "Просмотр страницы курса > 30 сек",
            "priority": "high",
        },
        {
            "name": "AddToCart",
            "trigger": "Клик на кнопку «Записаться»",
            "priority": "high",
        },
        {
            "name": "InitiateCheckout",
            "trigger": "Начало оформления оплаты",
            "priority": "high",
        },
        {
            "name": "Purchase",
            "trigger": "Успешная оплата курса",
            "priority": "critical",
        },
        {"name": "Lead", "trigger": "Скачивание лид-магнита", "priority": "medium"},
        {
            "name": "CompleteRegistration",
            "trigger": "Регистрация на вебинар/демо",
            "priority": "medium",
        },
    ],
    "tiktok": [
        {
            "name": "PageView",
            "trigger": "Визит на лендинг с TikTok",
            "priority": "high",
        },
        {"name": "ClickButton", "trigger": "Клик на CTA в био", "priority": "high"},
        {
            "name": "SubmitForm",
            "trigger": "Заполнение формы захвата",
            "priority": "high",
        },
        {"name": "CompletePayment", "trigger": "Оплата курса", "priority": "critical"},
        {
            "name": "Download",
            "trigger": "Скачивание бесплатного материала",
            "priority": "medium",
        },
    ],
    "youtube": [
        {"name": "video_view", "trigger": "Просмотр видео > 50%", "priority": "high"},
        {"name": "channel_visit", "trigger": "Посещение канала", "priority": "medium"},
        {"name": "subscribe", "trigger": "Подписка на канал", "priority": "high"},
        {
            "name": "link_click",
            "trigger": "Клик на ссылку в описании",
            "priority": "high",
        },
        {
            "name": "card_click",
            "trigger": "Клик на подсказку/карточку",
            "priority": "medium",
        },
    ],
}

AUDIENCES: list[dict[str, str | int]] = [
    {
        "name": "Тёплые — посетители лендинга",
        "source": "Все посетители лендингов курсов за 30 дней",
        "window_days": 30,
        "size_estimate": "5K-20K",
        "action": "Показать отзывы, кейсы, ограниченное предложение",
    },
    {
        "name": "Горячие — начали оформление",
        "source": "InitiateCheckout / SubmitForm без Purchase за 14 дней",
        "window_days": 14,
        "size_estimate": "500-2K",
        "action": "Ретаргетинг скидкой, ограниченное время, бонусы",
    },
    {
        "name": "Ледяные — касание > 60 дней назад",
        "source": "Все посетители 60-180 дней без конверсии",
        "window_days": 180,
        "size_estimate": "10K-50K",
        "action": "Новый контент, обновления курса, бесплатный вебинар",
    },
    {
        "name": "Покупатели — апсейл",
        "source": "Purchase за последние 90 дней",
        "window_days": 90,
        "size_estimate": "1K-5K",
        "action": "Рекомендовать смежный курс, продвинутый уровень",
    },
    {
        "name": "Лид-магнит — нёрчеринг",
        "source": "Скачали лид-магнит без покупки за 30 дней",
        "window_days": 30,
        "size_estimate": "2K-10K",
        "action": "Email-серия + ретаргет с социальным доказательством",
    },
    {
        "name": "Lookalike — топ-покупатели",
        "source": "1% Lookalike от Purchase аудитории",
        "window_days": 0,
        "size_estimate": "200K-1M",
        "action": "Холодный трафик: обзорный контент, проблема → решение",
    },
]

SETUP_STEPS: dict[str, list[str]] = {
    "meta": [
        "1. Создать Meta Pixel в Events Manager",
        "2. Установить базовый код на все страницы лендингов",
        "3. Настроить стандартные события (PageView, ViewContent, Purchase)",
        "4. Подключить Conversions API для серверных событий",
        "5. Создать Custom Audiences (посетители, покупатели, lead)",
        "6. Создать Lookalike Audiences (1%, 3%, 5%)",
        "7. Настроить Dynamic Product Ads для курсов",
        "8. Проверить события в Events Manager → Test Events",
    ],
    "tiktok": [
        "1. Создать TikTok Pixel в TikTok Ads Manager",
        "2. Установить код через Tag Manager или напрямую",
        "3. Настроить события: PageView, ClickButton, CompletePayment",
        "4. Создать Custom Audiences по событиям",
        "5. Создать Lookalike Audiences",
        "6. Подключить TikTok Events API (серверная отправка)",
        "7. Проверить в разделе Assets → Events",
    ],
    "youtube": [
        "1. Связать канал YouTube с Google Ads",
        "2. Создать аудитории ремаркетинга в Google Ads",
        "3. Сегменты: зрители видео, посетители канала, подписчики",
        "4. Настроить YouTube Video Action Campaigns",
        "5. Создать Similar Audiences на основе конверсий",
        "6. Проверить в Audience Manager → Audience lists",
    ],
}


@dataclass(frozen=True, slots=True)
class PixelEvent:
    platform: str
    name: str
    trigger: str
    priority: str


@dataclass(frozen=True, slots=True)
class AudienceSegment:
    name: str
    source: str
    window_days: int
    size_estimate: str
    action: str


@dataclass(frozen=True, slots=True)
class RetargetingGuide:
    platform: str
    events: tuple[PixelEvent, ...]
    setup_steps: tuple[str, ...]


def generate_pixel_events(platform: str | None = None) -> list[PixelEvent]:
    platforms = [platform] if platform else list(PLATFORMS)
    return [
        PixelEvent(
            platform=plat,
            name=ev["name"],
            trigger=ev["trigger"],
            priority=ev["priority"],
        )
        for plat in platforms
        for ev in EVENTS.get(plat, [])
    ]


def generate_audiences() -> list[AudienceSegment]:
    return [
        AudienceSegment(
            name=a["name"],
            source=a["source"],
            window_days=a["window_days"],  # type: ignore[arg-type]
            size_estimate=a["size_estimate"],  # type: ignore[arg-type]
            action=a["action"],  # type: ignore[arg-type]
        )
        for a in AUDIENCES
    ]


def generate_retargeting_guides() -> list[RetargetingGuide]:
    return [
        RetargetingGuide(
            platform=plat,
            events=tuple(generate_pixel_events(platform=plat)),
            setup_steps=tuple(SETUP_STEPS.get(plat, [])),
        )
        for plat in PLATFORMS
    ]


def export_retargeting_json(
    guides: list[RetargetingGuide],
    audiences: list[AudienceSegment],
    path: Path,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "platforms": [
            {
                "platform": g.platform,
                "events": [
                    {"name": e.name, "trigger": e.trigger, "priority": e.priority}
                    for e in g.events
                ],
                "setup_steps": list(g.setup_steps),
            }
            for g in guides
        ],
        "audiences": [
            {
                "name": a.name,
                "source": a.source,
                "window_days": a.window_days,
                "size_estimate": a.size_estimate,
                "action": a.action,
            }
            for a in audiences
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_retargeting_txt(
    guides: list[RetargetingGuide],
    audiences: list[AudienceSegment],
    path: Path,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "ГАЙД ПО РЕТАРГЕТИНГУ",
        "=" * 60,
    ]

    for g in guides:
        lines.append(f"\n{'━' * 50}")
        lines.append(f"📡 {g.platform.upper()}")
        lines.append("━" * 50)

        lines.append("\n  События (пиксель):")
        lines.extend(
            f"    [{e.priority.upper()}] {e.name} — {e.trigger}" for e in g.events
        )

        lines.append("\n  Шаги настройки:")
        lines.extend(f"    {s}" for s in g.setup_steps)

    lines.append(f"\n{'━' * 50}")
    lines.append("👥 СЕГМЕНТЫ АУДИТОРИИ")
    lines.append("━" * 50)
    for a in audiences:
        lines.append(f"\n  {a.name}")
        lines.append(f"    Источник: {a.source}")
        lines.append(f"    Окно: {a.window_days} дней")
        lines.append(f"    Размер: ~{a.size_estimate}")
        lines.append(f"    Действие: {a.action}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def retargeting_summary(
    guides: list[RetargetingGuide], audiences: list[AudienceSegment]
) -> str:
    total_events = sum(len(g.events) for g in guides)
    return (
        f"Ретаргетинг: {len(guides)} платформы, "
        f"{total_events} событий, {len(audiences)} сегментов аудитории"
    )
