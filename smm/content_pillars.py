"""Контентные столпы и готовые темы для всех направлений бизнеса.

Каждый столп привязан к конкретному продукту (курс или реферальная ссылка)
и содержит готовые темы для генерации контента.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ContentPillar:
    name: str
    product: str
    referral_label: str
    topics: list[str] = field(default_factory=list)
    hashtags_ru: list[str] = field(default_factory=list)
    hashtags_en: list[str] = field(default_factory=list)


PILLARS: list[ContentPillar] = [
    ContentPillar(
        name="Cyber Security & Ethical Hacking",
        product="course",
        referral_label="Курс Cyber Security & Ethical Hacking",
        topics=[
            "5 инструментов для пентеста, которые должен знать каждый",
            "Как хакеры взламывают Wi-Fi за 5 минут (и как защититься)",
            "OSINT: как найти информацию о любом человеке в интернете",
            "Топ-10 уязвимостей веб-приложений (OWASP 2024)",
            "Как начать карьеру в кибербезопасности с нуля",
            "Burp Suite: полный гайд для начинающих",
            "SQL-инъекции: как это работает и как защититься",
            "Kali Linux: первые шаги для новичка",
            "Как пройти сертификацию CEH — мой опыт",
            "Социальная инженерия: как хакеры обманывают людей",
            "XSS-атаки: разбор реальных кейсов",
            "Nmap: сканирование сети как профессионал",
            "Bug Bounty: как заработать на поиске уязвимостей",
            "Metasploit Framework: гайд для начинающих",
            "Как защитить свой смартфон от взлома",
            "Reverse Engineering: с чего начать",
            "CTF-соревнования: лучшие платформы для практики",
            "Wireshark: анализ сетевого трафика для новичков",
            "Фишинг: как распознать и не попасться",
            "Криптография для хакеров: основы шифрования",
            "Как настроить безопасный VPN за 10 минут",
        ],
        hashtags_ru=[
            "кибербезопасность",
            "хакинг",
            "пентест",
            "этичныйхакинг",
            "информационнаябезопасность",
            "взлом",
            "безопасность",
            "хакер",
            "кибератака",
            "защитаданных",
        ],
        hashtags_en=[
            "cybersecurity",
            "hacking",
            "ethicalhacking",
            "pentest",
            "infosec",
            "bugbounty",
            "ctf",
            "hackerlife",
            "cybersec",
            "offsec",
        ],
    ),
    ContentPillar(
        name="Blue Team / Defensive Security",
        product="course",
        referral_label="Курс Blue Team / Defensive Security",
        topics=[
            "SOC-аналитик: что делает и сколько зарабатывает",
            "SIEM-системы: Splunk vs ELK — что выбрать",
            "Incident Response: как реагировать на инцидент за 60 минут",
            "Threat Hunting: как искать угрозы проактивно",
            "Как настроить мониторинг безопасности с нуля",
            "Malware Analysis: разбор реального трояна",
            "Как построить свой SOC на бюджете",
            "YARA-правила: написание и применение",
            "Форензика: как расследовать кибер-инцидент",
            "Windows Event Logs: что нужно мониторить",
            "IDS/IPS: как они работают и какой выбрать",
            "Threat Intelligence: источники и инструменты",
            "Базовые настройки безопасности Linux-сервера",
            "EDR-решения: как они ловят хакеров",
        ],
        hashtags_ru=[
            "blueteam",
            "soc",
            "защитаинформации",
            "мониторинг",
            "инцидентыбезопасности",
            "форензика",
        ],
        hashtags_en=[
            "blueteam",
            "dfir",
            "threatintel",
            "soc",
            "incidentresponse",
            "malwareanalysis",
            "threathunting",
        ],
    ),
    ContentPillar(
        name="Red Team / Offensive Security",
        product="course",
        referral_label="Курс Red Team / Offensive Security",
        topics=[
            "Red Team vs Pentest: в чем разница",
            "Active Directory: атаки и защита",
            "Cobalt Strike: что это и как работает",
            "Lateral Movement: как хакеры перемещаются по сети",
            "Privilege Escalation в Windows: топ-5 техник",
            "Privilege Escalation в Linux: практический гайд",
            "Evasion Techniques: как обойти антивирус",
            "Как получить OSCP — подготовка и советы",
            "Пост-эксплуатация: что делать после взлома",
            "Physical Security: проникновение в здание",
            "C2-фреймворки: обзор для Red Team",
            "Bloodhound: визуализация Active Directory",
            "Phishing-кампании: как строят Red Team",
            "Cloud Security: атаки на AWS/Azure",
        ],
        hashtags_ru=[
            "redteam",
            "пентест",
            "взлом",
            "наступательнаябезопасность",
            "хакинг",
            "activedirectory",
        ],
        hashtags_en=[
            "redteam",
            "pentesting",
            "oscp",
            "offsec",
            "activedirectory",
            "privesc",
            "lateralmovement",
        ],
    ),
    ContentPillar(
        name="Machine Learning & AI",
        product="course",
        referral_label="Курс Machine Learning & AI",
        topics=[
            "Нейросети за 10 минут: как это работает",
            "Python для ML: с чего начать в 2024",
            "ChatGPT vs Claude vs Gemini: большое сравнение",
            "Как обучить свою нейросеть с нуля",
            "RAG: как сделать AI который знает ваши документы",
            "Fine-tuning модели: практический гайд",
            "Computer Vision: распознавание объектов для новичков",
            "NLP: обработка естественного языка на пальцах",
            "AI-агенты: как они работают и зачем нужны",
            "Stable Diffusion: генерация изображений на своем GPU",
            "LangChain: создание AI-приложений",
            "Prompt Engineering: как правильно общаться с AI",
            "TensorFlow vs PyTorch: что выбрать в 2024",
            "Data Science: roadmap для карьеры",
            "AutoML: машинное обучение без кода",
            "Топ-10 AI-инструментов для продуктивности",
            "Как AI меняет кибербезопасность",
            "Reinforcement Learning: обучение с подкреплением",
        ],
        hashtags_ru=[
            "машинноеобучение",
            "нейросети",
            "искусственныйинтеллект",
            "datascience",
            "python",
            "ии",
            "deeplearning",
        ],
        hashtags_en=[
            "machinelearning",
            "ai",
            "deeplearning",
            "datascience",
            "python",
            "artificialintelligence",
            "llm",
            "chatgpt",
        ],
    ),
    ContentPillar(
        name="AliExpress - Гаджеты",
        product="referral",
        referral_label="AliExpress - Гаджеты для хакеров",
        topics=[
            "Топ-5 гаджетов для хакера с AliExpress до $20",
            "WiFi Pineapple с AliExpress: стоит ли?",
            "USB Rubber Ducky за копейки: обзор клонов",
            "Лучшие WiFi-адаптеры для Kali Linux",
            "Flipper Zero vs дешевые аналоги с AliExpress",
            "Сетевые анализаторы с AliExpress: топ-5",
            "HackRF vs RTL-SDR: что купить начинающему",
            "Raspberry Pi для хакинга: лучшие проекты",
            "ESP32: хакерские проекты для начинающих",
            "Лучшие powerbank для полевого хакинга",
            "Мини-компьютеры с AliExpress для пентеста",
            "Камеры безопасности: обзор и как их взламывают",
        ],
        hashtags_ru=[
            "aliexpress",
            "гаджеты",
            "хакерскиегаджеты",
            "обзор",
            "распаковка",
            "техника",
        ],
        hashtags_en=[
            "aliexpress",
            "hackergadgets",
            "techreview",
            "gadgets",
            "unboxing",
            "securitytools",
        ],
    ),
]


def get_pillar_by_name(name: str) -> ContentPillar | None:
    for p in PILLARS:
        if name.lower() in p.name.lower():
            return p
    return None


def all_topics_flat() -> list[tuple[str, str, str]]:
    """Возвращает (тема, название_столпа, реферальная_метка)."""
    return [
        (topic, pillar.name, pillar.referral_label)
        for pillar in PILLARS
        for topic in pillar.topics
    ]
