"""Influencer outreach templates and partnership configs.

Generates outreach messages, collaboration formats, and
tracking setup for influencer partnerships across pillars.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

COLLAB_TYPES: tuple[str, ...] = (
    "guest_post",
    "joint_live",
    "review",
    "giveaway",
    "affiliate",
)

COLLAB_LABELS: dict[str, str] = {
    "guest_post": "Гостевой пост / кросс-контент",
    "joint_live": "Совместный эфир / стрим",
    "review": "Обзор курса / гаджета",
    "giveaway": "Розыгрыш для аудитории",
    "affiliate": "Партнёрская программа (% от продаж)",
}

OUTREACH_TEMPLATES: dict[str, dict[str, str]] = {
    "cold_dm": {
        "subject": "Привет! Предложение о сотрудничестве",
        "body": (
            "Привет, {influencer_name}! 👋\n\n"
            "Слежу за твоим контентом по {niche} — крутой подход!\n\n"
            "Я развиваю проект ShadowRigs — онлайн-курсы по кибербезопасности и ML.\n"
            "Хотел бы предложить коллаборацию: {collab_type_label}.\n\n"
            "Формат гибкий — обсудим, что интересно обоим.\n"
            "Можно связаться: {contact_link}\n\n"
            "С уважением!"
        ),
    },
    "follow_up": {
        "subject": "Касательно сотрудничества — напоминание",
        "body": (
            "Привет, {influencer_name}!\n\n"
            "Писал недавно по поводу коллаборации. "
            "Понимаю, что ты занят(а) — "
            "просто хочу подтвердить интерес.\n\n"
            "Готов обсудить в любое удобное время.\n"
            "Контакт: {contact_link}"
        ),
    },
    "partnership_proposal": {
        "subject": "Предложение о партнёрстве — ShadowRigs",
        "body": (
            "Здравствуйте, {influencer_name}!\n\n"
            "Предлагаем партнёрскую программу:\n\n"
            "📌 Формат: {collab_type_label}\n"
            "📌 Ваша аудитория: {audience_size}+ подписчиков\n"
            "📌 Наши ресурсы: бесплатный доступ к курсу + {commission}% комиссии\n\n"
            "Детали и условия: {contact_link}\n\n"
            "Будем рады сотрудничеству!"
        ),
    },
}

IDEAL_INFLUENCER_CRITERIA: list[dict[str, str]] = [
    {
        "pillar": "Cyber Security & Ethical Hacking",
        "niche": "кибербезопасность, этичный хакинг, CTF",
        "min_followers": "5000",
        "platforms": "YouTube, Telegram, Twitter/X",
    },
    {
        "pillar": "Blue Team / Defensive Security",
        "niche": "SOC, SIEM, защита инфраструктуры",
        "min_followers": "3000",
        "platforms": "YouTube, LinkedIn, Telegram",
    },
    {
        "pillar": "Red Team / Offensive Security",
        "niche": "пентест, bug bounty, offensive tools",
        "min_followers": "5000",
        "platforms": "YouTube, Twitter/X, Telegram",
    },
    {
        "pillar": "Machine Learning & AI",
        "niche": "ML, data science, нейросети, AI",
        "min_followers": "10000",
        "platforms": "YouTube, Instagram, TikTok",
    },
    {
        "pillar": "AliExpress — Гаджеты",
        "niche": "гаджеты, техно-обзоры, DIY электроника",
        "min_followers": "10000",
        "platforms": "YouTube, TikTok, Instagram",
    },
]


@dataclass(frozen=True, slots=True)
class OutreachMessage:
    template_key: str
    subject: str
    body: str


@dataclass(frozen=True, slots=True)
class InfluencerCriteria:
    pillar: str
    niche: str
    min_followers: int
    platforms: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CollabFormat:
    key: str
    label: str


@dataclass(frozen=True, slots=True)
class InfluencerOutreach:
    messages: tuple[OutreachMessage, ...]
    criteria: tuple[InfluencerCriteria, ...]
    collab_formats: tuple[CollabFormat, ...]


def generate_outreach_messages() -> tuple[OutreachMessage, ...]:
    return tuple(
        OutreachMessage(
            template_key=key,
            subject=tmpl["subject"],
            body=tmpl["body"],
        )
        for key, tmpl in OUTREACH_TEMPLATES.items()
    )


def generate_influencer_criteria() -> tuple[InfluencerCriteria, ...]:
    return tuple(
        InfluencerCriteria(
            pillar=c["pillar"],
            niche=c["niche"],
            min_followers=int(c["min_followers"]),
            platforms=tuple(p.strip() for p in c["platforms"].split(",")),
        )
        for c in IDEAL_INFLUENCER_CRITERIA
    )


def generate_collab_formats() -> tuple[CollabFormat, ...]:
    return tuple(CollabFormat(key=k, label=v) for k, v in COLLAB_LABELS.items())


def generate_influencer_outreach() -> InfluencerOutreach:
    return InfluencerOutreach(
        messages=generate_outreach_messages(),
        criteria=generate_influencer_criteria(),
        collab_formats=generate_collab_formats(),
    )


def export_outreach_json(outreach: InfluencerOutreach, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "messages": [
            {
                "template_key": m.template_key,
                "subject": m.subject,
                "body": m.body,
            }
            for m in outreach.messages
        ],
        "criteria": [
            {
                "pillar": c.pillar,
                "niche": c.niche,
                "min_followers": c.min_followers,
                "platforms": list(c.platforms),
            }
            for c in outreach.criteria
        ],
        "collab_formats": [
            {"key": f.key, "label": f.label} for f in outreach.collab_formats
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_outreach_txt(outreach: InfluencerOutreach, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "ИНФЛЮЕНСЕР-АУТРИЧ — ШАБЛОНЫ И КРИТЕРИИ",
        "=" * 60,
        "\n📨 ШАБЛОНЫ СООБЩЕНИЙ",
        "━" * 50,
    ]
    for m in outreach.messages:
        lines.append(f"\n  [{m.template_key}]")
        lines.append(f"  Тема: {m.subject}")
        lines.extend(f"  {line}" for line in m.body.split("\n"))

    lines.append(f"\n{'━' * 50}")
    lines.append("🎯 КРИТЕРИИ ИНФЛЮЕНСЕРОВ")
    lines.append("━" * 50)
    for c in outreach.criteria:
        lines.append(f"\n  [{c.pillar}]")
        lines.append(f"    Ниша: {c.niche}")
        lines.append(f"    Мин. подписчиков: {c.min_followers:,}")
        lines.append(f"    Платформы: {', '.join(c.platforms)}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🤝 ФОРМАТЫ КОЛЛАБОРАЦИЙ")
    lines.append("━" * 50)
    lines.extend(f"  • {f.label}" for f in outreach.collab_formats)

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def outreach_summary(outreach: InfluencerOutreach) -> str:
    return (
        f"Инфлюенсер-аутрич: {len(outreach.messages)} шаблонов, "
        f"{len(outreach.criteria)} профилей, "
        f"{len(outreach.collab_formats)} форматов коллаборации"
    )
