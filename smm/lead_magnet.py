"""Lead magnet generator — PDF-ready checklists and cheat sheets.

Creates lead magnet content outlines for each pillar to capture emails.
Each lead magnet has a title, subtitle, sections with bullet points,
and a CTA driving to the course or referral link.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

LEAD_MAGNETS_DATA: list[dict[str, object]] = [
    {
        "id": "cyber-checklist",
        "pillar": "Cyber Security & Ethical Hacking",
        "title": "Чеклист: 30 шагов к первому пентесту",
        "subtitle": "Пошаговый план от нуля до первого Bug Bounty",
        "format": "PDF-чеклист",
        "sections": [
            {
                "heading": "Подготовка (дни 1-7)",
                "items": [
                    "Установить Kali Linux на виртуальную машину",
                    "Настроить лабораторию: VirtualBox + Metasploitable",
                    "Пройти 5 комнат на TryHackMe (бесплатно)",
                    "Изучить основы TCP/IP и DNS",
                    "Настроить Burp Suite Community Edition",
                ],
            },
            {
                "heading": "Базовые навыки (дни 8-14)",
                "items": [
                    "Освоить Nmap: 5 типов сканирования",
                    "Научиться перечислению сервисов (enumeration)",
                    "Изучить OWASP Top 10 уязвимостей",
                    "Практика SQL-инъекций на DVWA",
                    "Практика XSS на XSS Game",
                ],
            },
            {
                "heading": "Продвинутый уровень (дни 15-30)",
                "items": [
                    "Пройти 3 машины на HackTheBox",
                    "Написать первый отчёт о пентесте",
                    "Зарегистрироваться на Bug Bounty платформе",
                    "Отправить первый баг-репорт",
                    "Начать подготовку к CEH/OSCP",
                ],
            },
        ],
        "cta": "Хочешь пройти этот путь с наставником? Записывайся на курс!",
    },
    {
        "id": "blue-team-playbook",
        "pillar": "Blue Team / Defensive Security",
        "title": "Плейбук: реагирование на инциденты",
        "subtitle": "Что делать в первые 60 минут после обнаружения взлома",
        "format": "PDF-гайд",
        "sections": [
            {
                "heading": "Обнаружение (0-15 минут)",
                "items": [
                    "Определить тип инцидента по классификации NIST",
                    "Зафиксировать время обнаружения и первичные IOC",
                    "Уведомить дежурного аналитика и менеджера",
                    "Начать запись всех действий в журнал инцидента",
                ],
            },
            {
                "heading": "Сдерживание (15-30 минут)",
                "items": [
                    "Изолировать заражённые системы от сети",
                    "Сохранить volatile data (RAM, сетевые соединения)",
                    "Заблокировать скомпрометированные учётные записи",
                    "Обновить правила файрвола для блокировки C2",
                ],
            },
            {
                "heading": "Расследование (30-60 минут)",
                "items": [
                    "Собрать логи из SIEM за последние 72 часа",
                    "Провести анализ артефактов на заражённых хостах",
                    "Определить вектор атаки и масштаб компрометации",
                    "Подготовить предварительный отчёт для руководства",
                ],
            },
        ],
        "cta": "Хочешь освоить Incident Response профессионально? Записывайся на курс Blue Team!",
    },
    {
        "id": "red-team-toolkit",
        "pillar": "Red Team / Offensive Security",
        "title": "Шпаргалка: 50 команд для пентестера",
        "subtitle": "Самые нужные команды Nmap, Metasploit, Burp Suite и других инструментов",
        "format": "PDF-шпаргалка",
        "sections": [
            {
                "heading": "Разведка и сканирование",
                "items": [
                    "nmap -sV -sC -O target — полное сканирование",
                    "gobuster dir -u URL -w wordlist — перебор директорий",
                    "whatweb target — определение технологий",
                    "theHarvester -d domain -b all — сбор email и субдоменов",
                    "amass enum -d domain — перечисление субдоменов",
                ],
            },
            {
                "heading": "Эксплуатация",
                "items": [
                    "msfconsole → search → use → set → exploit",
                    "sqlmap -u URL --dbs — автоматизация SQL-инъекций",
                    "hydra -l user -P wordlist ssh://target — брутфорс",
                    "john --wordlist=rockyou.txt hash.txt — взлом хешей",
                    "responder -I eth0 — перехват NTLM-хешей",
                ],
            },
            {
                "heading": "Пост-эксплуатация",
                "items": [
                    "linpeas.sh — автоматический поиск привилегий Linux",
                    "winPEAS.exe — автоматический поиск привилегий Windows",
                    "mimikatz — дамп учётных данных из памяти",
                    "BloodHound — анализ путей атаки в AD",
                    "Chisel — туннелирование через скомпрометированный хост",
                ],
            },
        ],
        "cta": "Хочешь освоить все инструменты на практике? Курс Red Team ждёт!",
    },
    {
        "id": "ml-quickstart",
        "pillar": "Machine Learning & AI",
        "title": "Гайд: твоя первая ML-модель за вечер",
        "subtitle": "От датасета до работающей модели — пошаговая инструкция с кодом",
        "format": "PDF-гайд с кодом",
        "sections": [
            {
                "heading": "Шаг 1: Подготовка среды",
                "items": [
                    "Установить Python 3.11+ и Jupyter Notebook",
                    "pip install scikit-learn pandas matplotlib",
                    "Скачать датасет Iris (встроен в sklearn)",
                    "Создать новый notebook для эксперимента",
                ],
            },
            {
                "heading": "Шаг 2: Анализ данных",
                "items": [
                    "Загрузить данные и посмотреть первые 5 строк",
                    "Визуализировать распределение классов",
                    "Проверить на пропущенные значения",
                    "Разделить на train/test (80/20)",
                ],
            },
            {
                "heading": "Шаг 3: Обучение и оценка",
                "items": [
                    "Обучить RandomForestClassifier",
                    "Оценить accuracy на тестовых данных",
                    "Построить confusion matrix",
                    "Сохранить модель с joblib",
                    "Бонус: попробовать на своих данных",
                ],
            },
        ],
        "cta": "Готов к серьёзным проектам? На курсе ML построишь 10 реальных моделей!",
    },
    {
        "id": "gadget-guide",
        "pillar": "AliExpress — Гаджеты",
        "title": "Топ-10 хакерских гаджетов с AliExpress",
        "subtitle": "Проверенные устройства для домашней лаборатории от $5 до $50",
        "format": "PDF-каталог",
        "sections": [
            {
                "heading": "WiFi и сети ($5-15)",
                "items": [
                    "WiFi-адаптер с режимом мониторинга (RTL8812AU)",
                    "Ethernet-адаптер USB 3.0 для сниффинга",
                    "Портативный роутер для путешествий (OpenWrt)",
                ],
            },
            {
                "heading": "USB-устройства ($10-30)",
                "items": [
                    "USB Rubber Ducky аналог (Digispark ATtiny85)",
                    "USB-хаб с индивидуальными выключателями",
                    "Флешка с аппаратным шифрованием",
                ],
            },
            {
                "heading": "Продвинутые ($20-50)",
                "items": [
                    "ESP32 для WiFi-деаутентификации (образовательные цели)",
                    "RTL-SDR приёмник для анализа радиочастот",
                    "Raspberry Pi Zero W для портативных проектов",
                    "RFID-ридер RC522 для изучения NFC",
                ],
            },
        ],
        "cta": "Все ссылки на проверенных продавцов — в нашем реферальном каталоге!",
    },
]


@dataclass(frozen=True, slots=True)
class LeadMagnetSection:
    heading: str
    items: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class LeadMagnet:
    id: str
    pillar: str
    title: str
    subtitle: str
    format: str
    sections: tuple[LeadMagnetSection, ...]
    cta: str


def _to_lead_magnet(data: dict[str, object]) -> LeadMagnet:
    sections = tuple(
        LeadMagnetSection(
            heading=str(s["heading"]),  # type: ignore[index]
            items=tuple(str(i) for i in s["items"]),  # type: ignore[index]
        )
        for s in data["sections"]  # type: ignore[union-attr]
    )
    return LeadMagnet(
        id=str(data["id"]),
        pillar=str(data["pillar"]),
        title=str(data["title"]),
        subtitle=str(data["subtitle"]),
        format=str(data["format"]),
        sections=sections,
        cta=str(data["cta"]),
    )


def generate_lead_magnets(
    pillar: str | None = None,
) -> list[LeadMagnet]:
    result: list[LeadMagnet] = []
    for data in LEAD_MAGNETS_DATA:
        if pillar and str(data["pillar"]) != pillar:
            continue
        result.append(_to_lead_magnet(data))
    return result


def export_lead_magnets_json(magnets: list[LeadMagnet], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "id": m.id,
            "pillar": m.pillar,
            "title": m.title,
            "subtitle": m.subtitle,
            "format": m.format,
            "sections": [
                {"heading": s.heading, "items": list(s.items)} for s in m.sections
            ],
            "cta": m.cta,
        }
        for m in magnets
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_lead_magnets_txt(magnets: list[LeadMagnet], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "ЛИД-МАГНИТЫ — КОНТЕНТ ДЛЯ СБОРА EMAIL",
        "=" * 60,
    ]

    for m in magnets:
        lines.append(f"\n{'━' * 50}")
        lines.append(f"📥 {m.title}")
        lines.append(f"   {m.subtitle}")
        lines.append(f"   Формат: {m.format} | Направление: {m.pillar}")
        lines.append(f"{'━' * 50}")

        for s in m.sections:
            lines.append(f"\n  {s.heading}:")
            lines.extend(f"    ✅ {item}" for item in s.items)

        lines.append(f"\n  CTA: {m.cta}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def lead_magnets_summary(magnets: list[LeadMagnet]) -> str:
    if not magnets:
        return "Лид-магниты: 0 материалов"

    total_items = sum(len(s.items) for m in magnets for s in m.sections)
    lines: list[str] = [
        f"Лид-магниты: {len(magnets)} материалов, {total_items} пунктов",
        "\nМатериалы:",
    ]
    lines.extend(f"  [{m.format}] {m.title} — {m.pillar}" for m in magnets)
    return "\n".join(lines)
