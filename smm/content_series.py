"""Content series generator — themed multi-day narrative arcs.

Creates engaging content series like "5 Days — 5 Hacker Tools" or
"Security Week Challenge" that keep the audience returning daily.
Each series has a unifying theme, numbered episodes, and builds
toward a CTA on the final day.

Series drive higher engagement through anticipation and completion bias.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from smm.content_bank import get_ctas, get_hooks
from smm.content_pillars import PILLARS, ContentPillar

SERIES_TEMPLATES: list[dict[str, str | int]] = [
    {
        "name": "5 дней — 5 инструментов",
        "days": 5,
        "intro": "День {day}/5: {tool}",
        "pattern": "Каждый день — новый инструмент. Сохраняй, чтобы не потерять!",
        "finale": "Все 5 инструментов в одном посте! Ссылка в био",
        "type": "listicle_series",
    },
    {
        "name": "Челлендж на неделю",
        "days": 7,
        "intro": "День {day}: {task}",
        "pattern": "7-дневный челлендж! Отмечай друга и проходите вместе",
        "finale": "Челлендж пройден! Результаты в stories. Старт курса — ссылка в био",
        "type": "challenge",
    },
    {
        "name": "Разбор мифов",
        "days": 5,
        "intro": "Миф #{day}: «{myth}»",
        "pattern": "Серия разборов популярных заблуждений. Правда или ложь?",
        "finale": "Все мифы разобраны! Полный курс — ссылка в био",
        "type": "myth_busting",
    },
    {
        "name": "От нуля до героя",
        "days": 7,
        "intro": "Шаг {day}/7: {step}",
        "pattern": "Пошаговое руководство для начинающих. Сохраняй серию!",
        "finale": "Путь пройден! Следующий уровень — на курсе. Ссылка в био",
        "type": "tutorial_series",
    },
    {
        "name": "Топ ошибок новичков",
        "days": 5,
        "intro": "Ошибка #{day}: {mistake}",
        "pattern": "Не повторяй чужих ошибок! Серия для тех, кто начинает",
        "finale": "Все ошибки разобраны! Учись правильно — ссылка в био",
        "type": "mistakes_series",
    },
]

SERIES_CONTENT: dict[str, dict[str, list[str]]] = {
    "Cyber Security & Ethical Hacking": {
        "tools": [
            "Nmap — сканирование сети",
            "Wireshark — анализ трафика",
            "Burp Suite — тестирование веб-приложений",
            "Metasploit — фреймворк для эксплойтов",
            "Hashcat — взлом паролей на GPU",
            "SQLmap — автоматизация SQL-инъекций",
            "John the Ripper — брутфорс паролей",
        ],
        "tasks": [
            "Установи Kali Linux",
            "Просканируй свою сеть через Nmap",
            "Перехвати HTTP-трафик в Wireshark",
            "Найди открытые порты на роутере",
            "Проверь свои пароли на утечки",
            "Настрой двухфакторную аутентификацию везде",
            "Пройди один room на TryHackMe",
        ],
        "myths": [
            "Mac нельзя взломать",
            "VPN делает тебя анонимным",
            "Хакеры — это преступники",
            "Антивирус защищает от всего",
            "Сложный пароль = безопасность",
        ],
        "steps": [
            "Что такое этичный хакинг",
            "Установка инструментов",
            "Основы сетевого сканирования",
            "Анализ уязвимостей",
            "Эксплуатация и отчёт",
            "Построение карьеры",
            "Сертификации и ресурсы",
        ],
        "mistakes": [
            "Учишь теорию без практики",
            "Начинаешь с CTF вместо основ",
            "Игнорируешь сетевые протоколы",
            "Не ведёшь заметки",
            "Пропускаешь линукс",
        ],
    },
    "Blue Team / Defensive Security": {
        "tools": [
            "Splunk — SIEM-аналитика",
            "Zeek — мониторинг трафика",
            "YARA — сигнатуры малвари",
            "Volatility — форензика памяти",
            "Suricata — IDS/IPS",
            "TheHive — реагирование на инциденты",
            "Velociraptor — endpoint-мониторинг",
        ],
        "tasks": [
            "Установи ELK Stack",
            "Настрой базовый мониторинг сети",
            "Создай первое YARA-правило",
            "Проанализируй дамп памяти",
            "Напиши playbook реагирования",
            "Настрой алерты в SIEM",
            "Проведи табличные учения",
        ],
        "myths": [
            "Файрвол — это всё, что нужно",
            "SIEM ловит все угрозы",
            "Маленькие компании не атакуют",
            "Автоматизация заменит аналитиков",
            "Инцидент = провал",
        ],
        "steps": [
            "Основы защитной безопасности",
            "Мониторинг и логирование",
            "Детектирование угроз",
            "Реагирование на инциденты",
            "Форензика и анализ",
            "Автоматизация SOC",
            "Карьера в Blue Team",
        ],
        "mistakes": [
            "Не читаешь логи регулярно",
            "Нет плана реагирования",
            "Игнорируешь фишинг-тренинги",
            "Не обновляешь сигнатуры",
            "Не тестируешь бэкапы",
        ],
    },
    "Red Team / Offensive Security": {
        "tools": [
            "BloodHound — картография AD",
            "Cobalt Strike — C2-фреймворк",
            "Impacket — атаки на Windows",
            "Responder — перехват NTLM",
            "CrackMapExec — автоматизация",
            "Rubeus — атаки на Kerberos",
            "Covenant — C2 на .NET",
        ],
        "tasks": [
            "Развернуть лабу с AD",
            "Провести разведку сети",
            "Получить initial access",
            "Выполнить lateral movement",
            "Повысить привилегии",
            "Извлечь данные (exfiltration)",
            "Написать отчёт операции",
        ],
        "myths": [
            "Пентест = настоящий взлом",
            "Red Team работает в одиночку",
            "Нужны только 0-day",
            "Социальная инженерия — не хакинг",
            "Автоматические сканеры достаточно",
        ],
        "steps": [
            "Теория наступательной безопасности",
            "Разведка и OSINT",
            "Начальный доступ",
            "Закрепление в сети",
            "Эскалация привилегий",
            "Цель операции",
            "Отчёт и рекомендации",
        ],
        "mistakes": [
            "Шумишь в сети при разведке",
            "Не документируешь шаги",
            "Пропускаешь пост-эксплуатацию",
            "Не чистишь следы",
            "Слабый отчёт заказчику",
        ],
    },
    "Machine Learning & AI": {
        "tools": [
            "Jupyter Notebook — эксперименты",
            "Hugging Face — готовые модели",
            "Pandas — работа с данными",
            "Scikit-learn — классический ML",
            "PyTorch — нейросети",
            "Weights & Biases — трекинг",
            "LangChain — цепочки для LLM",
        ],
        "tasks": [
            "Установи Jupyter и библиотеки",
            "Загрузи и исследуй датасет",
            "Обучи первую модель",
            "Визуализируй результаты",
            "Улучши метрики модели",
            "Разверни модель как API",
            "Поделись результатом в GitHub",
        ],
        "myths": [
            "AI заменит программистов",
            "Для ML нужна дорогая GPU",
            "Нейросети думают как люди",
            "Больше данных = лучше модель",
            "ML — это только Python",
        ],
        "steps": [
            "Что такое машинное обучение",
            "Подготовка данных",
            "Первая модель классификации",
            "Оценка и улучшение",
            "Нейронные сети",
            "Deployment в продакшн",
            "Карьера в ML/AI",
        ],
        "mistakes": [
            "Начинаешь с нейросетей вместо основ",
            "Не чистишь данные",
            "Игнорируешь переобучение",
            "Не отслеживаешь эксперименты",
            "Пропускаешь статистику",
        ],
    },
    "AliExpress - Гаджеты": {
        "tools": [
            "WiFi-адаптер с мониторингом",
            "USB Rubber Ducky",
            "Flipper Zero",
            "Raspberry Pi",
            "SDR-приёмник",
            "Lockpick-набор",
            "Сетевой хаб для MITM",
        ],
        "tasks": [
            "Выбери свой первый гаджет",
            "Настрой WiFi-адаптер в Kali",
            "Собери мини-лабораторию",
            "Протестируй USB Rubber Ducky",
            "Настрой Raspberry Pi как сервер",
            "Попробуй SDR-анализ",
            "Собери полный набор инструментов",
        ],
        "myths": [
            "Дешёвые гаджеты — мусор",
            "AliExpress — только подделки",
            "Доставка идёт месяцами",
            "Для практики нужно дорогое оборудование",
            "Хакерские гаджеты нелегальны",
        ],
        "steps": [
            "Зачем нужны гаджеты",
            "Выбор первых инструментов",
            "Заказ и доставка",
            "Первая настройка",
            "Базовые эксперименты",
            "Продвинутые сценарии",
            "Полная лаборатория",
        ],
        "mistakes": [
            "Покупаешь без исследования",
            "Берёшь несовместимый чипсет",
            "Не проверяешь продавца",
            "Заказываешь всё сразу",
            "Игнорируешь отзывы",
        ],
    },
}


@dataclass(frozen=True, slots=True)
class SeriesEpisode:
    day: int
    title: str
    caption: str
    hashtags: str
    visual_note: str
    cta: str


@dataclass(frozen=True, slots=True)
class ContentSeries:
    pillar: str
    series_name: str
    series_type: str
    total_days: int
    episodes: list[SeriesEpisode]

    def to_dict(self) -> dict[str, object]:
        return {
            "pillar": self.pillar,
            "series_name": self.series_name,
            "series_type": self.series_type,
            "total_days": self.total_days,
            "episodes": [
                {
                    "day": e.day,
                    "title": e.title,
                    "caption": e.caption,
                    "hashtags": e.hashtags,
                    "visual_note": e.visual_note,
                    "cta": e.cta,
                }
                for e in self.episodes
            ],
        }


def _content_key(series_type: str) -> str:
    mapping = {
        "listicle_series": "tools",
        "challenge": "tasks",
        "myth_busting": "myths",
        "tutorial_series": "steps",
        "mistakes_series": "mistakes",
    }
    return mapping.get(series_type, "tools")


def generate_series(
    pillar: ContentPillar,
    template: dict[str, str | int] | None = None,
    seed: int | None = None,
) -> ContentSeries:
    if seed is not None:
        random.seed(seed)

    if template is None:
        template = random.choice(SERIES_TEMPLATES)

    series_type = str(template["type"])
    total_days = int(template["days"])
    series_name = str(template["name"])
    pattern = str(template["pattern"])
    finale = str(template["finale"])
    intro_tmpl = str(template["intro"])

    keyword = pillar.name.split("/")[0].strip().split("&")[0].strip()
    hooks = get_hooks(keyword, count=3)
    ctas = get_ctas("referral" if pillar.product == "referral" else "course", count=2)
    content_key = _content_key(series_type)
    content_items = SERIES_CONTENT.get(pillar.name, {}).get(content_key, [])

    if not content_items:
        content_items = [f"Элемент {i + 1}" for i in range(total_days)]

    episodes: list[SeriesEpisode] = []
    for day in range(1, total_days + 1):
        item = content_items[(day - 1) % len(content_items)]

        title = intro_tmpl.replace("{day}", str(day))
        for placeholder in ("tool", "task", "myth", "step", "mistake"):
            title = title.replace(f"{{{placeholder}}}", item)

        if day == 1:
            caption = f"{hooks[0]}\n\n{pattern}\n\n{title}\n\n{item}"
        elif day == total_days:
            caption = f"{title}\n\n{finale}\n\n{ctas[0]}"
        else:
            caption = f"{title}\n\n{item}\n\nСледующий выпуск — завтра!"

        hashtags = f"#{series_name.replace(' ', '').replace('—', '')} #день{day} #{keyword.replace(' ', '')}"

        if day == 1:
            visual = f"Обложка серии: «{series_name}» — яркий дизайн, нумерация"
        elif day == total_days:
            visual = "Финальный слайд: итоги + CTA + стрелка на ссылку в био"
        else:
            visual = f"День {day}: тёмный фон, номер крупно, контент по центру"

        cta = ctas[0] if day >= total_days - 1 else "Подпишись, чтобы не пропустить!"

        episodes.append(
            SeriesEpisode(
                day=day,
                title=title,
                caption=caption,
                hashtags=hashtags,
                visual_note=visual,
                cta=cta,
            )
        )

    return ContentSeries(
        pillar=pillar.name,
        series_name=series_name,
        series_type=series_type,
        total_days=total_days,
        episodes=episodes,
    )


def generate_all_series(
    seed: int | None = None,
) -> list[ContentSeries]:
    if seed is not None:
        random.seed(seed)

    result: list[ContentSeries] = []
    templates = list(SERIES_TEMPLATES)
    random.shuffle(templates)

    for i, pillar in enumerate(PILLARS):
        tmpl = templates[i % len(templates)]
        series = generate_series(pillar, template=tmpl)
        result.append(series)
    return result


def export_series_json(series_list: list[ContentSeries], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [s.to_dict() for s in series_list]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_series_txt(series_list: list[ContentSeries], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for i, series in enumerate(series_list, 1):
        lines.append(f"{'=' * 60}")
        lines.append(f"СЕРИЯ #{i}: {series.series_name}")
        lines.append(f"Направление: {series.pillar}")
        lines.append(f"Тип: {series.series_type} | Дней: {series.total_days}")
        lines.append(f"{'=' * 60}")
        for ep in series.episodes:
            lines.append(f"\n  --- День {ep.day} ---")
            lines.append(f"  Заголовок: {ep.title}")
            lines.append(f"  Подпись:\n    {ep.caption[:200]}...")
            lines.append(f"  Хештеги: {ep.hashtags}")
            lines.append(f"  Визуал: {ep.visual_note}")
            lines.append(f"  CTA: {ep.cta}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def series_summary(series_list: list[ContentSeries]) -> str:
    total_episodes = sum(len(s.episodes) for s in series_list)
    by_type: dict[str, int] = {}
    for s in series_list:
        by_type[s.series_type] = by_type.get(s.series_type, 0) + 1

    lines = [
        f"Контент-серии: {len(series_list)} шт.",
        f"Всего эпизодов: {total_episodes}",
        "\nПо направлениям:",
    ]
    lines.extend(
        f"  {s.pillar}: «{s.series_name}» ({s.total_days} дн.)" for s in series_list
    )
    lines.append("\nПо типам:")
    lines.extend(f"  {t}: {count}" for t, count in sorted(by_type.items()))
    return "\n".join(lines)
