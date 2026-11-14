"""UGC templates — user-generated content frameworks for social proof.

Generates templates that students and customers can fill in to create
testimonials, success stories, before/after posts, and case studies.
These serve as social proof to drive course sales and referral clicks.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from smm.content_pillars import PILLARS

UGC_TYPES = ("testimonial", "before_after", "case_study", "quick_win", "challenge")

UGC_TYPE_LABELS: dict[str, str] = {
    "testimonial": "Отзыв",
    "before_after": "До / После",
    "case_study": "Кейс",
    "quick_win": "Быстрая победа",
    "challenge": "Челлендж-результат",
}


@dataclass(frozen=True, slots=True)
class UGCTemplate:
    pillar: str
    ugc_type: str
    type_label: str
    title: str
    prompt_text: str
    example: str
    hashtags: list[str]
    cta: str


PILLAR_UGC: dict[str, dict[str, list[dict[str, str | list[str]]]]] = {
    "Cyber Security & Ethical Hacking": {
        "testimonial": [
            {
                "title": "Отзыв о курсе кибербезопасности",
                "prompt": "Расскажи, как курс изменил твою карьеру или навыки. "
                "Что ты умел ДО и что умеешь ПОСЛЕ?",
                "example": "До курса я не знал, что такое Nmap. Сейчас я провожу "
                "аудит безопасности для трёх компаний. Спасибо @ShadowRigs!",
                "hashtags": [
                    "#кибербезопасность",
                    "#пентест",
                    "#отзыв",
                    "#этичныйхакинг",
                ],
                "cta": "Хочешь так же? Ссылка на курс в био",
            },
        ],
        "before_after": [
            {
                "title": "До/После: путь в кибербезопасности",
                "prompt": "Покажи свой прогресс: скриншот первого сканирования "
                "vs текущий уровень. Что изменилось?",
                "example": "ДО: «Что такое порт 443?»\n"
                "ПОСЛЕ: Провожу полный пентест веб-приложений",
                "hashtags": ["#доипосле", "#кибербез", "#прогресс", "#обучение"],
                "cta": "Начни свой путь — ссылка на курс в описании",
            },
        ],
        "case_study": [
            {
                "title": "Кейс: найденная уязвимость",
                "prompt": "Расскажи о реальной уязвимости, которую ты нашёл "
                "после обучения (без NDA-деталей).",
                "example": "Нашёл XSS на сайте крупного магазина. "
                "Получил благодарность и $500 через Bug Bounty.",
                "hashtags": ["#bugbounty", "#кейс", "#пентест", "#уязвимость"],
                "cta": "Найди свою первую уязвимость — курс в био",
            },
        ],
        "quick_win": [
            {
                "title": "Быстрая победа: первый день курса",
                "prompt": "Что ты узнал/сделал в первый день обучения?",
                "example": "День 1: научился сканировать сеть и нашёл "
                "3 открытых порта на своём роутере 😱",
                "hashtags": ["#деньпервый", "#кибербез", "#быстрыйстарт"],
                "cta": "Твой первый день — завтра. Ссылка в био",
            },
        ],
        "challenge": [
            {
                "title": "Результат 30-дневного челленджа",
                "prompt": "Расскажи, чего достиг за 30 дней обучения кибербезопасности",
                "example": "30 дней назад я не знал Linux. Сегодня решил 10 машин на HackTheBox!",
                "hashtags": ["#30дней", "#челлендж", "#hackthebox", "#результат"],
                "cta": "Прими челлендж — начни с курса в описании",
            },
        ],
    },
    "Blue Team / Defensive Security": {
        "testimonial": [
            {
                "title": "Отзыв о курсе Blue Team",
                "prompt": "Как курс по защите помог тебе в работе/карьере?",
                "example": "После курса настроил SIEM для своей компании. "
                "Руководство оценило — повысили зарплату на 30%!",
                "hashtags": ["#blueteam", "#soc", "#отзыв", "#карьера"],
                "cta": "Построй карьеру в Blue Team — ссылка в био",
            },
        ],
        "before_after": [
            {
                "title": "До/После: навыки защиты",
                "prompt": "Покажи дашборд SIEM до и после обучения",
                "example": "ДО: Пустой дашборд, ноль алертов\n"
                "ПОСЛЕ: 50+ правил, 99.9% coverage",
                "hashtags": ["#blueteam", "#siem", "#доипосле", "#мониторинг"],
                "cta": "Настрой свой SOC — курс в описании",
            },
        ],
        "case_study": [
            {
                "title": "Кейс: обнаруженная атака",
                "prompt": "Расскажи, как обнаружил и предотвратил реальную атаку",
                "example": "Поймал фишинг-кампанию на 200 сотрудников "
                "благодаря правилам, которые настроил после курса.",
                "hashtags": ["#incidentresponse", "#кейс", "#защита"],
                "cta": "Стань защитником — курс в био",
            },
        ],
        "quick_win": [
            {
                "title": "Быстрая победа: первый алерт",
                "prompt": "Какой первый алерт ты настроил после начала обучения?",
                "example": "Настроил алерт на brute-force SSH за 20 минут. "
                "Уже на следующий день поймал 3 попытки!",
                "hashtags": ["#firstalert", "#blueteam", "#быстрыйрезультат"],
                "cta": "Настрой первый алерт сегодня — курс в описании",
            },
        ],
        "challenge": [
            {
                "title": "Результат: неделя Threat Hunting",
                "prompt": "Что ты нашёл за неделю Threat Hunting?",
                "example": "7 дней охоты за угрозами: нашёл 2 подозрительных процесса "
                "и 1 C2-канал в логах!",
                "hashtags": ["#threathunting", "#blueteam", "#результат"],
                "cta": "Начни охоту — курс в описании",
            },
        ],
    },
    "Red Team / Offensive Security": {
        "testimonial": [
            {
                "title": "Отзыв о курсе Red Team",
                "prompt": "Как курс помог тебе в пентесте или Bug Bounty?",
                "example": "За 3 месяца после курса заработал $3000 на Bug Bounty. "
                "Лучшая инвестиция в карьеру!",
                "hashtags": ["#redteam", "#bugbounty", "#отзыв", "#пентест"],
                "cta": "Начни зарабатывать на баг-баунти — курс в био",
            },
        ],
        "before_after": [
            {
                "title": "До/После: навыки атаки",
                "prompt": "Покажи прогресс на HTB/THM до и после курса",
                "example": "ДО: 0 решённых машин\n"
                "ПОСЛЕ: 25 машин, рейтинг Hacker на HTB",
                "hashtags": ["#hackthebox", "#redteam", "#прогресс"],
                "cta": "Начни решать машины — курс в описании",
            },
        ],
        "case_study": [
            {
                "title": "Кейс: успешный пентест",
                "prompt": "Расскажи о своём лучшем пентесте (без NDA-деталей)",
                "example": "Провёл пентест для стартапа. Нашёл RCE через "
                "десериализацию. Клиент доволен, я тоже!",
                "hashtags": ["#пентест", "#rce", "#кейс", "#redteam"],
                "cta": "Стань пентестером — курс в био",
            },
        ],
        "quick_win": [
            {
                "title": "Первый баг за неделю",
                "prompt": "Какой первый баг ты нашёл после начала обучения?",
                "example": "Неделя 1: нашёл открытый .git на продакшн-сервере "
                "компании из Fortune 500!",
                "hashtags": ["#firstbug", "#bugbounty", "#быстрыйрезультат"],
                "cta": "Найди свой первый баг — курс в описании",
            },
        ],
        "challenge": [
            {
                "title": "CTF-марафон: результаты",
                "prompt": "Как ты выступил на CTF после обучения?",
                "example": "Команда из 3 студентов курса — 5-е место на национальном CTF!",
                "hashtags": ["#ctf", "#redteam", "#результат", "#команда"],
                "cta": "Собери команду — начни с курса в описании",
            },
        ],
    },
    "Machine Learning & AI": {
        "testimonial": [
            {
                "title": "Отзыв о курсе ML & AI",
                "prompt": "Как курс помог тебе в работе с AI?",
                "example": "Автоматизировал отчётность с помощью LLM. "
                "Экономлю 10 часов в неделю благодаря курсу!",
                "hashtags": ["#machinelearning", "#ai", "#отзыв", "#автоматизация"],
                "cta": "Научись автоматизировать — курс в био",
            },
        ],
        "before_after": [
            {
                "title": "До/После: AI-проекты",
                "prompt": "Покажи свой первый и текущий AI-проект",
                "example": "ДО: print('Hello World')\n"
                "ПОСЛЕ: Свой RAG-бот, обученный на 10K документов",
                "hashtags": ["#ai", "#ml", "#доипосле", "#проект"],
                "cta": "Создай свой AI-проект — курс в описании",
            },
        ],
        "case_study": [
            {
                "title": "Кейс: AI в бизнесе",
                "prompt": "Расскажи, как применил AI в реальном проекте",
                "example": "Сделал чат-бота для службы поддержки. "
                "Снизил нагрузку на операторов на 40%.",
                "hashtags": ["#aiбизнес", "#чатбот", "#кейс", "#ml"],
                "cta": "Внедри AI в бизнес — курс в био",
            },
        ],
        "quick_win": [
            {
                "title": "Первый AI-проект за выходные",
                "prompt": "Что ты создал за первые выходные обучения?",
                "example": "Суббота: установил Python. Воскресенье: "
                "мой бот генерирует посты для соцсетей!",
                "hashtags": ["#aiзавыходные", "#первыйпроект", "#ml"],
                "cta": "Создай проект за выходные — курс в описании",
            },
        ],
        "challenge": [
            {
                "title": "30-дневный AI-челлендж",
                "prompt": "Покажи 30 AI-проектов за 30 дней",
                "example": "30 дней — 30 мини-проектов на Python: от классификатора "
                "до генератора музыки. Каждый день новый навык!",
                "hashtags": ["#30дней", "#aichallenge", "#ml", "#python"],
                "cta": "Прими AI-челлендж — курс в описании",
            },
        ],
    },
    "AliExpress - Гаджеты": {
        "testimonial": [
            {
                "title": "Отзыв о гаджете",
                "prompt": "Расскажи о лучшей покупке с AliExpress по нашей ссылке",
                "example": "Купил WiFi-адаптер за $12 по ссылке @ShadowRigs. "
                "Работает в Kali из коробки! Рекомендую.",
                "hashtags": ["#aliexpress", "#обзор", "#гаджет", "#хакинг"],
                "cta": "Купи со скидкой — ссылка в описании",
            },
        ],
        "before_after": [
            {
                "title": "До/После: лаборатория",
                "prompt": "Покажи рабочее место до и после покупки гаджетов",
                "example": "ДО: Ноутбук и всё\n"
                "ПОСЛЕ: Полная лаборатория за $150 с AliExpress",
                "hashtags": ["#лаборатория", "#доипосле", "#гаджеты", "#бюджет"],
                "cta": "Собери лабораторию — все ссылки в описании",
            },
        ],
        "case_study": [
            {
                "title": "Кейс: тест гаджета",
                "prompt": "Протестируй гаджет и расскажи о результатах",
                "example": "Тестирую ESP32 с AliExpress: WiFi-деаутентификация "
                "работает, Bluetooth-сниффинг — тоже. За $8!",
                "hashtags": ["#тест", "#esp32", "#aliexpress", "#гаджеты"],
                "cta": "Купи и протестируй — ссылка в описании",
            },
        ],
        "quick_win": [
            {
                "title": "Распаковка дня",
                "prompt": "Сними 30-секундное видео распаковки гаджета",
                "example": "Распаковка: USB Rubber Ducky аналог за $5. "
                "Подключил — работает! 🦆",
                "hashtags": ["#распаковка", "#unboxing", "#aliexpress"],
                "cta": "Закажи такой же — ссылка в био",
            },
        ],
        "challenge": [
            {
                "title": "Набор пентестера за $50",
                "prompt": "Собери набор гаджетов с AliExpress за минимальный бюджет",
                "example": "Собрал набор пентестера за $47: WiFi-адаптер, "
                "ESP32, USB Rubber Ducky, SDR-приёмник. Всё работает!",
                "hashtags": ["#бюджет", "#пентест", "#aliexpress", "#набор"],
                "cta": "Все ссылки на гаджеты — в описании",
            },
        ],
    },
}


def generate_ugc_templates(pillar_name: str) -> list[UGCTemplate]:
    pillar_data = PILLAR_UGC.get(pillar_name)
    if pillar_data is None:
        return []

    templates: list[UGCTemplate] = []
    for ugc_type in UGC_TYPES:
        items = pillar_data.get(ugc_type, [])
        for item in items:
            hashtags = item.get("hashtags", [])
            assert isinstance(hashtags, list)
            templates.append(
                UGCTemplate(
                    pillar=pillar_name,
                    ugc_type=ugc_type,
                    type_label=UGC_TYPE_LABELS[ugc_type],
                    title=str(item["title"]),
                    prompt_text=str(item["prompt"]),
                    example=str(item["example"]),
                    hashtags=hashtags,
                    cta=str(item["cta"]),
                )
            )
    return templates


def generate_all_ugc_templates() -> list[UGCTemplate]:
    result: list[UGCTemplate] = []
    for pillar in PILLARS:
        result.extend(generate_ugc_templates(pillar.name))
    return result


def export_ugc_json(templates: list[UGCTemplate], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "pillar": t.pillar,
            "type": t.ugc_type,
            "type_label": t.type_label,
            "title": t.title,
            "prompt": t.prompt_text,
            "example": t.example,
            "hashtags": t.hashtags,
            "cta": t.cta,
        }
        for t in templates
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_ugc_txt(templates: list[UGCTemplate], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "UGC-ШАБЛОНЫ — ПОЛЬЗОВАТЕЛЬСКИЙ КОНТЕНТ",
        "=" * 60,
    ]

    current_pillar = ""
    for t in templates:
        if t.pillar != current_pillar:
            current_pillar = t.pillar
            lines.append(f"\n{'─' * 50}")
            lines.append(f"📌 {current_pillar}")
            lines.append(f"{'─' * 50}")

        lines.append(f"\n  [{t.type_label}] {t.title}")
        lines.append(f"  Задание: {t.prompt_text}")
        lines.append(f"  Пример: {t.example}")
        lines.append(f"  Хештеги: {' '.join(t.hashtags)}")
        lines.append(f"  CTA: {t.cta}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def ugc_summary(templates: list[UGCTemplate]) -> str:
    by_pillar: dict[str, int] = {}
    by_type: dict[str, int] = {}
    for t in templates:
        by_pillar[t.pillar] = by_pillar.get(t.pillar, 0) + 1
        by_type[t.type_label] = by_type.get(t.type_label, 0) + 1

    lines: list[str] = [
        f"UGC-шаблоны: {len(templates)} шт.",
        f"Направлений: {len(by_pillar)}",
    ]
    lines.extend(f"  {name}: {count}" for name, count in by_pillar.items())
    lines.append("\nПо типам:")
    lines.extend(f"  {name}: {count}" for name, count in by_type.items())
    return "\n".join(lines)
