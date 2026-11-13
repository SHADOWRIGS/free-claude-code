"""Post generator from content plan."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from smm.content_pillars import PILLARS, ContentPillar
from smm.hashtag_engine import HASHTAG_POOLS, generate_hashtags
from smm.platforms import PLATFORM_SPECS, Platform


@dataclass(frozen=True, slots=True)
class PostSlot:
    day: date
    time_slot: str
    platform: Platform
    pillar: ContentPillar
    topic: str
    format: str
    hook: str
    body: str
    cta: str
    hashtags: list[str]
    referral_url: str


HOOKS_TEMPLATES = [
    "Это должен знать каждый, кто работает в IT...",
    "99% людей не знают об этом...",
    "Хакеры используют это каждый день. А ты?",
    "Я потратил 100 часов, чтобы ты не тратил ни одного.",
    "Стоп. Если ты не знаешь {keyword} — смотри до конца.",
    "Этот инструмент изменил мою карьеру навсегда.",
    "POV: ты впервые открываешь {keyword}",
    "3 ошибки новичка в {keyword}, которые стоят карьеры",
    "Тебя могут взломать за 5 минут. Вот как.",
    "Как зарабатывать на {keyword}? Рассказываю.",
    "Секрет, который не расскажут на обычных курсах.",
    "Ты точно не знал, что {keyword} умеет это.",
    "Бесплатно vs Платно: что реально работает в {keyword}",
    "Топ-инструмент для {keyword} в 2024 году",
    "Этот гаджет за $10 заменяет оборудование за $500",
]

CTA_COURSE = [
    "Хочешь освоить это на практике? Ссылка на курс в шапке профиля",
    "Подробнее в нашем курсе — ссылка в био",
    "Полный гайд в курсе. Переходи по ссылке в описании",
    "Начни учиться уже сегодня — ссылка в профиле",
    "Хватит смотреть, пора действовать. Курс в шапке",
]

CTA_REFERRAL = [
    "Ссылка на гаджет в описании — проверено лично",
    "Заказывал через нашу ссылку — все пришло. Ссылка в био",
    "Берите по ссылке в описании, пока есть скидка",
    "Проверенный магазин — ссылка в шапке профиля",
]

CTA_ENGAGE = [
    "Сохрани, чтобы не потерять! Ставь лайк",
    "Поделись с другом, которому это нужно",
    "Напиши в комменты, какой инструмент используешь ты",
    "Подписывайся, чтобы не пропустить следующий разбор",
    "Какую тему разобрать следующей? Пиши в комменты",
]

FORMATS_BY_PLATFORM: dict[Platform, list[str]] = {
    Platform.INSTAGRAM: ["reels", "carousel", "stories", "static_post"],
    Platform.TIKTOK: ["short_video", "short_video", "short_video", "duet"],
    Platform.YOUTUBE: ["shorts", "shorts", "full_video", "shorts"],
}


def _pick_hook(topic: str, pillar: ContentPillar) -> str:
    keyword = pillar.name.split("/")[0].strip().split("&")[0].strip()
    template = random.choice(HOOKS_TEMPLATES)
    return template.format(keyword=keyword) if "{keyword}" in template else template


def _pick_cta(pillar: ContentPillar) -> str:
    if pillar.product == "course":
        pool = CTA_COURSE + CTA_ENGAGE
    else:
        pool = CTA_REFERRAL + CTA_ENGAGE
    return random.choice(pool)


def _build_body(topic: str, pillar: ContentPillar, platform: Platform) -> str:
    body_lines = [
        f"{topic}",
        "",
        f"В этом посте разбираем {topic.lower()}.",
        "",
        "Что внутри:",
        "- Пошаговый разбор",
        "- Практические примеры",
        "- Инструменты и ресурсы",
        "",
    ]
    return "\n".join(body_lines)


def _pick_hashtags(pillar: ContentPillar, platform: Platform) -> list[str]:
    spec = PLATFORM_SPECS[platform]
    max_tags = spec.hashtag_range[1]

    if pillar.name in HASHTAG_POOLS:
        ht = generate_hashtags(pillar.name, count=max_tags)
        return ht.all_tags

    combined = pillar.hashtags_ru + pillar.hashtags_en
    random.shuffle(combined)
    return [f"#{h}" for h in combined[:max_tags]]


def _referral_url(pillar: ContentPillar, platform: Platform) -> str:
    base_urls = {
        "Курс Cyber Security & Ethical Hacking": "https://shadowrigs.com/courses/cybersecurity",
        "Курс Blue Team / Defensive Security": "https://shadowrigs.com/courses/blue-team",
        "Курс Red Team / Offensive Security": "https://shadowrigs.com/courses/red-team",
        "Курс Machine Learning & AI": "https://shadowrigs.com/courses/machine-learning",
        "AliExpress - Гаджеты для хакеров": "https://aliexpress.com/store/shadowrigs",
        "AliExpress - Сетевое оборудование": "https://aliexpress.com/store/shadowrigs-network",
    }
    base = base_urls.get(pillar.referral_label, "")
    if base:
        return f"{base}?utm_source={platform.value}&utm_medium=social&utm_campaign={pillar.name.lower().replace(' ', '-').replace('/', '-')}"
    return ""


def generate_week_plan(
    start: date | None = None,
    days: int = 7,
    seed: int | None = None,
) -> list[PostSlot]:
    if seed is not None:
        random.seed(seed)

    start = start or date.today()
    slots: list[PostSlot] = []
    all_topics: list[tuple[str, ContentPillar]] = [
        (topic, pillar) for pillar in PILLARS for topic in pillar.topics
    ]

    random.shuffle(all_topics)
    topic_idx = 0

    for day_offset in range(days):
        current_date = start + timedelta(days=day_offset)

        for platform in Platform:
            spec = PLATFORM_SPECS[platform]
            formats = FORMATS_BY_PLATFORM[platform]

            for slot_idx, time_str in enumerate(spec.posting_times):
                topic_text, pillar = all_topics[topic_idx % len(all_topics)]
                topic_idx += 1

                fmt = formats[slot_idx % len(formats)]
                hook = _pick_hook(topic_text, pillar)
                body = _build_body(topic_text, pillar, platform)
                cta = _pick_cta(pillar)
                hashtags = _pick_hashtags(pillar, platform)
                ref_url = _referral_url(pillar, platform)

                slots.append(
                    PostSlot(
                        day=current_date,
                        time_slot=time_str,
                        platform=platform,
                        pillar=pillar,
                        topic=topic_text,
                        format=fmt,
                        hook=hook,
                        body=body,
                        cta=cta,
                        hashtags=hashtags,
                        referral_url=ref_url,
                    )
                )

    return slots


def export_plan_json(slots: list[PostSlot], path: Path) -> None:
    data = [
        {
            "day": s.day.isoformat(),
            "time": s.time_slot,
            "platform": s.platform.value,
            "pillar": s.pillar.name,
            "topic": s.topic,
            "format": s.format,
            "hook": s.hook,
            "body": s.body,
            "cta": s.cta,
            "hashtags": s.hashtags,
            "referral_url": s.referral_url,
        }
        for s in slots
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def export_plan_markdown(slots: list[PostSlot], path: Path) -> None:
    lines: list[str] = ["# Контент-план SMM\n"]
    current_day = None

    for s in sorted(slots, key=lambda x: (x.day, x.time_slot, x.platform.value)):
        if s.day != current_day:
            current_day = s.day
            weekdays = [
                "Понедельник",
                "Вторник",
                "Среда",
                "Четверг",
                "Пятница",
                "Суббота",
                "Воскресенье",
            ]
            day_name = weekdays[current_day.weekday()]
            lines.append(f"\n## {day_name}, {current_day.isoformat()}\n")

        lines.append(f"### {s.time_slot} | {s.platform.value.upper()} | {s.format}")
        lines.append(f"**Столп:** {s.pillar.name}")
        lines.append(f"**Тема:** {s.topic}")
        lines.append(f"**Хук:** {s.hook}")
        lines.append(f"**CTA:** {s.cta}")
        lines.append(f"**Хештеги:** {' '.join(s.hashtags)}")
        if s.referral_url:
            lines.append(f"**Ссылка:** {s.referral_url}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    plan = generate_week_plan(seed=42)
    out_dir = Path("smm_data")
    out_dir.mkdir(exist_ok=True)
    export_plan_json(plan, out_dir / "week_plan.json")
    export_plan_markdown(plan, out_dir / "week_plan.md")
    print(f"Создан план на {len(plan)} постов.")
    for s in plan[:6]:
        print(
            f"  {s.day} {s.time_slot} | {s.platform.value:<10} | "
            f"{s.pillar.name:<30} | {s.topic[:50]}"
        )
    print(f"  ... и еще {len(plan) - 6} постов")
