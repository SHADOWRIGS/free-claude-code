# Быстрый старт: продвижение курсов и реферального канала

## Установка

```bash
cd free-claude-code
uv sync
```

## 1. Генерация недельного контент-плана

```bash
uv run -m smm.cli generate --days 7
```

Результат: 63 поста (9/день) по 5 направлениям в `smm_data/`.

## 2. Готовые посты по платформам

```bash
# Полный недельный пакет (все платформы сразу)
uv run -m smm.cli week-pack --days 7 --output smm_data/week

# Или по отдельности
uv run -m smm.cli distribute --output smm_data/dist
```

Выходные файлы:
- `instagram_posts.json` — подписи, хештеги, визуальные брифы
- `tiktok_posts.json` — скрипты, хуки, звуковые рекомендации
- `youtube_posts.json` — названия, описания, теги, скрипты, брифы миниатюр

## 3. Хештеги

```bash
uv run -m smm.cli hashtags --pillar "Cyber Security" --output smm_data/tags.json
```

## 4. Карусели и сторис

```bash
uv run -m smm.cli carousel --pillar "Red Team" --output smm_data/carousel.json
uv run -m smm.cli stories --pillar "Blue Team" --output smm_data/stories.json
```

## 5. Экспорт в планировщики

```bash
# Buffer CSV
uv run -m smm.cli scheduler-export --format buffer --output smm_data/buffer.csv

# iCal (для Google Calendar)
uv run -m smm.cli scheduler-export --format ical --output smm_data/calendar.ics

# Notion JSON
uv run -m smm.cli scheduler-export --format notion --output smm_data/notion.json
```

## 6. Лендинг и коммерческое предложение

```bash
# Лендинг услуги
uv run -m smm.cli landing --output smm_data/landing.html

# КП для клиента
uv run -m smm.cli proposal --client "Acme Corp" --niche cybersecurity --output smm_data/proposal.html
```

## 7. Аналитический дашборд

```bash
uv run -m smm.cli analytics-dash --output smm_data/dashboard.json
```

---

## Продвижение курсов

Каждый пост автоматически содержит CTA со ссылкой на соответствующий курс:

| Направление | Курс | Ссылка |
|---|---|---|
| Cyber Security & Ethical Hacking | Основной курс | `shadowrigs.com/courses/cybersecurity` |
| Blue Team / Defensive Security | Защитный курс | `shadowrigs.com/courses/blue-team` |
| Red Team / Offensive Security | Наступательный курс | `shadowrigs.com/courses/red-team` |
| Machine Learning & AI | ML-курс | `shadowrigs.com/courses/machine-learning` |

> **Нужно решение:** заменить placeholder-ссылки на реальные URL лендингов курсов.

## Продвижение реферального канала (AliExpress)

Посты с направлением "AliExpress — Гаджеты" содержат реферальные ссылки с UTM-метками.
Формат: `aliexpress.com/store/shadowrigs?utm_source=instagram&utm_medium=social&utm_campaign=gadgets`

> **Нужно решение:** заменить placeholder на реальную партнёрскую ссылку AliExpress.

## Рабочий цикл (еженедельно)

1. **Понедельник** — `uv run -m smm.cli week-pack --days 7` (генерация)
2. **Понедельник** — `uv run -m smm.cli scheduler-export --format buffer` (экспорт в Buffer)
3. **Ежедневно** — публикация по расписанию (09:00/13:00/18:00 IG, 08:00/12:00/20:00 TT, 10:00/14:00/17:00 YT)
4. **Пятница** — `uv run -m smm.cli report` (аналитика за неделю)

## Полный список команд

Всего 91 CLI-команда. Основные:

```
plan, generate, write, distribute, week-pack, batch,
hashtags, carousel, stories, landing, proposal,
scheduler-export, preview, report, dashboard,
referral, ab-test, validate, repurpose, cross-promo,
emails, ctas, auto-poster, benchmark, calendar
```

Полный список: `uv run -m smm.cli --help`
