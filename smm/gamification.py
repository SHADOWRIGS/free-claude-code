"""Gamification — subscriber engagement through achievements and challenges.

Generates structured gamification configs:
- Achievement badges for subscriber milestones
- Level progression system
- Weekly/monthly challenges
- Point system and rewards
- Leaderboard mechanics
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

BADGES: list[dict[str, str | int]] = [
    {
        "id": "first_comment",
        "name": "Первый комментарий",
        "description": "Оставь первый комментарий под постом",
        "icon": "💬",
        "points": 10,
    },
    {
        "id": "week_streak",
        "name": "Неделя вовлечённости",
        "description": "Реагируй на посты 7 дней подряд",
        "icon": "🔥",
        "points": 50,
    },
    {
        "id": "quiz_master",
        "name": "Мастер квизов",
        "description": "Ответь правильно на 10 квизов в сторис",
        "icon": "🧠",
        "points": 75,
    },
    {
        "id": "content_sharer",
        "name": "Амбассадор",
        "description": "Поделись нашим постом 5 раз",
        "icon": "📢",
        "points": 60,
    },
    {
        "id": "course_starter",
        "name": "Начало пути",
        "description": "Запишись на первый курс",
        "icon": "🎓",
        "points": 100,
    },
    {
        "id": "referral_hero",
        "name": "Реферальный герой",
        "description": "Приведи 3 друзей по реферальной ссылке",
        "icon": "🤝",
        "points": 150,
    },
    {
        "id": "gadget_buyer",
        "name": "Охотник за гаджетами",
        "description": "Купи гаджет по нашей ссылке AliExpress",
        "icon": "🛒",
        "points": 80,
    },
    {
        "id": "month_veteran",
        "name": "Ветеран сообщества",
        "description": "Будь активным подписчиком 30 дней",
        "icon": "⭐",
        "points": 200,
    },
]

LEVELS: list[dict[str, str | int]] = [
    {
        "level": 1,
        "name": "Новичок",
        "min_points": 0,
        "perks": "Доступ к бесплатным материалам",
        "icon": "🌱",
    },
    {
        "level": 2,
        "name": "Исследователь",
        "min_points": 100,
        "perks": "Скидка 5% на курсы, эксклюзивные посты",
        "icon": "🔍",
    },
    {
        "level": 3,
        "name": "Хакер",
        "min_points": 300,
        "perks": "Скидка 10%, доступ к закрытому чату",
        "icon": "💻",
    },
    {
        "level": 4,
        "name": "Эксперт",
        "min_points": 600,
        "perks": "Скидка 15%, ранний доступ к курсам",
        "icon": "🏆",
    },
    {
        "level": 5,
        "name": "Легенда",
        "min_points": 1000,
        "perks": "Скидка 25%, менторство, бейдж в профиле",
        "icon": "👑",
    },
]

CHALLENGES: list[dict[str, str | int]] = [
    {
        "id": "weekly_quiz",
        "name": "Квиз недели",
        "type": "weekly",
        "description": "Ответь на 5 вопросов по кибербезопасности",
        "reward_points": 30,
        "pillar": "Cyber Security & Ethical Hacking",
    },
    {
        "id": "share_challenge",
        "name": "Расскажи другу",
        "type": "weekly",
        "description": "Поделись постом и отметь друга",
        "reward_points": 20,
        "pillar": "all",
    },
    {
        "id": "ctf_mini",
        "name": "Мини-CTF",
        "type": "monthly",
        "description": "Реши 3 задачи из нашего CTF-челленджа",
        "reward_points": 100,
        "pillar": "Red Team / Offensive Security",
    },
    {
        "id": "blue_team_drill",
        "name": "Учебная тревога",
        "type": "monthly",
        "description": "Пройди симуляцию инцидента за 15 минут",
        "reward_points": 80,
        "pillar": "Blue Team / Defensive Security",
    },
    {
        "id": "ml_project",
        "name": "ML-проект недели",
        "type": "weekly",
        "description": "Построй мини-модель и покажи результат",
        "reward_points": 50,
        "pillar": "Machine Learning & AI",
    },
    {
        "id": "gadget_review",
        "name": "Обзор гаджета",
        "type": "monthly",
        "description": "Сними обзор купленного гаджета",
        "reward_points": 70,
        "pillar": "AliExpress",
    },
]

REWARDS: list[dict[str, str | int]] = [
    {
        "id": "discount_5",
        "name": "Скидка 5%",
        "cost_points": 100,
        "type": "discount",
        "description": "На любой курс",
    },
    {
        "id": "discount_10",
        "name": "Скидка 10%",
        "cost_points": 250,
        "type": "discount",
        "description": "На любой курс",
    },
    {
        "id": "free_module",
        "name": "Бесплатный модуль",
        "cost_points": 500,
        "type": "access",
        "description": "Доступ к одному платному модулю",
    },
    {
        "id": "mentor_session",
        "name": "Сессия с ментором",
        "cost_points": 750,
        "type": "service",
        "description": "30-минутная консультация",
    },
    {
        "id": "full_course",
        "name": "Полный курс",
        "cost_points": 1500,
        "type": "access",
        "description": "Бесплатный доступ к любому курсу",
    },
]

LEADERBOARD_RULES: dict[str, str] = {
    "reset": "Еженедельный сброс (Пн 00:00 MSK)",
    "top_3_prize": "Топ-3 получают эксклюзивный бейдж недели",
    "display": "Показывать топ-10 в сторис каждое воскресенье",
    "anti_cheat": "Только уникальные действия, лимит 50 очков/день",
    "tie_breaker": "При равенстве — кто набрал раньше",
}


@dataclass(frozen=True, slots=True)
class Badge:
    id: str
    name: str
    description: str
    icon: str
    points: int


@dataclass(frozen=True, slots=True)
class Level:
    level: int
    name: str
    min_points: int
    perks: str
    icon: str


@dataclass(frozen=True, slots=True)
class Challenge:
    id: str
    name: str
    type: str
    description: str
    reward_points: int
    pillar: str


@dataclass(frozen=True, slots=True)
class Reward:
    id: str
    name: str
    cost_points: int
    type: str
    description: str


@dataclass(frozen=True, slots=True)
class GamificationSystem:
    badges: tuple[Badge, ...]
    levels: tuple[Level, ...]
    challenges: tuple[Challenge, ...]
    rewards: tuple[Reward, ...]
    leaderboard_rules: dict[str, str]


def generate_gamification() -> GamificationSystem:
    return GamificationSystem(
        badges=tuple(
            Badge(
                id=b["id"],
                name=b["name"],
                description=b["description"],
                icon=b["icon"],
                points=int(b["points"]),
            )
            for b in BADGES
        ),
        levels=tuple(
            Level(
                level=int(lv["level"]),
                name=lv["name"],
                min_points=int(lv["min_points"]),
                perks=lv["perks"],
                icon=lv["icon"],
            )
            for lv in LEVELS
        ),
        challenges=tuple(
            Challenge(
                id=c["id"],
                name=c["name"],
                type=c["type"],
                description=c["description"],
                reward_points=int(c["reward_points"]),
                pillar=c["pillar"],
            )
            for c in CHALLENGES
        ),
        rewards=tuple(
            Reward(
                id=r["id"],
                name=r["name"],
                cost_points=int(r["cost_points"]),
                type=r["type"],
                description=r["description"],
            )
            for r in REWARDS
        ),
        leaderboard_rules=dict(LEADERBOARD_RULES),
    )


def export_gamification_json(gs: GamificationSystem, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "badges": [
            {
                "id": b.id,
                "name": b.name,
                "description": b.description,
                "icon": b.icon,
                "points": b.points,
            }
            for b in gs.badges
        ],
        "levels": [
            {
                "level": lv.level,
                "name": lv.name,
                "min_points": lv.min_points,
                "perks": lv.perks,
                "icon": lv.icon,
            }
            for lv in gs.levels
        ],
        "challenges": [
            {
                "id": c.id,
                "name": c.name,
                "type": c.type,
                "description": c.description,
                "reward_points": c.reward_points,
                "pillar": c.pillar,
            }
            for c in gs.challenges
        ],
        "rewards": [
            {
                "id": r.id,
                "name": r.name,
                "cost_points": r.cost_points,
                "type": r.type,
                "description": r.description,
            }
            for r in gs.rewards
        ],
        "leaderboard_rules": gs.leaderboard_rules,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_gamification_txt(gs: GamificationSystem, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "ГЕЙМИФИКАЦИЯ — СИСТЕМА ВОВЛЕЧЕНИЯ ПОДПИСЧИКОВ",
        "=" * 60,
        "\n🏅 БЕЙДЖИ И ДОСТИЖЕНИЯ",
        "━" * 50,
    ]
    for b in gs.badges:
        lines.append(f"\n  {b.icon} [{b.id}] {b.name} (+{b.points} очков)")
        lines.append(f"    {b.description}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📊 УРОВНИ ПРОГРЕССИИ")
    lines.append("━" * 50)
    for lv in gs.levels:
        lines.append(
            f"\n  {lv.icon} Уровень {lv.level}: {lv.name} (от {lv.min_points} очков)"
        )
        lines.append(f"    Привилегии: {lv.perks}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🎯 ЧЕЛЛЕНДЖИ")
    lines.append("━" * 50)
    for c in gs.challenges:
        lines.append(f"\n  [{c.type}] {c.name} (+{c.reward_points} очков)")
        lines.append(f"    {c.description}")
        lines.append(f"    Направление: {c.pillar}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🎁 НАГРАДЫ")
    lines.append("━" * 50)
    for r in gs.rewards:
        lines.append(f"\n  [{r.type}] {r.name} ({r.cost_points} очков)")
        lines.append(f"    {r.description}")

    lines.append(f"\n{'━' * 50}")
    lines.append("🏆 ПРАВИЛА ЛИДЕРБОРДА")
    lines.append("━" * 50)
    for key, val in gs.leaderboard_rules.items():
        lines.append(f"  {key}: {val}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def gamification_summary(gs: GamificationSystem) -> str:
    return (
        f"Геймификация: "
        f"{len(gs.badges)} бейджей, "
        f"{len(gs.levels)} уровней, "
        f"{len(gs.challenges)} челленджей, "
        f"{len(gs.rewards)} наград, "
        f"{len(gs.leaderboard_rules)} правил лидерборда"
    )
