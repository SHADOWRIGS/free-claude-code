"""Batch generator for ready-to-post content packages.

Produces complete, varied captions without needing the AI writer API.
Each post includes a full caption, hashtag block, visual brief,
and optional video script — ready to copy-paste or import into
Buffer / Later / Meta Business Suite.

Export formats:
- JSON (per-platform packages)
- Buffer CSV (direct import into Buffer scheduling)
- Markdown (for manual review)
"""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from smm.content_pillars import ContentPillar
from smm.post_generator import PostSlot, generate_week_plan

CAPTION_TEMPLATES_COURSE: list[str] = [
    (
        "{hook}\n\n"
        "{topic} — тема, которая меняет карьеры.\n\n"
        "Что ты узнаешь:\n"
        "1. Как это работает на практике\n"
        "2. Какие инструменты нужны\n"
        "3. С чего начать прямо сейчас\n\n"
        "{cta}\n\n"
        "{hashtags}"
    ),
    (
        "{hook}\n\n"
        "Разбираем {topic_lower} от А до Я.\n\n"
        "Сохраняй этот пост — пригодится!\n\n"
        "Ключевые моменты:\n"
        "- Теория за 2 минуты\n"
        "- Практика на реальных примерах\n"
        "- Чек-лист для самопроверки\n\n"
        "{cta}\n\n"
        "{hashtags}"
    ),
    (
        "{hook}\n\n"
        "Многие спрашивали про {topic_lower}.\n"
        "Рассказываю всё, что нужно знать.\n\n"
        "В двух словах:\n"
        "Это навык, который выделит тебя среди 90% специалистов.\n\n"
        "Подробности — в посте выше.\n"
        "{cta}\n\n"
        "{hashtags}"
    ),
    (
        "{hook}\n\n"
        "Если ты серьёзно настроен в {pillar_short} —\n"
        "эта тема обязательна к изучению.\n\n"
        "{topic}.\n\n"
        "Я собрал для тебя ключевые моменты,\n"
        "чтобы ты не тратил время на поиск.\n\n"
        "{cta}\n\n"
        "{hashtags}"
    ),
    (
        "{hook}\n\n"
        "Один из самых частых вопросов:\n"
        "«Как разобраться в {topic_lower}?»\n\n"
        "Ответ — в этом посте.\n"
        "Проверенные методы + реальные кейсы.\n\n"
        "{cta}\n\n"
        "{hashtags}"
    ),
]

CAPTION_TEMPLATES_REFERRAL: list[str] = [
    (
        "{hook}\n\n"
        "Нашёл кое-что интересное: {topic_lower}.\n\n"
        "Проверил лично — работает.\n"
        "Качество отличное, а цена приятно удивила.\n\n"
        "Ссылка на гаджет — в шапке профиля.\n\n"
        "{hashtags}"
    ),
    (
        "{hook}\n\n"
        "Обзор: {topic_lower}.\n\n"
        "Плюсы:\n"
        "+ Доступная цена\n"
        "+ Быстрая доставка\n"
        "+ Реальная польза для практики\n\n"
        "Минусы:\n"
        "- Пока не нашёл, расскажите в комментах\n\n"
        "Ссылка в описании профиля.\n\n"
        "{hashtags}"
    ),
    (
        "{hook}\n\n"
        "Этот гаджет должен быть у каждого,\n"
        "кто серьёзно занимается {pillar_short}.\n\n"
        "{topic}.\n\n"
        "Заказывал с AliExpress — пришло за 2 недели.\n"
        "Ссылка в био, пока есть скидка.\n\n"
        "{hashtags}"
    ),
    (
        "{hook}\n\n"
        "Распаковка и тест: {topic_lower}.\n\n"
        "Стоит ли брать? Однозначно да, если:\n"
        "- Ты изучаешь {pillar_short}\n"
        "- Хочешь практиковаться на реальном железе\n"
        "- Ищешь бюджетный вариант\n\n"
        "Проверенная ссылка — в шапке профиля.\n\n"
        "{hashtags}"
    ),
]

VIDEO_SCRIPT_TEMPLATES: list[str] = [
    (
        "[0-3s] HOOK: {hook}\n"
        "[3-5s] Титр: {topic}\n"
        "[5-15s] Объяснение: что это и зачем нужно\n"
        "[15-22s] Демонстрация: пошаговый показ\n"
        "[22-27s] Результат: что получается\n"
        "[27-30s] CTA: {cta}"
    ),
    (
        "[0-2s] HOOK: {hook}\n"
        "[2-8s] Проблема: почему это важно\n"
        "[8-20s] Решение: разбор {topic_lower}\n"
        "[20-25s] Лайфхак: один секретный приём\n"
        "[25-30s] CTA: {cta}"
    ),
    (
        "[0-3s] HOOK: {hook}\n"
        "[3-10s] Контекст: для кого и зачем\n"
        "[10-20s] Основа: ключевые шаги\n"
        "[20-25s] Совет: чего избегать\n"
        "[25-30s] CTA: {cta}"
    ),
]

VISUAL_BRIEF_TEMPLATES: list[str] = [
    (
        "Стиль: тёмный фон с неоновым акцентом ({accent}).\n"
        "Текст-оверлей: «{hook_short}».\n"
        "Элементы: скриншот терминала / интерфейса.\n"
        "Формат: {format_label}."
    ),
    (
        "Стиль: градиент {accent} -> тёмный.\n"
        "Заголовок крупным шрифтом: «{topic_short}».\n"
        "Иконки: тематические по {pillar_short}.\n"
        "Формат: {format_label}."
    ),
    (
        "Стиль: минималистичный, тёмная тема.\n"
        "Центральный элемент: инфографика по {topic_short}.\n"
        "Акцентный цвет: {accent}.\n"
        "Формат: {format_label}."
    ),
]

ACCENT_COLORS: dict[str, str] = {
    "Cyber Security & Ethical Hacking": "#00ff41 (matrix green)",
    "Blue Team / Defensive Security": "#00bfff (defender blue)",
    "Red Team / Offensive Security": "#ff4444 (attacker red)",
    "Machine Learning & AI": "#a855f7 (AI purple)",
    "AliExpress - Гаджеты": "#ff6600 (AliExpress orange)",
}

FORMAT_LABELS: dict[str, str] = {
    "reels": "вертикальное видео 9:16",
    "carousel": "карусель 1080x1080, 5 слайдов",
    "stories": "сторис 1080x1920",
    "static_post": "статичная картинка 1080x1080",
    "short_video": "вертикальное видео 9:16, до 60с",
    "duet": "дуэт-видео 9:16",
    "shorts": "Shorts 9:16, до 60с",
    "full_video": "горизонтальное 16:9, 8-15 мин",
}


@dataclass(frozen=True, slots=True)
class ReadyPost:
    day: date
    time_slot: str
    platform: str
    pillar: str
    topic: str
    format: str
    caption: str
    visual_brief: str
    video_script: str
    hashtags: list[str]
    referral_url: str

    def to_dict(self) -> dict[str, object]:
        return {
            "day": self.day.isoformat(),
            "time": self.time_slot,
            "platform": self.platform,
            "pillar": self.pillar,
            "topic": self.topic,
            "format": self.format,
            "caption": self.caption,
            "visual_brief": self.visual_brief,
            "video_script": self.video_script,
            "hashtags": self.hashtags,
            "referral_url": self.referral_url,
        }


def _pillar_short(pillar: ContentPillar) -> str:
    return pillar.name.split("/")[0].strip().split("&")[0].strip().split("-")[0].strip()


def _build_caption(slot: PostSlot) -> str:
    is_referral = slot.pillar.product == "referral"
    templates = CAPTION_TEMPLATES_REFERRAL if is_referral else CAPTION_TEMPLATES_COURSE
    tpl = random.choice(templates)
    hashtags_str = " ".join(slot.hashtags)
    return tpl.format(
        hook=slot.hook,
        topic=slot.topic,
        topic_lower=slot.topic.lower() if slot.topic[0].isupper() else slot.topic,
        pillar_short=_pillar_short(slot.pillar),
        cta=slot.cta,
        hashtags=hashtags_str,
    )


def _build_visual_brief(slot: PostSlot) -> str:
    tpl = random.choice(VISUAL_BRIEF_TEMPLATES)
    accent = ACCENT_COLORS.get(slot.pillar.name, "#6366f1 (indigo)")
    fmt_label = FORMAT_LABELS.get(slot.format, slot.format)
    hook_short = slot.hook[:50] + "..." if len(slot.hook) > 50 else slot.hook
    topic_short = slot.topic[:40] + "..." if len(slot.topic) > 40 else slot.topic
    return tpl.format(
        accent=accent,
        hook_short=hook_short,
        topic_short=topic_short,
        format_label=fmt_label,
        pillar_short=_pillar_short(slot.pillar),
    )


def _build_video_script(slot: PostSlot) -> str:
    is_video = slot.format in ("reels", "short_video", "shorts", "duet", "full_video")
    if not is_video:
        return ""
    tpl = random.choice(VIDEO_SCRIPT_TEMPLATES)
    return tpl.format(
        hook=slot.hook,
        topic=slot.topic,
        topic_lower=slot.topic.lower() if slot.topic[0].isupper() else slot.topic,
        cta=slot.cta,
    )


def generate_ready_posts(
    days: int = 7,
    seed: int | None = None,
    start: date | None = None,
) -> list[ReadyPost]:
    plan = generate_week_plan(start=start, days=days, seed=seed)
    if seed is not None:
        random.seed(seed + 1000)

    return [
        ReadyPost(
            day=slot.day,
            time_slot=slot.time_slot,
            platform=slot.platform.value,
            pillar=slot.pillar.name,
            topic=slot.topic,
            format=slot.format,
            caption=_build_caption(slot),
            visual_brief=_build_visual_brief(slot),
            video_script=_build_video_script(slot),
            hashtags=slot.hashtags,
            referral_url=slot.referral_url,
        )
        for slot in plan
    ]


def export_ready_json(posts: list[ReadyPost], path: Path) -> Path:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    data = [p.to_dict() for p in posts]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_buffer_csv(posts: list[ReadyPost], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Text", "Date", "Time", "Profile"])
        for p in posts:
            pub_dt = datetime.combine(p.day, datetime.min.time())
            parts = p.time_slot.split(":")
            if len(parts) == 2:
                pub_dt = pub_dt.replace(hour=int(parts[0]), minute=int(parts[1]))
            date_str = pub_dt.strftime("%Y-%m-%d")
            time_str = pub_dt.strftime("%H:%M")
            profile = p.platform.title()
            writer.writerow([p.caption, date_str, time_str, profile])
    return path


def export_ready_markdown(posts: list[ReadyPost], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = ["# Готовые посты к публикации\n"]
    current_day: date | None = None
    weekdays = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
    ]

    for p in sorted(posts, key=lambda x: (x.day, x.time_slot, x.platform)):
        if p.day != current_day:
            current_day = p.day
            day_name = weekdays[current_day.weekday()]
            lines.append(f"\n## {day_name}, {current_day.isoformat()}\n")

        lines.append(f"### {p.time_slot} | {p.platform.upper()} | {p.format}")
        lines.append(f"**Столп:** {p.pillar}")
        lines.append(f"**Тема:** {p.topic}\n")
        lines.append("**Подпись (caption):**")
        lines.append(f"```\n{p.caption}\n```\n")
        lines.append(f"**Визуальный бриф:** {p.visual_brief}\n")
        if p.video_script:
            lines.append("**Сценарий видео:**")
            lines.append(f"```\n{p.video_script}\n```\n")
        if p.referral_url:
            lines.append(f"**Ссылка:** `{p.referral_url}`\n")
        lines.append("---\n")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def batch_summary(posts: list[ReadyPost]) -> str:
    by_platform: dict[str, int] = {}
    by_pillar: dict[str, int] = {}
    video_count = 0
    for p in posts:
        by_platform[p.platform] = by_platform.get(p.platform, 0) + 1
        by_pillar[p.pillar] = by_pillar.get(p.pillar, 0) + 1
        if p.video_script:
            video_count += 1

    lines = [
        f"Готовые посты: {len(posts)} шт.",
        "",
        "По платформам:",
    ]
    for pl, count in sorted(by_platform.items()):
        lines.append(f"  {pl}: {count}")
    lines.append("\nПо направлениям:")
    for name, count in sorted(by_pillar.items()):
        lines.append(f"  {name}: {count}")
    lines.append(f"\nВидео-сценариев: {video_count}")
    lines.append(
        f"Постов с реферальной ссылкой: {sum(1 for p in posts if p.referral_url)}"
    )
    return "\n".join(lines)
