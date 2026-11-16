"""Crisis management — social media incident response protocols.

Generates structured crisis configs:
- Crisis types and severity levels
- Response templates per crisis type
- Communication protocols
- Recovery action plans
- Post-crisis review checklists
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CRISIS_TYPES: list[dict[str, str]] = [
    {
        "type": "negative_viral",
        "name": "Вирусный негатив",
        "severity": "high",
        "description": "Негативный пост/комментарий набирает массовое распространение",
        "response_time": "1 час",
    },
    {
        "type": "data_breach_rumor",
        "name": "Слухи об утечке данных",
        "severity": "critical",
        "description": "Обвинения в утечке данных студентов/клиентов",
        "response_time": "30 минут",
    },
    {
        "type": "content_error",
        "name": "Ошибка в контенте",
        "severity": "medium",
        "description": "Фактическая ошибка, устаревшая информация, неверная ссылка",
        "response_time": "2 часа",
    },
    {
        "type": "account_hack",
        "name": "Взлом аккаунта",
        "severity": "critical",
        "description": "Несанкционированный доступ к аккаунту соцсети",
        "response_time": "15 минут",
    },
    {
        "type": "competitor_attack",
        "name": "Атака конкурентов",
        "severity": "medium",
        "description": "Целенаправленная дискредитация со стороны конкурентов",
        "response_time": "4 часа",
    },
    {
        "type": "platform_ban",
        "name": "Бан платформы",
        "severity": "high",
        "description": "Блокировка аккаунта или контента платформой",
        "response_time": "1 час",
    },
]

RESPONSE_TEMPLATES: list[dict[str, str]] = [
    {
        "crisis_type": "negative_viral",
        "stage": "immediate",
        "template": (
            "Мы видим ваши отзывы и относимся к ним серьёзно. "
            "Разбираемся в ситуации и вернёмся с ответом в течение {timeframe}."
        ),
    },
    {
        "crisis_type": "negative_viral",
        "stage": "follow_up",
        "template": (
            "Мы изучили ситуацию. {explanation}. "
            "Вот что мы делаем: {action_plan}. "
            "Благодарим за обратную связь — она помогает нам стать лучше."
        ),
    },
    {
        "crisis_type": "data_breach_rumor",
        "stage": "immediate",
        "template": (
            "Мы в курсе сообщений о возможной утечке данных. "
            "Безопасность наших студентов — приоритет №1. "
            "Проводим срочную проверку и сообщим результаты."
        ),
    },
    {
        "crisis_type": "content_error",
        "stage": "immediate",
        "template": (
            "Спасибо, что заметили! "
            "Исправляем информацию. Корректная версия: {correction}."
        ),
    },
    {
        "crisis_type": "account_hack",
        "stage": "immediate",
        "template": (
            "Мы обнаружили несанкционированную активность и "
            "восстанавливаем контроль. "
            "Любые посты за последние {hours}ч могут быть не от нас."
        ),
    },
    {
        "crisis_type": "platform_ban",
        "stage": "immediate",
        "template": (
            "Наш аккаунт на {platform} временно недоступен. "
            "Мы работаем над восстановлением. "
            "Следите за обновлениями в {alt_platform}."
        ),
    },
]

PROTOCOLS: list[dict[str, str | list[str]]] = [
    {
        "name": "Мониторинг",
        "description": "Постоянное отслеживание упоминаний и настроений",
        "steps": [
            "Настроить алерты на бренд-упоминания",
            "Мониторить комментарии каждые 30 минут",
            "Отслеживать хештеги и ключевые слова",
            "Проверять директ-сообщения",
        ],
    },
    {
        "name": "Эскалация",
        "description": "Порядок информирования при обнаружении кризиса",
        "steps": [
            "SMM-менеджер фиксирует инцидент",
            "Уведомить владельца в течение 15 минут",
            "Собрать факты и контекст",
            "Определить severity и выбрать шаблон ответа",
        ],
    },
    {
        "name": "Коммуникация",
        "description": "Правила общения во время кризиса",
        "steps": [
            "Не удалять негативные комментарии (кроме спама)",
            "Отвечать от имени бренда, не лично",
            "Факты > эмоции",
            "Один голос — все ответы согласованы",
            "Не обвинять и не оправдываться",
        ],
    },
    {
        "name": "Восстановление",
        "description": "Действия после стабилизации ситуации",
        "steps": [
            "Опубликовать итоговое заявление",
            "Вернуться к обычному графику постинга",
            "Запустить позитивный контент (кейсы, отзывы)",
            "Провести ретроспективу команды",
        ],
    },
]

RECOVERY_ACTIONS: list[dict[str, str | int]] = [
    {
        "action": "Позитивный контент-блиц",
        "description": "3-5 позитивных постов (кейсы, отзывы, достижения)",
        "timeline_days": 3,
        "priority": "high",
    },
    {
        "action": "Опрос аудитории",
        "description": "Спросить подписчиков, что им нравится и что улучшить",
        "timeline_days": 7,
        "priority": "medium",
    },
    {
        "action": "Эксклюзивный контент",
        "description": "Бесплатный вебинар/гайд для восстановления лояльности",
        "timeline_days": 14,
        "priority": "high",
    },
    {
        "action": "Партнёрские посты",
        "description": "Коллаборации с авторитетными аккаунтами для доверия",
        "timeline_days": 21,
        "priority": "medium",
    },
    {
        "action": "Аналитический отчёт",
        "description": "Оценить влияние кризиса на метрики, выводы на будущее",
        "timeline_days": 30,
        "priority": "low",
    },
]


@dataclass(frozen=True, slots=True)
class CrisisType:
    type: str
    name: str
    severity: str
    description: str
    response_time: str


@dataclass(frozen=True, slots=True)
class ResponseTemplate:
    crisis_type: str
    stage: str
    template: str


@dataclass(frozen=True, slots=True)
class Protocol:
    name: str
    description: str
    steps: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RecoveryAction:
    action: str
    description: str
    timeline_days: int
    priority: str


@dataclass(frozen=True, slots=True)
class CrisisManagement:
    crisis_types: tuple[CrisisType, ...]
    response_templates: tuple[ResponseTemplate, ...]
    protocols: tuple[Protocol, ...]
    recovery_actions: tuple[RecoveryAction, ...]


def generate_crisis_management() -> CrisisManagement:
    return CrisisManagement(
        crisis_types=tuple(
            CrisisType(
                type=c["type"],
                name=c["name"],
                severity=c["severity"],
                description=c["description"],
                response_time=c["response_time"],
            )
            for c in CRISIS_TYPES
        ),
        response_templates=tuple(
            ResponseTemplate(
                crisis_type=r["crisis_type"],
                stage=r["stage"],
                template=r["template"],
            )
            for r in RESPONSE_TEMPLATES
        ),
        protocols=tuple(
            Protocol(
                name=p["name"],
                description=p["description"],
                steps=tuple(p["steps"]),
            )
            for p in PROTOCOLS
        ),
        recovery_actions=tuple(
            RecoveryAction(
                action=a["action"],
                description=a["description"],
                timeline_days=int(a["timeline_days"]),
                priority=a["priority"],
            )
            for a in RECOVERY_ACTIONS
        ),
    )


def export_crisis_json(cm: CrisisManagement, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "crisis_types": [
            {
                "type": c.type,
                "name": c.name,
                "severity": c.severity,
                "description": c.description,
                "response_time": c.response_time,
            }
            for c in cm.crisis_types
        ],
        "response_templates": [
            {
                "crisis_type": r.crisis_type,
                "stage": r.stage,
                "template": r.template,
            }
            for r in cm.response_templates
        ],
        "protocols": [
            {
                "name": p.name,
                "description": p.description,
                "steps": list(p.steps),
            }
            for p in cm.protocols
        ],
        "recovery_actions": [
            {
                "action": a.action,
                "description": a.description,
                "timeline_days": a.timeline_days,
                "priority": a.priority,
            }
            for a in cm.recovery_actions
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_crisis_txt(cm: CrisisManagement, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "АНТИКРИЗИСНОЕ УПРАВЛЕНИЕ — ПРОТОКОЛЫ РЕАГИРОВАНИЯ",
        "=" * 60,
        "\n🚨 ТИПЫ КРИЗИСОВ",
        "━" * 50,
    ]
    for c in cm.crisis_types:
        lines.append(f"\n  [{c.type}] {c.name} ({c.severity})")
        lines.append(f"    {c.description}")
        lines.append(f"    Время реакции: {c.response_time}")

    lines.append(f"\n{'━' * 50}")
    lines.append("💬 ШАБЛОНЫ ОТВЕТОВ")
    lines.append("━" * 50)
    for r in cm.response_templates:
        lines.append(f"\n  [{r.crisis_type} → {r.stage}]")
        lines.append(f"    {r.template}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📋 ПРОТОКОЛЫ")
    lines.append("━" * 50)
    for p in cm.protocols:
        lines.append(f"\n  [{p.name}] {p.description}")
        lines.extend(f"    {i + 1}. {step}" for i, step in enumerate(p.steps))

    lines.append(f"\n{'━' * 50}")
    lines.append("🔄 ПЛАН ВОССТАНОВЛЕНИЯ")
    lines.append("━" * 50)
    for a in cm.recovery_actions:
        lines.append(f"\n  [{a.priority}] {a.action} (до {a.timeline_days} дней)")
        lines.append(f"    {a.description}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def crisis_summary(cm: CrisisManagement) -> str:
    return (
        f"Антикризисный план: "
        f"{len(cm.crisis_types)} типов кризисов, "
        f"{len(cm.response_templates)} шаблонов ответов, "
        f"{len(cm.protocols)} протоколов, "
        f"{len(cm.recovery_actions)} действий восстановления"
    )
