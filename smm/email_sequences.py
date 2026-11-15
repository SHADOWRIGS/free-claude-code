"""Email nurture sequences — automated drip campaigns per pillar.

Generates ready-to-use email sequences for each course pillar:
welcome series, lead nurture, cart abandonment, and post-purchase
upsell. Each email has subject, preview text, body outline, and CTA.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from smm.content_pillars import PILLARS

SEQUENCE_TYPES = ("welcome", "nurture", "abandon_cart", "upsell")

SEQUENCE_LABELS: dict[str, str] = {
    "welcome": "Приветственная серия",
    "nurture": "Прогрев лида",
    "abandon_cart": "Брошенная корзина",
    "upsell": "Допродажа",
}


@dataclass(frozen=True, slots=True)
class Email:
    pillar: str
    sequence_type: str
    sequence_label: str
    day: int
    subject: str
    preview: str
    body_outline: str
    cta: str


PILLAR_SEQUENCES: dict[str, dict[str, list[dict[str, str]]]] = {
    "Cyber Security & Ethical Hacking": {
        "welcome": [
            {
                "day": "0",
                "subject": "Добро пожаловать в мир кибербезопасности!",
                "preview": "Ты сделал первый шаг к профессии пентестера",
                "body": "Приветствие, что ждёт в рассылке, ссылка на бесплатный PDF '5 первых шагов в пентесте'",
                "cta": "Скачай бесплатный PDF",
            },
            {
                "day": "1",
                "subject": "Как выглядит день этичного хакера",
                "preview": "Реальный распорядок дня: от разведки до отчёта",
                "body": "Личный опыт, день пентестера пошагово, какие инструменты использую каждый день",
                "cta": "Подробнее в блоге",
            },
            {
                "day": "3",
                "subject": "Ошибка, которую делают 90% новичков в кибербезе",
                "preview": "И как её избежать одним действием",
                "body": "Типичная ошибка — учить всё подряд. Фокус на одном направлении. Как курс решает эту проблему",
                "cta": "Узнай программу курса",
            },
        ],
        "nurture": [
            {
                "day": "0",
                "subject": "Тебе понравился гайд? Вот следующий шаг",
                "preview": "Бесплатный мини-курс из 3 уроков",
                "body": "Напоминание о скачанном лид-магните, предложение мини-курса, социальное доказательство (X студентов)",
                "cta": "Начни мини-курс бесплатно",
            },
            {
                "day": "3",
                "subject": "Как Алексей за 4 месяца стал джуниор-пентестером",
                "preview": "История реального студента",
                "body": "Кейс студента: откуда пришёл, что изучал, где работает сейчас. Отзыв",
                "cta": "Хочу такой же результат",
            },
            {
                "day": "5",
                "subject": "Вопрос: что тебя останавливает?",
                "preview": "Я помогу разобраться",
                "body": "Обработка возражений (время, деньги, опыт). FAQ. Предложение созвона",
                "cta": "Запишись на бесплатную консультацию",
            },
            {
                "day": "7",
                "subject": "Последний шанс: скидка 20% на курс по кибербезопасности",
                "preview": "Только до конца недели",
                "body": "Срочность, итоговое предложение, бонусы за ранний старт",
                "cta": "Записаться со скидкой 20%",
            },
        ],
        "abandon_cart": [
            {
                "day": "0",
                "subject": "Ты забыл кое-что важное...",
                "preview": "Твоё место на курсе пока свободно",
                "body": "Напоминание о брошенной заявке, что входит в курс, гарантия возврата",
                "cta": "Завершить регистрацию",
            },
            {
                "day": "1",
                "subject": "Есть вопрос? Я помогу",
                "preview": "Может, что-то непонятно — напиши мне",
                "body": "Обработка типичных сомнений, ссылка на FAQ, предложение чата с ментором",
                "cta": "Задать вопрос в Telegram",
            },
            {
                "day": "3",
                "subject": "Бонус для тех, кто сомневается",
                "preview": "Дополнительная скидка + бонусный модуль",
                "body": "Финальный стимул: скидка + доп. модуль бесплатно. Срок: 48 часов",
                "cta": "Записаться с бонусом",
            },
        ],
        "upsell": [
            {
                "day": "0",
                "subject": "Поздравляю с окончанием курса!",
                "preview": "Вот что ждёт тебя дальше",
                "body": "Поздравление, краткий итог достижений, куда расти дальше",
                "cta": "Посмотри продвинутый курс",
            },
            {
                "day": "3",
                "subject": "Специальное предложение для выпускников",
                "preview": "Скидка 30% на продвинутый уровень",
                "body": "Эксклюзив для выпускников: скидка на Red Team / продвинутый модуль",
                "cta": "Перейти на продвинутый уровень",
            },
        ],
    },
    "Blue Team / Defensive Security": {
        "welcome": [
            {
                "day": "0",
                "subject": "Добро пожаловать в защиту инфраструктуры!",
                "preview": "Первый шаг к карьере SOC-аналитика",
                "body": "Приветствие, что ждёт, бесплатный чеклист 'Настройка домашнего SIEM за 1 час'",
                "cta": "Скачай чеклист бесплатно",
            },
            {
                "day": "1",
                "subject": "3 инструмента, с которых начинает каждый SOC-аналитик",
                "preview": "Бесплатные и мощные",
                "body": "Wazuh, Suricata, TheHive. Краткий обзор каждого, почему именно они",
                "cta": "Читай подробный гайд",
            },
            {
                "day": "3",
                "subject": "Почему Blue Team — самая востребованная специальность 2025",
                "preview": "Зарплаты, вакансии, перспективы",
                "body": "Статистика рынка, рост спроса, средние зарплаты, как курс помогает войти в профессию",
                "cta": "Узнай программу курса",
            },
        ],
        "nurture": [
            {
                "day": "0",
                "subject": "Понравился чеклист? Вот продолжение",
                "preview": "Бесплатный мини-курс: 3 дня — 3 навыка",
                "body": "Мини-курс: парсинг логов, написание правил, реагирование на инцидент",
                "cta": "Начать мини-курс",
            },
            {
                "day": "3",
                "subject": "Как Марина перешла из техподдержки в SOC за 5 месяцев",
                "preview": "Реальная история студентки",
                "body": "Кейс, путь, отзыв, текущая должность и зарплата",
                "cta": "Хочу такой же результат",
            },
            {
                "day": "7",
                "subject": "Открыт набор: курс по Blue Team со скидкой",
                "preview": "Количество мест ограничено",
                "body": "Программа, менторство, стажировка, ранний старт со скидкой",
                "cta": "Записаться со скидкой",
            },
        ],
        "abandon_cart": [
            {
                "day": "0",
                "subject": "Ты был близок к старту...",
                "preview": "Твоя заявка ещё ждёт",
                "body": "Напоминание, что входит в курс, гарантия",
                "cta": "Завершить регистрацию",
            },
            {
                "day": "2",
                "subject": "Бонус за решительность: доп. модуль бесплатно",
                "preview": "Только 48 часов",
                "body": "Дополнительный модуль по Threat Hunting в подарок",
                "cta": "Записаться с бонусом",
            },
        ],
        "upsell": [
            {
                "day": "0",
                "subject": "Поздравляю! Ты — дипломированный SOC-аналитик",
                "preview": "Что дальше?",
                "body": "Итоги, сертификат, следующие шаги: Red Team или Threat Intelligence",
                "cta": "Посмотри продвинутые курсы",
            },
        ],
    },
    "Red Team / Offensive Security": {
        "welcome": [
            {
                "day": "0",
                "subject": "Добро пожаловать в наступательную безопасность!",
                "preview": "Твой путь к сертификации OSCP начинается здесь",
                "body": "Приветствие, roadmap изучения, PDF 'Топ-10 команд для пентеста'",
                "cta": "Скачай PDF бесплатно",
            },
            {
                "day": "1",
                "subject": "Первая лаба: взломай это за 15 минут",
                "preview": "Легальный пентест для новичков",
                "body": "Ссылка на TryHackMe/HackTheBox комнату, пошаговый разбор",
                "cta": "Попробуй бесплатную лабу",
            },
            {
                "day": "3",
                "subject": "Сколько зарабатывает пентестер в 2025?",
                "preview": "Цифры, которые удивят",
                "body": "Статистика зарплат, фриланс vs штат, сертификации и их влияние",
                "cta": "Узнай программу курса",
            },
        ],
        "nurture": [
            {
                "day": "0",
                "subject": "PDF понравился? Вот практика",
                "preview": "3 бесплатных CTF-задачи с разбором",
                "body": "Мини-курс: SQL-инъекции, XSS, privilege escalation",
                "cta": "Начать практику",
            },
            {
                "day": "3",
                "subject": "Из сисадмина в пентестера: история Дмитрия",
                "preview": "Как курс изменил карьеру",
                "body": "Кейс, прогресс, первый багбаунти, текущая работа",
                "cta": "Хочу такой же путь",
            },
            {
                "day": "7",
                "subject": "Набор на курс по Red Team: осталось 10 мест",
                "preview": "Скидка для ранних — 25%",
                "body": "Программа, проекты, менторство, скидка за ранний старт",
                "cta": "Занять место со скидкой",
            },
        ],
        "abandon_cart": [
            {
                "day": "0",
                "subject": "Ты начал — осталось завершить",
                "preview": "Место на курсе пока за тобой",
                "body": "Напоминание, программа, гарантия возврата 14 дней",
                "cta": "Завершить регистрацию",
            },
            {
                "day": "2",
                "subject": "Бонус: доступ к закрытому CTF-серверу",
                "preview": "Только для студентов курса — и для тебя",
                "body": "Эксклюзивный CTF с 50+ задачами, доступен на год",
                "cta": "Записаться и получить доступ",
            },
        ],
        "upsell": [
            {
                "day": "0",
                "subject": "Курс пройден! Вот твой следующий уровень",
                "preview": "Продвинутый Red Team: Active Directory и C2",
                "body": "Поздравление, продвинутый модуль, скидка для выпускников",
                "cta": "Перейти на продвинутый уровень",
            },
        ],
    },
    "Machine Learning & AI": {
        "welcome": [
            {
                "day": "0",
                "subject": "Добро пожаловать в мир AI и Machine Learning!",
                "preview": "Ты на пути к профессии ML-инженера",
                "body": "Приветствие, что ждёт, PDF 'Первая нейросеть за 30 минут'",
                "cta": "Скачай PDF бесплатно",
            },
            {
                "day": "1",
                "subject": "5 ресурсов для старта в ML (бесплатно)",
                "preview": "Курсы, каналы, инструменты",
                "body": "Подборка бесплатных ресурсов + как мой курс ускоряет путь",
                "cta": "Читай подборку",
            },
            {
                "day": "3",
                "subject": "AI забирает работу? Нет — создаёт новую",
                "preview": "Профессии, которых не было 2 года назад",
                "body": "Новые роли в AI, зарплаты, как курс готовит к ним",
                "cta": "Узнай программу курса",
            },
        ],
        "nurture": [
            {
                "day": "0",
                "subject": "Понравился гайд? Вот продолжение",
                "preview": "Мини-курс: 3 проекта за 3 дня",
                "body": "Мини-проекты: чат-бот, классификатор изображений, рекомендательная система",
                "cta": "Начать мини-курс",
            },
            {
                "day": "3",
                "subject": "Из маркетолога в ML-инженера: история Елены",
                "preview": "6 месяцев — и новая карьера",
                "body": "Кейс, трансформация, текущий проект и зарплата",
                "cta": "Хочу такой же результат",
            },
            {
                "day": "7",
                "subject": "Курс по ML: старт через неделю, скидка 20%",
                "preview": "Успей записаться",
                "body": "Программа, проекты, менторство, скидка",
                "cta": "Записаться со скидкой",
            },
        ],
        "abandon_cart": [
            {
                "day": "0",
                "subject": "Ты не завершил заявку на курс AI",
                "preview": "Осталось 2 клика до старта",
                "body": "Напоминание, программа, гарантия",
                "cta": "Завершить регистрацию",
            },
            {
                "day": "2",
                "subject": "Бонус: доступ к GPU-серверу на 30 дней",
                "preview": "Бесплатно для новых студентов",
                "body": "GPU для обучения моделей, стоимость $50, для тебя бесплатно",
                "cta": "Записаться и получить GPU",
            },
        ],
        "upsell": [
            {
                "day": "0",
                "subject": "Ты — ML-инженер! Что дальше?",
                "preview": "Специализация: NLP, Computer Vision или MLOps",
                "body": "Поздравление, 3 направления углубления, скидка выпускника",
                "cta": "Выбери специализацию",
            },
        ],
    },
    "AliExpress - Гаджеты": {
        "welcome": [
            {
                "day": "0",
                "subject": "Добро пожаловать в мир хакерских гаджетов!",
                "preview": "Подборка лучших устройств с AliExpress",
                "body": "Приветствие, топ-5 гаджетов с обзорами, реферальные ссылки",
                "cta": "Смотри подборку",
            },
            {
                "day": "2",
                "subject": "Новинки недели: 3 гаджета, которые ты пропустил",
                "preview": "WiFi-адаптер, USB Rubber Ducky, SDR-приёмник",
                "body": "Обзор 3 новинок, цены, ссылки на AliExpress",
                "cta": "Перейти к обзорам",
            },
        ],
        "nurture": [
            {
                "day": "0",
                "subject": "Как выбрать WiFi-адаптер для Kali Linux",
                "preview": "Гайд для новичков + лучшие модели",
                "body": "Критерии выбора, топ-3 модели, реферальные ссылки",
                "cta": "Читай гайд и выбирай",
            },
            {
                "day": "3",
                "subject": "Скидки на гаджеты: до -40% на AliExpress",
                "preview": "Собрал лучшие предложения",
                "body": "Кураторская подборка скидок на проверенные гаджеты",
                "cta": "Смотри скидки",
            },
        ],
        "abandon_cart": [
            {
                "day": "0",
                "subject": "Гаджет ещё в корзине — успей купить!",
                "preview": "Цена может измениться",
                "body": "Напоминание, обзор товара, социальное доказательство (X человек купили)",
                "cta": "Вернуться к покупке",
            },
        ],
        "upsell": [
            {
                "day": "0",
                "subject": "Тебе понравился гаджет? Вот аксессуары к нему",
                "preview": "Антенны, кабели, кейсы — всё по ссылкам",
                "body": "Дополнительные товары к купленному, реферальные ссылки",
                "cta": "Смотри аксессуары",
            },
        ],
    },
}


def generate_emails(pillar_name: str) -> list[Email]:
    pillar_data = PILLAR_SEQUENCES.get(pillar_name)
    if pillar_data is None:
        return []

    emails: list[Email] = []
    for seq_type in SEQUENCE_TYPES:
        items = pillar_data.get(seq_type, [])
        emails.extend(
            Email(
                pillar=pillar_name,
                sequence_type=seq_type,
                sequence_label=SEQUENCE_LABELS[seq_type],
                day=int(item["day"]),
                subject=item["subject"],
                preview=item["preview"],
                body_outline=item["body"],
                cta=item["cta"],
            )
            for item in items
        )
    return emails


def generate_all_emails() -> list[Email]:
    result: list[Email] = []
    for pillar in PILLARS:
        result.extend(generate_emails(pillar.name))
    return result


def export_emails_json(emails: list[Email], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "pillar": e.pillar,
            "sequence": e.sequence_type,
            "sequence_label": e.sequence_label,
            "day": e.day,
            "subject": e.subject,
            "preview": e.preview,
            "body_outline": e.body_outline,
            "cta": e.cta,
        }
        for e in emails
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_emails_txt(emails: list[Email], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "EMAIL-ПОСЛЕДОВАТЕЛЬНОСТИ — АВТОМАТИЧЕСКИЕ СЕРИИ",
        "=" * 60,
    ]

    current_pillar = ""
    current_seq = ""
    for e in emails:
        if e.pillar != current_pillar:
            current_pillar = e.pillar
            lines.append(f"\n{'━' * 50}")
            lines.append(f"📌 {current_pillar}")
            lines.append(f"{'━' * 50}")
            current_seq = ""

        if e.sequence_type != current_seq:
            current_seq = e.sequence_type
            lines.append(f"\n  [{e.sequence_label}]")

        lines.append(f"\n  День {e.day}:")
        lines.append(f"    Тема: {e.subject}")
        lines.append(f"    Превью: {e.preview}")
        lines.append(f"    Тело: {e.body_outline}")
        lines.append(f"    CTA: {e.cta}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def emails_summary(emails: list[Email]) -> str:
    by_pillar: dict[str, int] = {}
    by_seq: dict[str, int] = {}
    for e in emails:
        by_pillar[e.pillar] = by_pillar.get(e.pillar, 0) + 1
        by_seq[e.sequence_label] = by_seq.get(e.sequence_label, 0) + 1

    lines: list[str] = [
        f"Email-последовательности: {len(emails)} писем",
        f"Направлений: {len(by_pillar)}",
    ]
    lines.extend(f"  {name}: {count}" for name, count in by_pillar.items())
    lines.append("\nПо типам серий:")
    lines.extend(f"  {seq}: {count}" for seq, count in by_seq.items())
    return "\n".join(lines)
