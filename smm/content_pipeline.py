"""Content pipeline orchestrator — ties all modules into one workflow.

Runs the full content generation pipeline:
1. Generate ready posts for the week
2. Score and rank them
3. Assign CTAs from the funnel stage
4. Attach social proof snippets
5. Pick audience persona match
6. Export the enriched package

This is the "one command to rule them all" for weekly content prep.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from smm.content_pillars import PILLARS
from smm.content_scoring import generate_scored_batch
from smm.cta_library import pick_cta
from smm.ready_posts import ReadyPost, generate_ready_posts
from smm.social_proof import generate_testimonials


@dataclass(frozen=True, slots=True)
class EnrichedPost:
    post: ReadyPost
    score: int
    cta_short: str
    cta_long: str
    funnel_stage: str
    testimonial_name: str
    testimonial_quote: str


@dataclass(slots=True)
class PipelineResult:
    posts: list[EnrichedPost] = field(default_factory=list)
    total: int = 0
    avg_score: float = 0.0
    top_posts: list[EnrichedPost] = field(default_factory=list)
    by_platform: dict[str, int] = field(default_factory=dict)
    by_pillar: dict[str, int] = field(default_factory=dict)
    by_stage: dict[str, int] = field(default_factory=dict)


STAGE_CYCLE = ("tofu", "mofu", "bofu")


def _pillar_for_post(post: ReadyPost) -> str:
    for p in PILLARS:
        if p.name == post.pillar:
            return p.name
    return PILLARS[0].name


def run_pipeline(
    days: int = 7,
    seed: int | None = None,
    start: date | None = None,
) -> PipelineResult:
    posts = generate_ready_posts(days=days, seed=seed, start=start)
    scored = generate_scored_batch(count=len(posts), seed=seed)

    testimonials_by_pillar: dict[str, list[tuple[str, str]]] = {}
    for pillar in PILLARS:
        ts = generate_testimonials(pillar=pillar.name)
        testimonials_by_pillar[pillar.name] = [(t.name, t.text) for t in ts]

    enriched: list[EnrichedPost] = []
    for i, post in enumerate(posts):
        score_val = scored[i % len(scored)].total_score if scored else 50
        stage = STAGE_CYCLE[i % 3]
        cta = pick_cta(stage=stage, platform=post.platform, seed=(seed or 0) + i)

        pillar_name = _pillar_for_post(post)
        t_pool = testimonials_by_pillar.get(pillar_name, [])
        t_idx = i % len(t_pool) if t_pool else 0
        t_name, t_quote = t_pool[t_idx] if t_pool else ("", "")

        enriched.append(
            EnrichedPost(
                post=post,
                score=score_val,
                cta_short=cta.short_text,
                cta_long=cta.long_text,
                funnel_stage=stage,
                testimonial_name=t_name,
                testimonial_quote=t_quote,
            )
        )

    enriched.sort(key=lambda e: e.score, reverse=True)

    total = len(enriched)
    avg_score = sum(e.score for e in enriched) / total if total else 0.0
    top_posts = enriched[:10]

    by_platform: dict[str, int] = {}
    by_pillar: dict[str, int] = {}
    by_stage: dict[str, int] = {}
    for e in enriched:
        by_platform[e.post.platform] = by_platform.get(e.post.platform, 0) + 1
        by_pillar[e.post.pillar] = by_pillar.get(e.post.pillar, 0) + 1
        by_stage[e.funnel_stage] = by_stage.get(e.funnel_stage, 0) + 1

    return PipelineResult(
        posts=enriched,
        total=total,
        avg_score=avg_score,
        top_posts=top_posts,
        by_platform=by_platform,
        by_pillar=by_pillar,
        by_stage=by_stage,
    )


def export_pipeline_json(result: PipelineResult, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "total": result.total,
        "avg_score": round(result.avg_score, 1),
        "by_platform": result.by_platform,
        "by_pillar": result.by_pillar,
        "by_stage": result.by_stage,
        "posts": [
            {
                "day": e.post.day.isoformat(),
                "platform": e.post.platform,
                "pillar": e.post.pillar,
                "topic": e.post.topic,
                "score": e.score,
                "funnel_stage": e.funnel_stage,
                "cta_short": e.cta_short,
                "cta_long": e.cta_long,
                "testimonial": e.testimonial_name,
                "caption": e.post.caption[:200],
            }
            for e in result.posts
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_pipeline_txt(result: PipelineResult, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "КОНТЕНТ-ПАЙПЛАЙН — РЕЗУЛЬТАТ",
        "=" * 60,
        f"\nВсего постов: {result.total}",
        f"Средний скоринг: {result.avg_score:.1f}/100",
        "\n📊 По платформам:",
    ]
    lines.extend(f"  {plat}: {cnt}" for plat, cnt in sorted(result.by_platform.items()))
    lines.append("\n📂 По направлениям:")
    lines.extend(f"  {pil}: {cnt}" for pil, cnt in sorted(result.by_pillar.items()))
    lines.append("\n🔄 По стадиям воронки:")
    lines.extend(
        f"  {stg.upper()}: {cnt}" for stg, cnt in sorted(result.by_stage.items())
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("🏆 ТОП-10 ПОСТОВ ПО СКОРИНГУ")
    lines.append("━" * 50)
    for i, e in enumerate(result.top_posts, 1):
        lines.append(f"\n  {i}. [{e.score}/100] {e.post.platform} | {e.post.pillar}")
        lines.append(f"     Тема: {e.post.topic}")
        lines.append(f"     CTA: {e.cta_short}")
        if e.testimonial_name:
            lines.append(f"     Отзыв: {e.testimonial_name}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def pipeline_summary(result: PipelineResult) -> str:
    return (
        f"Пайплайн: {result.total} постов, "
        f"средний скоринг {result.avg_score:.1f}/100, "
        f"платформы: {', '.join(sorted(result.by_platform))}"
    )
