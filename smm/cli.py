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

    p_svc = sub.add_parser("service", help="Show service specification")
    p_svc.add_argument(
        "action", choices=["pricing", "full"], default="pricing", nargs="?"
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    async_commands = {"plan", "post", "script", "trends", "write"}
    if args.command in async_commands:
        asyncio.run(globals()[f"cmd_{args.command}"](args))
    else:
        globals()[f"cmd_{args.command}"](args)


if __name__ == "__main__":
    main()
