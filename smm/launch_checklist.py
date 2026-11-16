"""Launch checklist — step-by-step guide for going live.

Generates a structured pre-launch checklist covering:
- Account setup (IG, TikTok, YT, Telegram)
- Content pipeline readiness
- API/tool integration status
- Referral link verification
- First-week execution plan
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CHECKLIST_PHASES: tuple[str, ...] = (
    "accounts",
    "content",
    "tools",
    "referral",
    "launch",
)

CHECKLIST_ITEMS: list[dict[str, str]] = [
    # Phase: accounts
    {
        "phase": "accounts",
        "item": "Instagram Business аккаунт создан и оптимизирован",
        "details": "Био, аватар, ссылка в Linktree, категория бизнеса",
        "status": "pending",
        "priority": "high",
    },
    {
        "phase": "accounts",
        "item": "TikTok Pro аккаунт создан",
        "details": "Био, ссылка на курсы, бизнес-профиль",
        "status": "pending",
        "priority": "high",
    },
    {
        "phase": "accounts",
        "item": "YouTube канал настроен",
        "details": "Описание, баннер, плейлисты по курсам, ссылки",
        "status": "pending",
        "priority": "high",
    },
    {
        "phase": "accounts",
        "item": "Telegram-бот запущен",
        "details": "BotFather, команды, welcome message, webhook",
        "status": "pending",
        "priority": "high",
    },
    {
        "phase": "accounts",
        "item": "Telegram-канал создан",
        "details": "Описание, закреп с навигацией, ссылки на курсы",
        "status": "pending",
        "priority": "medium",
    },
    # Phase: content
    {
        "phase": "content",
        "item": "Недельный пакет контента сгенерирован",
        "details": "uv run -m smm.cli week-pack — 63 поста, видео-скрипты, визуальные брифы",
        "status": "ready",
        "priority": "high",
    },
    {
        "phase": "content",
        "item": "Лид-магниты готовы к раздаче",
        "details": "PDF чеклисты, roadmap, шпаргалки — загружены на хостинг",
        "status": "pending",
        "priority": "high",
    },
    {
        "phase": "content",
        "item": "Email-последовательности настроены",
        "details": "Welcome, nurture, abandon, upsell — в email-сервисе",
        "status": "pending",
        "priority": "medium",
    },
    {
        "phase": "content",
        "item": "Вебинарная воронка запущена",
        "details": "Invite → reminder → last_chance → replay → sales",
        "status": "pending",
        "priority": "medium",
    },
    {
        "phase": "content",
        "item": "SEO-оптимизация применена",
        "details": "Ключевые слова в описаниях, мета-теги на лендинге",
        "status": "ready",
        "priority": "medium",
    },
    # Phase: tools
    {
        "phase": "tools",
        "item": "Инструмент постинга подключён",
        "details": "Buffer / Later / Meta Business Suite — API токен настроен",
        "status": "pending",
        "priority": "high",
    },
    {
        "phase": "tools",
        "item": "Аналитика настроена",
        "details": "Instagram Insights, TikTok Analytics, YouTube Studio",
        "status": "pending",
        "priority": "medium",
    },
    {
        "phase": "tools",
        "item": "Пиксели ретаргетинга установлены",
        "details": "Meta Pixel, TikTok Pixel — на лендинге курсов",
        "status": "pending",
        "priority": "medium",
    },
    {
        "phase": "tools",
        "item": "UTM-трекинг проверен",
        "details": "Все реферальные ссылки с UTM-метками, отслеживание в GA4",
        "status": "ready",
        "priority": "high",
    },
    # Phase: referral
    {
        "phase": "referral",
        "item": "Лендинги курсов опубликованы",
        "details": "4 лендинга по курсам с формами оплаты/записи",
        "status": "pending",
        "priority": "high",
    },
    {
        "phase": "referral",
        "item": "Реферальные ссылки AliExpress активны",
        "details": "Партнёрские ссылки на гаджеты с UTM-трекингом",
        "status": "pending",
        "priority": "high",
    },
    {
        "phase": "referral",
        "item": "Биолинк-страница опубликована",
        "details": "Linktree-аналог со всеми ссылками — в био всех платформ",
        "status": "ready",
        "priority": "high",
    },
    # Phase: launch
    {
        "phase": "launch",
        "item": "Первая неделя постов запланирована",
        "details": "63 поста загружены в планировщик, время публикации проверено",
        "status": "pending",
        "priority": "high",
    },
    {
        "phase": "launch",
        "item": "Коммьюнити-скрипты готовы",
        "details": "Шаблоны ответов на комментарии, DM-автоответы настроены",
        "status": "ready",
        "priority": "medium",
    },
    {
        "phase": "launch",
        "item": "Инфлюенсер-аутрич начат",
        "details": "Первые 10 DM отправлены потенциальным партнёрам",
        "status": "pending",
        "priority": "low",
    },
    {
        "phase": "launch",
        "item": "Мониторинг запущен",
        "details": "Ежедневная проверка аналитики, еженедельный отчёт",
        "status": "pending",
        "priority": "medium",
    },
]

PHASE_LABELS: dict[str, str] = {
    "accounts": "📱 Настройка аккаунтов",
    "content": "📝 Контент-пайплайн",
    "tools": "🔧 Инструменты и интеграции",
    "referral": "🔗 Реферальные каналы",
    "launch": "🚀 Запуск первой недели",
}


@dataclass(frozen=True, slots=True)
class ChecklistItem:
    phase: str
    item: str
    details: str
    status: str
    priority: str


@dataclass(frozen=True, slots=True)
class LaunchChecklist:
    items: tuple[ChecklistItem, ...]
    total: int
    ready: int
    pending: int
    ready_percent: float


def generate_launch_checklist() -> LaunchChecklist:
    items = tuple(
        ChecklistItem(
            phase=c["phase"],
            item=c["item"],
            details=c["details"],
            status=c["status"],
            priority=c["priority"],
        )
        for c in CHECKLIST_ITEMS
    )
    total = len(items)
    ready = sum(1 for i in items if i.status == "ready")
    pending = total - ready
    pct = round((ready / total) * 100, 1) if total > 0 else 0.0
    return LaunchChecklist(
        items=items,
        total=total,
        ready=ready,
        pending=pending,
        ready_percent=pct,
    )


def export_checklist_json(checklist: LaunchChecklist, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "summary": {
            "total": checklist.total,
            "ready": checklist.ready,
            "pending": checklist.pending,
            "ready_percent": checklist.ready_percent,
        },
        "items": [
            {
                "phase": i.phase,
                "phase_label": PHASE_LABELS.get(i.phase, i.phase),
                "item": i.item,
                "details": i.details,
                "status": i.status,
                "priority": i.priority,
            }
            for i in checklist.items
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_checklist_txt(checklist: LaunchChecklist, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "ЧЕКЛИСТ ЗАПУСКА SMM-АВТОМАТИЗАЦИИ",
        "=" * 60,
        f"\n📊 Прогресс: {checklist.ready}/{checklist.total} "
        f"({checklist.ready_percent}% готово)",
        f"✅ Готово: {checklist.ready} | ⏳ Ожидает: {checklist.pending}",
    ]
    for phase in CHECKLIST_PHASES:
        label = PHASE_LABELS.get(phase, phase)
        phase_items = [i for i in checklist.items if i.phase == phase]
        lines.append(f"\n{'━' * 50}")
        lines.append(label)
        lines.append("━" * 50)
        for i in phase_items:
            icon = "✅" if i.status == "ready" else "⏳"
            prio = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(i.priority, "⚪")
            lines.append(f"  {icon} {prio} {i.item}")
            lines.append(f"       {i.details}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def checklist_summary(checklist: LaunchChecklist) -> str:
    return (
        f"Чеклист запуска: {checklist.ready}/{checklist.total} готово "
        f"({checklist.ready_percent}%), "
        f"{checklist.pending} ожидает действий владельца"
    )
