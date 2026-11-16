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
| Хештег-движок (150 тегов, 5 пулов) | Готово | `smm/hashtag_engine.py` |
| Визуальный контент-календарь (HTML) | Готово | `smm/content_calendar_html.py` |
| Engagement-хуки (опросы, квизы, вопросы) | Готово | `smm/engagement_hooks.py` |
| Валидатор подписей (проверка по платформам) | Готово | `smm/caption_validator.py` |
| Генератор сторис-пакетов (5-7 слайдов) | Готово | `smm/story_generator.py` |
| Генератор каруселей (4-5 слайдов) | Готово | `smm/carousel_generator.py` |
| Контент-репёрпозер (кросс-платформа) | Готово | `smm/content_repurposer.py` |
| Оптимизатор расписания (тепловая карта) | Готово | `smm/posting_schedule_optimizer.py` |
| Генератор контент-серий (многодневные арки) | Готово | `smm/content_series.py` |
| Анализ конкурентов и гэпов | Готово | `smm/competitor_analysis.py` |
| Контент-стратегия (единый план) | Готово | `smm/content_strategy.py` |
| HTML-дашборд (единая панель управления) | Готово | `smm/dashboard.py` |
| Конверсионная воронка (TOFU/MOFU/BOFU) | Готово | `smm/conversion_funnel.py` |
| UGC-шаблоны (отзывы, кейсы, до/после) | Готово | `smm/ugc_templates.py` |
| Контент-миксер (баланс типов по дням) | Готово | `smm/content_mixer.py` |
| Вирусные хуки (стоп-скролл контент) | Готово | `smm/viral_hooks.py` |
| Кросс-промо (перегонка трафика между платформами) | Готово | `smm/cross_promo.py` |
| Email-последовательности (welcome, nurture, abandon, upsell) | Готово | `smm/email_sequences.py` |
| Скоринг контента (приоритизация 0-100) | Готово | `smm/content_scoring.py` |
| Библиотека CTA (TOFU/MOFU/BOFU, 24 варианта) | Готово | `smm/cta_library.py` |
| Аналитика реферальных кампаний (UTM, ROAS) | Готово | `smm/referral_analytics.py` |
| A/B тестирование тем (75 пар, сплит-тесты) | Готово | `smm/topic_ab_test.py` |
| Профили целевой аудитории (5 персон) | Готово | `smm/audience_personas.py` |
| Лид-магниты (5 материалов для сбора email) | Готово | `smm/lead_magnet.py` |
| Социальное доказательство (отзывы, статистика, гарантии) | Готово | `smm/social_proof.py` |
| Контент-пайплайн (обогащение, скоринг, ранжирование) | Готово | `smm/content_pipeline.py` |
| Гайд по ретаргетингу (пиксели, аудитории, сегменты) | Готово | `smm/retargeting_guide.py` |
| Калькулятор стоимости и ROI (3 тарифа, проекции) | Готово | `smm/pricing_calculator.py` |
| Вебинарная воронка (invite→reminder→replay→sales) | Готово | `smm/webinar_funnel.py` |
| Telegram-бот (команды, FAQ, уведомления) | Готово | `smm/telegram_bot_config.py` |
| Авто-постинг (API-профили, слоты, retry, лимиты) | Готово | `smm/auto_poster.py` |
| Аналитический дашборд (KPI, ROI, прогноз роста) | Готово | `smm/analytics_dashboard.py` |
| Инфлюенсер-аутрич (шаблоны, критерии, коллаборации) | Готово | `smm/influencer_outreach.py` |
| Коммьюнити-менеджмент (ответы, ЛС, стримы, модерация) | Готово | `smm/community_manager.py` |
| SEO-оптимизация (ключевые слова, мета, YT, alt) | Готово | `smm/seo_optimizer.py` |
| CLI (61 команда) | Готово | `smm/cli.py` |
| Тесты | 459 passed | `tests/test_smm.py` |
| Интеграция постинга (API) | Ожидает | — |
| Реальные URL/ключи | Ожидает | — |

*AI-райтер требует API-ключ (пункт 3)
