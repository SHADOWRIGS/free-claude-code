"""Competitor analysis and niche benchmarking for SMM strategy.

Provides competitor profiling, content gap analysis, and benchmarking
tools to understand the competitive landscape in each pillar's niche.

Uses research-backed engagement benchmarks and content patterns
to identify opportunities and differentiate the brand.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from smm.content_pillars import PILLARS, ContentPillar

NICHE_BENCHMARKS: dict[str, dict[str, float]] = {
    "Cyber Security & Ethical Hacking": {
        "avg_engagement_rate": 3.2,
        "avg_post_frequency": 5.0,
        "avg_follower_growth": 2.1,
        "avg_video_views_rate": 8.5,
        "hashtag_reach_rate": 12.0,
    },
    "Blue Team / Defensive Security": {
        "avg_engagement_rate": 2.8,
        "avg_post_frequency": 4.0,
        "avg_follower_growth": 1.8,
        "avg_video_views_rate": 7.2,
        "hashtag_reach_rate": 10.5,
    },
    "Red Team / Offensive Security": {
        "avg_engagement_rate": 3.5,
        "avg_post_frequency": 4.5,
        "avg_follower_growth": 2.4,
        "avg_video_views_rate": 9.8,
        "hashtag_reach_rate": 13.2,
    },
    "Machine Learning & AI": {
        "avg_engagement_rate": 2.5,
        "avg_post_frequency": 6.0,
        "avg_follower_growth": 3.0,
        "avg_video_views_rate": 7.0,
        "hashtag_reach_rate": 11.0,
    },
    "AliExpress - Гаджеты": {
        "avg_engagement_rate": 4.0,
        "avg_post_frequency": 7.0,
        "avg_follower_growth": 2.8,
        "avg_video_views_rate": 12.0,
        "hashtag_reach_rate": 15.0,
    },
}

COMPETITOR_PROFILES: dict[str, list[dict[str, str | int | float]]] = {
    "Cyber Security & Ethical Hacking": [
        {
            "name": "CyberMentor (Heath Adams)",
            "platform": "youtube",
            "followers": 500_000,
            "strength": "Длинные практические туториалы, курсы с нуля",
            "weakness": "Мало коротких форматов, нет Reels/TikTok",
            "content_type": "Видеокурсы, стримы, вебинары",
        },
        {
            "name": "John Hammond",
            "platform": "youtube",
            "followers": 1_200_000,
            "strength": "CTF-разборы, вирусный контент, подача с юмором",
            "weakness": "Узкая ниша CTF, мало про карьеру",
            "content_type": "CTF walkthroughs, разбор малвари",
        },
        {
            "name": "NetworkChuck",
            "platform": "youtube",
            "followers": 3_500_000,
            "strength": "Энергичная подача, простое объяснение сложного",
            "weakness": "Поверхностное покрытие тем, много рекламы",
            "content_type": "Туториалы, обзоры железа, хаки",
        },
    ],
    "Blue Team / Defensive Security": [
        {
            "name": "13Cubed",
            "platform": "youtube",
            "followers": 90_000,
            "strength": "Глубокий DFIR-контент, профессиональный подход",
            "weakness": "Мало вовлекающего контента, сухая подача",
            "content_type": "DFIR, форензика, расследования",
        },
        {
            "name": "SANS Institute",
            "platform": "instagram",
            "followers": 200_000,
            "strength": "Авторитет бренда, инфографики, новости",
            "weakness": "Корпоративный стиль, мало личного контента",
            "content_type": "Инфографики, статистика, новости",
        },
    ],
    "Red Team / Offensive Security": [
        {
            "name": "IppSec",
            "platform": "youtube",
            "followers": 350_000,
            "strength": "Детальные HTB-прохождения, методичность",
            "weakness": "Длинные видео, нет коротких форматов",
            "content_type": "HackTheBox walkthroughs",
        },
        {
            "name": "LiveOverflow",
            "platform": "youtube",
            "followers": 900_000,
            "strength": "Глубокий технический контент, уникальный стиль",
            "weakness": "Нерегулярный выход, сложный для новичков",
            "content_type": "Эксплойты, реверс, исследования",
        },
    ],
    "Machine Learning & AI": [
        {
            "name": "Sentdex",
            "platform": "youtube",
            "followers": 1_200_000,
            "strength": "Практические проекты, Python-фокус",
            "weakness": "Мало современных тем (LLM), устаревший контент",
            "content_type": "Python ML туториалы, проекты",
        },
        {
            "name": "Two Minute Papers",
            "platform": "youtube",
            "followers": 1_500_000,
            "strength": "Вирусный формат, визуализации, тренды",
            "weakness": "Только обзоры, нет практики",
            "content_type": "Обзоры научных статей, демо AI",
        },
    ],
    "AliExpress - Гаджеты": [
        {
            "name": "Hak5",
            "platform": "youtube",
            "followers": 800_000,
            "strength": "Обзоры хакерского железа, собственные продукты",
            "weakness": "Высокие цены, нишевая аудитория",
            "content_type": "Обзоры гаджетов, пентест-железо",
        },
        {
            "name": "David Bombal",
            "platform": "youtube",
            "followers": 2_000_000,
            "strength": "Обзоры сетевого оборудования, сертификации",
            "weakness": "Длинные видео, мало коротких форматов",
            "content_type": "Обзоры железа, лабораторные стенды",
        },
    ],
}

CONTENT_GAPS: dict[str, list[str]] = {
    "Cyber Security & Ethical Hacking": [
        "Короткие Reels/TikTok с быстрыми хаками (< 60 сек)",
        "Карусели с пошаговыми инструкциями на русском",
        "Сторис с интерактивными опросами и квизами",
        "Контент о карьере в кибербезопасности на русском рынке",
        "Сравнения инструментов (Kali vs Parrot, Burp vs ZAP)",
    ],
    "Blue Team / Defensive Security": [
        "Визуальные гайды по настройке SIEM",
        "Истории реальных инцидентов (storytelling)",
        "Чеклисты безопасности для бизнеса",
        "Контент для начинающих SOC-аналитиков",
        "Карусели: топ-инструменты Blue Team",
    ],
    "Red Team / Offensive Security": [
        "Быстрые демо-видео атак (этичных)",
        "Серии «Взломай это за 5 минут» (с разрешением)",
        "Мемы и юмор про пентест",
        "Контент про Bug Bounty заработок",
        "Карусели: шпаргалки по инструментам",
    ],
    "Machine Learning & AI": [
        "Простые объяснения нейросетей для новичков",
        "Практические проекты на Python с результатом за 15 минут",
        "Сравнения AI-сервисов (ChatGPT vs Claude vs Gemini)",
        "Контент про AI в кибербезопасности",
        "Тренды AI на русском языке",
    ],
    "AliExpress - Гаджеты": [
        "Распаковки и обзоры с ценами (бюджетный сегмент)",
        "«Топ-5 гаджетов до $20» — формат списка",
        "Видео «Работает или нет?» — тестирование гаджетов",
        "Сравнения аналогов: AliExpress vs оригинал",
        "Сборка домашней лаборатории за минимальный бюджет",
    ],
}


@dataclass(frozen=True, slots=True)
class CompetitorProfile:
    name: str
    platform: str
    followers: int
    strength: str
    weakness: str
    content_type: str


@dataclass(frozen=True, slots=True)
class NicheBenchmark:
    pillar: str
    avg_engagement_rate: float
    avg_post_frequency: float
    avg_follower_growth: float
    avg_video_views_rate: float
    hashtag_reach_rate: float

    def to_dict(self) -> dict[str, str | float]:
        return {
            "pillar": self.pillar,
            "avg_engagement_rate": self.avg_engagement_rate,
            "avg_post_frequency": self.avg_post_frequency,
            "avg_follower_growth": self.avg_follower_growth,
            "avg_video_views_rate": self.avg_video_views_rate,
            "hashtag_reach_rate": self.hashtag_reach_rate,
        }


@dataclass(frozen=True, slots=True)
class GapAnalysis:
    pillar: str
    gaps: list[str]
    competitors: list[CompetitorProfile]
    benchmark: NicheBenchmark
    recommendations: list[str] = field(default_factory=list)


def get_benchmark(pillar_name: str) -> NicheBenchmark:
    data = NICHE_BENCHMARKS.get(pillar_name, {})
    return NicheBenchmark(
        pillar=pillar_name,
        avg_engagement_rate=data.get("avg_engagement_rate", 2.0),
        avg_post_frequency=data.get("avg_post_frequency", 5.0),
        avg_follower_growth=data.get("avg_follower_growth", 2.0),
        avg_video_views_rate=data.get("avg_video_views_rate", 7.0),
        hashtag_reach_rate=data.get("hashtag_reach_rate", 10.0),
    )


def get_competitors(pillar_name: str) -> list[CompetitorProfile]:
    raw = COMPETITOR_PROFILES.get(pillar_name, [])
    return [
        CompetitorProfile(
            name=str(c["name"]),
            platform=str(c["platform"]),
            followers=int(c["followers"]),
            strength=str(c["strength"]),
            weakness=str(c["weakness"]),
            content_type=str(c["content_type"]),
        )
        for c in raw
    ]


def get_content_gaps(pillar_name: str) -> list[str]:
    return list(CONTENT_GAPS.get(pillar_name, []))


def _generate_recommendations(
    pillar: ContentPillar,
    gaps: list[str],
    competitors: list[CompetitorProfile],
) -> list[str]:
    recs: list[str] = []
    weaknesses = [c.weakness for c in competitors]

    if any("коротк" in w.lower() for w in weaknesses):
        recs.append(
            "Делай короткие видео (Reels, TikTok) — конкуренты упускают этот формат"
        )
    if any("русск" in g.lower() for g in gaps):
        recs.append("Создавай контент на русском языке — рынок недообслужен")
    if pillar.product == "referral":
        recs.append(
            "Фокусируйся на обзорах бюджетных гаджетов — конкуренты продают дорого"
        )
    else:
        recs.append(
            "Комбинируй образовательный контент с развлекательным (edutainment)"
        )

    recs.append("Используй серии и челленджи для удержания аудитории")
    recs.append("Публикуй карусели с чеклистами — высокий save rate")

    return recs


def analyze_niche(pillar_name: str) -> GapAnalysis:
    pillar = None
    for p in PILLARS:
        if p.name == pillar_name:
            pillar = p
            break
    if pillar is None:
        pillar = PILLARS[0]

    benchmark = get_benchmark(pillar.name)
    competitors = get_competitors(pillar.name)
    gaps = get_content_gaps(pillar.name)
    recs = _generate_recommendations(pillar, gaps, competitors)

    return GapAnalysis(
        pillar=pillar.name,
        gaps=gaps,
        competitors=competitors,
        benchmark=benchmark,
        recommendations=recs,
    )


def analyze_all_niches() -> list[GapAnalysis]:
    return [analyze_niche(p.name) for p in PILLARS]


def export_analysis_json(analyses: list[GapAnalysis], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "pillar": a.pillar,
            "benchmark": a.benchmark.to_dict(),
            "competitors": [
                {
                    "name": c.name,
                    "platform": c.platform,
                    "followers": c.followers,
                    "strength": c.strength,
                    "weakness": c.weakness,
                    "content_type": c.content_type,
                }
                for c in a.competitors
            ],
            "content_gaps": a.gaps,
            "recommendations": a.recommendations,
        }
        for a in analyses
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_analysis_txt(analyses: list[GapAnalysis], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for i, a in enumerate(analyses, 1):
        lines.append(f"{'=' * 60}")
        lines.append(f"АНАЛИЗ #{i}: {a.pillar}")
        lines.append(f"{'=' * 60}")

        lines.append("\n  Бенчмарки ниши:")
        lines.append(f"    Engagement Rate: {a.benchmark.avg_engagement_rate}%")
        lines.append(f"    Частота постинга: {a.benchmark.avg_post_frequency}/нед")
        lines.append(f"    Рост подписчиков: {a.benchmark.avg_follower_growth}%/мес")
        lines.append(f"    Просмотры видео: {a.benchmark.avg_video_views_rate}%")
        lines.append(f"    Охват хештегов: {a.benchmark.hashtag_reach_rate}%")

        lines.append(f"\n  Конкуренты ({len(a.competitors)}):")
        for c in a.competitors:
            lines.append(f"    {c.name} ({c.platform}, {c.followers:,} подп.)")
            lines.append(f"      +: {c.strength}")
            lines.append(f"      -: {c.weakness}")

        lines.append(f"\n  Контент-гэпы ({len(a.gaps)}):")
        lines.extend(f"    - {g}" for g in a.gaps)

        lines.append(f"\n  Рекомендации ({len(a.recommendations)}):")
        lines.extend(f"    -> {r}" for r in a.recommendations)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def analysis_summary(analyses: list[GapAnalysis]) -> str:
    total_competitors = sum(len(a.competitors) for a in analyses)
    total_gaps = sum(len(a.gaps) for a in analyses)
    total_recs = sum(len(a.recommendations) for a in analyses)

    lines: list[str] = [
        f"Анализ конкурентов: {len(analyses)} ниш",
        f"Всего конкурентов: {total_competitors}",
        f"Контент-гэпов: {total_gaps}",
        f"Рекомендаций: {total_recs}",
        "\nПо нишам:",
    ]
    lines.extend(
        f"  {a.pillar}: {len(a.competitors)} конк., {len(a.gaps)} гэпов"
        for a in analyses
    )
    return "\n".join(lines)
