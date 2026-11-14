"""Weekly content pack generator — a complete ready-to-use package.

Assembles everything a person needs to run SMM for one week:
- 63 ready-to-post captions (9/day, 3 platforms)
- Visual briefs for designers
- Video scripts for video content
- Bio link page
- Scheduling files for Buffer/Later/Meta/Notion/iCal
- Summary statistics

Output: a directory with all files organized by platform.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from smm.ab_variants import export_ab_csv, export_ab_json, generate_ab_posts
from smm.biolink import generate_biolink_file
from smm.caption_validator import validate_posts
from smm.engagement_hooks import (
    POLLS_BY_PILLAR,
    generate_poll,
    generate_question,
    generate_quiz,
    generate_this_or_that,
)
from smm.hashtag_engine import HASHTAG_POOLS, hashtag_report
from smm.ready_posts import (
    ReadyPost,
    batch_summary,
    export_buffer_csv,
    export_ready_json,
    export_ready_markdown,
    generate_ready_posts,
)
from smm.scheduler_export import export_all_formats
from smm.story_generator import (
    export_story_packs_json,
    export_story_packs_txt,
    generate_story_packs,
)


def generate_week_pack(
    days: int = 7,
    seed: int | None = None,
    start: date | None = None,
    out_dir: Path | None = None,
) -> dict[str, Path]:
    if out_dir is None:
        out_dir = Path("smm_data") / "week_pack"
    out_dir.mkdir(parents=True, exist_ok=True)

    posts = generate_ready_posts(days=days, seed=seed, start=start)

    paths: dict[str, Path] = {}

    paths["json"] = export_ready_json(posts, out_dir / "posts.json")
    paths["csv"] = export_buffer_csv(posts, out_dir / "buffer_import.csv")
    paths["markdown"] = export_ready_markdown(posts, out_dir / "posts.md")

    scheduler_dir = out_dir / "scheduler"
    scheduler_paths = export_all_formats(posts, scheduler_dir)
    for name, path in scheduler_paths.items():
        paths[f"scheduler_{name}"] = path

    paths["biolink"] = generate_biolink_file(output=out_dir / "biolink.html")

    ab_dir = out_dir / "ab_test"
    ab_dir.mkdir(exist_ok=True)
    ab_posts = generate_ab_posts(days=days, seed=seed, start=start)
    paths["ab_json"] = export_ab_json(ab_posts, ab_dir / "ab_variants.json")
    paths["ab_csv"] = export_ab_csv(ab_posts, ab_dir / "ab_variants.csv")

    hashtag_dir = out_dir / "hashtags"
    hashtag_dir.mkdir(exist_ok=True)
    ht_lines: list[str] = []
    for pillar_name in sorted(HASHTAG_POOLS):
        ht_lines.append(hashtag_report(pillar_name))
        ht_lines.append("")
    ht_path = hashtag_dir / "hashtag_pools.txt"
    ht_path.write_text("\n".join(ht_lines), encoding="utf-8")
    paths["hashtag_pools"] = ht_path

    engage_dir = out_dir / "engagement"
    engage_dir.mkdir(exist_ok=True)
    engage_lines: list[str] = []
    for pillar_name in sorted(POLLS_BY_PILLAR):
        engage_lines.append(f"=== {pillar_name} ===\n")
        poll = generate_poll(pillar_name, seed=seed)
        engage_lines.append(f"ОПРОС: {poll.content}")
        for i, opt in enumerate(poll.options, 1):
            engage_lines.append(f"  {i}. {opt}")
        engage_lines.append("")
        quiz = generate_quiz(pillar_name, seed=seed)
        engage_lines.append(f"КВИЗ: {quiz.content}")
        for i, opt in enumerate(quiz.options, 1):
            marker = " [верно]" if i - 1 == quiz.correct_index else ""
            engage_lines.append(f"  {i}. {opt}{marker}")
        engage_lines.append("")
        q = generate_question(pillar_name, seed=seed)
        engage_lines.append(f"ВОПРОС: {q}")
        a, b = generate_this_or_that(pillar_name, seed=seed)
        engage_lines.append(f"THIS OR THAT: {a} vs {b}\n")
    eng_path = engage_dir / "engagement_hooks.txt"
    eng_path.write_text("\n".join(engage_lines), encoding="utf-8")
    paths["engagement"] = eng_path

    story_dir = out_dir / "stories"
    story_dir.mkdir(exist_ok=True)
    story_packs = generate_story_packs(count=5, seed=seed)
    paths["stories_json"] = export_story_packs_json(
        story_packs, story_dir / "story_packs.json"
    )
    paths["stories_txt"] = export_story_packs_txt(
        story_packs, story_dir / "story_packs.txt"
    )

    by_platform = _split_by_platform(posts)
    platform_dir = out_dir / "platforms"
    platform_dir.mkdir(exist_ok=True)
    for platform, platform_posts in by_platform.items():
        pf = platform_dir / platform
        pf.mkdir(exist_ok=True)
        captions_path = pf / "captions.txt"
        _export_captions_txt(platform_posts, captions_path)
        paths[f"captions_{platform}"] = captions_path

        scripts = [p for p in platform_posts if p.video_script]
        if scripts:
            scripts_path = pf / "video_scripts.txt"
            _export_scripts_txt(scripts, scripts_path)
            paths[f"scripts_{platform}"] = scripts_path

        briefs_path = pf / "visual_briefs.txt"
        _export_briefs_txt(platform_posts, briefs_path)
        paths[f"briefs_{platform}"] = briefs_path

    summary_path = out_dir / "README.txt"
    _export_summary(posts, paths, summary_path)
    paths["readme"] = summary_path

    return paths


def _split_by_platform(posts: list[ReadyPost]) -> dict[str, list[ReadyPost]]:
    result: dict[str, list[ReadyPost]] = {}
    for p in posts:
        result.setdefault(p.platform, []).append(p)
    return result


def _export_captions_txt(posts: list[ReadyPost], path: Path) -> None:
    lines: list[str] = []
    for i, p in enumerate(posts, 1):
        lines.append(f"--- Post {i} | {p.day.isoformat()} {p.time_slot} ---")
        lines.append(f"Topic: {p.topic}")
        lines.append(f"Format: {p.format}")
        lines.append("")
        lines.append(p.caption)
        lines.append("")
        if p.referral_url:
            lines.append(f"Link: {p.referral_url}")
            lines.append("")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _export_scripts_txt(posts: list[ReadyPost], path: Path) -> None:
    lines: list[str] = []
    for i, p in enumerate(posts, 1):
        lines.append(f"--- Script {i} | {p.day.isoformat()} {p.time_slot} ---")
        lines.append(f"Topic: {p.topic}")
        lines.append(f"Format: {p.format}")
        lines.append("")
        lines.append(p.video_script)
        lines.append("")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _export_briefs_txt(posts: list[ReadyPost], path: Path) -> None:
    lines: list[str] = []
    for i, p in enumerate(posts, 1):
        lines.append(f"--- Brief {i} | {p.day.isoformat()} {p.time_slot} ---")
        lines.append(f"Topic: {p.topic}")
        lines.append(f"Format: {p.format}")
        lines.append("")
        lines.append(p.visual_brief)
        lines.append("")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _export_summary(posts: list[ReadyPost], paths: dict[str, Path], path: Path) -> None:
    summary = batch_summary(posts)
    file_list = "\n".join(f"  {name}: {p}" for name, p in sorted(paths.items()))

    validation = validate_posts(posts)
    val_status = "ALL PASSED" if validation.ok else f"{validation.failed} FAILED"

    stats = json.dumps(
        {
            "total_posts": len(posts),
            "platforms": sorted({p.platform for p in posts}),
            "days": sorted({p.day.isoformat() for p in posts}),
            "video_scripts": sum(1 for p in posts if p.video_script),
            "referral_posts": sum(1 for p in posts if p.referral_url),
            "files_generated": len(paths) + 1,
            "validation": val_status,
        },
        ensure_ascii=False,
        indent=2,
    )

    content = f"""SMM Week Pack
=============

{summary}

Validation: {val_status}
{validation.summary()}

Generated Files:
{file_list}

Stats (JSON):
{stats}
"""
    path.write_text(content, encoding="utf-8")
