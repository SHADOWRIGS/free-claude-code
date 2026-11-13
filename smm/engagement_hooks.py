"""Engagement hooks — polls, quizzes, questions for audience interaction.

Generates interactive elements that boost engagement metrics:
- Polls (Instagram/TikTok stories)
- Quiz questions (with correct answers for story quizzes)
- Discussion questions (for captions and comments)
- This-or-That comparisons
- Challenge prompts

Each hook is tied to a content pillar for relevance.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

POLLS_BY_PILLAR: dict[str, list[dict[str, Any]]] = {
    "Cyber Security & Ethical Hacking": [
        {
            "question": "Какой язык лучше для хакинга?",
            "options": ["Python", "Bash", "Go", "C"],
        },
        {
            "question": "Какая ОС для пентеста?",
            "options": ["Kali Linux", "Parrot OS", "BlackArch", "Ubuntu"],
        },
        {
            "question": "Первый инструмент для новичка?",
            "options": ["Nmap", "Burp Suite", "Wireshark", "Metasploit"],
        },
        {
            "question": "CTF или Bug Bounty?",
            "options": ["CTF", "Bug Bounty", "Оба", "Ни то, ни другое"],
        },
    ],
    "Blue Team / Defensive Security": [
        {
            "question": "Лучший SIEM в 2024?",
            "options": ["Splunk", "Elastic SIEM", "QRadar", "Sentinel"],
        },
        {
            "question": "Zero Trust — это реально?",
            "options": [
                "Да, must-have",
                "Нет, маркетинг",
                "Частично",
                "Зависит от бюджета",
            ],
        },
        {
            "question": "Что важнее в SOC?",
            "options": ["Автоматизация", "Люди", "Процессы", "Всё вместе"],
        },
        {
            "question": "Антивирус ещё нужен?",
            "options": ["Обязательно", "EDR лучше", "Не нужен", "Зависит"],
        },
    ],
    "Red Team / Offensive Security": [
        {
            "question": "Лучший C2 фреймворк?",
            "options": ["Cobalt Strike", "Sliver", "Havoc", "Mythic"],
        },
        {
            "question": "Физический пентест — нужен?",
            "options": ["Обязательно", "Опционально", "Не нужен", "Зависит от скоупа"],
        },
        {
            "question": "AD атаки — что учить первым?",
            "options": ["Kerberoasting", "AS-REP Roast", "Pass-the-Hash", "BloodHound"],
        },
        {
            "question": "Социалка vs техника?",
            "options": [
                "Social Engineering",
                "Технический эксплойт",
                "50/50",
                "Зависит от цели",
            ],
        },
    ],
    "Machine Learning & AI": [
        {
            "question": "Лучший фреймворк для ML?",
            "options": ["PyTorch", "TensorFlow", "JAX", "scikit-learn"],
        },
        {
            "question": "LLM заменит программистов?",
            "options": ["Да, скоро", "Нет, никогда", "Частично", "Через 10 лет"],
        },
        {
            "question": "Что учить первым в ML?",
            "options": ["Линейная алгебра", "Python", "Статистика", "Нейросети"],
        },
        {
            "question": "RAG vs Fine-tuning?",
            "options": ["RAG", "Fine-tuning", "Оба", "Зависит от задачи"],
        },
    ],
    "AliExpress - Гаджеты": [
        {
            "question": "Бюджет на хакер-гаджет?",
            "options": ["До $10", "$10-30", "$30-50", "Больше $50"],
        },
        {
            "question": "Flipper Zero стоит своих денег?",
            "options": [
                "Да, must-have",
                "Нет, переоценён",
                "Есть альтернативы",
                "Не знаю",
            ],
        },
        {
            "question": "Лучший WiFi-адаптер?",
            "options": ["Alfa AWUS036ACH", "TP-Link", "Panda Wireless", "Другой"],
        },
        {
            "question": "ESP32 или Raspberry Pi?",
            "options": ["ESP32", "Raspberry Pi", "Оба", "Arduino"],
        },
    ],
}

QUIZ_BY_PILLAR: dict[str, list[dict[str, Any]]] = {
    "Cyber Security & Ethical Hacking": [
        {
            "question": "Какой порт у SSH?",
            "options": ["21", "22", "23", "80"],
            "correct": 1,
        },
        {
            "question": "Что такое SQL injection?",
            "options": ["Вирус", "Атака на БД", "Тип шифрования", "Протокол"],
            "correct": 1,
        },
        {
            "question": "Что делает Nmap?",
            "options": [
                "Взлом паролей",
                "Сканирование портов",
                "Перехват трафика",
                "DDoS",
            ],
            "correct": 1,
        },
    ],
    "Blue Team / Defensive Security": [
        {
            "question": "Что такое SIEM?",
            "options": [
                "Антивирус",
                "Управление событиями безопасности",
                "Файрвол",
                "VPN",
            ],
            "correct": 1,
        },
        {
            "question": "Что делает SOC-аналитик?",
            "options": [
                "Пишет код",
                "Мониторит угрозы",
                "Чинит принтеры",
                "Настраивает сеть",
            ],
            "correct": 1,
        },
        {
            "question": "MITRE ATT&CK — это...?",
            "options": ["Инструмент", "База знаний атак", "Сертификация", "Компания"],
            "correct": 1,
        },
    ],
    "Red Team / Offensive Security": [
        {
            "question": "Что такое lateral movement?",
            "options": [
                "Физическая атака",
                "Перемещение по сети",
                "Тип малвари",
                "Шифрование",
            ],
            "correct": 1,
        },
        {
            "question": "Mimikatz извлекает...?",
            "options": ["Файлы", "Учётные данные", "Логи", "Трафик"],
            "correct": 1,
        },
        {
            "question": "OSINT расшифровывается как...?",
            "options": [
                "Open Source INTelligence",
                "Online Security INTegrity",
                "Offensive Security INTrusion",
                "Open System INTerface",
            ],
            "correct": 0,
        },
    ],
    "Machine Learning & AI": [
        {
            "question": "Что такое epoch в ML?",
            "options": [
                "Один проход по данным",
                "Тип модели",
                "Метрика",
                "Функция потерь",
            ],
            "correct": 0,
        },
        {
            "question": "Transformer придумали в...?",
            "options": ["Google", "OpenAI", "Meta", "Microsoft"],
            "correct": 0,
        },
        {
            "question": "Что такое overfitting?",
            "options": ["Недообучение", "Переобучение", "Оптимизация", "Нормализация"],
            "correct": 1,
        },
    ],
    "AliExpress - Гаджеты": [
        {
            "question": "Flipper Zero работает на частоте...?",
            "options": ["Sub-1 GHz", "Только WiFi", "Bluetooth only", "5G"],
            "correct": 0,
        },
        {
            "question": "HackRF — это...?",
            "options": [
                "WiFi адаптер",
                "SDR приёмопередатчик",
                "GPS трекер",
                "USB хаб",
            ],
            "correct": 1,
        },
        {
            "question": "ESP32 создан компанией...?",
            "options": ["Espressif", "Arduino", "Raspberry Pi Foundation", "Intel"],
            "correct": 0,
        },
    ],
}

QUESTIONS_BY_PILLAR: dict[str, list[str]] = {
    "Cyber Security & Ethical Hacking": [
        "С какого инструмента ты начал свой путь в кибербезопасности?",
        "Какую сертификацию ты считаешь самой ценной?",
        "Что бы ты посоветовал новичку в кибербезопасности?",
        "Какой CTF запомнился больше всего?",
        "Python или Bash — что используешь чаще?",
    ],
    "Blue Team / Defensive Security": [
        "Какой алерт в SOC выводит тебя из себя больше всего?",
        "Автоматизация в SOC — что уже автоматизировал?",
        "Какой SIEM/EDR используешь на работе?",
        "Самый интересный инцидент, который ты расследовал?",
        "Что сложнее — настроить мониторинг или реагировать на инцидент?",
    ],
    "Red Team / Offensive Security": [
        "Самый интересный баг, который ты находил?",
        "Какой инструмент ты используешь чаще всего?",
        "Физический пентест — пробовал?",
        "Какой C2 фреймворк предпочитаешь?",
        "Red Team vs Penetration Testing — в чём разница для тебя?",
    ],
    "Machine Learning & AI": [
        "PyTorch или TensorFlow — и почему?",
        "Какую модель ты обучал последней?",
        "LLM изменили твою работу? Как?",
        "Самый крутой ML-проект, который ты видел?",
        "Что сложнее — собрать данные или обучить модель?",
    ],
    "AliExpress - Гаджеты": [
        "Какой гаджет с AliExpress стал твоим любимым?",
        "Сколько ты обычно тратишь на хакер-гаджеты?",
        "Какой гаджет ты хотел бы протестировать?",
        "Доставка с AliExpress — сколько ждал максимум?",
        "Самый бесполезный гаджет, который ты покупал?",
    ],
}

THIS_OR_THAT: dict[str, list[tuple[str, str]]] = {
    "Cyber Security & Ethical Hacking": [
        ("Kali Linux", "Parrot OS"),
        ("Bug Bounty", "CTF"),
        ("Black Hat", "White Hat"),
        ("Burp Suite", "OWASP ZAP"),
        ("Сертификация", "Самообучение"),
    ],
    "Blue Team / Defensive Security": [
        ("Splunk", "Elastic"),
        ("EDR", "Антивирус"),
        ("Cloud Security", "On-Premise"),
        ("Автоматизация", "Ручной анализ"),
        ("SOC Tier 1", "SOC Tier 3"),
    ],
    "Red Team / Offensive Security": [
        ("Cobalt Strike", "Sliver"),
        ("Социальная инженерия", "Технический эксплойт"),
        ("Active Directory", "Web Application"),
        ("OSINT", "Fuzzing"),
        ("Linux", "Windows"),
    ],
    "Machine Learning & AI": [
        ("PyTorch", "TensorFlow"),
        ("GPT", "Open Source LLM"),
        ("RAG", "Fine-tuning"),
        ("Computer Vision", "NLP"),
        ("Kaggle", "Реальные проекты"),
    ],
    "AliExpress - Гаджеты": [
        ("Flipper Zero", "HackRF"),
        ("ESP32", "Raspberry Pi"),
        ("Дешёвый гаджет", "Дорогой инструмент"),
        ("WiFi адаптер", "SDR"),
        ("Покупать сразу", "Ждать скидку"),
    ],
}


@dataclass(frozen=True, slots=True)
class EngagementHook:
    hook_type: str
    pillar: str
    content: str
    options: list[str]
    correct_index: int | None = None


def generate_poll(pillar_name: str, seed: int | None = None) -> EngagementHook:
    if seed is not None:
        random.seed(seed)
    polls = POLLS_BY_PILLAR.get(
        pillar_name, POLLS_BY_PILLAR["Cyber Security & Ethical Hacking"]
    )
    poll = random.choice(polls)
    return EngagementHook(
        hook_type="poll",
        pillar=pillar_name,
        content=str(poll["question"]),
        options=[str(o) for o in poll["options"]],
    )


def generate_quiz(pillar_name: str, seed: int | None = None) -> EngagementHook:
    if seed is not None:
        random.seed(seed)
    quizzes = QUIZ_BY_PILLAR.get(
        pillar_name, QUIZ_BY_PILLAR["Cyber Security & Ethical Hacking"]
    )
    quiz = random.choice(quizzes)
    return EngagementHook(
        hook_type="quiz",
        pillar=pillar_name,
        content=str(quiz["question"]),
        options=[str(o) for o in quiz["options"]],
        correct_index=int(quiz["correct"]),
    )


def generate_question(pillar_name: str, seed: int | None = None) -> str:
    if seed is not None:
        random.seed(seed)
    questions = QUESTIONS_BY_PILLAR.get(
        pillar_name, QUESTIONS_BY_PILLAR["Cyber Security & Ethical Hacking"]
    )
    return random.choice(questions)


def generate_this_or_that(pillar_name: str, seed: int | None = None) -> tuple[str, str]:
    if seed is not None:
        random.seed(seed)
    pairs = THIS_OR_THAT.get(
        pillar_name, THIS_OR_THAT["Cyber Security & Ethical Hacking"]
    )
    return random.choice(pairs)


def engagement_summary(pillar_name: str) -> str:
    polls = len(POLLS_BY_PILLAR.get(pillar_name, []))
    quizzes = len(QUIZ_BY_PILLAR.get(pillar_name, []))
    questions = len(QUESTIONS_BY_PILLAR.get(pillar_name, []))
    pairs = len(THIS_OR_THAT.get(pillar_name, []))
    total = polls + quizzes + questions + pairs
    return (
        f"Engagement-хуки для «{pillar_name}»:\n"
        f"  Опросы: {polls}\n"
        f"  Квизы: {quizzes}\n"
        f"  Вопросы: {questions}\n"
        f"  This-or-That: {pairs}\n"
        f"  Всего: {total}"
    )
