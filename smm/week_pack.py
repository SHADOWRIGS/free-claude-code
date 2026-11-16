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
from smm.analytics_dashboard import (
    export_analytics_dashboard_json,
    export_analytics_dashboard_txt,
    generate_analytics_dashboard,
)
from smm.audience_personas import (
    export_personas_json,
    export_personas_txt,
    generate_personas,
)
from smm.auto_poster import (
    export_auto_poster_json,
    export_auto_poster_txt,
    generate_auto_poster_config,
)
from smm.biolink import generate_biolink_file
from smm.caption_validator import validate_posts
from smm.carousel_generator import (
    export_carousels_json,
    export_carousels_txt,
    generate_carousels,
)
from smm.community_manager import (
    export_community_json,
    export_community_txt,
    generate_community_config,
)
from smm.content_scoring import (
    export_scores_json,
    export_scores_txt,
    generate_scored_batch,
)
from smm.content_series import (
    export_series_json,
    export_series_txt,
    generate_all_series,
)
from smm.conversion_funnel import (
    export_funnel_json,
    export_funnel_txt,
    generate_all_funnels,
)
from smm.cross_promo import (
    export_promos_json,
    export_promos_txt,
    generate_cross_promos,
)
from smm.cta_library import (
    export_ctas_json,
    export_ctas_txt,
    generate_ctas,
)
from smm.email_sequences import (
    export_emails_json,
    export_emails_txt,
    generate_all_emails,
)
from smm.engagement_hooks import (
    POLLS_BY_PILLAR,
    generate_poll,
    generate_question,
    generate_quiz,
    generate_this_or_that,
)
from smm.hashtag_engine import HASHTAG_POOLS, hashtag_report
from smm.influencer_outreach import (
    export_outreach_json,
    export_outreach_txt,
    generate_influencer_outreach,
)
from smm.lead_magnet import (
    export_lead_magnets_json,
    export_lead_magnets_txt,
    generate_lead_magnets,
)
from smm.ready_posts import (
    ReadyPost,
    batch_summary,
    export_buffer_csv,
    export_ready_json,
    export_ready_markdown,
    generate_ready_posts,
)
from smm.referral_analytics import (
    export_analytics_json,
    export_analytics_txt,
    generate_campaign_metrics,
)
from smm.scheduler_export import export_all_formats
from smm.seo_optimizer import (
    export_seo_json,
    export_seo_txt,
    generate_seo_pack,
)
from smm.social_proof import (
    export_social_proof_json,
    export_social_proof_txt,
    generate_social_proof_pack,
)
from smm.story_generator import (
    export_story_packs_json,
    export_story_packs_txt,
    generate_story_packs,
)
from smm.telegram_bot_config import (
    export_bot_config_json,
    export_bot_config_txt,
    generate_bot_config,
)
from smm.topic_ab_test import (
    export_ab_topics_json,
    export_ab_topics_txt,
    generate_ab_topics,
)
from smm.webinar_funnel import (
    export_webinar_json,
    export_webinar_txt,
    generate_webinar_funnel,
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

    carousel_dir = out_dir / "carousels"
    carousel_dir.mkdir(exist_ok=True)
    carousel_packs = generate_carousels(count=5, seed=seed)
    paths["carousels_json"] = export_carousels_json(
        carousel_packs, carousel_dir / "carousels.json"
    )
    paths["carousels_txt"] = export_carousels_txt(
        carousel_packs, carousel_dir / "carousels.txt"
    )

    series_dir = out_dir / "series"
    series_dir.mkdir(exist_ok=True)
    all_series = generate_all_series(seed=seed)
    paths["series_json"] = export_series_json(all_series, series_dir / "series.json")
    paths["series_txt"] = export_series_txt(all_series, series_dir / "series.txt")

    funnel_dir = out_dir / "funnel"
    funnel_dir.mkdir(exist_ok=True)
    funnels = generate_all_funnels()
    paths["funnel_json"] = export_funnel_json(funnels, funnel_dir / "funnel.json")
    paths["funnel_txt"] = export_funnel_txt(funnels, funnel_dir / "funnel.txt")

    xp_dir = out_dir / "cross_promo"
    xp_dir.mkdir(exist_ok=True)
    promos = generate_cross_promos(seed=seed)
    paths["cross_promo_json"] = export_promos_json(promos, xp_dir / "cross_promo.json")
    paths["cross_promo_txt"] = export_promos_txt(promos, xp_dir / "cross_promo.txt")

    email_dir = out_dir / "emails"
    email_dir.mkdir(exist_ok=True)
    emails = generate_all_emails()
    paths["emails_json"] = export_emails_json(emails, email_dir / "emails.json")
    paths["emails_txt"] = export_emails_txt(emails, email_dir / "emails.txt")

    cta_dir = out_dir / "ctas"
    cta_dir.mkdir(exist_ok=True)
    ctas = generate_ctas()
    paths["ctas_json"] = export_ctas_json(ctas, cta_dir / "ctas.json")
    paths["ctas_txt"] = export_ctas_txt(ctas, cta_dir / "ctas.txt")

    score_dir = out_dir / "scoring"
    score_dir.mkdir(exist_ok=True)
    scored = generate_scored_batch(count=len(posts), seed=seed)
    paths["scores_json"] = export_scores_json(scored, score_dir / "scores.json")
    paths["scores_txt"] = export_scores_txt(scored, score_dir / "scores.txt")

    ra_dir = out_dir / "referral_analytics"
    ra_dir.mkdir(exist_ok=True)
    metrics = generate_campaign_metrics(seed=seed)
    paths["ref_analytics_json"] = export_analytics_json(
        metrics, ra_dir / "analytics.json"
    )
    paths["ref_analytics_txt"] = export_analytics_txt(metrics, ra_dir / "analytics.txt")

    persona_dir = out_dir / "personas"
    persona_dir.mkdir(exist_ok=True)
    personas = generate_personas()
    paths["personas_json"] = export_personas_json(
        personas, persona_dir / "personas.json"
    )
    paths["personas_txt"] = export_personas_txt(personas, persona_dir / "personas.txt")

    lm_dir = out_dir / "lead_magnets"
    lm_dir.mkdir(exist_ok=True)
    magnets = generate_lead_magnets()
    paths["lead_magnets_json"] = export_lead_magnets_json(
        magnets, lm_dir / "lead_magnets.json"
    )
    paths["lead_magnets_txt"] = export_lead_magnets_txt(
        magnets, lm_dir / "lead_magnets.txt"
    )

    sp_dir = out_dir / "social_proof"
    sp_dir.mkdir(exist_ok=True)
    sp_pack = generate_social_proof_pack(seed=seed)
    paths["social_proof_json"] = export_social_proof_json(
        sp_pack, sp_dir / "social_proof.json"
    )
    paths["social_proof_txt"] = export_social_proof_txt(
        sp_pack, sp_dir / "social_proof.txt"
    )

    wb_dir = out_dir / "webinar"
    wb_dir.mkdir(exist_ok=True)
    wb_messages = generate_webinar_funnel()
    paths["webinar_json"] = export_webinar_json(wb_messages, wb_dir / "webinar.json")
    paths["webinar_txt"] = export_webinar_txt(wb_messages, wb_dir / "webinar.txt")

    tg_dir = out_dir / "telegram_bot"
    tg_dir.mkdir(exist_ok=True)
    bot_config = generate_bot_config()
    paths["tg_bot_json"] = export_bot_config_json(
        bot_config, tg_dir / "bot_config.json"
    )
    paths["tg_bot_txt"] = export_bot_config_txt(bot_config, tg_dir / "bot_config.txt")

    ap_dir = out_dir / "auto_poster"
    ap_dir.mkdir(exist_ok=True)
    ap_config = generate_auto_poster_config()
    paths["auto_poster_json"] = export_auto_poster_json(
        ap_config, ap_dir / "auto_poster.json"
    )
    paths["auto_poster_txt"] = export_auto_poster_txt(
        ap_config, ap_dir / "auto_poster.txt"
    )

    seo_dir = out_dir / "seo"
    seo_dir.mkdir(exist_ok=True)
    seo_pack = generate_seo_pack()
    paths["seo_json"] = export_seo_json(seo_pack, seo_dir / "seo.json")
    paths["seo_txt"] = export_seo_txt(seo_pack, seo_dir / "seo.txt")

    cm_dir = out_dir / "community"
    cm_dir.mkdir(exist_ok=True)
    cm_config = generate_community_config()
    paths["community_json"] = export_community_json(
        cm_config, cm_dir / "community.json"
    )
    paths["community_txt"] = export_community_txt(cm_config, cm_dir / "community.txt")

    inf_dir = out_dir / "influencer"
    inf_dir.mkdir(exist_ok=True)
    inf_outreach = generate_influencer_outreach()
    paths["influencer_json"] = export_outreach_json(
        inf_outreach, inf_dir / "outreach.json"
    )
    paths["influencer_txt"] = export_outreach_txt(
        inf_outreach, inf_dir / "outreach.txt"
    )

    dash_dir = out_dir / "analytics_dashboard"
    dash_dir.mkdir(exist_ok=True)
    dashboard = generate_analytics_dashboard(seed=seed)
    paths["dashboard_json"] = export_analytics_dashboard_json(
        dashboard, dash_dir / "dashboard.json"
    )
    paths["dashboard_txt"] = export_analytics_dashboard_txt(
        dashboard, dash_dir / "dashboard.txt"
    )

    tab_dir = out_dir / "topic_ab"
    tab_dir.mkdir(exist_ok=True)
    ab_topics = generate_ab_topics(seed=seed)
    paths["topic_ab_json"] = export_ab_topics_json(ab_topics, tab_dir / "topic_ab.json")
    paths["topic_ab_txt"] = export_ab_topics_txt(ab_topics, tab_dir / "topic_ab.txt")

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
