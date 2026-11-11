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

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    async_commands = {"plan", "post", "script", "trends"}
    if args.command in async_commands:
        asyncio.run(globals()[f"cmd_{args.command}"](args))
    else:
        globals()[f"cmd_{args.command}"](args)


if __name__ == "__main__":
    main()
