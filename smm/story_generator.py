"""Story pack generator — ready-to-post story sequences.

Assembles 5-7 slide story packs for Instagram/TikTok stories.
Each pack uses a story framework from content_bank, enriched with
engagement hooks (polls/quizzes) and pillar-specific content.

Output: complete story scripts with slide text, visual directions,
and interactive elements.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from smm.content_bank import (
    MYTHS_BY_NICHE,
    PROBLEMS_BY_NICHE,
    STORY_FRAMEWORKS,
    get_ctas,
    get_hooks,
)
from smm.content_pillars import PILLARS, ContentPillar
from smm.engagement_hooks import (
    generate_poll,
    generate_question,
    generate_quiz,
)

ACCENT_COLORS: dict[str, str] = {
    "Cyber Security & Ethical Hacking": "#00ff41",
    "Blue Team / Defensive Security": "#00bfff",
    "Red Team / Offensive Security": "#ff4444",
    "Machine Learning & AI": "#a855f7",
    "AliExpress - Гаджеты": "#ff6600",
}


@dataclass(frozen=True, slots=True)
class StorySlide:
    number: int
    text: str
    visual_note: str
    interactive: str


@dataclass(frozen=True, slots=True)
class StoryPack:
    pillar: str
    topic: str
    framework: str
    slides: list[StorySlide]
    accent_color: str

    def to_dict(self) -> dict[str, object]:
        return {
            "pillar": self.pillar,
            "topic": self.topic,
            "framework": self.framework,
            "accent_color": self.accent_color,
            "slides": [
                {
                    "number": s.number,
                    "text": s.text,
                    "visual_note": s.visual_note,
                    "interactive": s.interactive,
                }
                for s in self.slides
            ],
        }


def _pillar_keyword(pillar: ContentPillar) -> str:
    return pillar.name.split("/")[0].strip().split("&")[0].strip().split("-")[0].strip()


def _get_problem(pillar: ContentPillar) -> str:
    for key, problems in PROBLEMS_BY_NICHE.items():
        if key.lower() in pillar.name.lower():
            return random.choice(problems)
    return "Проблема, которую все игнорируют"


def _get_myth(pillar: ContentPillar) -> str:
    for key, myths in MYTHS_BY_NICHE.items():
        if key.lower() in pillar.name.lower():
            return random.choice(myths)
    return "Распространённое заблуждение"


def generate_story_pack(
    pillar: ContentPillar,
    topic: str,
    seed: int | None = None,
) -> StoryPack:
    if seed is not None:
        random.seed(seed)

    keyword = _pillar_keyword(pillar)
    fw = random.choice(STORY_FRAMEWORKS)
    hooks = get_hooks(keyword, count=3)
    ctas = get_ctas("referral" if pillar.product == "referral" else "course", count=2)
    problem = _get_problem(pillar)
    myth = _get_myth(pillar)
    accent = ACCENT_COLORS.get(pillar.name, "#6366f1")
    topic_lower = topic.lower() if topic[0].isupper() else topic

    subs = {
        "topic": topic,
        "topic_lower": topic_lower,
        "problem": problem,
        "myth": myth,
        "cta": ctas[0],
        "hook": hooks[0],
    }

    slides: list[StorySlide] = []
    slide_keys = sorted(k for k in fw if k.startswith("slide_"))

    for i, key in enumerate(slide_keys, 1):
        text = fw[key]
        for k, v in subs.items():
            text = text.replace(f"{{{k}}}", v)

        if i == 1:
            visual = f"Яркий фон {accent}, крупный текст, анимация появления"
        elif i == len(slide_keys):
            visual = f"CTA-слайд: стрелка вверх «ссылка в био», цвет {accent}"
        else:
            visual = f"Тёмный фон, контрастный текст, иконка по теме {keyword}"

        interactive = ""
        if i == 2:
            poll = generate_poll(pillar.name)
            interactive = f"Опрос: {poll.content} | {' / '.join(poll.options[:2])}"
        elif i == 3:
            quiz = generate_quiz(pillar.name)
            interactive = (
                f"Квиз: {quiz.content} | "
                f"Ответ: {quiz.options[quiz.correct_index] if quiz.correct_index is not None else '?'}"
            )
        elif i == 4:
            q = generate_question(pillar.name)
            interactive = f"Поле ответа: {q}"

        slides.append(
            StorySlide(number=i, text=text, visual_note=visual, interactive=interactive)
        )

    return StoryPack(
        pillar=pillar.name,
        topic=topic,
        framework=fw["name"],
        slides=slides,
        accent_color=accent,
    )


def generate_story_packs(
    count: int = 5,
    seed: int | None = None,
) -> list[StoryPack]:
    if seed is not None:
        random.seed(seed)

    packs: list[StoryPack] = []
    all_topics = [(t, p) for p in PILLARS for t in p.topics]
    random.shuffle(all_topics)

    for i in range(min(count, len(all_topics))):
        topic, pillar = all_topics[i]
        pack = generate_story_pack(pillar, topic)
        packs.append(pack)

    return packs


def export_story_packs_json(packs: list[StoryPack], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [p.to_dict() for p in packs]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_story_packs_txt(packs: list[StoryPack], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for i, pack in enumerate(packs, 1):
        lines.append(f"{'=' * 50}")
        lines.append(f"СТОРИС #{i} | {pack.framework}")
        lines.append(f"Тема: {pack.topic}")
        lines.append(f"Направление: {pack.pillar}")
        lines.append(f"Акцент: {pack.accent_color}")
        lines.append(f"{'=' * 50}")
        for slide in pack.slides:
            lines.append(f"\n  Слайд {slide.number}:")
            lines.append(f"    Текст: {slide.text}")
            lines.append(f"    Визуал: {slide.visual_note}")
            if slide.interactive:
                lines.append(f"    Интерактив: {slide.interactive}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def story_summary(packs: list[StoryPack]) -> str:
    by_pillar: dict[str, int] = {}
    by_fw: dict[str, int] = {}
    total_slides = 0
    interactive_count = 0
    for p in packs:
        by_pillar[p.pillar] = by_pillar.get(p.pillar, 0) + 1
        by_fw[p.framework] = by_fw.get(p.framework, 0) + 1
        total_slides += len(p.slides)
        interactive_count += sum(1 for s in p.slides if s.interactive)

    lines = [
        f"Сторис-пакеты: {len(packs)} шт.",
        f"Всего слайдов: {total_slides}",
        f"С интерактивом: {interactive_count}",
        "\nПо направлениям:",
    ]
    for name, count in sorted(by_pillar.items()):
        lines.append(f"  {name}: {count}")
    lines.append("\nПо фреймворкам:")
    for name, count in sorted(by_fw.items()):
        lines.append(f"  {name}: {count}")
    return "\n".join(lines)
