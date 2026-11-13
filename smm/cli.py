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
    output: list[dict[str, str]] = []
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
