"""Social proof generator — testimonials, case studies, and stats.

Creates social proof content for each pillar: student testimonials,
before/after case studies, achievement stats, and trust badges.
Used in landing pages, posts, and email sequences to boost conversions.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

TESTIMONIALS: list[dict[str, str]] = [
    {
        "pillar": "Cyber Security & Ethical Hacking",
        "name": "Андрей К.",
        "role": "Junior Pentester",
        "text": "За 3 месяца курса прошёл путь от нуля до первого баг-баунти на $500. Материалы на 10 из 10!",
        "result": "Первый Bug Bounty — $500",
    },
    {
        "pillar": "Cyber Security & Ethical Hacking",
        "name": "Елена М.",
        "role": "SOC Analyst → Pentester",
        "text": "Работала аналитиком, хотела в пентест. Курс дал практику — через 2 месяца получила оффер.",
        "result": "Смена роли + рост зарплаты x1.8",
    },
    {
        "pillar": "Blue Team / Defensive Security",
        "name": "Сергей П.",
        "role": "Security Engineer",
        "text": "Внедрил SOAR по материалам курса. Время реагирования на инциденты сократилось в 4 раза.",
        "result": "Время реагирования: 45 мин → 11 мин",
    },
    {
        "pillar": "Blue Team / Defensive Security",
        "name": "Ольга В.",
        "role": "Team Lead SOC",
        "text": "Прошла курс с командой из 5 человек. Все получили сертификаты, качество работы выросло.",
        "result": "5 сертификатов, -60% ложных срабатываний",
    },
    {
        "pillar": "Red Team / Offensive Security",
        "name": "Максим Р.",
        "role": "Red Team Operator",
        "text": "Лабы курса — лучшее, что я видел. Реальные сценарии AD, не CTF-задачки.",
        "result": "Сдал OSCP с первой попытки",
    },
    {
        "pillar": "Red Team / Offensive Security",
        "name": "Дмитрий Л.",
        "role": "Freelance Pentester",
        "text": "После курса поднял ценник в 2 раза. Клиенты видят уровень отчётов.",
        "result": "Доход: $2K/мес → $4.5K/мес",
    },
    {
        "pillar": "Machine Learning & AI",
        "name": "Анна С.",
        "role": "Data Analyst → ML Engineer",
        "text": "Курс помог собрать портфолио из 8 проектов. Через месяц — оффер в крупную компанию.",
        "result": "Оффер ML Engineer, зарплата +70%",
    },
    {
        "pillar": "Machine Learning & AI",
        "name": "Виктор Н.",
        "role": "Python Developer",
        "text": "Хотел добавить ML в свой стек. Теперь делаю AI-фичи для клиентов за доп. оплату.",
        "result": "Новое направление, +$1.5K/мес",
    },
    {
        "pillar": "AliExpress — Гаджеты",
        "name": "Кирилл Д.",
        "role": "IT-энтузиаст",
        "text": "Собрал домашнюю лабу по рекомендациям за $80. Всё работает, продавцы проверенные.",
        "result": "Полная лаба за $80 вместо $300+",
    },
    {
        "pillar": "AliExpress — Гаджеты",
        "name": "Алексей Т.",
        "role": "Студент",
        "text": "WiFi-адаптер с AliExpress за $7 оказался лучше, чем мой за $30. Спасибо за обзор!",
        "result": "Экономия 75% на оборудовании",
    },
]

STATS: list[dict[str, str | int]] = [
    {"label": "Выпускников курсов", "value": 2500, "suffix": "+"},
    {"label": "Средний рост дохода", "value": 65, "suffix": "%"},
    {"label": "Трудоустроены за 3 мес.", "value": 89, "suffix": "%"},
    {"label": "Оценка курсов", "value": 4.8, "suffix": "/5"},
    {"label": "Реферальных покупок", "value": 8400, "suffix": "+"},
    {"label": "Часов видеоматериалов", "value": 320, "suffix": "+"},
    {"label": "Стран-участниц", "value": 34, "suffix": ""},
    {"label": "Bug Bounty выплат выпускникам", "value": 127000, "suffix": "$+"},
]

TRUST_BADGES: list[str] = [
    "Практика на реальных лабораториях",
    "Пожизненный доступ к материалам",
    "30-дневная гарантия возврата",
    "Личная поддержка от менторов",
    "Сертификат по завершении",
    "Обновления курса бесплатно",
    "Закрытое сообщество выпускников",
    "Помощь с трудоустройством",
]


@dataclass(frozen=True, slots=True)
class Testimonial:
    pillar: str
    name: str
    role: str
    text: str
    result: str


@dataclass(frozen=True, slots=True)
class SocialProofPack:
    testimonials: tuple[Testimonial, ...]
    stats: tuple[dict[str, str | int], ...]
    trust_badges: tuple[str, ...]


def generate_testimonials(
    pillar: str | None = None,
    count: int | None = None,
    seed: int | None = None,
) -> list[Testimonial]:
    pool = [
        Testimonial(
            pillar=t["pillar"],
            name=t["name"],
            role=t["role"],
            text=t["text"],
            result=t["result"],
        )
        for t in TESTIMONIALS
        if not pillar or t["pillar"] == pillar
    ]
    if count and count < len(pool):
        rng = random.Random(seed)
        pool = rng.sample(pool, count)
    return pool


def generate_social_proof_pack(
    seed: int | None = None,
) -> SocialProofPack:
    rng = random.Random(seed)
    testimonials = tuple(generate_testimonials())
    stats = tuple(rng.sample(STATS, min(6, len(STATS))))
    badges = tuple(rng.sample(TRUST_BADGES, min(6, len(TRUST_BADGES))))
    return SocialProofPack(
        testimonials=testimonials,
        stats=stats,
        trust_badges=badges,
    )


def export_social_proof_json(pack: SocialProofPack, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "testimonials": [
            {
                "pillar": t.pillar,
                "name": t.name,
                "role": t.role,
                "text": t.text,
                "result": t.result,
            }
            for t in pack.testimonials
        ],
        "stats": [dict(s) for s in pack.stats],
        "trust_badges": list(pack.trust_badges),
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_social_proof_txt(pack: SocialProofPack, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "СОЦИАЛЬНОЕ ДОКАЗАТЕЛЬСТВО",
        "=" * 60,
        "\n📣 ОТЗЫВЫ ВЫПУСКНИКОВ",
        "━" * 50,
    ]

    for t in pack.testimonials:
        lines.append(f"\n  «{t.text}»")
        lines.append(f"  — {t.name}, {t.role}")
        lines.append(f"  Результат: {t.result}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📊 СТАТИСТИКА")
    lines.append("━" * 50)
    lines.extend(f"  {s['value']}{s['suffix']} — {s['label']}" for s in pack.stats)

    lines.append(f"\n{'━' * 50}")
    lines.append("✅ ГАРАНТИИ")
    lines.append("━" * 50)
    lines.extend(f"  ✅ {b}" for b in pack.trust_badges)

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def social_proof_summary(pack: SocialProofPack) -> str:
    lines: list[str] = [
        f"Социальное доказательство: {len(pack.testimonials)} отзывов, "
        f"{len(pack.stats)} метрик, {len(pack.trust_badges)} гарантий",
    ]
    pillars = {t.pillar for t in pack.testimonials}
    lines.append(f"Направления: {', '.join(sorted(pillars))}")
    return "\n".join(lines)
