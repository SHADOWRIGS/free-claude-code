"""Conversion funnel — stage-specific content for course and referral sales.

Maps each pillar through TOFU→MOFU→BOFU funnel stages and generates
posts, lead magnets, and CTA sequences designed to convert followers
into course buyers and referral link clickers.

TOFU = Top of Funnel (awareness, reach)
MOFU = Middle of Funnel (interest, nurture)
BOFU = Bottom of Funnel (decision, purchase)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from smm.content_pillars import PILLARS

FUNNEL_STAGES = ("tofu", "mofu", "bofu")

STAGE_LABELS: dict[str, str] = {
    "tofu": "Осведомлённость (TOFU)",
    "mofu": "Интерес (MOFU)",
    "bofu": "Конверсия (BOFU)",
}

PILLAR_FUNNELS: dict[str, dict[str, dict[str, list[str]]]] = {
    "Cyber Security & Ethical Hacking": {
        "tofu": {
            "hooks": [
                "5 вещей, которые хакеры знают о тебе прямо сейчас",
                "Проверь: твой пароль уже в базе утечек?",
                "Топ-3 инструмента, которые используют пентестеры каждый день",
                "Что видит хакер, когда сканирует твою сеть",
                "90% компаний уязвимы к ЭТОЙ атаке",
            ],
            "formats": ["reel", "carousel", "short_video"],
            "cta": ["Подпишись, чтобы не пропустить разборы"],
        },
        "mofu": {
            "hooks": [
                "Бесплатный чеклист: аудит безопасности за 30 минут",
                "Пошаговый разбор: как я нашёл уязвимость на $5000",
                "Мини-гайд: настрой VPN + firewall за 15 минут",
                "Разбираем реальный кейс взлома (легально!)",
                "Сравнение Kali vs Parrot — что выбрать новичку?",
            ],
            "formats": ["carousel", "tutorial", "long_video"],
            "cta": ["Скачай бесплатный гайд в описании"],
        },
        "bofu": {
            "hooks": [
                "Готов стать пентестером? Вот твой план на 90 дней",
                "Мои студенты нашли первый баг за 2 недели — вот как",
                "Отзыв ученика: от нуля до Bug Bounty за 3 месяца",
                "Последние 5 мест на курс — старт в понедельник",
                "Бонус для подписчиков: скидка 30% до конца недели",
            ],
            "formats": ["story", "reel", "static_post"],
            "cta": ["Запишись на курс — ссылка в био"],
        },
    },
    "Blue Team / Defensive Security": {
        "tofu": {
            "hooks": [
                "Что делает SOC-аналитик каждый день (и почему это круто)",
                "3 бесплатных инструмента для мониторинга безопасности",
                "Как выглядит реальная кибератака изнутри SIEM",
                "Blue Team vs Red Team — в чём разница?",
                "Топ-5 логов, которые спасут твою сеть",
            ],
            "formats": ["carousel", "reel", "short_video"],
            "cta": ["Сохрани себе этот чеклист"],
        },
        "mofu": {
            "hooks": [
                "Бесплатный шаблон: план реагирования на инциденты",
                "Настраиваем SIEM за 1 час — пошаговый гайд",
                "Как читать логи как профи: 5 паттернов атак",
                "Мини-курс: основы Threat Hunting бесплатно",
                "Сравнение: Splunk vs ELK для малого бизнеса",
            ],
            "formats": ["tutorial", "carousel", "long_video"],
            "cta": ["Забери бесплатный шаблон IR-плана"],
        },
        "bofu": {
            "hooks": [
                "Курс Blue Team: от логов до Threat Intelligence",
                "Отзыв: «Устроился SOC-аналитиком через 4 месяца»",
                "Программа курса — что ты будешь уметь через 3 месяца",
                "Групповой старт через 7 дней — присоединяйся",
                "Карьера в Blue Team: зарплаты от 150К в месяц",
            ],
            "formats": ["story", "static_post", "reel"],
            "cta": ["Записывайся на курс — ссылка в описании"],
        },
    },
    "Red Team / Offensive Security": {
        "tofu": {
            "hooks": [
                "Взламываю WiFi за 3 минуты (легально!) 🔓",
                "Топ-5 инструментов Red Team, о которых ты не знал",
                "Как я обошёл двухфакторку (в рамках пентеста)",
                "OSINT-разведка: что можно узнать по номеру телефона",
                "Social Engineering: как хакеры манипулируют людьми",
            ],
            "formats": ["reel", "short_video", "carousel"],
            "cta": ["Подпишись — каждый день новый хак"],
        },
        "mofu": {
            "hooks": [
                "Бесплатный мини-курс: OSINT для начинающих",
                "Пошаговый разбор: пентест веб-приложения от А до Я",
                "Cheatsheet: 50 команд для пентестера",
                "Практика на HackTheBox: разбор машины для новичков",
                "Как составить отчёт по пентесту (шаблон внутри)",
            ],
            "formats": ["tutorial", "long_video", "carousel"],
            "cta": ["Скачай чеклист пентестера бесплатно"],
        },
        "bofu": {
            "hooks": [
                "Полный курс Red Team: от разведки до пост-эксплуатации",
                "Ученик получил первый заказ на пентест через месяц",
                "Демо урока: ломаем Active Directory пошагово",
                "Скидка 40% для подписчиков — только 3 дня",
                "Стань пентестером: пошаговая программа на 6 месяцев",
            ],
            "formats": ["story", "reel", "static_post"],
            "cta": ["Жми на ссылку в био — запишись на курс"],
        },
    },
    "Machine Learning & AI": {
        "tofu": {
            "hooks": [
                "ChatGPT vs Claude vs Gemini — кто лучше кодит?",
                "Автоматизировал работу за 10 минут с помощью AI",
                "5 нейросетей, которые заменят тебе целый отдел",
                "AI написал эту подпись (или нет? 🤔)",
                "Как AI зарабатывает деньги прямо сейчас: 5 способов",
            ],
            "formats": ["reel", "short_video", "carousel"],
            "cta": ["Подпишись — AI-лайфхаки каждый день"],
        },
        "mofu": {
            "hooks": [
                "Бесплатный гайд: первая нейросеть на Python за 1 час",
                "Промпт-инжиниринг: 10 техник, которые изменят всё",
                "Строим RAG-систему с нуля — пошаговый туториал",
                "AI для бизнеса: автоматизируем рутину за вечер",
                "Fine-tuning модели: когда и зачем это нужно",
            ],
            "formats": ["tutorial", "long_video", "carousel"],
            "cta": ["Забери бесплатный шаблон промптов"],
        },
        "bofu": {
            "hooks": [
                "Курс ML & AI: от нуля до своего AI-продукта",
                "Отзыв: «Сделал AI-бота и продал за $2000»",
                "Программа курса: Python → ML → LLM → деплой",
                "Последние места — старт группы в понедельник",
                "Карьера в AI: вакансии от 200К — курс откроет двери",
            ],
            "formats": ["story", "static_post", "reel"],
            "cta": ["Запишись на курс — ссылка в описании"],
        },
    },
    "AliExpress - Гаджеты": {
        "tofu": {
            "hooks": [
                "Гаджет за $15, который пугает даже хакеров 😱",
                "Топ-5 устройств с AliExpress для кибербезопасности",
                "WiFi Pineapple за копейки? Проверяем аналог!",
                "Распаковка: 10 хакерских гаджетов с AliExpress",
                "Этот USB-кабель крадёт данные (и стоит $8)",
            ],
            "formats": ["reel", "short_video", "carousel"],
            "cta": ["Подпишись — распаковки каждую неделю"],
        },
        "mofu": {
            "hooks": [
                "Обзор: ESP32 для пентеста — настройка за 10 минут",
                "Сравниваю 5 SDR-приёмников с AliExpress",
                "Полный гайд: собираем набор пентестера за $100",
                "Тест Flipper Zero альтернатив: что работает?",
                "WiFi-адаптеры для Kali: какой купить в 2024?",
            ],
            "formats": ["tutorial", "long_video", "carousel"],
            "cta": ["Все ссылки на гаджеты — в описании"],
        },
        "bofu": {
            "hooks": [
                "Мой ТОП-10 покупок с AliExpress за год (со ссылками)",
                "Набор пентестера за $50 vs $500 — разница есть?",
                "Скидки на хакерские гаджеты — успей до конца распродажи",
                "Промокод для подписчиков: -15% на любой гаджет",
                "Собрал подборку — 20 гаджетов со скидкой прямо сейчас",
            ],
            "formats": ["story", "carousel", "reel"],
            "cta": ["Переходи по ссылке — все гаджеты со скидкой"],
        },
    },
}

LEAD_MAGNETS: dict[str, list[dict[str, str]]] = {
    "Cyber Security & Ethical Hacking": [
        {
            "name": "Чеклист: аудит безопасности за 30 минут",
            "type": "pdf",
            "description": "Пошаговый чеклист для самостоятельного аудита",
        },
        {
            "name": "ТОП-20 инструментов пентестера 2024",
            "type": "pdf",
            "description": "Подборка лучших бесплатных инструментов",
        },
    ],
    "Blue Team / Defensive Security": [
        {
            "name": "Шаблон плана реагирования на инциденты",
            "type": "docx",
            "description": "Готовый IR-план для малого бизнеса",
        },
        {
            "name": "Чеклист настройки SIEM",
            "type": "pdf",
            "description": "Пошаговая настройка мониторинга",
        },
    ],
    "Red Team / Offensive Security": [
        {
            "name": "Cheatsheet пентестера: 100 команд",
            "type": "pdf",
            "description": "Шпаргалка по основным командам для пентеста",
        },
        {
            "name": "Шаблон отчёта по пентесту",
            "type": "docx",
            "description": "Профессиональный шаблон отчёта",
        },
    ],
    "Machine Learning & AI": [
        {
            "name": "10 промптов, которые изменят твою работу",
            "type": "pdf",
            "description": "Шаблоны промптов для продуктивности",
        },
        {
            "name": "Roadmap: от нуля до ML-инженера",
            "type": "pdf",
            "description": "Пошаговый план обучения на 6 месяцев",
        },
    ],
    "AliExpress - Гаджеты": [
        {
            "name": "Подборка: 30 гаджетов для хакера с AliExpress",
            "type": "pdf",
            "description": "Каталог с прямыми ссылками и ценами",
        },
        {
            "name": "Гайд: собираем лабораторию пентестера за $100",
            "type": "pdf",
            "description": "Минимальный набор для старта",
        },
    ],
}


@dataclass(frozen=True, slots=True)
class FunnelPost:
    pillar: str
    stage: str
    stage_label: str
    hook: str
    formats: list[str]
    cta: str


@dataclass(frozen=True, slots=True)
class LeadMagnet:
    pillar: str
    name: str
    magnet_type: str
    description: str


@dataclass(frozen=True, slots=True)
class PillarFunnel:
    pillar: str
    tofu_posts: list[FunnelPost]
    mofu_posts: list[FunnelPost]
    bofu_posts: list[FunnelPost]
    lead_magnets: list[LeadMagnet]
    total_posts: int


def generate_funnel_posts(pillar_name: str) -> list[FunnelPost]:
    funnel_data = PILLAR_FUNNELS.get(pillar_name)
    if funnel_data is None:
        return []

    posts: list[FunnelPost] = []
    for stage in FUNNEL_STAGES:
        stage_data = funnel_data[stage]
        cta = stage_data["cta"][0]
        posts.extend(
            FunnelPost(
                pillar=pillar_name,
                stage=stage,
                stage_label=STAGE_LABELS[stage],
                hook=hook,
                formats=stage_data["formats"],
                cta=cta,
            )
            for hook in stage_data["hooks"]
        )
    return posts


def generate_lead_magnets(pillar_name: str) -> list[LeadMagnet]:
    magnets_data = LEAD_MAGNETS.get(pillar_name, [])
    return [
        LeadMagnet(
            pillar=pillar_name,
            name=m["name"],
            magnet_type=m["type"],
            description=m["description"],
        )
        for m in magnets_data
    ]


def generate_pillar_funnel(pillar_name: str) -> PillarFunnel:
    posts = generate_funnel_posts(pillar_name)
    magnets = generate_lead_magnets(pillar_name)
    tofu = [p for p in posts if p.stage == "tofu"]
    mofu = [p for p in posts if p.stage == "mofu"]
    bofu = [p for p in posts if p.stage == "bofu"]
    return PillarFunnel(
        pillar=pillar_name,
        tofu_posts=tofu,
        mofu_posts=mofu,
        bofu_posts=bofu,
        lead_magnets=magnets,
        total_posts=len(posts),
    )


def generate_all_funnels() -> list[PillarFunnel]:
    return [generate_pillar_funnel(p.name) for p in PILLARS]


def export_funnel_json(funnels: list[PillarFunnel], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "pillar": f.pillar,
            "tofu": [
                {"hook": p.hook, "formats": p.formats, "cta": p.cta}
                for p in f.tofu_posts
            ],
            "mofu": [
                {"hook": p.hook, "formats": p.formats, "cta": p.cta}
                for p in f.mofu_posts
            ],
            "bofu": [
                {"hook": p.hook, "formats": p.formats, "cta": p.cta}
                for p in f.bofu_posts
            ],
            "lead_magnets": [
                {"name": m.name, "type": m.magnet_type, "description": m.description}
                for m in f.lead_magnets
            ],
            "total_posts": f.total_posts,
        }
        for f in funnels
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_funnel_txt(funnels: list[PillarFunnel], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "КОНВЕРСИОННАЯ ВОРОНКА — SMM",
        "=" * 60,
    ]

    for f in funnels:
        lines.append(f"\n{'─' * 50}")
        lines.append(f"📌 {f.pillar} ({f.total_posts} постов)")
        lines.append(f"{'─' * 50}")

        for label, posts in [
            ("🔝 TOFU — Осведомлённость", f.tofu_posts),
            ("🔄 MOFU — Интерес", f.mofu_posts),
            ("💰 BOFU — Конверсия", f.bofu_posts),
        ]:
            lines.append(f"\n  {label}")
            for p in posts:
                lines.append(f"    • {p.hook}")
                lines.append(f"      CTA: {p.cta}")
                lines.append(f"      Форматы: {', '.join(p.formats)}")

        if f.lead_magnets:
            lines.append("\n  🎁 Лид-магниты:")
            for m in f.lead_magnets:
                lines.append(f"    • {m.name} ({m.magnet_type})")
                lines.append(f"      {m.description}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def funnel_summary(funnels: list[PillarFunnel]) -> str:
    total = sum(f.total_posts for f in funnels)
    magnets = sum(len(f.lead_magnets) for f in funnels)
    lines: list[str] = [
        f"Конверсионная воронка: {total} постов, {magnets} лид-магнитов",
        f"Направлений: {len(funnels)}",
    ]
    lines.extend(
        f"  {f.pillar}: TOFU={len(f.tofu_posts)} "
        f"MOFU={len(f.mofu_posts)} BOFU={len(f.bofu_posts)} "
        f"лиды={len(f.lead_magnets)}"
        for f in funnels
    )
    return "\n".join(lines)
