"""Extended content bank — hooks, CTAs, caption frameworks, and story templates.

Provides a richer library of content building blocks that ready_posts.py
and other generators can draw from. Organized by content type and pillar.
"""

from __future__ import annotations

HOOKS_EXTENDED: list[str] = [
    "Это должен знать каждый, кто работает в IT...",
    "99% людей не знают об этом...",
    "Хакеры используют это каждый день. А ты?",
    "Я потратил 100 часов, чтобы ты не тратил ни одного.",
    "Стоп. Если ты не знаешь {keyword} — смотри до конца.",
    "Этот инструмент изменил мою карьеру навсегда.",
    "POV: ты впервые открываешь {keyword}",
    "3 ошибки новичка в {keyword}, которые стоят карьеры",
    "Тебя могут взломать за 5 минут. Вот как.",
    "Как зарабатывать на {keyword}? Рассказываю.",
    "Секрет, который не расскажут на обычных курсах.",
    "Ты точно не знал, что {keyword} умеет это.",
    "Бесплатно vs Платно: что реально работает в {keyword}",
    "Топ-инструмент для {keyword} в 2024 году",
    "Этот гаджет за $10 заменяет оборудование за $500",
    "Только не делай ЭТО в {keyword}. Серьёзно.",
    "Мой путь от нуля до профи в {keyword}",
    "Если бы я начинал с нуля — вот мой план на {keyword}",
    "Этот трюк экономит 10 часов в неделю.",
    "Все говорят про {keyword}. Но никто не показывает ЭТО.",
    "Один инструмент. Три минуты. Результат — шок.",
    "Почему 90% новичков бросают {keyword}?",
    "Проверь себя: ты знаешь эти 5 команд?",
    "Я перепробовал всё. Работает только это.",
    "Не трать деньги на курсы, пока не узнаешь ЭТО.",
    "Формула успеха в {keyword}: 3 шага",
    "Этот навык стоит $100K/год. И его можно освоить бесплатно.",
    "Серьёзно, почему об этом молчат?",
    "Один скрипт, который делает всю работу.",
    "Топ-3 ресурса для изучения {keyword} бесплатно",
]

CTA_COURSE_EXTENDED: list[str] = [
    "Хочешь освоить это на практике? Ссылка на курс в шапке профиля",
    "Подробнее в нашем курсе — ссылка в био",
    "Полный гайд в курсе. Переходи по ссылке в описании",
    "Начни учиться уже сегодня — ссылка в профиле",
    "Хватит смотреть, пора действовать. Курс в шапке",
    "Бесплатный урок доступен по ссылке в профиле",
    "Всё это и больше — в нашем курсе. Ссылка в био",
    "Хочешь разобраться глубже? Ссылка на курс в описании",
    "Получи доступ к полному курсу — ссылка в шапке",
    "Практика ждёт. Переходи по ссылке в профиле",
]

CTA_REFERRAL_EXTENDED: list[str] = [
    "Ссылка на гаджет в описании — проверено лично",
    "Заказывал через нашу ссылку — все пришло. Ссылка в био",
    "Берите по ссылке в описании, пока есть скидка",
    "Проверенный магазин — ссылка в шапке профиля",
    "Ссылка на товар — в первом закреплённом комментарии",
    "Берите по нашей ссылке и получите скидку",
    "Заказал 3 штуки — ни одного брака. Ссылка в био",
    "Цена упала — успей по ссылке в описании",
]

CTA_ENGAGE_EXTENDED: list[str] = [
    "Сохрани, чтобы не потерять! Ставь лайк",
    "Поделись с другом, которому это нужно",
    "Напиши в комменты, какой инструмент используешь ты",
    "Подписывайся, чтобы не пропустить следующий разбор",
    "Какую тему разобрать следующей? Пиши в комменты",
    "Согласен? Ставь огонёк в комментах",
    "Отправь другу, который ищет работу в IT",
    "Лайк, если хочешь вторую часть",
    "Сохраняй себе — пригодится через неделю",
    "Подписывайся — такой контент каждый день",
]

STORY_FRAMEWORKS: list[dict[str, str]] = [
    {
        "name": "problem_solution",
        "slide_1": "Проблема: {problem}",
        "slide_2": "Почему это важно",
        "slide_3": "Решение: {topic}",
        "slide_4": "Результат",
        "slide_5": "CTA: {cta}",
    },
    {
        "name": "step_by_step",
        "slide_1": "Как сделать {topic_lower}",
        "slide_2": "Шаг 1: Подготовка",
        "slide_3": "Шаг 2: Действие",
        "slide_4": "Шаг 3: Результат",
        "slide_5": "CTA: {cta}",
    },
    {
        "name": "myth_busting",
        "slide_1": "Миф: {myth}",
        "slide_2": "Правда: {topic}",
        "slide_3": "Доказательства",
        "slide_4": "Что делать",
        "slide_5": "CTA: {cta}",
    },
    {
        "name": "before_after",
        "slide_1": "До: без {topic_lower}",
        "slide_2": "Проблемы и боли",
        "slide_3": "После: с {topic_lower}",
        "slide_4": "Результаты",
        "slide_5": "CTA: {cta}",
    },
]

CAROUSEL_FRAMEWORKS: list[dict[str, str]] = [
    {
        "name": "listicle",
        "cover": "{hook}",
        "slide_2": "#{num_1}: {point_1}",
        "slide_3": "#{num_2}: {point_2}",
        "slide_4": "#{num_3}: {point_3}",
        "cta_slide": "{cta}",
    },
    {
        "name": "tutorial",
        "cover": "Как {topic_lower}",
        "slide_2": "Что понадобится",
        "slide_3": "Пошаговый процесс",
        "slide_4": "Результат + советы",
        "cta_slide": "{cta}",
    },
    {
        "name": "comparison",
        "cover": "{option_a} vs {option_b}",
        "slide_2": "Плюсы {option_a}",
        "slide_3": "Плюсы {option_b}",
        "slide_4": "Итог: что выбрать",
        "cta_slide": "{cta}",
    },
]

MYTHS_BY_NICHE: dict[str, list[str]] = {
    "Cyber Security": [
        "Mac нельзя взломать",
        "VPN полностью анонимен",
        "Хакерам нужен суперкомпьютер",
        "Антивирус защищает от всего",
    ],
    "Blue Team": [
        "Файрвол достаточно для защиты",
        "SIEM ловит все инциденты",
        "Маленькие компании не атакуют",
    ],
    "Red Team": [
        "Пентест = взлом",
        "Хакеры всегда используют 0-day",
        "Социальная инженерия — не настоящий хакинг",
    ],
    "Machine Learning": [
        "AI заменит всех программистов",
        "Нейросети думают как люди",
        "Для ML нужна GPU за $10K",
    ],
    "AliExpress": [
        "Дешёвое = некачественное",
        "С AliExpress всё идёт месяцами",
        "Все гаджеты там — подделки",
    ],
}

PROBLEMS_BY_NICHE: dict[str, list[str]] = {
    "Cyber Security": [
        "Данные утекают, а ты не знаешь",
        "Пароли — слабое звено",
        "Фишинг атакует каждый день",
    ],
    "Blue Team": [
        "Инциденты остаются незамеченными",
        "Логи не анализируются",
        "Команда не готова к реагированию",
    ],
    "Red Team": [
        "Вы не знаете свои уязвимости",
        "Тесты проходят, а атаки — нет",
        "Периметр защищён, а люди — нет",
    ],
    "Machine Learning": [
        "Модель работает, но не объясняет",
        "Данных много, инсайтов мало",
        "Автоматизация буксует без ML",
    ],
    "AliExpress": [
        "Оборудование стоит целое состояние",
        "Не знаешь, что купить для практики",
        "Купил не то — деньги на ветер",
    ],
}


def get_hooks(keyword: str, count: int = 5) -> list[str]:
    import random

    templates = list(HOOKS_EXTENDED)
    random.shuffle(templates)
    return [
        t.format(keyword=keyword) if "{keyword}" in t else t for t in templates[:count]
    ]


def get_ctas(product_type: str, count: int = 3) -> list[str]:
    import random

    if product_type == "course":
        pool = CTA_COURSE_EXTENDED + CTA_ENGAGE_EXTENDED
    else:
        pool = CTA_REFERRAL_EXTENDED + CTA_ENGAGE_EXTENDED
    random.shuffle(pool)
    return pool[:count]


def get_story_framework(topic: str, cta: str, niche: str = "") -> dict[str, str]:
    import random

    fw = random.choice(STORY_FRAMEWORKS).copy()
    niche_key = next(
        (k for k in PROBLEMS_BY_NICHE if k.lower() in niche.lower()),
        "",
    )
    problems = PROBLEMS_BY_NICHE.get(niche_key, ["Проблема, которую все игнорируют"])
    myths = MYTHS_BY_NICHE.get(niche_key, ["Популярное заблуждение"])

    replacements = {
        "{topic}": topic,
        "{topic_lower}": topic.lower(),
        "{cta}": cta,
        "{problem}": random.choice(problems),
        "{myth}": random.choice(myths),
    }
    for key, val in fw.items():
        for placeholder, replacement in replacements.items():
            val = val.replace(placeholder, replacement)
        fw[key] = val
    return fw
