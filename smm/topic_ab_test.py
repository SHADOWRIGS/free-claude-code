"""Topic A/B testing — generate theme variants for split-testing.

Creates A/B variants of topic angles for each pillar so the SMM manager
can test which framing resonates better with the audience. Each pair
has a control (A) and a challenger (B) with different hooks.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

ANGLE_PAIRS: dict[str, list[tuple[str, str]]] = {
    "Cyber Security & Ethical Hacking": [
        (
            "Как хакеры взламывают пароли за 5 секунд",
            "5 паролей, которые взламываются мгновенно",
        ),
        (
            "Топ-3 инструмента для пентеста",
            "Какой инструмент пентеста выбрать новичку?",
        ),
        ("Почему антивирус не спасёт от хакеров", "Антивирус vs хакер: кто победит?"),
        (
            "Этичный хакинг: с чего начать карьеру",
            "Сколько зарабатывает этичный хакер в 2025",
        ),
        ("Реальный взлом WiFi за 2 минуты", "WiFi-безопасность: что знает твой сосед"),
    ],
    "Blue Team / Defensive Security": [
        ("SIEM за 10 минут: настройка с нуля", "Лучший SIEM для малого бизнеса"),
        (
            "Как обнаружить атаку до того, как она случится",
            "3 признака, что тебя уже взломали",
        ),
        (
            "Incident Response: пошаговый план",
            "Что делать в первые 60 минут после взлома",
        ),
        ("SOC-аналитик: день из жизни", "Почему SOC — самая стрессовая работа в IT"),
        (
            "Hardening Linux-сервера: чеклист",
            "10 настроек Linux, которые спасут от взлома",
        ),
    ],
    "Red Team / Offensive Security": [
        (
            "Social Engineering: как я взломал компанию",
            "Фишинг-письмо, которое обманет любого",
        ),
        ("Metasploit: первая атака за 5 минут", "Лучший фреймворк для пентеста в 2025"),
        ("Active Directory: вектор атаки №1", "Почему AD — мечта хакера"),
        (
            "Bug Bounty: как заработать первые $1000",
            "Реальный кейс Bug Bounty на $5000",
        ),
        ("Reverse Engineering малвари", "Как разобрать вирус по частям"),
    ],
    "Machine Learning & AI": [
        ("Нейросеть за 10 строк кода", "ChatGPT vs свою модель: что лучше?"),
        (
            "AI для кибербезопасности: реальные кейсы",
            "Как AI ловит хакеров быстрее людей",
        ),
        (
            "Prompt Engineering: гайд для продвинутых",
            "5 промптов, которые изменят твою работу",
        ),
        ("Fine-tuning модели на своих данных", "Свой ChatGPT за вечер: пошаговый гайд"),
        (
            "AI-автоматизация: заменит ли нас ИИ?",
            "Профессии, которые AI не заменит никогда",
        ),
    ],
    "AliExpress — Гаджеты": [
        ("WiFi-адаптер за $7, который удивит", "Топ-3 хакерских гаджета с AliExpress"),
        ("Flipper Zero vs дешёвые аналоги", "Гаджет за $15 делает то же, что Flipper"),
        ("USB Rubber Ducky своими руками", "Самый опасный USB-гаджет за $10"),
        (
            "Сетевое оборудование для лаба: что купить",
            "Домашняя лаборатория хакера за $50",
        ),
        (
            "Лучший power bank для хакера",
            "5 гаджетов, без которых хакер не выходит из дома",
        ),
    ],
}

PLATFORMS = ("instagram", "tiktok", "youtube")


@dataclass(frozen=True, slots=True)
class TopicABPair:
    pillar: str
    platform: str
    variant_a: str
    variant_b: str
    test_id: str
    hypothesis: str


def generate_ab_topics(
    pillar: str | None = None,
    platform: str | None = None,
    seed: int | None = None,
) -> list[TopicABPair]:
    rng = random.Random(seed)
    pairs: list[TopicABPair] = []

    pillars = [pillar] if pillar and pillar in ANGLE_PAIRS else list(ANGLE_PAIRS)
    platforms = [platform] if platform and platform in PLATFORMS else list(PLATFORMS)

    for pil in pillars:
        for plat in platforms:
            for i, (a, b) in enumerate(ANGLE_PAIRS[pil]):
                if rng.random() > 0.5:
                    a, b = b, a
                test_id = f"{pil[:3].lower()}-{plat[:2]}-{i + 1:02d}"
                hypothesis = _make_hypothesis(a, b, plat)
                pairs.append(
                    TopicABPair(
                        pillar=pil,
                        platform=plat,
                        variant_a=a,
                        variant_b=b,
                        test_id=test_id,
                        hypothesis=hypothesis,
                    )
                )

    return pairs


def _make_hypothesis(a: str, b: str, platform: str) -> str:
    metric = {
        "instagram": "охват и сохранения",
        "tiktok": "просмотры и шеры",
        "youtube": "CTR и удержание",
    }.get(platform, "вовлечённость")
    return f"Вариант B даст больше {metric}, чем A, за счёт более провокационной формулировки"


def export_ab_topics_json(pairs: list[TopicABPair], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "test_id": p.test_id,
            "pillar": p.pillar,
            "platform": p.platform,
            "variant_a": p.variant_a,
            "variant_b": p.variant_b,
            "hypothesis": p.hypothesis,
        }
        for p in pairs
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_ab_topics_txt(pairs: list[TopicABPair], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "A/B ТЕСТЫ ТЕМ — СПЛИТ-ТЕСТИРОВАНИЕ ЗАГОЛОВКОВ",
        "=" * 60,
    ]

    current_pillar = ""
    for p in pairs:
        if p.pillar != current_pillar:
            current_pillar = p.pillar
            lines.append(f"\n{'━' * 50}")
            lines.append(f"📊 {p.pillar}")
            lines.append(f"{'━' * 50}")

        lines.append(f"\n  [{p.test_id}] {p.platform.upper()}")
        lines.append(f"  A: {p.variant_a}")
        lines.append(f"  B: {p.variant_b}")
        lines.append(f"  Гипотеза: {p.hypothesis}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def ab_topics_summary(pairs: list[TopicABPair]) -> str:
    if not pairs:
        return "A/B тесты тем: 0 пар"

    by_pillar: dict[str, int] = {}
    by_platform: dict[str, int] = {}
    for p in pairs:
        by_pillar[p.pillar] = by_pillar.get(p.pillar, 0) + 1
        by_platform[p.platform] = by_platform.get(p.platform, 0) + 1

    lines: list[str] = [
        f"A/B тесты тем: {len(pairs)} пар",
        "\nПо направлениям:",
    ]
    lines.extend(f"  {pil}: {cnt}" for pil, cnt in by_pillar.items())
    lines.append("\nПо платформам:")
    lines.extend(f"  {plat}: {cnt}" for plat, cnt in sorted(by_platform.items()))
    return "\n".join(lines)
