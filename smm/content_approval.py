"""Content approval workflow — review pipeline before publishing.

Generates structured approval configs:
- Workflow stages (draft → review → approve → schedule → publish)
- Role definitions (creator, reviewer, approver)
- Review checklists per content type
- SLA timers for each stage
- Rejection reasons and feedback templates
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

WORKFLOW_STAGES: list[dict[str, str | int]] = [
    {
        "stage": "draft",
        "name": "Черновик",
        "description": "Контент создан AI или вручную",
        "responsible": "creator",
        "sla_hours": 0,
        "next": "review",
    },
    {
        "stage": "review",
        "name": "Ревью",
        "description": "Проверка качества, тональности, фактов",
        "responsible": "reviewer",
        "sla_hours": 4,
        "next": "approve",
    },
    {
        "stage": "approve",
        "name": "Одобрение",
        "description": "Финальное утверждение владельцем",
        "responsible": "approver",
        "sla_hours": 12,
        "next": "schedule",
    },
    {
        "stage": "schedule",
        "name": "Планирование",
        "description": "Назначение даты и времени публикации",
        "responsible": "creator",
        "sla_hours": 2,
        "next": "publish",
    },
    {
        "stage": "publish",
        "name": "Публикация",
        "description": "Автоматическая отправка через API",
        "responsible": "system",
        "sla_hours": 0,
        "next": "done",
    },
]

ROLES: list[dict[str, str | list[str]]] = [
    {
        "role": "creator",
        "name": "Создатель контента",
        "permissions": [
            "создание черновиков",
            "редактирование черновиков",
            "планирование публикации",
        ],
        "description": "AI-генератор или SMM-менеджер",
    },
    {
        "role": "reviewer",
        "name": "Ревьюер",
        "permissions": [
            "просмотр черновиков",
            "добавление комментариев",
            "возврат на доработку",
        ],
        "description": "Проверяет качество и соответствие бренду",
    },
    {
        "role": "approver",
        "name": "Утверждающий",
        "permissions": [
            "финальное одобрение",
            "отклонение контента",
            "изменение приоритетов",
        ],
        "description": "Владелец аккаунта или руководитель",
    },
]

REVIEW_CHECKLISTS: list[dict[str, str | list[str]]] = [
    {
        "content_type": "post",
        "name": "Чеклист поста",
        "items": [
            "Соответствие бренд-гайду (цвета, тон)",
            "Грамматика и орфография",
            "CTA присутствует и корректен",
            "Хештеги релевантны (5-15 штук)",
            "Ссылка/UTM корректны",
            "Визуал соответствует формату платформы",
        ],
    },
    {
        "content_type": "video_script",
        "name": "Чеклист видео-скрипта",
        "items": [
            "Хук в первые 3 секунды",
            "Длительность соответствует платформе",
            "CTA в конце видео",
            "Субтитры предусмотрены",
            "Музыка без авторских претензий",
        ],
    },
    {
        "content_type": "story",
        "name": "Чеклист сторис",
        "items": [
            "5-7 слайдов (не больше)",
            "Первый слайд — хук",
            "Последний — CTA со свайпом",
            "Текст читаем на мобильном",
            "Стикеры/опросы для вовлечения",
        ],
    },
    {
        "content_type": "ad",
        "name": "Чеклист рекламы",
        "items": [
            "Целевая аудитория корректна",
            "Бюджет согласован",
            "Лендинг работает и загружается < 3с",
            "Пиксель/аналитика настроены",
            "Текст соответствует правилам площадки",
            "A/B варианты подготовлены",
        ],
    },
]

REJECTION_REASONS: list[dict[str, str]] = [
    {
        "code": "tone_mismatch",
        "name": "Несоответствие тональности",
        "template": "Тональность не соответствует гайду для {platform}. Нужно: {expected_tone}",
    },
    {
        "code": "factual_error",
        "name": "Фактическая ошибка",
        "template": "Обнаружена фактическая неточность: {detail}. Проверить и исправить.",
    },
    {
        "code": "missing_cta",
        "name": "Отсутствует CTA",
        "template": "В контенте нет призыва к действию. Добавить CTA: {suggested_cta}",
    },
    {
        "code": "brand_violation",
        "name": "Нарушение бренд-гайда",
        "template": "Нарушены правила бренда: {violation}. См. brand_kit.",
    },
    {
        "code": "quality_low",
        "name": "Низкое качество",
        "template": "Контент не прошёл проверку качества: {issues}. Переработать.",
    },
    {
        "code": "duplicate",
        "name": "Дубликат",
        "template": "Похожий контент уже опубликован {date}. Создать уникальный вариант.",
    },
]


@dataclass(frozen=True, slots=True)
class WorkflowStage:
    stage: str
    name: str
    description: str
    responsible: str
    sla_hours: int
    next: str


@dataclass(frozen=True, slots=True)
class Role:
    role: str
    name: str
    permissions: tuple[str, ...]
    description: str


@dataclass(frozen=True, slots=True)
class ReviewChecklist:
    content_type: str
    name: str
    items: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RejectionReason:
    code: str
    name: str
    template: str


@dataclass(frozen=True, slots=True)
class ContentApprovalWorkflow:
    stages: tuple[WorkflowStage, ...]
    roles: tuple[Role, ...]
    checklists: tuple[ReviewChecklist, ...]
    rejection_reasons: tuple[RejectionReason, ...]


def generate_approval_workflow() -> ContentApprovalWorkflow:
    return ContentApprovalWorkflow(
        stages=tuple(
            WorkflowStage(
                stage=s["stage"],
                name=s["name"],
                description=s["description"],
                responsible=s["responsible"],
                sla_hours=int(s["sla_hours"]),
                next=s["next"],
            )
            for s in WORKFLOW_STAGES
        ),
        roles=tuple(
            Role(
                role=r["role"],
                name=r["name"],
                permissions=tuple(r["permissions"]),
                description=r["description"],
            )
            for r in ROLES
        ),
        checklists=tuple(
            ReviewChecklist(
                content_type=c["content_type"],
                name=c["name"],
                items=tuple(c["items"]),
            )
            for c in REVIEW_CHECKLISTS
        ),
        rejection_reasons=tuple(
            RejectionReason(
                code=r["code"],
                name=r["name"],
                template=r["template"],
            )
            for r in REJECTION_REASONS
        ),
    )


def export_approval_json(wf: ContentApprovalWorkflow, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "stages": [
            {
                "stage": s.stage,
                "name": s.name,
                "description": s.description,
                "responsible": s.responsible,
                "sla_hours": s.sla_hours,
                "next": s.next,
            }
            for s in wf.stages
        ],
        "roles": [
            {
                "role": r.role,
                "name": r.name,
                "permissions": list(r.permissions),
                "description": r.description,
            }
            for r in wf.roles
        ],
        "checklists": [
            {
                "content_type": c.content_type,
                "name": c.name,
                "items": list(c.items),
            }
            for c in wf.checklists
        ],
        "rejection_reasons": [
            {"code": r.code, "name": r.name, "template": r.template}
            for r in wf.rejection_reasons
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_approval_txt(wf: ContentApprovalWorkflow, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "КОНТЕНТ-ВОРКФЛОУ — РЕВЬЮ И ОДОБРЕНИЕ",
        "=" * 60,
        "\n📋 ЭТАПЫ ВОРКФЛОУ",
        "━" * 50,
    ]
    for s in wf.stages:
        sla = f" (SLA: {s.sla_hours}ч)" if s.sla_hours > 0 else ""
        lines.append(f"\n  [{s.stage}] {s.name}{sla}")
        lines.append(f"    {s.description}")
        lines.append(f"    Ответственный: {s.responsible} → Далее: {s.next}")

    lines.append(f"\n{'━' * 50}")
    lines.append("👥 РОЛИ")
    lines.append("━" * 50)
    for r in wf.roles:
        lines.append(f"\n  [{r.role}] {r.name}")
        lines.append(f"    {r.description}")
        lines.extend(f"    • {p}" for p in r.permissions)

    lines.append(f"\n{'━' * 50}")
    lines.append("✅ ЧЕКЛИСТЫ РЕВЬЮ")
    lines.append("━" * 50)
    for c in wf.checklists:
        lines.append(f"\n  [{c.content_type}] {c.name}")
        lines.extend(f"    ☐ {item}" for item in c.items)

    lines.append(f"\n{'━' * 50}")
    lines.append("❌ ПРИЧИНЫ ОТКЛОНЕНИЯ")
    lines.append("━" * 50)
    for r in wf.rejection_reasons:
        lines.append(f"\n  [{r.code}] {r.name}")
        lines.append(f"    Шаблон: {r.template}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def approval_summary(wf: ContentApprovalWorkflow) -> str:
    return (
        f"Воркфлоу одобрения: "
        f"{len(wf.stages)} этапов, "
        f"{len(wf.roles)} ролей, "
        f"{len(wf.checklists)} чеклистов, "
        f"{len(wf.rejection_reasons)} причин отклонения"
    )
