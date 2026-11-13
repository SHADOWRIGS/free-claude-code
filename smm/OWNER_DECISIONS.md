# Нужно решение владельца

## Высокий приоритет

1. **Реальные URL курсов** — сейчас используются placeholder-ы:
   - `https://shadowrigs.com/courses/cybersecurity`
   - `https://shadowrigs.com/courses/blue-team`
   - `https://shadowrigs.com/courses/red-team`
   - `https://shadowrigs.com/courses/machine-learning`
   → Нужны реальные URL лендингов

2. **Реальные реферальные ссылки AliExpress** — сейчас:
   - `https://aliexpress.com/store/shadowrigs`
   - `https://aliexpress.com/store/shadowrigs-network`
   → Нужны реальные партнерские ссылки

3. **API-ключ для AI-генерации** — команда `write` требует:
   - `SMM_API_BASE` (по умолчанию `http://localhost:4444`)
   - `SMM_API_KEY`
   → Решить, какой endpoint использовать (free-claude-code proxy?)

## Средний приоритет

4. **Ценообразование услуги** — предложены тарифы:
   - Starter: $97/мес (21 пост/нед, 1 платформа)
   - Growth: $197/мес (42 поста/нед, 2 платформы)
   - Pro: $397/мес (63 поста/нед, 3 платформы)
   → Утвердить/скорректировать цены

5. **Аккаунты соцсетей** — для реального постинга нужны:
   - Instagram Business API token
   - TikTok API credentials
   - YouTube API key + OAuth
   → Какие аккаунты использовать?

6. **Инструмент для постинга** — варианты интеграции:
   - Buffer / Later / Hootsuite API
   - Meta Business Suite (Instagram)
   - TikTok Creator Tools
   → Какой инструмент предпочтительнее?

## Низкий приоритет

7. **Брендинг** — ShadowRigs или другое название для SMM-услуги?
8. **Язык контента** — только русский или двуязычный (RU + EN)?
9. **Частота генерации** — 63 поста/нед достаточно или нужно больше/меньше?
10. **Telegram-контакт** — `https://t.me/shadowrigs` на лендинге верный?

## Статус реализации

| Модуль | Статус | Файл |
|---|---|---|
| Контент-столпы (5 направлений, 79 тем) | Готово | `smm/content_pillars.py` |
| Генератор плана (63 поста/нед) | Готово | `smm/post_generator.py` |
| Реферальная система (UTM-трекинг) | Готово | `smm/referral.py` |
| AI-райтер (Anthropic API) | Готово* | `smm/ai_writer.py` |
| Дистрибутор (пакеты IG/TT/YT) | Готово | `smm/distributor.py` |
| Спецификация услуги (3 тарифа) | Готово | `smm/service_spec.py` |
| Визуальное превью постов | Готово | `smm/preview.py` |
| Аналитика и отчётность | Готово | `smm/analytics.py` |
| Лендинг услуги (HTML) | Готово | `smm/landing.py` |
| Батч-генератор готовых постов | Готово | `smm/ready_posts.py` |
| Экспорт в планировщики (Buffer/Later/Meta/iCal/Notion) | Готово | `smm/scheduler_export.py` |
| Коммерческое предложение (HTML) | Готово | `smm/proposal.py` |
| Контент-банк (хуки, CTA, сторис, карусели) | Готово | `smm/content_bank.py` |
| Биолинк-страница (Linktree-аналог) | Готово | `smm/biolink.py` |
| Недельный пакет контента (all-in-one) | Готово | `smm/week_pack.py` |
| A/B тестирование подписей | Готово | `smm/ab_variants.py` |
| CLI (21 команда) | Готово | `smm/cli.py` |
| Тесты | 140 passed | `tests/test_smm.py` |
| Интеграция постинга (API) | Ожидает | — |
| Реальные URL/ключи | Ожидает | — |

*AI-райтер требует API-ключ (пункт 3)
