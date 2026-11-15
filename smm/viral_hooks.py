"""Viral hooks — attention-grabbing openers optimized per platform.

Generates first-line hooks, thumbnail text, and reel openers
designed to maximize stop-scroll rate and algorithm reach.
Each hook uses proven psychological triggers: curiosity gap,
fear of missing out, social proof, controversy, and urgency.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from smm.content_pillars import PILLARS

HOOK_TYPES = (
    "curiosity",
    "fomo",
    "controversy",
    "listicle",
    "challenge",
    "story",
)

HOOK_TYPE_LABELS: dict[str, str] = {
    "curiosity": "Любопытство",
    "fomo": "Страх упустить",
    "controversy": "Провокация",
    "listicle": "Список",
    "challenge": "Вызов",
    "story": "История",
}


@dataclass(frozen=True, slots=True)
class ViralHook:
    pillar: str
    hook_type: str
    type_label: str
    text: str
    thumbnail_text: str
    platform_best: str


PILLAR_HOOKS: dict[str, dict[str, list[dict[str, str]]]] = {
    "Cyber Security & Ethical Hacking": {
        "curiosity": [
            {
                "text": "Я проверил свой пароль в базе утечек — и офигел...",
                "thumb": "ТВОЙ ПАРОЛЬ\nУЖЕ СЛИТ?",
                "platform": "tiktok",
            },
            {
                "text": "Что видит хакер, когда заходит на твой WiFi",
                "thumb": "ЧТО ВИДИТ\nХАКЕР",
                "platform": "youtube",
            },
            {
                "text": "Этот бесплатный сайт покажет все утечки твоих данных",
                "thumb": "ПРОВЕРЬ\nСВОИ ДАННЫЕ",
                "platform": "instagram",
            },
        ],
        "fomo": [
            {
                "text": "Пока ты читаешь это — кто-то уже сканирует твою сеть",
                "thumb": "ТЕБЯ УЖЕ\nСКАНИРУЮТ",
                "platform": "instagram",
            },
            {
                "text": "95% людей не знают ЭТО о своём роутере",
                "thumb": "95% НЕ ЗНАЮТ",
                "platform": "tiktok",
            },
        ],
        "controversy": [
            {
                "text": "Антивирусы бесполезны. И вот почему...",
                "thumb": "АНТИВИРУС\n= МУСОР?",
                "platform": "youtube",
            },
            {
                "text": "VPN не защищает тебя. Вот что реально работает",
                "thumb": "VPN НЕ\nРАБОТАЕТ",
                "platform": "tiktok",
            },
        ],
        "listicle": [
            {
                "text": "5 вещей, которые хакеры делают первым делом (и ты тоже можешь)",
                "thumb": "5 ПРИЁМОВ\nХАКЕРОВ",
                "platform": "instagram",
            },
        ],
        "challenge": [
            {
                "text": "Попробуй взломать ЭТО за 5 минут (легально)",
                "thumb": "ВЗЛОМАЙ\nЗА 5 МИНУТ",
                "platform": "tiktok",
            },
        ],
        "story": [
            {
                "text": "Как я нашёл уязвимость в крупном банке и что было дальше",
                "thumb": "ВЗЛОМАЛ\nБАНК",
                "platform": "youtube",
            },
        ],
    },
    "Blue Team / Defensive Security": {
        "curiosity": [
            {
                "text": "Так выглядит реальная кибератака в SIEM — пошагово",
                "thumb": "АТАКА\nВ РЕАЛЬНОМ\nВРЕМЕНИ",
                "platform": "youtube",
            },
            {
                "text": "Один лог, который спасёт твою компанию от взлома",
                "thumb": "ОДИН ЛОГ\nСПАСЁТ ВСЁ",
                "platform": "instagram",
            },
        ],
        "fomo": [
            {
                "text": "Пока ты не мониторишь — хакеры уже внутри",
                "thumb": "ОНИ УЖЕ\nВНУТРИ",
                "platform": "tiktok",
            },
        ],
        "controversy": [
            {
                "text": "SOC-аналитик — самая переоценённая профессия? Разбираемся",
                "thumb": "SOC =\nПЕРЕОЦЕНКА?",
                "platform": "youtube",
            },
        ],
        "listicle": [
            {
                "text": "ТОП-3 бесплатных SIEM, которые реально работают",
                "thumb": "ТОП-3\nSIEM",
                "platform": "instagram",
            },
        ],
        "challenge": [
            {
                "text": "Найди угрозу в этих логах за 60 секунд",
                "thumb": "НАЙДИ\nУГРОЗУ",
                "platform": "tiktok",
            },
        ],
        "story": [
            {
                "text": "Как я поймал хакера в корпоративной сети за 2 часа",
                "thumb": "ПОЙМАЛ\nХАКЕРА",
                "platform": "youtube",
            },
        ],
    },
    "Red Team / Offensive Security": {
        "curiosity": [
            {
                "text": "Я взломал WiFi соседа за 3 минуты. Легально.",
                "thumb": "WIFI\nЗА 3 МИНУТЫ",
                "platform": "tiktok",
            },
            {
                "text": "Что можно узнать о человеке за 5 минут OSINT",
                "thumb": "5 МИНУТ\nOSINT",
                "platform": "youtube",
            },
        ],
        "fomo": [
            {
                "text": "Этот инструмент знают только пентестеры. Теперь и ты",
                "thumb": "СЕКРЕТНЫЙ\nИНСТРУМЕНТ",
                "platform": "instagram",
            },
        ],
        "controversy": [
            {
                "text": "OSCP — пустая трата денег? Мой честный отзыв",
                "thumb": "OSCP =\nРАЗВОД?",
                "platform": "youtube",
            },
        ],
        "listicle": [
            {
                "text": "7 команд, которые должен знать каждый пентестер",
                "thumb": "7 КОМАНД\nПЕНТЕСТЕРА",
                "platform": "instagram",
            },
        ],
        "challenge": [
            {
                "text": "Сможешь обойти эту защиту? CTF для новичков",
                "thumb": "ОБОЙДИ\nЗАЩИТУ",
                "platform": "tiktok",
            },
        ],
        "story": [
            {
                "text": "Мой первый пентест: всё пошло не по плану...",
                "thumb": "ВСЁ ПОШЛО\nНЕ ТАК",
                "platform": "youtube",
            },
        ],
    },
    "Machine Learning & AI": {
        "curiosity": [
            {
                "text": "Я заставил AI написать код лучше, чем я сам",
                "thumb": "AI КОДИТ\nЛУЧШЕ ТЕБЯ",
                "platform": "tiktok",
            },
            {
                "text": "Этот промпт-трюк меняет ВСЁ (серьёзно)",
                "thumb": "ПРОМПТ\nКОТОРЫЙ\nМЕНЯЕТ ВСЁ",
                "platform": "instagram",
            },
        ],
        "fomo": [
            {
                "text": "AI уже заменяет эти 5 профессий. Твоя в списке?",
                "thumb": "AI ЗАМЕНИТ\nТЕБЯ?",
                "platform": "youtube",
            },
        ],
        "controversy": [
            {
                "text": "ChatGPT — это пузырь. И вот мои аргументы",
                "thumb": "ChatGPT =\nПУЗЫРЬ?",
                "platform": "youtube",
            },
        ],
        "listicle": [
            {
                "text": "5 нейросетей, которые сэкономят тебе 10 часов в неделю",
                "thumb": "5 AI\n= 10 ЧАСОВ",
                "platform": "instagram",
            },
        ],
        "challenge": [
            {
                "text": "Сделай свою первую нейросеть за 10 минут — повторяй за мной",
                "thumb": "НЕЙРОСЕТЬ\nЗА 10 МИНУТ",
                "platform": "tiktok",
            },
        ],
        "story": [
            {
                "text": "Как я автоматизировал бизнес с помощью AI за один вечер",
                "thumb": "AI-БИЗНЕС\nЗА ВЕЧЕР",
                "platform": "youtube",
            },
        ],
    },
    "AliExpress - Гаджеты": {
        "curiosity": [
            {
                "text": "Этот гаджет за $8 с AliExpress напугает любого хакера",
                "thumb": "$8 ГАДЖЕТ\nПУГАЕТ\nХАКЕРОВ",
                "platform": "tiktok",
            },
            {
                "text": "Распаковка: 10 самых странных хакерских устройств",
                "thumb": "10 СТРАННЫХ\nГАДЖЕТОВ",
                "platform": "youtube",
            },
        ],
        "fomo": [
            {
                "text": "Эту штуку с AliExpress раскупают за часы — успей!",
                "thumb": "РАСКУПАЮТ\nЗА ЧАСЫ",
                "platform": "instagram",
            },
        ],
        "controversy": [
            {
                "text": "Flipper Zero — игрушка или реальный инструмент? Тест",
                "thumb": "FLIPPER =\nИГРУШКА?",
                "platform": "youtube",
            },
        ],
        "listicle": [
            {
                "text": "ТОП-5 гаджетов с AliExpress до $20 для кибербезопасности",
                "thumb": "ТОП-5\nДО $20",
                "platform": "instagram",
            },
        ],
        "challenge": [
            {
                "text": "Собираю набор пентестера за $50 с AliExpress — реально?",
                "thumb": "НАБОР\nЗА $50",
                "platform": "tiktok",
            },
        ],
        "story": [
            {
                "text": "Купил 20 гаджетов с AliExpress — половина оказалась мусором",
                "thumb": "ПОЛОВИНА\n= МУСОР",
                "platform": "youtube",
            },
        ],
    },
}


def generate_hooks(pillar_name: str) -> list[ViralHook]:
    pillar_data = PILLAR_HOOKS.get(pillar_name)
    if pillar_data is None:
        return []

    hooks: list[ViralHook] = []
    for hook_type in HOOK_TYPES:
        items = pillar_data.get(hook_type, [])
        hooks.extend(
            ViralHook(
                pillar=pillar_name,
                hook_type=hook_type,
                type_label=HOOK_TYPE_LABELS[hook_type],
                text=item["text"],
                thumbnail_text=item["thumb"],
                platform_best=item["platform"],
            )
            for item in items
        )
    return hooks


def generate_all_hooks() -> list[ViralHook]:
    result: list[ViralHook] = []
    for pillar in PILLARS:
        result.extend(generate_hooks(pillar.name))
    return result


def pick_random_hooks(
    count: int = 10,
    pillar: str | None = None,
    seed: int | None = None,
) -> list[ViralHook]:
    rng = random.Random(seed)
    pool = generate_hooks(pillar) if pillar else generate_all_hooks()
    return rng.sample(pool, min(count, len(pool)))


def export_hooks_json(hooks: list[ViralHook], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "pillar": h.pillar,
            "type": h.hook_type,
            "type_label": h.type_label,
            "text": h.text,
            "thumbnail_text": h.thumbnail_text,
            "platform_best": h.platform_best,
        }
        for h in hooks
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_hooks_txt(hooks: list[ViralHook], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "ВИРУСНЫЕ ХУКИ — СТОП-СКРОЛЛ КОНТЕНТ",
        "=" * 60,
    ]

    current_pillar = ""
    for h in hooks:
        if h.pillar != current_pillar:
            current_pillar = h.pillar
            lines.append(f"\n{'─' * 50}")
            lines.append(f"📌 {current_pillar}")
            lines.append(f"{'─' * 50}")

        lines.append(f"\n  [{h.type_label}] {h.platform_best.upper()}")
        lines.append(f"  Хук: {h.text}")
        lines.append(f"  Превью: {h.thumbnail_text.replace(chr(10), ' | ')}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def hooks_summary(hooks: list[ViralHook]) -> str:
    by_pillar: dict[str, int] = {}
    by_type: dict[str, int] = {}
    by_platform: dict[str, int] = {}
    for h in hooks:
        by_pillar[h.pillar] = by_pillar.get(h.pillar, 0) + 1
        by_type[h.type_label] = by_type.get(h.type_label, 0) + 1
        by_platform[h.platform_best] = by_platform.get(h.platform_best, 0) + 1

    lines: list[str] = [
        f"Вирусные хуки: {len(hooks)} шт.",
        f"Направлений: {len(by_pillar)}",
    ]
    lines.extend(f"  {name}: {count}" for name, count in by_pillar.items())
    lines.append("\nПо платформам:")
    lines.extend(f"  {plat}: {count}" for plat, count in sorted(by_platform.items()))
    return "\n".join(lines)
