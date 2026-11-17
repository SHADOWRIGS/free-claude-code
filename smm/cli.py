"""CLI entry point for the SMM automation tool.

Usage:
    uv run -m smm.cli plan --days 7
    uv run -m smm.cli post --platform instagram --topic "ChatGPT tips"
    uv run -m smm.cli script --topic "Midjourney tutorial" --duration 30
    uv run -m smm.cli schedule --days 7
    uv run -m smm.cli export --format csv --output calendar.csv
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from smm.generator import ContentGenerator, GeneratorConfig
from smm.platforms import Platform
from smm.post_generator import (
    export_plan_json,
    export_plan_markdown,
    generate_week_plan,
)
from smm.referral import ReferralRegistry
from smm.scheduler import ContentCalendar

DATA_DIR = Path("smm_data")
CALENDAR_PATH = DATA_DIR / "calendar.json"
REFERRAL_PATH = DATA_DIR / "referrals.json"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(exist_ok=True)


def _load_generator() -> ContentGenerator:
    _ensure_data_dir()
    referrals = ReferralRegistry.load(REFERRAL_PATH)
    return ContentGenerator(config=GeneratorConfig(), referrals=referrals)


def _load_calendar() -> ContentCalendar:
    _ensure_data_dir()
    return ContentCalendar.load(CALENDAR_PATH)


async def cmd_plan(args: argparse.Namespace) -> None:
    gen = _load_generator()
    plan = await gen.generate_plan(days=args.days, posts_per_day=args.posts)
    print(json.dumps(plan, ensure_ascii=False, indent=2))


async def cmd_post(args: argparse.Namespace) -> None:
    gen = _load_generator()
    result = await gen.generate_post(
        platform=Platform(args.platform),
        fmt=args.format,
        topic=args.topic,
        cta_goal=args.cta,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


async def cmd_script(args: argparse.Namespace) -> None:
    gen = _load_generator()
    result = await gen.generate_script(topic=args.topic, duration=args.duration)
    print(json.dumps(result, ensure_ascii=False, indent=2))


async def cmd_trends(args: argparse.Namespace) -> None:
    gen = _load_generator()
    result = await gen.analyze_trends()
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_schedule(args: argparse.Namespace) -> None:
    cal = _load_calendar()
    created = cal.fill_week(days=args.days)
    cal.save()
    print(f"Created {len(created)} scheduled slots for {args.days} days.")
    for post in created[:9]:
        print(
            f"  {post.publish_at:%Y-%m-%d %H:%M}  "
            f"{post.platform.value:<10} {post.format:<15} {post.topic}"
        )
    if len(created) > 9:
        print(f"  ... and {len(created) - 9} more")


def cmd_export(args: argparse.Namespace) -> None:
    cal = _load_calendar()
    output = Path(args.output)
    if args.format == "csv":
        cal.export_csv(output)
    else:
        cal.export_buffer_json(output)
    print(f"Exported {len(cal.posts)} posts to {output}")


def cmd_referral(args: argparse.Namespace) -> None:
    _ensure_data_dir()
    registry = ReferralRegistry.load(REFERRAL_PATH)
    if args.action == "add":
        from smm.referral import ReferralLink

        link = ReferralLink(
            label=args.label,
            url=args.url,
            utm_source=args.utm_source or "",
            utm_campaign=args.utm_campaign or "",
        )
        registry.add(link)
        registry.save(REFERRAL_PATH)
        print(f"Added: {link.label} -> {link.build_url()}")
    elif args.action == "list":
        if not registry.links:
            print("No referral links configured.")
            return
        for lnk in registry.links:
            print(f"  {lnk.label}: {lnk.build_url()}")


async def cmd_write(args: argparse.Namespace) -> None:
    from smm.ai_writer import AIWriter

    _ensure_data_dir()
    plan = generate_week_plan(days=1, seed=args.seed)
    slots = plan[: args.count]

    writer = AIWriter()
    print(f"Генерирую {len(slots)} постов через AI...\n")

    posts = await writer.write_batch(slots)
    output: list[dict[str, str | list[str]]] = []
    for p in posts:
        print(f"[{p.slot.platform.value}] {p.slot.topic}")
        print(f"  {p.caption[:120]}...")
        print()
        output.append(
            {
                "platform": p.slot.platform.value,
                "topic": p.slot.topic,
                "caption": p.caption,
                "visual_brief": p.visual_brief,
                "script": p.script,
                "alt_hooks": p.alt_hooks,
            }
        )

    out_path = DATA_DIR / "ai_posts.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"Сохранено в {out_path}")


def cmd_distribute(args: argparse.Namespace) -> None:
    from smm.distributor import build_distribution

    _ensure_data_dir()
    dist = build_distribution(days=args.days, seed=args.seed)
    out_dir = DATA_DIR / "packages"
    paths = dist.export_all(out_dir)
    print(dist.summary())
    print("\nЭкспортированы пакеты:")
    for platform, path in paths.items():
        print(f"  {platform}: {path}")


def cmd_preview(args: argparse.Namespace) -> None:
    from smm.preview import render_preview_file

    _ensure_data_dir()
    out = DATA_DIR / "preview.html" if not args.output else Path(args.output)
    path = render_preview_file(days=args.days, seed=args.seed, output=out)
    print(f"Превью сгенерировано: {path}")


def cmd_report(args: argparse.Namespace) -> None:
    from smm.analytics import create_tracking_template

    _ensure_data_dir()
    report = create_tracking_template(days=args.days, seed=args.seed)
    if args.format == "json":
        out = DATA_DIR / "report.json"
        report.export_json(out)
    else:
        out = DATA_DIR / "report.md"
        report.export_markdown(out)
    print(report.summary())
    print(f"\nСохранено: {out}")


def cmd_landing(args: argparse.Namespace) -> None:
    from smm.landing import generate_landing_file

    _ensure_data_dir()
    out = DATA_DIR / "landing.html" if not args.output else Path(args.output)
    kwargs: dict[str, str] = {}
    if args.brand:
        kwargs["brand"] = args.brand
    if args.contact:
        kwargs["contact_url"] = args.contact
    path = generate_landing_file(output=out, **kwargs)
    print(f"Лендинг сгенерирован: {path}")


def cmd_batch(args: argparse.Namespace) -> None:
    from smm.ready_posts import (
        batch_summary,
        export_buffer_csv,
        export_ready_json,
        export_ready_markdown,
        generate_ready_posts,
    )

    _ensure_data_dir()
    posts = generate_ready_posts(days=args.days, seed=args.seed)
    print(batch_summary(posts))

    batch_dir = DATA_DIR / "batch"
    batch_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_ready_json(posts, batch_dir / "ready_posts.json")
        print(f"\nJSON: {batch_dir / 'ready_posts.json'}")
    if args.format in ("csv", "all"):
        export_buffer_csv(posts, batch_dir / "buffer_import.csv")
        print(f"Buffer CSV: {batch_dir / 'buffer_import.csv'}")
    if args.format in ("markdown", "all"):
        export_ready_markdown(posts, batch_dir / "ready_posts.md")
        print(f"Markdown: {batch_dir / 'ready_posts.md'}")


def cmd_scheduler_export(args: argparse.Namespace) -> None:
    from smm.ready_posts import generate_ready_posts
    from smm.scheduler_export import export_all_formats

    _ensure_data_dir()
    posts = generate_ready_posts(days=args.days, seed=args.seed)
    out_dir = DATA_DIR / "scheduler"
    paths = export_all_formats(posts, out_dir)
    print(f"Экспортировано {len(posts)} постов в форматы планировщиков:\n")
    for name, path in paths.items():
        print(f"  {name}: {path}")


def cmd_proposal(args: argparse.Namespace) -> None:
    from smm.proposal import ClientProfile, generate_proposal_file

    _ensure_data_dir()
    client = ClientProfile(
        name=args.client_name,
        business=args.business,
        niche=args.niche,
        current_platforms=[p.strip() for p in args.platforms.split(",")],
        posts_per_week_goal=args.posts,
        main_goal=args.goal,
    )
    path = generate_proposal_file(client)
    print(f"Коммерческое предложение для {client.name}:")
    print(
        f"  Рекомендованный тариф: {client.recommended_tier.name} (${client.recommended_tier.price_monthly_usd}/мес)"
    )
    print(f"  Файл: {path}")


def cmd_hashtags(args: argparse.Namespace) -> None:
    from smm.hashtag_engine import generate_hashtags, hashtag_report

    if args.action == "generate":
        hs = generate_hashtags(args.pillar, count=args.count)
        print(f"Хештеги для «{args.pillar}» ({hs.count} шт.):\n")
        print(f"  Высокочастотные: {' '.join(hs.high)}")
        print(f"  Среднечастотные: {' '.join(hs.mid)}")
        print(f"  Нишевые: {' '.join(hs.niche)}")
        print(f"\nКопировать:\n{hs.as_string}")
    elif args.action == "report":
        print(hashtag_report(args.pillar))


def cmd_validate(args: argparse.Namespace) -> None:
    from smm.caption_validator import validate_posts
    from smm.ready_posts import generate_ready_posts

    _ensure_data_dir()
    posts = generate_ready_posts(days=args.days, seed=args.seed)
    report = validate_posts(posts)
    print(report.summary())
    if report.ok:
        print("\nВсе посты прошли валидацию!")


def cmd_cross_promo(args: argparse.Namespace) -> None:
    from smm.cross_promo import (
        export_promos_json,
        export_promos_txt,
        generate_cross_promos,
        promos_summary,
    )

    _ensure_data_dir()
    pillar = args.pillar if args.pillar else None
    promos = generate_cross_promos(pillar_name=pillar, seed=args.seed)
    print(promos_summary(promos))

    xp_dir = DATA_DIR / "cross_promo"
    xp_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_promos_json(promos, xp_dir / "cross_promo.json")
        print(f"\nJSON: {xp_dir / 'cross_promo.json'}")
    if args.format in ("txt", "all"):
        export_promos_txt(promos, xp_dir / "cross_promo.txt")
        print(f"TXT: {xp_dir / 'cross_promo.txt'}")


def cmd_emails(args: argparse.Namespace) -> None:
    from smm.email_sequences import (
        emails_summary,
        export_emails_json,
        export_emails_txt,
        generate_all_emails,
        generate_emails,
    )

    _ensure_data_dir()
    emails = generate_emails(args.pillar) if args.pillar else generate_all_emails()
    print(emails_summary(emails))

    em_dir = DATA_DIR / "emails"
    em_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_emails_json(emails, em_dir / "emails.json")
        print(f"\nJSON: {em_dir / 'emails.json'}")
    if args.format in ("txt", "all"):
        export_emails_txt(emails, em_dir / "emails.txt")
        print(f"TXT: {em_dir / 'emails.txt'}")


def cmd_ctas(args: argparse.Namespace) -> None:
    from smm.cta_library import (
        cta_summary,
        export_ctas_json,
        export_ctas_txt,
        generate_ctas,
    )

    _ensure_data_dir()
    ctas = generate_ctas(stage=args.stage or None, platform=args.platform or None)
    print(cta_summary(ctas))

    cta_dir = DATA_DIR / "ctas"
    cta_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_ctas_json(ctas, cta_dir / "ctas.json")
        print(f"\nJSON: {cta_dir / 'ctas.json'}")
    if args.format in ("txt", "all"):
        export_ctas_txt(ctas, cta_dir / "ctas.txt")
        print(f"TXT: {cta_dir / 'ctas.txt'}")


def cmd_ref_analytics(args: argparse.Namespace) -> None:
    from smm.referral_analytics import (
        analytics_summary,
        export_analytics_json,
        export_analytics_txt,
        generate_campaign_metrics,
    )

    _ensure_data_dir()
    metrics = generate_campaign_metrics(seed=args.seed)
    print(analytics_summary(metrics))

    ra_dir = DATA_DIR / "referral_analytics"
    ra_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_analytics_json(metrics, ra_dir / "analytics.json")
        print(f"\nJSON: {ra_dir / 'analytics.json'}")
    if args.format in ("txt", "all"):
        export_analytics_txt(metrics, ra_dir / "analytics.txt")
        print(f"TXT: {ra_dir / 'analytics.txt'}")


def cmd_lead_magnets(args: argparse.Namespace) -> None:
    from smm.lead_magnet import (
        export_lead_magnets_json,
        export_lead_magnets_txt,
        generate_lead_magnets,
        lead_magnets_summary,
    )

    _ensure_data_dir()
    magnets = generate_lead_magnets(pillar=args.pillar or None)
    print(lead_magnets_summary(magnets))

    lm_dir = DATA_DIR / "lead_magnets"
    lm_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_lead_magnets_json(magnets, lm_dir / "lead_magnets.json")
        print(f"\nJSON: {lm_dir / 'lead_magnets.json'}")
    if args.format in ("txt", "all"):
        export_lead_magnets_txt(magnets, lm_dir / "lead_magnets.txt")
        print(f"TXT: {lm_dir / 'lead_magnets.txt'}")


def cmd_tg_bot(args: argparse.Namespace) -> None:
    from smm.telegram_bot_config import (
        bot_config_summary,
        export_bot_config_json,
        export_bot_config_txt,
        generate_bot_config,
    )

    _ensure_data_dir()
    config = generate_bot_config()
    print(bot_config_summary(config))

    tg_dir = DATA_DIR / "telegram_bot"
    tg_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_bot_config_json(config, tg_dir / "bot_config.json")
        print(f"\nJSON: {tg_dir / 'bot_config.json'}")
    if args.format in ("txt", "all"):
        export_bot_config_txt(config, tg_dir / "bot_config.txt")
        print(f"TXT: {tg_dir / 'bot_config.txt'}")


def cmd_auto_poster(args: argparse.Namespace) -> None:
    from smm.auto_poster import (
        auto_poster_summary,
        export_auto_poster_json,
        export_auto_poster_txt,
        generate_auto_poster_config,
    )

    _ensure_data_dir()
    config = generate_auto_poster_config()
    print(auto_poster_summary(config))

    ap_dir = DATA_DIR / "auto_poster"
    ap_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_auto_poster_json(config, ap_dir / "auto_poster.json")
        print(f"\nJSON: {ap_dir / 'auto_poster.json'}")
    if args.format in ("txt", "all"):
        export_auto_poster_txt(config, ap_dir / "auto_poster.txt")
        print(f"TXT: {ap_dir / 'auto_poster.txt'}")


def cmd_analytics_dash(args: argparse.Namespace) -> None:
    from smm.analytics_dashboard import (
        analytics_dashboard_summary,
        export_analytics_dashboard_json,
        export_analytics_dashboard_txt,
        generate_analytics_dashboard,
    )

    _ensure_data_dir()
    dashboard = generate_analytics_dashboard(seed=args.seed)
    print(analytics_dashboard_summary(dashboard))

    ad_dir = DATA_DIR / "analytics_dashboard"
    ad_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_analytics_dashboard_json(dashboard, ad_dir / "dashboard.json")
        print(f"\nJSON: {ad_dir / 'dashboard.json'}")
    if args.format in ("txt", "all"):
        export_analytics_dashboard_txt(dashboard, ad_dir / "dashboard.txt")
        print(f"TXT: {ad_dir / 'dashboard.txt'}")


def cmd_influencer(args: argparse.Namespace) -> None:
    from smm.influencer_outreach import (
        export_outreach_json,
        export_outreach_txt,
        generate_influencer_outreach,
        outreach_summary,
    )

    _ensure_data_dir()
    outreach = generate_influencer_outreach()
    print(outreach_summary(outreach))

    inf_dir = DATA_DIR / "influencer"
    inf_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_outreach_json(outreach, inf_dir / "outreach.json")
        print(f"\nJSON: {inf_dir / 'outreach.json'}")
    if args.format in ("txt", "all"):
        export_outreach_txt(outreach, inf_dir / "outreach.txt")
        print(f"TXT: {inf_dir / 'outreach.txt'}")


def cmd_community(args: argparse.Namespace) -> None:
    from smm.community_manager import (
        community_summary,
        export_community_json,
        export_community_txt,
        generate_community_config,
    )

    _ensure_data_dir()
    config = generate_community_config()
    print(community_summary(config))

    cm_dir = DATA_DIR / "community"
    cm_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_community_json(config, cm_dir / "community.json")
        print(f"\nJSON: {cm_dir / 'community.json'}")
    if args.format in ("txt", "all"):
        export_community_txt(config, cm_dir / "community.txt")
        print(f"TXT: {cm_dir / 'community.txt'}")


def cmd_seo(args: argparse.Namespace) -> None:
    from smm.seo_optimizer import (
        export_seo_json,
        export_seo_txt,
        generate_seo_pack,
        seo_summary,
    )

    _ensure_data_dir()
    pack = generate_seo_pack()
    print(seo_summary(pack))

    seo_dir = DATA_DIR / "seo"
    seo_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_seo_json(pack, seo_dir / "seo.json")
        print(f"\nJSON: {seo_dir / 'seo.json'}")
    if args.format in ("txt", "all"):
        export_seo_txt(pack, seo_dir / "seo.txt")
        print(f"TXT: {seo_dir / 'seo.txt'}")


def cmd_launch_check(args: argparse.Namespace) -> None:
    from smm.launch_checklist import (
        checklist_summary,
        export_checklist_json,
        export_checklist_txt,
        generate_launch_checklist,
    )

    _ensure_data_dir()
    checklist = generate_launch_checklist()
    print(checklist_summary(checklist))

    lc_dir = DATA_DIR / "launch_checklist"
    lc_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_checklist_json(checklist, lc_dir / "checklist.json")
        print(f"\nJSON: {lc_dir / 'checklist.json'}")
    if args.format in ("txt", "all"):
        export_checklist_txt(checklist, lc_dir / "checklist.txt")
        print(f"TXT: {lc_dir / 'checklist.txt'}")


def cmd_ad_creative(args: argparse.Namespace) -> None:
    from smm.ad_creative import (
        ad_creative_summary,
        export_ad_json,
        export_ad_txt,
        generate_ad_creatives,
    )

    _ensure_data_dir()
    pack = generate_ad_creatives()
    print(ad_creative_summary(pack))

    ad_dir = DATA_DIR / "ad_creatives"
    ad_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_ad_json(pack, ad_dir / "ad_creatives.json")
        print(f"\nJSON: {ad_dir / 'ad_creatives.json'}")
    if args.format in ("txt", "all"):
        export_ad_txt(pack, ad_dir / "ad_creatives.txt")
        print(f"TXT: {ad_dir / 'ad_creatives.txt'}")


def cmd_brand_kit(args: argparse.Namespace) -> None:
    from smm.brand_kit import (
        brand_kit_summary,
        export_brand_kit_json,
        export_brand_kit_txt,
        generate_brand_kit,
    )

    _ensure_data_dir()
    kit = generate_brand_kit()
    print(brand_kit_summary(kit))

    kit_dir = DATA_DIR / "brand_kit"
    kit_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_brand_kit_json(kit, kit_dir / "brand_kit.json")
        print(f"\nJSON: {kit_dir / 'brand_kit.json'}")
    if args.format in ("txt", "all"):
        export_brand_kit_txt(kit, kit_dir / "brand_kit.txt")
        print(f"TXT: {kit_dir / 'brand_kit.txt'}")


def cmd_utm_builder(args: argparse.Namespace) -> None:
    from smm.utm_builder import (
        export_utm_json,
        export_utm_txt,
        generate_utm_builder,
        utm_summary,
    )

    _ensure_data_dir()
    ub = generate_utm_builder()
    print(utm_summary(ub))

    ub_dir = DATA_DIR / "utm"
    ub_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_utm_json(ub, ub_dir / "utm_links.json")
        print(f"\nJSON: {ub_dir / 'utm_links.json'}")
    if args.format in ("txt", "all"):
        export_utm_txt(ub, ub_dir / "utm_links.txt")
        print(f"TXT: {ub_dir / 'utm_links.txt'}")


def cmd_onboarding(args: argparse.Namespace) -> None:
    from smm.onboarding_flow import (
        export_onboarding_json,
        export_onboarding_txt,
        generate_onboarding_flow,
        onboarding_summary,
    )

    _ensure_data_dir()
    ob = generate_onboarding_flow()
    print(onboarding_summary(ob))

    ob_dir = DATA_DIR / "onboarding"
    ob_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_onboarding_json(ob, ob_dir / "onboarding.json")
        print(f"\nJSON: {ob_dir / 'onboarding.json'}")
    if args.format in ("txt", "all"):
        export_onboarding_txt(ob, ob_dir / "onboarding.txt")
        print(f"TXT: {ob_dir / 'onboarding.txt'}")


def cmd_social_listening(args: argparse.Namespace) -> None:
    from smm.social_listening import (
        export_listening_json,
        export_listening_txt,
        generate_social_listening,
        listening_summary,
    )

    _ensure_data_dir()
    sl = generate_social_listening()
    print(listening_summary(sl))

    sl_dir = DATA_DIR / "social_listening"
    sl_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_listening_json(sl, sl_dir / "social_listening.json")
        print(f"\nJSON: {sl_dir / 'social_listening.json'}")
    if args.format in ("txt", "all"):
        export_listening_txt(sl, sl_dir / "social_listening.txt")
        print(f"TXT: {sl_dir / 'social_listening.txt'}")


def cmd_content_audit(args: argparse.Namespace) -> None:
    from smm.content_audit import (
        audit_summary,
        export_audit_json,
        export_audit_txt,
        generate_content_audit,
    )

    _ensure_data_dir()
    audit = generate_content_audit()
    print(audit_summary(audit))

    audit_dir = DATA_DIR / "content_audit"
    audit_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_audit_json(audit, audit_dir / "content_audit.json")
        print(f"\nJSON: {audit_dir / 'content_audit.json'}")
    if args.format in ("txt", "all"):
        export_audit_txt(audit, audit_dir / "content_audit.txt")
        print(f"TXT: {audit_dir / 'content_audit.txt'}")


def cmd_ab_price_test(args: argparse.Namespace) -> None:
    from smm.ab_price_test import (
        ab_price_summary,
        export_ab_price_json,
        export_ab_price_txt,
        generate_ab_price_test,
    )

    _ensure_data_dir()
    ab = generate_ab_price_test()
    print(ab_price_summary(ab))

    ab_dir = DATA_DIR / "ab_price_test"
    ab_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_ab_price_json(ab, ab_dir / "ab_price_test.json")
        print(f"\nJSON: {ab_dir / 'ab_price_test.json'}")
    if args.format in ("txt", "all"):
        export_ab_price_txt(ab, ab_dir / "ab_price_test.txt")
        print(f"TXT: {ab_dir / 'ab_price_test.txt'}")


def cmd_compliance(args: argparse.Namespace) -> None:
    from smm.compliance_checker import (
        compliance_summary,
        export_compliance_json,
        export_compliance_txt,
        generate_compliance_checker,
    )

    _ensure_data_dir()
    cc = generate_compliance_checker()
    print(compliance_summary(cc))

    cc_dir = DATA_DIR / "compliance"
    cc_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_compliance_json(cc, cc_dir / "compliance.json")
        print(f"\nJSON: {cc_dir / 'compliance.json'}")
    if args.format in ("txt", "all"):
        export_compliance_txt(cc, cc_dir / "compliance.txt")
        print(f"TXT: {cc_dir / 'compliance.txt'}")


def cmd_roi_tracker(args: argparse.Namespace) -> None:
    from smm.roi_tracker import (
        export_roi_json,
        export_roi_txt,
        generate_roi_tracker,
        roi_summary,
    )

    _ensure_data_dir()
    rt = generate_roi_tracker()
    print(roi_summary(rt))

    roi_dir = DATA_DIR / "roi"
    roi_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_roi_json(rt, roi_dir / "roi_tracker.json")
        print(f"\nJSON: {roi_dir / 'roi_tracker.json'}")
    if args.format in ("txt", "all"):
        export_roi_txt(rt, roi_dir / "roi_tracker.txt")
        print(f"TXT: {roi_dir / 'roi_tracker.txt'}")


def cmd_content_recycle(args: argparse.Namespace) -> None:
    from smm.content_recycler import (
        export_recycler_json,
        export_recycler_txt,
        generate_content_recycler,
        recycler_summary,
    )

    _ensure_data_dir()
    cr = generate_content_recycler()
    print(recycler_summary(cr))

    cr_dir = DATA_DIR / "recycler"
    cr_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_recycler_json(cr, cr_dir / "content_recycler.json")
        print(f"\nJSON: {cr_dir / 'content_recycler.json'}")
    if args.format in ("txt", "all"):
        export_recycler_txt(cr, cr_dir / "content_recycler.txt")
        print(f"TXT: {cr_dir / 'content_recycler.txt'}")


def cmd_funnel_auto(args: argparse.Namespace) -> None:
    from smm.funnel_automation import (
        export_funnel_json,
        export_funnel_txt,
        funnel_summary,
        generate_funnel_automation,
    )

    _ensure_data_dir()
    fa = generate_funnel_automation()
    print(funnel_summary(fa))

    fa_dir = DATA_DIR / "funnel"
    fa_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_funnel_json(fa, fa_dir / "funnel_automation.json")
        print(f"\nJSON: {fa_dir / 'funnel_automation.json'}")
    if args.format in ("txt", "all"):
        export_funnel_txt(fa, fa_dir / "funnel_automation.txt")
        print(f"TXT: {fa_dir / 'funnel_automation.txt'}")


def cmd_gamification(args: argparse.Namespace) -> None:
    from smm.gamification import (
        export_gamification_json,
        export_gamification_txt,
        gamification_summary,
        generate_gamification,
    )

    _ensure_data_dir()
    gs = generate_gamification()
    print(gamification_summary(gs))

    gs_dir = DATA_DIR / "gamification"
    gs_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_gamification_json(gs, gs_dir / "gamification.json")
        print(f"\nJSON: {gs_dir / 'gamification.json'}")
    if args.format in ("txt", "all"):
        export_gamification_txt(gs, gs_dir / "gamification.txt")
        print(f"TXT: {gs_dir / 'gamification.txt'}")


def cmd_seasonal_calendar(args: argparse.Namespace) -> None:
    from smm.seasonal_calendar import (
        export_seasonal_json,
        export_seasonal_txt,
        generate_seasonal_calendar,
        seasonal_summary,
    )

    _ensure_data_dir()
    sc = generate_seasonal_calendar()
    print(seasonal_summary(sc))

    sc_dir = DATA_DIR / "seasonal"
    sc_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_seasonal_json(sc, sc_dir / "seasonal_calendar.json")
        print(f"\nJSON: {sc_dir / 'seasonal_calendar.json'}")
    if args.format in ("txt", "all"):
        export_seasonal_txt(sc, sc_dir / "seasonal_calendar.txt")
        print(f"TXT: {sc_dir / 'seasonal_calendar.txt'}")


def cmd_media_library(args: argparse.Namespace) -> None:
    from smm.media_library import (
        export_media_json,
        export_media_txt,
        generate_media_library,
        media_library_summary,
    )

    _ensure_data_dir()
    ml = generate_media_library()
    print(media_library_summary(ml))

    ml_dir = DATA_DIR / "media_library"
    ml_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_media_json(ml, ml_dir / "media_library.json")
        print(f"\nJSON: {ml_dir / 'media_library.json'}")
    if args.format in ("txt", "all"):
        export_media_txt(ml, ml_dir / "media_library.txt")
        print(f"TXT: {ml_dir / 'media_library.txt'}")


def cmd_localization(args: argparse.Namespace) -> None:
    from smm.localization import (
        export_localization_json,
        export_localization_txt,
        generate_localization,
        localization_summary,
    )

    _ensure_data_dir()
    lp = generate_localization()
    print(localization_summary(lp))

    lp_dir = DATA_DIR / "localization"
    lp_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_localization_json(lp, lp_dir / "localization.json")
        print(f"\nJSON: {lp_dir / 'localization.json'}")
    if args.format in ("txt", "all"):
        export_localization_txt(lp, lp_dir / "localization.txt")
        print(f"TXT: {lp_dir / 'localization.txt'}")


def cmd_partnership(args: argparse.Namespace) -> None:
    from smm.partnership_program import (
        export_partnership_json,
        export_partnership_txt,
        generate_partnership_program,
        partnership_summary,
    )

    _ensure_data_dir()
    pp = generate_partnership_program()
    print(partnership_summary(pp))

    pp_dir = DATA_DIR / "partnership"
    pp_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_partnership_json(pp, pp_dir / "partnership_program.json")
        print(f"\nJSON: {pp_dir / 'partnership_program.json'}")
    if args.format in ("txt", "all"):
        export_partnership_txt(pp, pp_dir / "partnership_program.txt")
        print(f"TXT: {pp_dir / 'partnership_program.txt'}")


def cmd_crisis(args: argparse.Namespace) -> None:
    from smm.crisis_management import (
        crisis_summary,
        export_crisis_json,
        export_crisis_txt,
        generate_crisis_management,
    )

    _ensure_data_dir()
    cm = generate_crisis_management()
    print(crisis_summary(cm))

    cm_dir = DATA_DIR / "crisis"
    cm_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_crisis_json(cm, cm_dir / "crisis_management.json")
        print(f"\nJSON: {cm_dir / 'crisis_management.json'}")
    if args.format in ("txt", "all"):
        export_crisis_txt(cm, cm_dir / "crisis_management.txt")
        print(f"TXT: {cm_dir / 'crisis_management.txt'}")


def cmd_content_approval(args: argparse.Namespace) -> None:
    from smm.content_approval import (
        approval_summary,
        export_approval_json,
        export_approval_txt,
        generate_approval_workflow,
    )

    _ensure_data_dir()
    wf = generate_approval_workflow()
    print(approval_summary(wf))

    wf_dir = DATA_DIR / "content_approval"
    wf_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_approval_json(wf, wf_dir / "approval_workflow.json")
        print(f"\nJSON: {wf_dir / 'approval_workflow.json'}")
    if args.format in ("txt", "all"):
        export_approval_txt(wf, wf_dir / "approval_workflow.txt")
        print(f"TXT: {wf_dir / 'approval_workflow.txt'}")


def cmd_notifications(args: argparse.Namespace) -> None:
    from smm.notification_system import (
        export_notifications_json,
        export_notifications_txt,
        generate_notification_system,
        notification_summary,
    )

    _ensure_data_dir()
    ns = generate_notification_system()
    print(notification_summary(ns))

    ns_dir = DATA_DIR / "notifications"
    ns_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_notifications_json(ns, ns_dir / "notifications.json")
        print(f"\nJSON: {ns_dir / 'notifications.json'}")
    if args.format in ("txt", "all"):
        export_notifications_txt(ns, ns_dir / "notifications.txt")
        print(f"TXT: {ns_dir / 'notifications.txt'}")


def cmd_webinar(args: argparse.Namespace) -> None:
    from smm.webinar_funnel import (
        export_webinar_json,
        export_webinar_txt,
        generate_webinar_funnel,
        webinar_summary,
    )

    _ensure_data_dir()
    messages = generate_webinar_funnel(pillar=args.pillar or None)
    print(webinar_summary(messages))

    wb_dir = DATA_DIR / "webinar"
    wb_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_webinar_json(messages, wb_dir / "webinar.json")
        print(f"\nJSON: {wb_dir / 'webinar.json'}")
    if args.format in ("txt", "all"):
        export_webinar_txt(messages, wb_dir / "webinar.txt")
        print(f"TXT: {wb_dir / 'webinar.txt'}")


def cmd_pricing(args: argparse.Namespace) -> None:
    from smm.pricing_calculator import (
        export_pricing_json,
        export_pricing_txt,
        generate_roi_projections,
        generate_tier_breakdowns,
        pricing_summary,
    )

    _ensure_data_dir()
    tiers = generate_tier_breakdowns()
    roi = generate_roi_projections()
    print(pricing_summary(tiers, roi))

    pr_dir = DATA_DIR / "pricing"
    pr_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_pricing_json(tiers, roi, pr_dir / "pricing.json")
        print(f"\nJSON: {pr_dir / 'pricing.json'}")
    if args.format in ("txt", "all"):
        export_pricing_txt(tiers, roi, pr_dir / "pricing.txt")
        print(f"TXT: {pr_dir / 'pricing.txt'}")


def cmd_retargeting(args: argparse.Namespace) -> None:
    from smm.retargeting_guide import (
        export_retargeting_json,
        export_retargeting_txt,
        generate_audiences,
        generate_retargeting_guides,
        retargeting_summary,
    )

    _ensure_data_dir()
    guides = generate_retargeting_guides()
    audiences = generate_audiences()
    print(retargeting_summary(guides, audiences))

    rt_dir = DATA_DIR / "retargeting"
    rt_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_retargeting_json(guides, audiences, rt_dir / "retargeting.json")
        print(f"\nJSON: {rt_dir / 'retargeting.json'}")
    if args.format in ("txt", "all"):
        export_retargeting_txt(guides, audiences, rt_dir / "retargeting.txt")
        print(f"TXT: {rt_dir / 'retargeting.txt'}")


def cmd_pipeline(args: argparse.Namespace) -> None:
    from smm.content_pipeline import (
        export_pipeline_json,
        export_pipeline_txt,
        pipeline_summary,
        run_pipeline,
    )

    _ensure_data_dir()
    result = run_pipeline(days=args.days, seed=args.seed)
    print(pipeline_summary(result))

    pl_dir = DATA_DIR / "pipeline"
    pl_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_pipeline_json(result, pl_dir / "pipeline.json")
        print(f"\nJSON: {pl_dir / 'pipeline.json'}")
    if args.format in ("txt", "all"):
        export_pipeline_txt(result, pl_dir / "pipeline.txt")
        print(f"TXT: {pl_dir / 'pipeline.txt'}")


def cmd_social_proof(args: argparse.Namespace) -> None:
    from smm.social_proof import (
        export_social_proof_json,
        export_social_proof_txt,
        generate_social_proof_pack,
        social_proof_summary,
    )

    _ensure_data_dir()
    pack = generate_social_proof_pack(seed=args.seed)
    print(social_proof_summary(pack))

    sp_dir = DATA_DIR / "social_proof"
    sp_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_social_proof_json(pack, sp_dir / "social_proof.json")
        print(f"\nJSON: {sp_dir / 'social_proof.json'}")
    if args.format in ("txt", "all"):
        export_social_proof_txt(pack, sp_dir / "social_proof.txt")
        print(f"TXT: {sp_dir / 'social_proof.txt'}")


def cmd_personas(args: argparse.Namespace) -> None:
    from smm.audience_personas import (
        export_personas_json,
        export_personas_txt,
        generate_personas,
        personas_summary,
    )

    _ensure_data_dir()
    personas = generate_personas(pillar=args.pillar or None)
    print(personas_summary(personas))

    p_dir = DATA_DIR / "personas"
    p_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_personas_json(personas, p_dir / "personas.json")
        print(f"\nJSON: {p_dir / 'personas.json'}")
    if args.format in ("txt", "all"):
        export_personas_txt(personas, p_dir / "personas.txt")
        print(f"TXT: {p_dir / 'personas.txt'}")


def cmd_topic_ab(args: argparse.Namespace) -> None:
    from smm.topic_ab_test import (
        ab_topics_summary,
        export_ab_topics_json,
        export_ab_topics_txt,
        generate_ab_topics,
    )

    _ensure_data_dir()
    pairs = generate_ab_topics(
        pillar=args.pillar or None,
        platform=args.platform or None,
        seed=args.seed,
    )
    print(ab_topics_summary(pairs))

    ab_dir = DATA_DIR / "topic_ab"
    ab_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_ab_topics_json(pairs, ab_dir / "topic_ab.json")
        print(f"\nJSON: {ab_dir / 'topic_ab.json'}")
    if args.format in ("txt", "all"):
        export_ab_topics_txt(pairs, ab_dir / "topic_ab.txt")
        print(f"TXT: {ab_dir / 'topic_ab.txt'}")


def cmd_score(args: argparse.Namespace) -> None:
    from smm.content_scoring import (
        export_scores_json,
        export_scores_txt,
        generate_scored_batch,
        scoring_summary,
    )

    _ensure_data_dir()
    scored = generate_scored_batch(count=args.count, seed=args.seed)
    print(scoring_summary(scored))

    sc_dir = DATA_DIR / "scoring"
    sc_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_scores_json(scored, sc_dir / "scores.json")
        print(f"\nJSON: {sc_dir / 'scores.json'}")
    if args.format in ("txt", "all"):
        export_scores_txt(scored, sc_dir / "scores.txt")
        print(f"TXT: {sc_dir / 'scores.txt'}")


def cmd_engage(args: argparse.Namespace) -> None:
    from smm.engagement_hooks import (
        engagement_summary,
        generate_poll,
        generate_question,
        generate_quiz,
        generate_this_or_that,
    )

    pillar = args.pillar
    if args.action == "poll":
        hook = generate_poll(pillar)
        print(f"Опрос: {hook.content}")
        for i, opt in enumerate(hook.options, 1):
            print(f"  {i}. {opt}")
    elif args.action == "quiz":
        hook = generate_quiz(pillar)
        print(f"Квиз: {hook.content}")
        for i, opt in enumerate(hook.options, 1):
            marker = " ✓" if i - 1 == hook.correct_index else ""
            print(f"  {i}. {opt}{marker}")
    elif args.action == "question":
        q = generate_question(pillar)
        print(f"Вопрос для аудитории: {q}")
    elif args.action == "this-or-that":
        a, b = generate_this_or_that(pillar)
        print(f"This or That: {a} vs {b}")
    elif args.action == "summary":
        print(engagement_summary(pillar))


def cmd_calendar(args: argparse.Namespace) -> None:
    from smm.content_calendar_html import generate_calendar_file
    from smm.ready_posts import generate_ready_posts

    _ensure_data_dir()
    posts = generate_ready_posts(days=args.days, seed=args.seed)
    output = Path(args.output) if args.output else DATA_DIR / "calendar.html"
    path = generate_calendar_file(posts, output)
    print(f"Контент-календарь: {len(posts)} постов → {path}")


def cmd_ab_test(args: argparse.Namespace) -> None:
    from smm.ab_variants import (
        ab_summary,
        export_ab_csv,
        export_ab_json,
        export_ab_markdown,
        generate_ab_posts,
    )

    _ensure_data_dir()
    posts = generate_ab_posts(days=args.days, seed=args.seed)
    print(ab_summary(posts))

    ab_dir = DATA_DIR / "ab_test"
    ab_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_ab_json(posts, ab_dir / "ab_variants.json")
        print(f"\nJSON: {ab_dir / 'ab_variants.json'}")
    if args.format in ("csv", "all"):
        export_ab_csv(posts, ab_dir / "ab_variants.csv")
        print(f"CSV: {ab_dir / 'ab_variants.csv'}")
    if args.format in ("markdown", "all"):
        export_ab_markdown(posts, ab_dir / "ab_variants.md")
        print(f"Markdown: {ab_dir / 'ab_variants.md'}")


def cmd_week_pack(args: argparse.Namespace) -> None:
    from smm.week_pack import generate_week_pack

    _ensure_data_dir()
    out = Path(args.output) if args.output else None
    paths = generate_week_pack(days=args.days, seed=args.seed, out_dir=out)
    print(f"Недельный пакет контента сгенерирован ({len(paths)} файлов):\n")
    for name, path in sorted(paths.items()):
        print(f"  {name}: {path}")


def cmd_biolink(args: argparse.Namespace) -> None:
    from smm.biolink import BioLinkPage, generate_biolink_file

    _ensure_data_dir()
    page = BioLinkPage()
    if args.brand:
        page.brand = args.brand
    if args.tagline:
        page.tagline = args.tagline
    if args.telegram:
        page.telegram = args.telegram
    out = Path(args.output) if args.output else None
    path = generate_biolink_file(page, output=out)
    print(f"Биолинк-страница сгенерирована: {path}")
    print(f"  Ссылок: {len(page.links)}")


def cmd_optimize(args: argparse.Namespace) -> None:
    from smm.posting_schedule_optimizer import (
        optimizer_summary,
        recommend_schedule,
        schedule_heatmap,
    )

    _ensure_data_dir()
    if args.action == "recommend":
        recs = recommend_schedule(days=args.days, posts_per_platform=3)
        print(optimizer_summary(recs))
        print()
        for rec in recs[:9]:
            times_str = ", ".join(t.strftime("%H:%M") for t in rec.recommended_times)
            print(f"  {rec.day} {rec.platform:<10} -> {times_str}")
        if len(recs) > 9:
            print(f"  ... и ещё {len(recs) - 9}")
    elif args.action == "heatmap":
        print(schedule_heatmap(Platform(args.platform)))


def cmd_repurpose(args: argparse.Namespace) -> None:
    from smm.content_repurposer import (
        export_repurposed_json,
        repurpose_batch,
        repurpose_summary,
    )
    from smm.ready_posts import generate_ready_posts

    _ensure_data_dir()
    posts = generate_ready_posts(days=args.days, seed=args.seed)
    targets = (
        [Platform(p.strip()) for p in args.targets.split(",")] if args.targets else None
    )
    repurposed = repurpose_batch(posts, targets=targets)
    print(repurpose_summary(repurposed))

    rep_dir = DATA_DIR / "repurposed"
    rep_dir.mkdir(exist_ok=True)
    export_repurposed_json(repurposed, rep_dir / "repurposed.json")
    print(f"\nJSON: {rep_dir / 'repurposed.json'}")


def cmd_dashboard(args: argparse.Namespace) -> None:
    from smm.dashboard import dashboard_summary, generate_dashboard

    _ensure_data_dir()
    output = Path(args.output) if args.output else None
    path = generate_dashboard(days=args.days, seed=args.seed, output=output)
    print(dashboard_summary(path))


def cmd_hooks(args: argparse.Namespace) -> None:
    from smm.viral_hooks import (
        export_hooks_json,
        export_hooks_txt,
        generate_all_hooks,
        generate_hooks,
        hooks_summary,
        pick_random_hooks,
    )

    _ensure_data_dir()
    if args.count > 0:
        hooks = pick_random_hooks(
            count=args.count,
            pillar=args.pillar or None,
            seed=args.seed,
        )
    else:
        hooks = generate_hooks(args.pillar) if args.pillar else generate_all_hooks()
    print(hooks_summary(hooks))

    fmt = args.format
    if fmt in ("json", "all"):
        export_hooks_json(hooks, DATA_DIR / "viral_hooks.json")
        print(f"\nJSON: {DATA_DIR / 'viral_hooks.json'}")
    if fmt in ("txt", "all"):
        export_hooks_txt(hooks, DATA_DIR / "viral_hooks.txt")
        print(f"TXT: {DATA_DIR / 'viral_hooks.txt'}")


def cmd_funnel(args: argparse.Namespace) -> None:
    from smm.conversion_funnel import (
        export_funnel_json,
        export_funnel_txt,
        funnel_summary,
        generate_all_funnels,
        generate_pillar_funnel,
    )

    _ensure_data_dir()
    funnels = (
        [generate_pillar_funnel(args.pillar)] if args.pillar else generate_all_funnels()
    )
    print(funnel_summary(funnels))

    fmt = args.format
    if fmt in ("json", "all"):
        export_funnel_json(funnels, DATA_DIR / "funnel.json")
        print(f"\nJSON: {DATA_DIR / 'funnel.json'}")
    if fmt in ("txt", "all"):
        export_funnel_txt(funnels, DATA_DIR / "funnel.txt")
        print(f"TXT: {DATA_DIR / 'funnel.txt'}")


def cmd_mix(args: argparse.Namespace) -> None:
    from smm.content_mixer import (
        export_mix_json,
        export_mix_txt,
        generate_mixed_schedule,
        mix_summary,
    )

    _ensure_data_dir()
    day_mixes = generate_mixed_schedule(days=args.days, seed=args.seed)
    print(mix_summary(day_mixes))

    fmt = args.format
    if fmt in ("json", "all"):
        export_mix_json(day_mixes, DATA_DIR / "content_mix.json")
        print(f"\nJSON: {DATA_DIR / 'content_mix.json'}")
    if fmt in ("txt", "all"):
        export_mix_txt(day_mixes, DATA_DIR / "content_mix.txt")
        print(f"TXT: {DATA_DIR / 'content_mix.txt'}")


def cmd_ugc(args: argparse.Namespace) -> None:
    from smm.ugc_templates import (
        export_ugc_json,
        export_ugc_txt,
        generate_all_ugc_templates,
        generate_ugc_templates,
        ugc_summary,
    )

    _ensure_data_dir()
    templates = (
        generate_ugc_templates(args.pillar)
        if args.pillar
        else generate_all_ugc_templates()
    )
    print(ugc_summary(templates))

    fmt = args.format
    if fmt in ("json", "all"):
        export_ugc_json(templates, DATA_DIR / "ugc_templates.json")
        print(f"\nJSON: {DATA_DIR / 'ugc_templates.json'}")
    if fmt in ("txt", "all"):
        export_ugc_txt(templates, DATA_DIR / "ugc_templates.txt")
        print(f"TXT: {DATA_DIR / 'ugc_templates.txt'}")


def cmd_strategy(args: argparse.Namespace) -> None:
    from smm.content_strategy import (
        export_strategy_json,
        export_strategy_txt,
        generate_strategy,
        strategy_summary,
    )

    _ensure_data_dir()
    strategy = generate_strategy()
    print(strategy_summary(strategy))

    strat_dir = DATA_DIR / "strategy"
    strat_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_strategy_json(strategy, strat_dir / "strategy.json")
        print(f"\nJSON: {strat_dir / 'strategy.json'}")
    if args.format in ("txt", "all"):
        export_strategy_txt(strategy, strat_dir / "strategy.txt")
        print(f"TXT: {strat_dir / 'strategy.txt'}")


def cmd_competitors(args: argparse.Namespace) -> None:
    from smm.competitor_analysis import (
        analysis_summary,
        analyze_all_niches,
        analyze_niche,
        export_analysis_json,
        export_analysis_txt,
    )

    _ensure_data_dir()
    analyses = [analyze_niche(args.pillar)] if args.pillar else analyze_all_niches()
    print(analysis_summary(analyses))

    comp_dir = DATA_DIR / "competitors"
    comp_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_analysis_json(analyses, comp_dir / "analysis.json")
        print(f"\nJSON: {comp_dir / 'analysis.json'}")
    if args.format in ("txt", "all"):
        export_analysis_txt(analyses, comp_dir / "analysis.txt")
        print(f"TXT: {comp_dir / 'analysis.txt'}")


def cmd_series(args: argparse.Namespace) -> None:
    from smm.content_series import (
        export_series_json,
        export_series_txt,
        generate_all_series,
        series_summary,
    )

    _ensure_data_dir()
    all_series = generate_all_series(seed=args.seed)
    if args.pillar:
        all_series = [s for s in all_series if args.pillar.lower() in s.pillar.lower()]
    print(series_summary(all_series))

    ser_dir = DATA_DIR / "series"
    ser_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_series_json(all_series, ser_dir / "series.json")
        print(f"\nJSON: {ser_dir / 'series.json'}")
    if args.format in ("txt", "all"):
        export_series_txt(all_series, ser_dir / "series.txt")
        print(f"TXT: {ser_dir / 'series.txt'}")


def cmd_carousel(args: argparse.Namespace) -> None:
    from smm.carousel_generator import (
        carousel_summary,
        export_carousels_json,
        export_carousels_txt,
        generate_carousels,
    )

    _ensure_data_dir()
    packs = generate_carousels(count=args.count, seed=args.seed)
    print(carousel_summary(packs))

    car_dir = DATA_DIR / "carousels"
    car_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_carousels_json(packs, car_dir / "carousels.json")
        print(f"\nJSON: {car_dir / 'carousels.json'}")
    if args.format in ("txt", "all"):
        export_carousels_txt(packs, car_dir / "carousels.txt")
        print(f"TXT: {car_dir / 'carousels.txt'}")


def cmd_stories(args: argparse.Namespace) -> None:
    from smm.story_generator import (
        export_story_packs_json,
        export_story_packs_txt,
        generate_story_packs,
        story_summary,
    )

    _ensure_data_dir()
    packs = generate_story_packs(count=args.count, seed=args.seed)
    print(story_summary(packs))

    story_dir = DATA_DIR / "stories"
    story_dir.mkdir(exist_ok=True)

    if args.format in ("json", "all"):
        export_story_packs_json(packs, story_dir / "story_packs.json")
        print(f"\nJSON: {story_dir / 'story_packs.json'}")
    if args.format in ("txt", "all"):
        export_story_packs_txt(packs, story_dir / "story_packs.txt")
        print(f"TXT: {story_dir / 'story_packs.txt'}")


def cmd_content_bank(args: argparse.Namespace) -> None:
    from smm.content_bank import get_ctas, get_hooks, get_story_framework

    if args.action == "hooks":
        hooks = get_hooks(args.keyword, count=args.count)
        print(f"Хуки для «{args.keyword}» ({len(hooks)} шт.):\n")
        for i, h in enumerate(hooks, 1):
            print(f"  {i}. {h}")
    elif args.action == "ctas":
        ctas = get_ctas(args.product_type, count=args.count)
        print(f"CTA ({args.product_type}, {len(ctas)} шт.):\n")
        for i, c in enumerate(ctas, 1):
            print(f"  {i}. {c}")
    elif args.action == "story":
        fw = get_story_framework(args.keyword, "Подпишись", niche=args.niche)
        print(f"Сторис-фреймворк ({fw['name']}):\n")
        for key, val in fw.items():
            if key != "name":
                print(f"  {key}: {val}")


def cmd_service(args: argparse.Namespace) -> None:
    from smm.service_spec import ServiceSpec

    spec = ServiceSpec()
    if args.action == "pricing":
        print(spec.pricing_table())
    elif args.action == "full":
        print(spec.full_spec())


def cmd_generate(args: argparse.Namespace) -> None:
    _ensure_data_dir()
    plan = generate_week_plan(days=args.days, seed=args.seed)
    json_path = DATA_DIR / "week_plan.json"
    md_path = DATA_DIR / "week_plan.md"
    export_plan_json(plan, json_path)
    export_plan_markdown(plan, md_path)

    by_pillar: dict[str, int] = {}
    by_platform: dict[str, int] = {}
    for s in plan:
        by_pillar[s.pillar.name] = by_pillar.get(s.pillar.name, 0) + 1
        by_platform[s.platform.value] = by_platform.get(s.platform.value, 0) + 1

    print(f"Сгенерирован контент-план: {len(plan)} постов на {args.days} дней\n")
    print("По направлениям:")
    for name, count in sorted(by_pillar.items()):
        print(f"  {name}: {count}")
    print("\nПо платформам:")
    for name, count in sorted(by_platform.items()):
        print(f"  {name}: {count}")
    print("\nФайлы:")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="smm", description="AI-powered SMM automation toolkit"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_plan = sub.add_parser("plan", help="Generate a content plan")
    p_plan.add_argument("--days", type=int, default=7)
    p_plan.add_argument("--posts", type=int, default=3)

    p_post = sub.add_parser("post", help="Generate a single post")
    p_post.add_argument(
        "--platform", required=True, choices=[p.value for p in Platform]
    )
    p_post.add_argument("--format", default="static_post")
    p_post.add_argument("--topic", required=True)
    p_post.add_argument("--cta", default="link click")

    p_script = sub.add_parser("script", help="Generate a video script")
    p_script.add_argument("--topic", required=True)
    p_script.add_argument("--duration", type=int, default=60)

    sub.add_parser("trends", help="Analyze current trends")

    p_sched = sub.add_parser("schedule", help="Fill the content calendar")
    p_sched.add_argument("--days", type=int, default=7)

    p_export = sub.add_parser("export", help="Export calendar")
    p_export.add_argument("--format", choices=["csv", "buffer"], default="csv")
    p_export.add_argument("--output", default="calendar_export.csv")

    p_ref = sub.add_parser("referral", help="Manage referral links")
    p_ref.add_argument("action", choices=["add", "list"])
    p_ref.add_argument("--label", default="")
    p_ref.add_argument("--url", default="")
    p_ref.add_argument("--utm-source", default="")
    p_ref.add_argument("--utm-campaign", default="")

    p_gen = sub.add_parser("generate", help="Generate full weekly content plan")
    p_gen.add_argument("--days", type=int, default=7)
    p_gen.add_argument("--seed", type=int, default=None)

    p_write = sub.add_parser("write", help="AI-generate ready posts from plan")
    p_write.add_argument("--count", type=int, default=3)
    p_write.add_argument("--seed", type=int, default=None)

    p_dist = sub.add_parser(
        "distribute", help="Export platform-specific posting packages"
    )
    p_dist.add_argument("--days", type=int, default=7)
    p_dist.add_argument("--seed", type=int, default=None)

    p_prev = sub.add_parser("preview", help="Generate visual HTML preview of posts")
    p_prev.add_argument("--days", type=int, default=7)
    p_prev.add_argument("--seed", type=int, default=None)
    p_prev.add_argument("--output", default="")

    p_report = sub.add_parser(
        "report", help="Generate weekly analytics report template"
    )
    p_report.add_argument("--days", type=int, default=7)
    p_report.add_argument("--seed", type=int, default=None)
    p_report.add_argument("--format", choices=["json", "markdown"], default="markdown")

    p_land = sub.add_parser("landing", help="Generate service landing page")
    p_land.add_argument("--output", default="")
    p_land.add_argument("--brand", default="")
    p_land.add_argument("--contact", default="")

    p_batch = sub.add_parser(
        "batch", help="Generate ready-to-post content batch (no AI API needed)"
    )
    p_batch.add_argument("--days", type=int, default=7)
    p_batch.add_argument("--seed", type=int, default=None)
    p_batch.add_argument(
        "--format",
        choices=["json", "csv", "markdown", "all"],
        default="all",
    )

    p_sexp = sub.add_parser(
        "scheduler-export",
        help="Export content to Buffer/Later/Meta/iCal/Notion formats",
    )
    p_sexp.add_argument("--days", type=int, default=7)
    p_sexp.add_argument("--seed", type=int, default=None)

    p_prop = sub.add_parser("proposal", help="Generate a commercial proposal")
    p_prop.add_argument("--client-name", default="Client")
    p_prop.add_argument("--business", default="Tech Business")
    p_prop.add_argument("--niche", default="cybersecurity")
    p_prop.add_argument("--platforms", default="Instagram,TikTok")
    p_prop.add_argument("--posts", type=int, default=42)
    p_prop.add_argument("--goal", default="увеличить продажи через соцсети")

    p_svc = sub.add_parser("service", help="Show service specification")
    p_svc.add_argument(
        "action", choices=["pricing", "full"], default="pricing", nargs="?"
    )

    p_cb = sub.add_parser(
        "content-bank", help="Generate hooks, CTAs, and story frameworks"
    )
    p_cb.add_argument(
        "action", choices=["hooks", "ctas", "story"], default="hooks", nargs="?"
    )
    p_cb.add_argument("--keyword", default="Cyber Security")
    p_cb.add_argument("--count", type=int, default=5)
    p_cb.add_argument(
        "--product-type", choices=["course", "referral"], default="course"
    )
    p_cb.add_argument("--niche", default="cybersecurity")

    p_bio = sub.add_parser("biolink", help="Generate bio link page (Linktree-style)")
    p_bio.add_argument("--brand", default="")
    p_bio.add_argument("--tagline", default="")
    p_bio.add_argument("--telegram", default="")
    p_bio.add_argument("--output", default="")

    p_wp = sub.add_parser("week-pack", help="Generate complete weekly content package")
    p_wp.add_argument("--days", type=int, default=7)
    p_wp.add_argument("--seed", type=int, default=None)
    p_wp.add_argument("--output", default="")

    p_ab = sub.add_parser("ab-test", help="Generate A/B caption variants for testing")
    p_ab.add_argument("--days", type=int, default=7)
    p_ab.add_argument("--seed", type=int, default=None)
    p_ab.add_argument(
        "--format",
        choices=["json", "csv", "markdown", "all"],
        default="all",
    )

    p_ht = sub.add_parser("hashtags", help="Generate optimized hashtag sets")
    p_ht.add_argument(
        "action", choices=["generate", "report"], default="generate", nargs="?"
    )
    p_ht.add_argument("--pillar", default="Cyber Security & Ethical Hacking")
    p_ht.add_argument("--count", type=int, default=15)

    p_cal = sub.add_parser("calendar", help="Generate visual HTML content calendar")
    p_cal.add_argument("--days", type=int, default=7)
    p_cal.add_argument("--seed", type=int, default=None)
    p_cal.add_argument("--output", default="")

    p_val = sub.add_parser(
        "validate", help="Validate posts against platform constraints"
    )
    p_val.add_argument("--days", type=int, default=7)
    p_val.add_argument("--seed", type=int, default=None)

    p_rep = sub.add_parser("repurpose", help="Repurpose posts across platforms")
    p_rep.add_argument("--days", type=int, default=1)
    p_rep.add_argument("--seed", type=int, default=None)
    p_rep.add_argument("--targets", default="", help="Comma-separated target platforms")

    p_car = sub.add_parser("carousel", help="Generate carousel packs (4-5 slides)")
    p_car.add_argument("--count", type=int, default=5)
    p_car.add_argument("--seed", type=int, default=None)
    p_car.add_argument(
        "--format",
        choices=["json", "txt", "all"],
        default="all",
    )

    p_story = sub.add_parser("stories", help="Generate story packs (5-7 slides)")
    p_story.add_argument("--count", type=int, default=5)
    p_story.add_argument("--seed", type=int, default=None)
    p_story.add_argument(
        "--format",
        choices=["json", "txt", "all"],
        default="all",
    )

    p_hooks = sub.add_parser(
        "hooks", help="Generate viral hooks for stop-scroll content"
    )
    p_hooks.add_argument("--pillar", default="")
    p_hooks.add_argument("--count", type=int, default=0)
    p_hooks.add_argument("--seed", type=int, default=None)
    p_hooks.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_dash = sub.add_parser("dashboard", help="Generate interactive HTML dashboard")
    p_dash.add_argument("--days", type=int, default=7)
    p_dash.add_argument("--seed", type=int, default=None)
    p_dash.add_argument("--output", default="")

    p_funnel = sub.add_parser(
        "funnel", help="Generate conversion funnel content (TOFU/MOFU/BOFU)"
    )
    p_funnel.add_argument("--pillar", default="")
    p_funnel.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_ugc = sub.add_parser("ugc", help="Generate UGC templates for social proof")
    p_ugc.add_argument("--pillar", default="")
    p_ugc.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_mix = sub.add_parser("mix", help="Generate balanced content mix schedule")
    p_mix.add_argument("--days", type=int, default=7)
    p_mix.add_argument("--seed", type=int, default=None)
    p_mix.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_strat = sub.add_parser(
        "strategy", help="Generate unified content strategy document"
    )
    p_strat.add_argument(
        "--format",
        choices=["json", "txt", "all"],
        default="all",
    )

    p_comp = sub.add_parser(
        "competitors", help="Analyze competitors and content gaps per niche"
    )
    p_comp.add_argument("--pillar", default="", help="Analyze specific pillar only")
    p_comp.add_argument(
        "--format",
        choices=["json", "txt", "all"],
        default="all",
    )

    p_ser = sub.add_parser(
        "series", help="Generate multi-day content series (narrative arcs)"
    )
    p_ser.add_argument("--seed", type=int, default=None)
    p_ser.add_argument("--pillar", default="", help="Filter by pillar name")
    p_ser.add_argument(
        "--format",
        choices=["json", "txt", "all"],
        default="all",
    )

    p_opt = sub.add_parser(
        "optimize", help="Optimize posting schedule for maximum engagement"
    )
    p_opt.add_argument(
        "action", choices=["recommend", "heatmap"], default="recommend", nargs="?"
    )
    p_opt.add_argument("--days", type=int, default=7)
    p_opt.add_argument(
        "--platform", default="instagram", choices=[p.value for p in Platform]
    )

    p_xp = sub.add_parser("cross-promo", help="Generate cross-platform promotion posts")
    p_xp.add_argument("--pillar", default="", help="Filter by pillar name")
    p_xp.add_argument("--seed", type=int, default=None)
    p_xp.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_eng = sub.add_parser(
        "engage", help="Generate engagement hooks (polls, quizzes, questions)"
    )
    p_eng.add_argument(
        "action",
        choices=["poll", "quiz", "question", "this-or-that", "summary"],
        default="poll",
        nargs="?",
    )
    p_eng.add_argument("--pillar", default="Cyber Security & Ethical Hacking")

    p_email = sub.add_parser(
        "emails", help="Generate email nurture sequences per pillar"
    )
    p_email.add_argument("--pillar", default="", help="Filter by pillar name")
    p_email.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_cta = sub.add_parser(
        "ctas", help="CTA library — calls-to-action per funnel stage"
    )
    p_cta.add_argument("--stage", default="", help="Filter: tofu|mofu|bofu")
    p_cta.add_argument(
        "--platform", default="", help="Filter: instagram|tiktok|youtube"
    )
    p_cta.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_pers = sub.add_parser("personas", help="Audience personas and buyer profiles")
    p_pers.add_argument("--pillar", default="", help="Filter by pillar name")
    p_pers.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_score = sub.add_parser(
        "score", help="Score and prioritize content by performance"
    )
    p_score.add_argument("--count", type=int, default=30)
    p_score.add_argument("--seed", type=int, default=None)
    p_score.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_ra = sub.add_parser("ref-analytics", help="Referral campaign analytics report")
    p_ra.add_argument("--seed", type=int, default=None)
    p_ra.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_tab = sub.add_parser("topic-ab", help="A/B topic variants for split-testing")
    p_tab.add_argument("--pillar", default="", help="Filter by pillar name")
    p_tab.add_argument(
        "--platform", default="", help="Filter: instagram|tiktok|youtube"
    )
    p_tab.add_argument("--seed", type=int, default=None)
    p_tab.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_lm = sub.add_parser(
        "lead-magnets", help="Lead magnet content outlines for email capture"
    )
    p_lm.add_argument("--pillar", default="", help="Filter by pillar name")
    p_lm.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_sp = sub.add_parser("social-proof", help="Testimonials, stats and trust badges")
    p_sp.add_argument("--seed", type=int, default=None)
    p_sp.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_pl = sub.add_parser(
        "pipeline", help="Full content pipeline — enrich, score and rank posts"
    )
    p_pl.add_argument("--days", type=int, default=7)
    p_pl.add_argument("--seed", type=int, default=None)
    p_pl.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_rt = sub.add_parser(
        "retargeting", help="Retargeting pixel and audience setup guide"
    )
    p_rt.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_pr = sub.add_parser("pricing", help="Pricing tiers and ROI calculator")
    p_pr.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_wb = sub.add_parser("webinar", help="Webinar funnel messages (invite to sales)")
    p_wb.add_argument("--pillar", default="", help="Filter by pillar name")
    p_wb.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_tg = sub.add_parser("tg-bot", help="Telegram bot config and message templates")
    p_tg.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_ap = sub.add_parser(
        "auto-poster", help="Auto-posting config (API profiles, slots, retry)"
    )
    p_ap.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_ad = sub.add_parser(
        "analytics-dash", help="Analytics dashboard (KPI, ROI, growth)"
    )
    p_ad.add_argument("--seed", type=int, default=None)
    p_ad.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_inf = sub.add_parser(
        "influencer", help="Influencer outreach templates and criteria"
    )
    p_inf.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_cm = sub.add_parser("community", help="Community management templates and rules")
    p_cm.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_seo = sub.add_parser("seo", help="SEO pack (keywords, YT titles, meta, alt)")
    p_seo.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_lc = sub.add_parser("launch-check", help="Launch checklist — go-live readiness")
    p_lc.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_adc = sub.add_parser(
        "ad-creative", help="Ad creatives (copies, audiences, budgets)"
    )
    p_adc.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_bk = sub.add_parser(
        "brand-kit", help="Brand kit (colors, typography, tone of voice)"
    )
    p_bk.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_ntf = sub.add_parser(
        "notifications", help="Notification system (alerts, milestones, deadlines)"
    )
    p_ntf.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_ca = sub.add_parser(
        "content-approval",
        help="Content approval workflow (stages, roles, checklists)",
    )
    p_ca.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_crisis = sub.add_parser(
        "crisis", help="Crisis management (incident response protocols)"
    )
    p_crisis.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_partner = sub.add_parser(
        "partnership", help="Partnership program (affiliate, commissions, promo)"
    )
    p_partner.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_loc = sub.add_parser(
        "localization", help="Localization (glossary, CTA translations, rules)"
    )
    p_loc.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_ml = sub.add_parser(
        "media-library", help="Media library (image/video specs, templates, stocks)"
    )
    p_ml.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_utm = sub.add_parser(
        "utm-builder", help="UTM builder (campaign links, naming rules)"
    )
    p_utm.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_sc = sub.add_parser(
        "seasonal-calendar",
        help="Seasonal calendar (holidays, campaigns, BF/CM plan)",
    )
    p_sc.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_gam = sub.add_parser(
        "gamification",
        help="Gamification (badges, levels, challenges, rewards)",
    )
    p_gam.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_fa = sub.add_parser(
        "funnel-auto",
        help="Funnel automation (stages, messages, segments, re-engage)",
    )
    p_fa.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_rc = sub.add_parser(
        "content-recycle",
        help="Content recycler (evergreen rules, refresh, transforms)",
    )
    p_rc.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_roi = sub.add_parser(
        "roi-tracker",
        help="ROI tracker (revenue, costs, channels, projections)",
    )
    p_roi.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_comp = sub.add_parser(
        "compliance",
        help="Compliance checker (platform rules, disclosures, copyright)",
    )
    p_comp.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_ob = sub.add_parser(
        "onboarding",
        help="Onboarding flow (welcome, milestones, checklists, FAQ)",
    )
    p_ob.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_abp = sub.add_parser(
        "ab-price-test",
        help="A/B price testing (price variants, bundles, discounts)",
    )
    p_abp.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_audit = sub.add_parser(
        "content-audit",
        help="Content audit (quality, gaps, checklist, benchmarks)",
    )
    p_audit.add_argument("--format", choices=["json", "txt", "all"], default="all")

    p_listen = sub.add_parser(
        "social-listening",
        help="Social listening (keywords, sentiment, alerts, competitors)",
    )
    p_listen.add_argument("--format", choices=["json", "txt", "all"], default="all")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    async_commands = {"plan", "post", "script", "trends", "write"}
    func_name = f"cmd_{args.command.replace('-', '_')}"
    if args.command in async_commands:
        asyncio.run(globals()[func_name](args))
    else:
        globals()[func_name](args)


if __name__ == "__main__":
    main()
