"""Content calendar generator — builds a detailed posting plan for N days.

Generates structured calendar configs:
- Daily slot templates per platform
- Content type rotation rules
- Pillar distribution weights
- Holiday/event overlays
- Batch generation settings
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DAILY_SLOTS: list[dict[str, str]] = [
    {
        "platform": "Instagram",
        "slot_1": "09:00 — Reels (вовлечение)",
        "slot_2": "13:00 — Карусель (обучение)",
        "slot_3": "18:00 — Пост/сторис (конверсия)",
        "timezone": "Europe/Moscow",
    },
    {
        "platform": "TikTok",
        "slot_1": "08:00 — Trending hook (охват)",
        "slot_2": "12:00 — Обучающий ролик (ценность)",
        "slot_3": "20:00 — Развлекательный (вирусный)",
        "timezone": "Europe/Moscow",
    },
    {
        "platform": "YouTube",
        "slot_1": "10:00 — Short (промо)",
        "slot_2": "14:00 — Видео 10-20мин (глубокий контент)",
        "slot_3": "17:00 — Short (хук на следующее видео)",
        "timezone": "Europe/Moscow",
    },
]

ROTATION_RULES: list[dict[str, str | int]] = [
    {
        "day_of_week": "Понедельник",
        "day_num": 1,
        "theme": "Мотивация + план недели",
        "primary_format": "Reels/TikTok",
        "pillar_focus": "Cyber Security & Ethical Hacking",
    },
    {
        "day_of_week": "Вторник",
        "day_num": 2,
        "theme": "Обучающий контент (туториал)",
        "primary_format": "Карусель/Видео",
        "pillar_focus": "Blue Team / Defensive Security",
    },
    {
        "day_of_week": "Среда",
        "day_num": 3,
        "theme": "Кейс / история успеха",
        "primary_format": "Пост + сторис",
        "pillar_focus": "Red Team / Offensive Security",
    },
    {
        "day_of_week": "Четверг",
        "day_num": 4,
        "theme": "Инструменты и гаджеты",
        "primary_format": "Reels/TikTok + ссылка",
        "pillar_focus": "AliExpress Gadgets",
    },
    {
        "day_of_week": "Пятница",
        "day_num": 5,
        "theme": "AI/ML контент + тренды",
        "primary_format": "Карусель/Видео",
        "pillar_focus": "Machine Learning & AI",
    },
    {
        "day_of_week": "Суббота",
        "day_num": 6,
        "theme": "Вовлечение (квиз, опрос, челлендж)",
        "primary_format": "Сторис/Reels",
        "pillar_focus": "Микс (любой столп)",
    },
    {
        "day_of_week": "Воскресенье",
        "day_num": 7,
        "theme": "Итоги недели + промо",
        "primary_format": "Пост + карусель",
        "pillar_focus": "Промо курсов / услуги",
    },
]

PILLAR_WEIGHTS: list[dict[str, str | float]] = [
    {
        "pillar": "Cyber Security & Ethical Hacking",
        "weight_pct": 25.0,
        "posts_per_week": 4,
        "content_mix": "2 обучающих, 1 кейс, 1 промо",
    },
    {
        "pillar": "Blue Team / Defensive Security",
        "weight_pct": 20.0,
        "posts_per_week": 3,
        "content_mix": "1 обучающий, 1 инструмент, 1 кейс",
    },
    {
        "pillar": "Red Team / Offensive Security",
        "weight_pct": 20.0,
        "posts_per_week": 3,
        "content_mix": "1 обучающий, 1 CTF, 1 промо",
    },
    {
        "pillar": "Machine Learning & AI",
        "weight_pct": 20.0,
        "posts_per_week": 3,
        "content_mix": "1 обучающий, 1 проект, 1 тренд",
    },
    {
        "pillar": "AliExpress Gadgets",
        "weight_pct": 15.0,
        "posts_per_week": 2,
        "content_mix": "1 обзор, 1 подборка",
    },
]

HOLIDAY_OVERLAYS: list[dict[str, str]] = [
    {
        "event": "Новый год",
        "dates": "25 дек - 8 янв",
        "overlay": "Праздничные офферы, итоги года, промо бандлов",
    },
    {
        "event": "День Пи (14 марта)",
        "dates": "14 марта",
        "overlay": "ML/AI контент, математика в кибербезопасности",
    },
    {
        "event": "May the 4th (Star Wars Day)",
        "dates": "4 мая",
        "overlay": "Гик-контент, тематические мемы, промо гаджетов",
    },
    {
        "event": "GDPR Day (25 мая)",
        "dates": "25 мая",
        "overlay": "Privacy и compliance контент, Blue Team фокус",
    },
    {
        "event": "11.11 (AliExpress)",
        "dates": "9-12 ноября",
        "overlay": "Гаджеты со скидками, подборки, промо ссылки",
    },
    {
        "event": "Black Friday + Cyber Monday",
        "dates": "последняя пт ноября + пн",
        "overlay": "Максимальные скидки на курсы и бандлы",
    },
]

BATCH_SETTINGS: dict[str, str | int] = {
    "default_days": 7,
    "max_days": 90,
    "posts_per_day_per_platform": 3,
    "total_platforms": 3,
    "total_daily_posts": 9,
    "total_weekly_posts": 63,
    "output_formats": "JSON, TXT, iCal, Notion",
    "auto_hashtags": "yes",
    "auto_utm": "yes",
    "include_visual_brief": "yes",
}


@dataclass(frozen=True, slots=True)
class DailySlot:
    platform: str
    slot_1: str
    slot_2: str
    slot_3: str
    timezone: str


@dataclass(frozen=True, slots=True)
class RotationRule:
    day_of_week: str
    day_num: int
    theme: str
    primary_format: str
    pillar_focus: str


@dataclass(frozen=True, slots=True)
class PillarWeight:
    pillar: str
    weight_pct: float
    posts_per_week: int
    content_mix: str


@dataclass(frozen=True, slots=True)
class HolidayOverlay:
    event: str
    dates: str
    overlay: str


@dataclass(frozen=True, slots=True)
class ContentCalendarGen:
    daily_slots: tuple[DailySlot, ...]
    rotation_rules: tuple[RotationRule, ...]
    pillar_weights: tuple[PillarWeight, ...]
    holiday_overlays: tuple[HolidayOverlay, ...]
    batch_settings: dict[str, str | int]


def generate_content_calendar_gen() -> ContentCalendarGen:
    return ContentCalendarGen(
        daily_slots=tuple(
            DailySlot(
                platform=ds["platform"],
                slot_1=ds["slot_1"],
                slot_2=ds["slot_2"],
                slot_3=ds["slot_3"],
                timezone=ds["timezone"],
            )
            for ds in DAILY_SLOTS
        ),
        rotation_rules=tuple(
            RotationRule(
                day_of_week=rr["day_of_week"],
                day_num=int(rr["day_num"]),
                theme=rr["theme"],
                primary_format=rr["primary_format"],
                pillar_focus=rr["pillar_focus"],
            )
            for rr in ROTATION_RULES
        ),
        pillar_weights=tuple(
            PillarWeight(
                pillar=pw["pillar"],
                weight_pct=float(pw["weight_pct"]),
                posts_per_week=int(pw["posts_per_week"]),
                content_mix=pw["content_mix"],
            )
            for pw in PILLAR_WEIGHTS
        ),
        holiday_overlays=tuple(
            HolidayOverlay(
                event=ho["event"],
                dates=ho["dates"],
                overlay=ho["overlay"],
            )
            for ho in HOLIDAY_OVERLAYS
        ),
        batch_settings=dict(BATCH_SETTINGS),
    )


def export_calendar_gen_json(cg: ContentCalendarGen, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "daily_slots": [
            {
                "platform": ds.platform,
                "slot_1": ds.slot_1,
                "slot_2": ds.slot_2,
                "slot_3": ds.slot_3,
                "timezone": ds.timezone,
            }
            for ds in cg.daily_slots
        ],
        "rotation_rules": [
            {
                "day_of_week": rr.day_of_week,
                "day_num": rr.day_num,
                "theme": rr.theme,
                "primary_format": rr.primary_format,
                "pillar_focus": rr.pillar_focus,
            }
            for rr in cg.rotation_rules
        ],
        "pillar_weights": [
            {
                "pillar": pw.pillar,
                "weight_pct": pw.weight_pct,
                "posts_per_week": pw.posts_per_week,
                "content_mix": pw.content_mix,
            }
            for pw in cg.pillar_weights
        ],
        "holiday_overlays": [
            {"event": ho.event, "dates": ho.dates, "overlay": ho.overlay}
            for ho in cg.holiday_overlays
        ],
        "batch_settings": cg.batch_settings,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_calendar_gen_txt(cg: ContentCalendarGen, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "ГЕНЕРАТОР КОНТЕНТ-КАЛЕНДАРЯ",
        "=" * 60,
        "\n📅 СЛОТЫ ПУБЛИКАЦИЙ (ПО ПЛАТФОРМАМ)",
        "━" * 50,
    ]
    for ds in cg.daily_slots:
        lines.append(f"\n  [{ds.platform}] ({ds.timezone})")
        lines.append(f"    1: {ds.slot_1}")
        lines.append(f"    2: {ds.slot_2}")
        lines.append(f"    3: {ds.slot_3}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🔄 РОТАЦИЯ ПО ДНЯМ НЕДЕЛИ")
    lines.append("━" * 50)
    for rr in cg.rotation_rules:
        lines.append(f"\n  [{rr.day_of_week}] {rr.theme}")
        lines.append(f"    Формат: {rr.primary_format}")
        lines.append(f"    Столп: {rr.pillar_focus}")

    lines.append(f"\n{'━' * 50}")
    lines.append("⚖ РАСПРЕДЕЛЕНИЕ СТОЛПОВ")
    lines.append("━" * 50)
    for pw in cg.pillar_weights:
        lines.append(
            f"  [{pw.pillar}] {pw.weight_pct:.0f}% | {pw.posts_per_week} постов/нед"
        )
        lines.append(f"    Микс: {pw.content_mix}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🎉 ПРАЗДНИЧНЫЕ НАКЛАДКИ")
    lines.append("━" * 50)
    lines.extend(
        f"  [{ho.event}] {ho.dates}: {ho.overlay}" for ho in cg.holiday_overlays
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("⚙ НАСТРОЙКИ БАТЧ-ГЕНЕРАЦИИ")
    lines.append("━" * 50)
    for key, val in cg.batch_settings.items():
        lines.append(f"  {key}: {val}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def calendar_gen_summary(cg: ContentCalendarGen) -> str:
    return (
        f"Контент-календарь: "
        f"{len(cg.daily_slots)} платформ x 3 слота, "
        f"{len(cg.rotation_rules)} дней ротации, "
        f"{len(cg.pillar_weights)} столпов, "
        f"{len(cg.holiday_overlays)} праздничных накладок"
    )
