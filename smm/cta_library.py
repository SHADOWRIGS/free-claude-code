"""CTA library — platform-aware calls-to-action per funnel stage.

Provides a curated set of CTAs organized by funnel stage (TOFU/MOFU/BOFU),
target action (follow, save, comment, click, buy), and platform.
Each CTA has a short version (for captions) and a long version (for scripts).
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

FUNNEL_STAGES = ("tofu", "mofu", "bofu")
TARGET_ACTIONS = ("follow", "save", "comment", "click", "buy")

STAGE_LABELS: dict[str, str] = {
    "tofu": "Верх воронки (осведомлённость)",
    "mofu": "Середина воронки (интерес)",
    "bofu": "Низ воронки (конверсия)",
}

ACTION_LABELS: dict[str, str] = {
    "follow": "Подписка",
    "save": "Сохранение",
    "comment": "Комментарий",
    "click": "Переход по ссылке",
    "buy": "Покупка/регистрация",
}


@dataclass(frozen=True, slots=True)
class CTA:
    stage: str
    stage_label: str
    action: str
    action_label: str
    platform: str
    short_text: str
    long_text: str


CTA_DATA: list[dict[str, str]] = [
    # TOFU — follow
    {
        "stage": "tofu",
        "action": "follow",
        "platform": "instagram",
        "short": "Подписывайся, чтобы не пропустить!",
        "long": "Подписывайся на @shadowrigs — каждый день новые разборы, гайды и лайфхаки по кибербезопасности. Нажми колокольчик!",
    },
    {
        "stage": "tofu",
        "action": "follow",
        "platform": "tiktok",
        "short": "Подписывайся — будет ещё круче!",
        "long": "Если тебе зашло — подписывайся и ставь лайк, чтобы алгоритм показал тебе следующие видео. Новые ролики каждый день!",
    },
    {
        "stage": "tofu",
        "action": "follow",
        "platform": "youtube",
        "short": "Подпишись на канал и нажми колокольчик!",
        "long": "Подпишись на канал ShadowRigs — новые видео каждую неделю. Нажми колокольчик, чтобы не пропустить уведомления!",
    },
    # TOFU — save
    {
        "stage": "tofu",
        "action": "save",
        "platform": "instagram",
        "short": "Сохрани, чтобы не потерять!",
        "long": "Нажми на закладку — этот пост пригодится, когда будешь настраивать. Сохрани и поделись с другом!",
    },
    {
        "stage": "tofu",
        "action": "save",
        "platform": "tiktok",
        "short": "Сохрани видео — пригодится!",
        "long": "Добавь в избранное, чтобы вернуться к этому, когда будешь практиковаться. Делись с друзьями!",
    },
    {
        "stage": "tofu",
        "action": "save",
        "platform": "youtube",
        "short": "Добавь в «Смотреть позже»!",
        "long": "Нажми «Смотреть позже», чтобы вернуться к этому видео. Поделись с тем, кому это нужно!",
    },
    # TOFU — comment
    {
        "stage": "tofu",
        "action": "comment",
        "platform": "instagram",
        "short": "Напиши в комментариях, что думаешь!",
        "long": "Согласен? Не согласен? Напиши в комментариях — мне важно твоё мнение. Самые интересные комменты разберу в сторис!",
    },
    {
        "stage": "tofu",
        "action": "comment",
        "platform": "tiktok",
        "short": "Пиши в комменты!",
        "long": "Напиши «+» если хочешь продолжение! Или задай вопрос — отвечу в следующем видео.",
    },
    {
        "stage": "tofu",
        "action": "comment",
        "platform": "youtube",
        "short": "Оставь комментарий!",
        "long": "Напиши в комментариях, какую тему разобрать следующей. Лайк и комментарий помогают продвигать видео!",
    },
    # MOFU — click
    {
        "stage": "mofu",
        "action": "click",
        "platform": "instagram",
        "short": "Ссылка в био — переходи!",
        "long": "Хочешь узнать больше? Переходи по ссылке в био — там полный гайд, PDF-чеклист и бонусные материалы.",
    },
    {
        "stage": "mofu",
        "action": "click",
        "platform": "tiktok",
        "short": "Ссылка в профиле!",
        "long": "Полная версия + бонусные материалы — по ссылке в моём профиле. Переходи прямо сейчас!",
    },
    {
        "stage": "mofu",
        "action": "click",
        "platform": "youtube",
        "short": "Ссылка в описании под видео!",
        "long": "Все материалы из видео — в описании ниже. Переходи по ссылке и скачивай бесплатно!",
    },
    # MOFU — save
    {
        "stage": "mofu",
        "action": "save",
        "platform": "instagram",
        "short": "Сохрани карусель — там пошаговый план!",
        "long": "В этой карусели — полный пошаговый план. Сохрани, чтобы вернуться и пройти все шаги. Репост в сторис = помощь друзьям!",
    },
    {
        "stage": "mofu",
        "action": "save",
        "platform": "tiktok",
        "short": "Добавь в коллекцию!",
        "long": "Этот видеогайд стоит сохранить — пригодится на практике. Добавь в коллекцию и поделись!",
    },
    {
        "stage": "mofu",
        "action": "save",
        "platform": "youtube",
        "short": "Добавь в плейлист!",
        "long": "Создай плейлист «Обучение» и добавь это видео — так ты не потеряешь полезные уроки.",
    },
    # MOFU — comment
    {
        "stage": "mofu",
        "action": "comment",
        "platform": "instagram",
        "short": "Напиши «ГАЙД» — пришлю в директ!",
        "long": "Хочешь получить полный PDF-гайд бесплатно? Напиши «ГАЙД» в комментариях — пришлю в директ!",
    },
    {
        "stage": "mofu",
        "action": "comment",
        "platform": "tiktok",
        "short": "Напиши «хочу» в комменты!",
        "long": "Напиши «хочу» — и я скину тебе ссылку на бесплатный мини-курс прямо в ЛС.",
    },
    {
        "stage": "mofu",
        "action": "comment",
        "platform": "youtube",
        "short": "Напиши «PDF» в комментариях!",
        "long": "Хочешь чеклист из видео? Напиши «PDF» в комментариях — дам ссылку!",
    },
    # BOFU — buy (courses)
    {
        "stage": "bofu",
        "action": "buy",
        "platform": "instagram",
        "short": "Записывайся на курс — ссылка в био!",
        "long": "Готов стать профессионалом? Записывайся на курс по ссылке в био. Количество мест ограничено — не откладывай!",
    },
    {
        "stage": "bofu",
        "action": "buy",
        "platform": "tiktok",
        "short": "Курс — ссылка в профиле!",
        "long": "Хватит просто смотреть — пора действовать! Записывайся на курс по ссылке в профиле. Первым 10 — скидка!",
    },
    {
        "stage": "bofu",
        "action": "buy",
        "platform": "youtube",
        "short": "Записывайся — ссылка под видео!",
        "long": "Все подробности и запись на курс — в описании под видео. Не жди «понедельника» — начинай сейчас!",
    },
    # BOFU — click (referral)
    {
        "stage": "bofu",
        "action": "click",
        "platform": "instagram",
        "short": "Купить — ссылка в био!",
        "long": "Этот гаджет можно купить по моей ссылке в био со скидкой. Проверено лично — рекомендую!",
    },
    {
        "stage": "bofu",
        "action": "click",
        "platform": "tiktok",
        "short": "Ссылка на гаджет — в профиле!",
        "long": "Ссылка на AliExpress с проверенным продавцом — в моём профиле. Цена — огонь, бери пока есть!",
    },
    {
        "stage": "bofu",
        "action": "click",
        "platform": "youtube",
        "short": "Ссылка в описании!",
        "long": "Все ссылки на гаджеты из видео — в описании ниже. Реферальная ссылка, поддержи канал!",
    },
]


def generate_ctas(
    stage: str | None = None,
    action: str | None = None,
    platform: str | None = None,
) -> list[CTA]:
    result: list[CTA] = []
    for item in CTA_DATA:
        if stage and item["stage"] != stage:
            continue
        if action and item["action"] != action:
            continue
        if platform and item["platform"] != platform:
            continue

        result.append(
            CTA(
                stage=item["stage"],
                stage_label=STAGE_LABELS[item["stage"]],
                action=item["action"],
                action_label=ACTION_LABELS[item["action"]],
                platform=item["platform"],
                short_text=item["short"],
                long_text=item["long"],
            )
        )
    return result


def pick_cta(
    stage: str = "tofu",
    platform: str = "instagram",
    seed: int | None = None,
) -> CTA:
    rng = random.Random(seed)
    pool = generate_ctas(stage=stage, platform=platform)
    if not pool:
        pool = generate_ctas(stage=stage)
    if not pool:
        pool = generate_ctas()
    return rng.choice(pool)


def export_ctas_json(ctas: list[CTA], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "stage": c.stage,
            "stage_label": c.stage_label,
            "action": c.action,
            "action_label": c.action_label,
            "platform": c.platform,
            "short": c.short_text,
            "long": c.long_text,
        }
        for c in ctas
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_ctas_txt(ctas: list[CTA], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "БИБЛИОТЕКА CTA — ПРИЗЫВЫ К ДЕЙСТВИЮ",
        "=" * 60,
    ]

    current_stage = ""
    for c in ctas:
        if c.stage != current_stage:
            current_stage = c.stage
            lines.append(f"\n{'━' * 50}")
            lines.append(f"📌 {c.stage_label}")
            lines.append(f"{'━' * 50}")

        lines.append(f"\n  [{c.action_label}] {c.platform.upper()}")
        lines.append(f"  Короткий: {c.short_text}")
        lines.append(f"  Полный: {c.long_text}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def cta_summary(ctas: list[CTA]) -> str:
    by_stage: dict[str, int] = {}
    by_action: dict[str, int] = {}
    by_platform: dict[str, int] = {}
    for c in ctas:
        by_stage[c.stage_label] = by_stage.get(c.stage_label, 0) + 1
        by_action[c.action_label] = by_action.get(c.action_label, 0) + 1
        by_platform[c.platform] = by_platform.get(c.platform, 0) + 1

    lines: list[str] = [
        f"Библиотека CTA: {len(ctas)} вариантов",
        "\nПо этапам воронки:",
    ]
    lines.extend(f"  {stage}: {count}" for stage, count in by_stage.items())
    lines.append("\nПо действиям:")
    lines.extend(f"  {action}: {count}" for action, count in by_action.items())
    lines.append("\nПо платформам:")
    lines.extend(f"  {plat}: {count}" for plat, count in sorted(by_platform.items()))
    return "\n".join(lines)
