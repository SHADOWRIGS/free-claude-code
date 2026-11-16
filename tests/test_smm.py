"""Tests for the smm automation toolkit."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

from smm.content_pillars import PILLARS, all_topics_flat, get_pillar_by_name
from smm.platforms import PLATFORM_SPECS, Platform
from smm.post_generator import (
    export_plan_json,
    export_plan_markdown,
    generate_week_plan,
)
from smm.referral import ReferralLink, ReferralRegistry
from smm.scheduler import ContentCalendar, ScheduledPost
from smm.templates import ROLE_TEMPLATES

# --- Platform tests ---


class TestPlatform:
    def test_all_platforms_have_specs(self) -> None:
        for p in Platform:
            assert p in PLATFORM_SPECS

    def test_spec_posting_times_not_empty(self) -> None:
        for p, spec in PLATFORM_SPECS.items():
            assert spec.posting_times, f"{p} has no posting times"

    def test_spec_formats_not_empty(self) -> None:
        for p, spec in PLATFORM_SPECS.items():
            assert spec.formats, f"{p} has no formats"

    def test_hashtag_range_ordered(self) -> None:
        for p, spec in PLATFORM_SPECS.items():
            lo, hi = spec.hashtag_range
            assert lo < hi, f"{p} hashtag range is inverted"

    def test_platform_str_values(self) -> None:
        assert Platform.INSTAGRAM == "instagram"
        assert Platform.TIKTOK == "tiktok"
        assert Platform.YOUTUBE == "youtube"


# --- Referral tests ---


class TestReferralLink:
    def test_build_url_plain(self) -> None:
        link = ReferralLink(label="Test", url="https://example.com", utm_medium="")
        assert link.build_url() == "https://example.com"

    def test_build_url_default_medium(self) -> None:
        link = ReferralLink(label="Test", url="https://example.com")
        assert "utm_medium=social" in link.build_url()

    def test_build_url_with_utm(self) -> None:
        link = ReferralLink(
            label="Course",
            url="https://example.com/course",
            utm_source="instagram",
            utm_campaign="launch",
        )
        url = link.build_url()
        assert "utm_source=instagram" in url
        assert "utm_campaign=launch" in url
        assert "utm_medium=social" in url

    def test_build_url_platform_override(self) -> None:
        link = ReferralLink(label="Ref", url="https://example.com")
        url = link.build_url("tiktok")
        assert "utm_source=tiktok" in url

    def test_build_url_preserves_existing_query(self) -> None:
        link = ReferralLink(
            label="Ref",
            url="https://example.com?ref=123",
            utm_source="ig",
        )
        url = link.build_url()
        assert "?ref=123" in url
        assert "&utm_source=ig" in url


class TestReferralRegistry:
    def test_add_and_list(self) -> None:
        reg = ReferralRegistry()
        reg.add(ReferralLink(label="A", url="https://a.com"))
        reg.add(ReferralLink(label="B", url="https://b.com"))
        assert len(reg.links) == 2

    def test_for_platform_filter(self) -> None:
        reg = ReferralRegistry()
        reg.add(
            ReferralLink(label="IG only", url="https://ig.com", platforms=["instagram"])
        )
        reg.add(ReferralLink(label="All", url="https://all.com"))
        assert len(reg.for_platform("instagram")) == 2
        assert len(reg.for_platform("tiktok")) == 1

    def test_save_load_roundtrip(self, tmp_path: Path) -> None:
        path = tmp_path / "refs.json"
        reg = ReferralRegistry()
        reg.add(
            ReferralLink(
                label="Course",
                url="https://course.com",
                utm_source="test",
                utm_campaign="q1",
            )
        )
        reg.save(path)
        loaded = ReferralRegistry.load(path)
        assert len(loaded.links) == 1
        assert loaded.links[0].label == "Course"
        assert loaded.links[0].utm_campaign == "q1"

    def test_load_missing_file(self, tmp_path: Path) -> None:
        reg = ReferralRegistry.load(tmp_path / "missing.json")
        assert reg.links == []

    def test_context_string_empty(self) -> None:
        reg = ReferralRegistry()
        assert "No referral" in reg.context_string()


# --- Scheduler tests ---


class TestScheduledPost:
    def test_roundtrip(self) -> None:
        post = ScheduledPost(
            id="abc123",
            platform=Platform.INSTAGRAM,
            format="reels",
            topic="AI tips",
            publish_at=datetime(2025, 1, 15, 9, 0),
            status="draft",
        )
        data = post.to_dict()
        restored = ScheduledPost.from_dict(data)
        assert restored.id == post.id
        assert restored.platform == post.platform
        assert restored.publish_at == post.publish_at


class TestContentCalendar:
    def test_fill_week_creates_posts(self) -> None:
        cal = ContentCalendar()
        created = cal.fill_week(days=1)
        total_slots = sum(len(spec.posting_times) for spec in PLATFORM_SPECS.values())
        assert len(created) == total_slots

    def test_save_load_roundtrip(self, tmp_path: Path) -> None:
        path = tmp_path / "cal.json"
        cal = ContentCalendar(_path=path)
        cal.fill_week(days=1)
        cal.save()

        loaded = ContentCalendar.load(path)
        assert len(loaded.posts) == len(cal.posts)

    def test_upcoming_filters(self) -> None:
        cal = ContentCalendar()
        past = ScheduledPost(
            id="past",
            platform=Platform.TIKTOK,
            format="short_video",
            topic="old",
            publish_at=datetime.now() - timedelta(days=2),
        )
        future = ScheduledPost(
            id="future",
            platform=Platform.TIKTOK,
            format="short_video",
            topic="new",
            publish_at=datetime.now() + timedelta(days=1),
        )
        cal.add(past)
        cal.add(future)
        upcoming = cal.upcoming(days=7)
        assert len(upcoming) == 1
        assert upcoming[0].id == "future"

    def test_by_platform(self) -> None:
        cal = ContentCalendar()
        cal.fill_week(days=1)
        ig_posts = cal.by_platform(Platform.INSTAGRAM)
        assert all(p.platform == Platform.INSTAGRAM for p in ig_posts)
        assert len(ig_posts) == len(PLATFORM_SPECS[Platform.INSTAGRAM].posting_times)

    def test_export_csv(self, tmp_path: Path) -> None:
        cal = ContentCalendar()
        cal.fill_week(days=1)
        csv_path = tmp_path / "export.csv"
        cal.export_csv(csv_path)
        content = csv_path.read_text()
        assert "id,platform" in content
        assert len(content.strip().split("\n")) > 1

    def test_export_buffer_json(self, tmp_path: Path) -> None:
        cal = ContentCalendar()
        cal.fill_week(days=1)
        buf_path = tmp_path / "buffer.json"
        cal.export_buffer_json(buf_path)
        data = json.loads(buf_path.read_text())
        assert isinstance(data, list)
        assert all("text" in entry for entry in data)


# --- Template tests ---


class TestTemplates:
    def test_all_roles_have_templates(self) -> None:
        expected = {"strategist", "copywriter", "scriptwriter", "visual", "analyst"}
        assert set(ROLE_TEMPLATES.keys()) == expected

    def test_templates_have_placeholders(self) -> None:
        for role, tmpl in ROLE_TEMPLATES.items():
            assert "{" in tmpl, f"{role} template has no placeholders"


# --- Content Pillars tests ---


class TestContentPillars:
    def test_pillars_count(self) -> None:
        assert len(PILLARS) == 5

    def test_each_pillar_has_topics(self) -> None:
        for p in PILLARS:
            assert len(p.topics) >= 10, f"{p.name} has fewer than 10 topics"

    def test_each_pillar_has_hashtags(self) -> None:
        for p in PILLARS:
            assert p.hashtags_ru, f"{p.name} missing RU hashtags"
            assert p.hashtags_en, f"{p.name} missing EN hashtags"

    def test_product_types(self) -> None:
        products = {p.product for p in PILLARS}
        assert products == {"course", "referral"}

    def test_get_pillar_by_name_found(self) -> None:
        p = get_pillar_by_name("cyber")
        assert p is not None
        assert "Cyber" in p.name

    def test_get_pillar_by_name_not_found(self) -> None:
        assert get_pillar_by_name("nonexistent") is None

    def test_all_topics_flat(self) -> None:
        flat = all_topics_flat()
        total = sum(len(p.topics) for p in PILLARS)
        assert len(flat) == total
        assert all(len(t) == 3 for t in flat)


# --- Post Generator tests ---


class TestPostGenerator:
    def test_generate_week_plan_count(self) -> None:
        plan = generate_week_plan(days=7, seed=42)
        assert len(plan) == 63  # 3 platforms * 3 slots * 7 days

    def test_generate_week_plan_deterministic(self) -> None:
        a = generate_week_plan(days=1, seed=99)
        b = generate_week_plan(days=1, seed=99)
        assert len(a) == len(b)
        for sa, sb in zip(a, b, strict=True):
            assert sa.topic == sb.topic
            assert sa.platform == sb.platform

    def test_slots_cover_all_platforms(self) -> None:
        plan = generate_week_plan(days=1, seed=42)
        platforms = {s.platform for s in plan}
        assert platforms == {Platform.INSTAGRAM, Platform.TIKTOK, Platform.YOUTUBE}

    def test_each_slot_has_required_fields(self) -> None:
        plan = generate_week_plan(days=1, seed=42)
        for s in plan:
            assert s.topic
            assert s.hook
            assert s.cta
            assert s.hashtags
            assert s.format

    def test_referral_urls_have_utm(self) -> None:
        plan = generate_week_plan(days=1, seed=42)
        with_url = [s for s in plan if s.referral_url]
        assert len(with_url) > 0
        for s in with_url:
            assert "utm_source=" in s.referral_url
            assert "utm_medium=social" in s.referral_url

    def test_export_json(self, tmp_path: Path) -> None:
        plan = generate_week_plan(days=1, seed=42)
        out = tmp_path / "plan.json"
        export_plan_json(plan, out)
        data = json.loads(out.read_text())
        assert len(data) == len(plan)
        assert all("topic" in d for d in data)

    def test_export_markdown(self, tmp_path: Path) -> None:
        plan = generate_week_plan(days=1, seed=42)
        out = tmp_path / "plan.md"
        export_plan_markdown(plan, out)
        content = out.read_text()
        assert "# Контент-план SMM" in content
        assert "##" in content

    def test_custom_start_date(self) -> None:
        start = date(2025, 6, 1)
        plan = generate_week_plan(start=start, days=3, seed=42)
        days = {s.day for s in plan}
        assert start in days
        assert len(days) == 3


# --- AI Writer tests ---


class TestAIWriter:
    def test_ready_post_fields(self) -> None:
        from smm.ai_writer import ReadyPost

        plan = generate_week_plan(days=1, seed=42)
        slot = plan[0]
        rp = ReadyPost(
            slot=slot,
            caption="Test caption",
            visual_brief="Test brief",
            script="Test script",
            alt_hooks=["hook1", "hook2"],
        )
        assert rp.caption == "Test caption"
        assert rp.slot is slot
        assert len(rp.alt_hooks) == 2

    def test_writer_prompt_has_placeholders(self) -> None:
        from smm.ai_writer import POST_PROMPT

        assert "{platform}" in POST_PROMPT
        assert "{topic}" in POST_PROMPT
        assert "{hook}" in POST_PROMPT


# --- Distributor tests ---


class TestDistributor:
    def test_build_distribution_counts(self) -> None:
        from smm.distributor import build_distribution

        dist = build_distribution(days=1, seed=42)
        assert len(dist.instagram) == 3
        assert len(dist.tiktok) == 3
        assert len(dist.youtube) == 3

    def test_instagram_package_fields(self) -> None:
        from smm.distributor import build_distribution

        dist = build_distribution(days=1, seed=42)
        pkg = dist.instagram[0]
        assert pkg.date
        assert pkg.time
        assert pkg.caption
        assert pkg.hashtags
        assert pkg.pillar

    def test_tiktok_package_has_script(self) -> None:
        from smm.distributor import build_distribution

        dist = build_distribution(days=1, seed=42)
        pkg = dist.tiktok[0]
        assert pkg.script
        assert pkg.hook
        assert "Hook:" in pkg.script

    def test_youtube_package_has_title(self) -> None:
        from smm.distributor import build_distribution

        dist = build_distribution(days=1, seed=42)
        pkg = dist.youtube[0]
        assert pkg.title
        assert pkg.tags
        assert pkg.description

    def test_export_creates_files(self, tmp_path: Path) -> None:
        from smm.distributor import build_distribution

        dist = build_distribution(days=1, seed=42)
        paths = dist.export_all(tmp_path / "packages")
        assert len(paths) == 3
        for p in paths.values():
            assert p.exists()
            data = json.loads(p.read_text())
            assert isinstance(data, list)
            assert len(data) == 3

    def test_summary_output(self) -> None:
        from smm.distributor import build_distribution

        dist = build_distribution(days=1, seed=42)
        s = dist.summary()
        assert "Instagram: 3" in s
        assert "TikTok: 3" in s
        assert "YouTube: 3" in s
        assert "Total: 9" in s


# --- Service Spec tests ---


class TestServiceSpec:
    def test_tiers_count(self) -> None:
        from smm.service_spec import TIERS

        assert len(TIERS) == 3

    def test_tier_prices_ascending(self) -> None:
        from smm.service_spec import TIERS

        prices = [t.price_monthly_usd for t in TIERS]
        assert prices == sorted(prices)

    def test_pricing_table(self) -> None:
        from smm.service_spec import ServiceSpec

        spec = ServiceSpec()
        table = spec.pricing_table()
        assert "Starter" in table
        assert "Growth" in table
        assert "Pro" in table
        assert "$97" in table

    def test_full_spec_sections(self) -> None:
        from smm.service_spec import ServiceSpec

        spec = ServiceSpec()
        full = spec.full_spec()
        assert "# SMM Automation Service" in full
        assert "## Pricing" in full
        assert "## Target Audience" in full
        assert "## Deliverables" in full
        assert "## Tech Stack" in full

    def test_deliverables_count(self) -> None:
        from smm.service_spec import DELIVERABLES

        assert len(DELIVERABLES) >= 5


# --- Preview tests ---


class TestPreview:
    def test_render_preview_returns_html(self) -> None:
        from smm.preview import render_preview

        plan = generate_week_plan(days=1, seed=42)
        html_content = render_preview(plan)
        assert "<!DOCTYPE html>" in html_content
        assert "Instagram" in html_content
        assert "TikTok" in html_content
        assert "YouTube" in html_content

    def test_render_preview_contains_all_posts(self) -> None:
        from smm.preview import render_preview

        plan = generate_week_plan(days=1, seed=42)
        html_content = render_preview(plan)
        for slot in plan:
            assert slot.topic in html_content

    def test_render_preview_file_creates_file(self, tmp_path: Path) -> None:
        from smm.preview import render_preview_file

        out = tmp_path / "test_preview.html"
        result = render_preview_file(days=1, seed=42, output=out)
        assert result.exists()
        content = result.read_text()
        assert len(content) > 1000
        assert "card" in content

    def test_render_preview_custom_title(self) -> None:
        from smm.preview import render_preview

        plan = generate_week_plan(days=1, seed=42)
        html_content = render_preview(plan, title="Test Preview")
        assert "Test Preview" in html_content

    def test_render_preview_stats(self) -> None:
        from smm.preview import render_preview

        plan = generate_week_plan(days=1, seed=42)
        html_content = render_preview(plan)
        assert "3</strong> Instagram" in html_content
        assert "3</strong> TikTok" in html_content
        assert "3</strong> YouTube" in html_content

    def test_render_preview_escapes_html(self) -> None:
        from smm.preview import _escape

        assert _escape("<script>") == "&lt;script&gt;"
        assert _escape('"test"') == "&quot;test&quot;"


# --- Analytics tests ---


class TestAnalytics:
    def test_post_metrics_defaults(self) -> None:
        from smm.analytics import PostMetrics

        pm = PostMetrics(
            date="2025-01-01",
            platform="instagram",
            topic="Test",
            pillar="Cyber",
            format="reels",
        )
        assert pm.impressions == 0
        assert pm.engagement_rate == 0.0
        assert pm.click_through_rate == 0.0

    def test_engagement_rate_calculation(self) -> None:
        from smm.analytics import PostMetrics

        pm = PostMetrics(
            date="2025-01-01",
            platform="instagram",
            topic="Test",
            pillar="Cyber",
            format="reels",
            impressions=1000,
            likes=50,
            comments=10,
            shares=5,
            saves=15,
        )
        assert pm.engagement_rate == 8.0

    def test_click_through_rate(self) -> None:
        from smm.analytics import PostMetrics

        pm = PostMetrics(
            date="2025-01-01",
            platform="tiktok",
            topic="Test",
            pillar="ML",
            format="short_video",
            impressions=2000,
            link_clicks=40,
        )
        assert pm.click_through_rate == 2.0

    def test_create_tracking_template(self) -> None:
        from smm.analytics import create_tracking_template

        report = create_tracking_template(days=1, seed=42)
        assert report.total_posts == 9
        assert all(p.impressions == 0 for p in report.posts)

    def test_weekly_report_summary(self) -> None:
        from smm.analytics import create_tracking_template

        report = create_tracking_template(days=1, seed=42)
        summary = report.summary()
        assert "SMM" in summary
        assert "0" in summary

    def test_weekly_report_by_platform(self) -> None:
        from smm.analytics import create_tracking_template

        report = create_tracking_template(days=1, seed=42)
        by_plat = report.by_platform()
        assert "instagram" in by_plat
        assert "tiktok" in by_plat
        assert "youtube" in by_plat

    def test_weekly_report_by_pillar(self) -> None:
        from smm.analytics import create_tracking_template

        report = create_tracking_template(days=1, seed=42)
        by_pil = report.by_pillar()
        assert len(by_pil) >= 1

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.analytics import create_tracking_template

        report = create_tracking_template(days=1, seed=42)
        out = tmp_path / "report.json"
        report.export_json(out)
        data = json.loads(out.read_text())
        assert data["summary"]["total_posts"] == 9
        assert len(data["posts"]) == 9

    def test_export_markdown(self, tmp_path: Path) -> None:
        from smm.analytics import create_tracking_template

        report = create_tracking_template(days=1, seed=42)
        out = tmp_path / "report.md"
        report.export_markdown(out)
        content = out.read_text()
        assert "SMM" in content

    def test_top_posts_empty(self) -> None:
        from smm.analytics import create_tracking_template

        report = create_tracking_template(days=1, seed=42)
        top = report.top_posts(3)
        assert len(top) == 3
        assert all(p.engagement_rate == 0.0 for p in top)

    def test_load_report_missing(self, tmp_path: Path) -> None:
        from smm.analytics import load_report

        report = load_report(tmp_path / "missing.json")
        assert report.total_posts > 0

    def test_load_report_roundtrip(self, tmp_path: Path) -> None:
        from smm.analytics import create_tracking_template, load_report

        report = create_tracking_template(days=1, seed=42)
        out = tmp_path / "report.json"
        report.export_json(out)
        loaded = load_report(out)
        assert loaded.total_posts == report.total_posts
        assert loaded.week_start == report.week_start


# --- Landing tests ---


class TestLanding:
    def test_generate_landing_returns_html(self) -> None:
        from smm.landing import generate_landing

        html_content = generate_landing()
        assert "<!DOCTYPE html>" in html_content
        assert "ShadowRigs SMM" in html_content

    def test_generate_landing_has_tiers(self) -> None:
        from smm.landing import generate_landing

        html_content = generate_landing()
        assert "Starter" in html_content
        assert "Growth" in html_content
        assert "Pro" in html_content
        assert "$97" in html_content
        assert "$197" in html_content
        assert "$397" in html_content

    def test_generate_landing_custom_brand(self) -> None:
        from smm.landing import generate_landing

        html_content = generate_landing(brand="My Brand")
        assert "My Brand" in html_content

    def test_generate_landing_has_deliverables(self) -> None:
        from smm.landing import generate_landing

        html_content = generate_landing()
        for d in ["Weekly Calendar", "Platform Packages"]:
            assert d in html_content or len(html_content) > 1000

    def test_generate_landing_file(self, tmp_path: Path) -> None:
        from smm.landing import generate_landing_file

        out = tmp_path / "landing.html"
        result = generate_landing_file(output=out)
        assert result.exists()
        content = result.read_text()
        assert len(content) > 2000
        assert "tier-card" in content

    def test_generate_landing_contact_url(self) -> None:
        from smm.landing import generate_landing

        html_content = generate_landing(contact_url="https://example.com/contact")
        assert "https://example.com/contact" in html_content

    def test_generate_landing_escapes_html(self) -> None:
        from smm.landing import generate_landing

        html_content = generate_landing(brand="<script>alert(1)</script>")
        assert "<script>alert(1)</script>" not in html_content
        assert "&lt;script&gt;" in html_content


# --- ReadyPosts tests ---


class TestReadyPosts:
    def test_generate_ready_posts_count(self) -> None:
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        assert len(posts) == 9

    def test_generate_ready_posts_week(self) -> None:
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=7, seed=42)
        assert len(posts) == 63

    def test_ready_post_has_caption(self) -> None:
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        for p in posts:
            assert p.caption
            assert len(p.caption) > 50

    def test_ready_post_has_visual_brief(self) -> None:
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        for p in posts:
            assert p.visual_brief
            assert len(p.visual_brief) > 20

    def test_video_posts_have_script(self) -> None:
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=7, seed=42)
        video_formats = {"reels", "short_video", "shorts", "duet", "full_video"}
        for p in posts:
            if p.format in video_formats:
                assert p.video_script, f"video post {p.format} has no script"
            else:
                assert p.video_script == ""

    def test_all_platforms_present(self) -> None:
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        platforms = {p.platform for p in posts}
        assert platforms == {"instagram", "tiktok", "youtube"}

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.ready_posts import export_ready_json, generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        out = tmp_path / "posts.json"
        export_ready_json(posts, out)
        data = json.loads(out.read_text())
        assert len(data) == 9
        assert "caption" in data[0]

    def test_export_buffer_csv(self, tmp_path: Path) -> None:
        import csv as csv_mod

        from smm.ready_posts import export_buffer_csv, generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        out = tmp_path / "buffer.csv"
        export_buffer_csv(posts, out)
        with out.open(newline="", encoding="utf-8") as f:
            reader = list(csv_mod.reader(f))
        assert reader[0] == ["Text", "Date", "Time", "Profile"]
        assert len(reader) == 10

    def test_export_markdown(self, tmp_path: Path) -> None:
        from smm.ready_posts import export_ready_markdown, generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        out = tmp_path / "posts.md"
        export_ready_markdown(posts, out)
        content = out.read_text()
        assert "Готовые посты" in content
        assert "caption" in content

    def test_to_dict(self) -> None:
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        d = posts[0].to_dict()
        assert "day" in d
        assert "caption" in d
        assert "visual_brief" in d

    def test_batch_summary(self) -> None:
        from smm.ready_posts import batch_summary, generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        s = batch_summary(posts)
        assert "Готовые посты: 9" in s
        assert "instagram" in s
        assert "tiktok" in s
        assert "youtube" in s

    def test_seed_reproducibility(self) -> None:
        from smm.ready_posts import generate_ready_posts

        a = generate_ready_posts(days=1, seed=99)
        b = generate_ready_posts(days=1, seed=99)
        assert [p.topic for p in a] == [p.topic for p in b]
        assert [p.caption for p in a] == [p.caption for p in b]


# --- SchedulerExport tests ---


class TestSchedulerExport:
    def test_export_later_csv(self, tmp_path: Path) -> None:
        import csv as csv_mod

        from smm.ready_posts import generate_ready_posts
        from smm.scheduler_export import export_later_csv

        posts = generate_ready_posts(days=1, seed=42)
        out = tmp_path / "later.csv"
        export_later_csv(posts, out)
        with out.open(newline="", encoding="utf-8") as f:
            rows = list(csv_mod.reader(f))
        assert rows[0][0] == "Caption"
        assert len(rows) == 10

    def test_export_meta_json(self, tmp_path: Path) -> None:
        from smm.ready_posts import generate_ready_posts
        from smm.scheduler_export import export_meta_json

        posts = generate_ready_posts(days=1, seed=42)
        out = tmp_path / "meta.json"
        export_meta_json(posts, out)
        data = json.loads(out.read_text())
        assert data["platform"] == "instagram"
        assert data["total"] == 3

    def test_export_ical(self, tmp_path: Path) -> None:
        from smm.ready_posts import generate_ready_posts
        from smm.scheduler_export import export_ical

        posts = generate_ready_posts(days=1, seed=42)
        out = tmp_path / "cal.ics"
        export_ical(posts, out)
        content = out.read_text()
        assert "BEGIN:VCALENDAR" in content
        assert "BEGIN:VEVENT" in content
        assert content.count("BEGIN:VEVENT") == 9

    def test_export_notion_json(self, tmp_path: Path) -> None:
        from smm.ready_posts import generate_ready_posts
        from smm.scheduler_export import export_notion_json

        posts = generate_ready_posts(days=1, seed=42)
        out = tmp_path / "notion.json"
        export_notion_json(posts, out)
        data = json.loads(out.read_text())
        assert data["total"] == 9
        assert "properties" in data["database_rows"][0]

    def test_export_all_formats(self, tmp_path: Path) -> None:
        from smm.ready_posts import generate_ready_posts
        from smm.scheduler_export import export_all_formats

        posts = generate_ready_posts(days=1, seed=42)
        paths = export_all_formats(posts, tmp_path / "exports")
        assert len(paths) == 4
        for p in paths.values():
            assert p.exists()


# --- Proposal tests ---


class TestProposal:
    def _client(self):
        from smm.proposal import ClientProfile

        return ClientProfile(
            name="Test Corp",
            business="Cybersecurity Training",
            niche="cybersecurity",
            current_platforms=["Instagram", "TikTok"],
            posts_per_week_goal=42,
            main_goal="increase course sales",
        )

    def test_generate_proposal_returns_html(self) -> None:
        from smm.proposal import generate_proposal

        html_content = generate_proposal(self._client())
        assert "<!DOCTYPE html>" in html_content
        assert "Test Corp" in html_content

    def test_recommended_tier_growth(self) -> None:
        client = self._client()
        assert client.recommended_tier.name == "Growth"

    def test_recommended_tier_starter(self) -> None:
        from smm.proposal import ClientProfile

        client = ClientProfile(
            name="Small Biz",
            business="Blog",
            niche="ai",
            current_platforms=["Instagram"],
            posts_per_week_goal=15,
            main_goal="grow followers",
        )
        assert client.recommended_tier.name == "Starter"

    def test_recommended_tier_pro(self) -> None:
        from smm.proposal import ClientProfile

        client = ClientProfile(
            name="Big Corp",
            business="Enterprise",
            niche="gadgets",
            current_platforms=["Instagram", "TikTok", "YouTube"],
            posts_per_week_goal=63,
            main_goal="maximize reach",
        )
        assert client.recommended_tier.name == "Pro"

    def test_niche_samples_cybersecurity(self) -> None:
        from smm.proposal import generate_proposal

        html_content = generate_proposal(self._client())
        assert "пентест" in html_content.lower() or "OWASP" in html_content

    def test_niche_samples_default(self) -> None:
        from smm.proposal import ClientProfile, generate_proposal

        client = ClientProfile(
            name="Generic",
            business="Shop",
            niche="fashion",
            current_platforms=["Instagram"],
            posts_per_week_goal=21,
            main_goal="sales",
        )
        html_content = generate_proposal(client)
        assert "Контент-план" in html_content or "охваты" in html_content

    def test_escapes_html(self) -> None:
        from smm.proposal import ClientProfile, generate_proposal

        client = ClientProfile(
            name="<script>alert(1)</script>",
            business="Test",
            niche="ai",
            current_platforms=["Instagram"],
            posts_per_week_goal=21,
            main_goal="test",
        )
        html_content = generate_proposal(client)
        assert "<script>alert(1)</script>" not in html_content
        assert "&lt;script&gt;" in html_content

    def test_generate_file(self, tmp_path: Path) -> None:
        from smm.proposal import generate_proposal_file

        path = generate_proposal_file(self._client(), output=tmp_path / "p.html")
        assert path.exists()
        content = path.read_text()
        assert "Growth" in content

    def test_roi_calculation(self) -> None:
        from smm.proposal import generate_proposal

        html_content = generate_proposal(self._client())
        assert "168" in html_content
        assert "$1.17" in html_content


# --- Content bank tests ---


class TestContentBank:
    def test_hooks_extended_count(self) -> None:
        from smm.content_bank import HOOKS_EXTENDED

        assert len(HOOKS_EXTENDED) >= 25

    def test_get_hooks_returns_requested_count(self) -> None:
        from smm.content_bank import get_hooks

        hooks = get_hooks("Cyber Security", count=5)
        assert len(hooks) == 5
        for h in hooks:
            assert len(h) > 10

    def test_get_hooks_substitutes_keyword(self) -> None:
        import random

        from smm.content_bank import get_hooks

        random.seed(42)
        hooks = get_hooks("Nmap", count=30)
        assert any("Nmap" in h for h in hooks)

    def test_get_ctas_course(self) -> None:
        from smm.content_bank import get_ctas

        ctas = get_ctas("course", count=3)
        assert len(ctas) == 3
        for cta in ctas:
            assert len(cta) > 10

    def test_get_ctas_referral(self) -> None:
        from smm.content_bank import get_ctas

        ctas = get_ctas("referral", count=3)
        assert len(ctas) == 3

    def test_cta_pools_are_different(self) -> None:
        from smm.content_bank import CTA_COURSE_EXTENDED, CTA_REFERRAL_EXTENDED

        assert set(CTA_COURSE_EXTENDED) != set(CTA_REFERRAL_EXTENDED)

    def test_story_framework_returns_dict(self) -> None:
        from smm.content_bank import get_story_framework

        fw = get_story_framework("Nmap", "Подпишись", niche="Cyber Security")
        assert isinstance(fw, dict)
        assert "name" in fw
        assert "slide_1" in fw

    def test_story_framework_substitutes_topic(self) -> None:
        import random

        from smm.content_bank import get_story_framework

        random.seed(99)
        fw = get_story_framework("Wireshark", "Подпишись", niche="Cyber Security")
        values = " ".join(fw.values())
        assert "Wireshark" in values or "wireshark" in values

    def test_myths_by_niche_all_pillars(self) -> None:
        from smm.content_bank import MYTHS_BY_NICHE

        assert len(MYTHS_BY_NICHE) >= 5
        for niche, myths in MYTHS_BY_NICHE.items():
            assert len(myths) >= 3, f"{niche} has too few myths"

    def test_problems_by_niche_all_pillars(self) -> None:
        from smm.content_bank import PROBLEMS_BY_NICHE

        assert len(PROBLEMS_BY_NICHE) >= 5
        for niche, problems in PROBLEMS_BY_NICHE.items():
            assert len(problems) >= 3, f"{niche} has too few problems"

    def test_carousel_frameworks_exist(self) -> None:
        from smm.content_bank import CAROUSEL_FRAMEWORKS

        assert len(CAROUSEL_FRAMEWORKS) >= 3
        for fw in CAROUSEL_FRAMEWORKS:
            assert "name" in fw
            assert "cover" in fw

    def test_extended_templates_used_in_ready_posts(self) -> None:
        from smm.ready_posts import CAPTION_TEMPLATES_COURSE, CAPTION_TEMPLATES_REFERRAL

        assert len(CAPTION_TEMPLATES_COURSE) >= 8
        assert len(CAPTION_TEMPLATES_REFERRAL) >= 6


# --- Bio link page tests ---


class TestBioLink:
    def test_default_html_contains_brand(self) -> None:
        from smm.biolink import generate_biolink_html

        html = generate_biolink_html()
        assert "ShadowRigs" in html

    def test_default_has_all_links(self) -> None:
        from smm.biolink import DEFAULT_LINKS, generate_biolink_html

        html = generate_biolink_html()
        for link in DEFAULT_LINKS:
            assert link.url in html

    def test_custom_brand(self) -> None:
        from smm.biolink import BioLinkPage, generate_biolink_html

        page = BioLinkPage(brand="TestBrand", tagline="Test tagline")
        html = generate_biolink_html(page)
        assert "TestBrand" in html
        assert "Test tagline" in html

    def test_xss_prevention(self) -> None:
        from smm.biolink import BioLinkPage, generate_biolink_html

        page = BioLinkPage(brand='<script>alert("xss")</script>')
        html = generate_biolink_html(page)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_add_link(self) -> None:
        from smm.biolink import BioLinkPage, generate_biolink_html

        page = BioLinkPage()
        page.add("Test Link", "https://example.com", category="general")
        html = generate_biolink_html(page)
        assert "https://example.com" in html
        assert "Test Link" in html

    def test_generate_file(self, tmp_path: Path) -> None:
        from smm.biolink import generate_biolink_file

        path = generate_biolink_file(output=tmp_path / "bio.html")
        assert path.exists()
        content = path.read_text()
        assert "ShadowRigs" in content
        assert "<!DOCTYPE html>" in content

    def test_telegram_link(self) -> None:
        from smm.biolink import BioLinkPage, generate_biolink_html

        page = BioLinkPage(telegram="https://t.me/test_channel")
        html = generate_biolink_html(page)
        assert "https://t.me/test_channel" in html

    def test_category_headers(self) -> None:
        from smm.biolink import generate_biolink_html

        html = generate_biolink_html()
        assert "Курсы" in html
        assert "Гаджеты" in html

    def test_dark_light_theme(self) -> None:
        from smm.biolink import generate_biolink_html

        html = generate_biolink_html()
        assert "prefers-color-scheme: light" in html
        assert 'data-theme="dark"' in html


# --- Week pack tests ---


class TestWeekPack:
    def test_generates_all_files(self, tmp_path: Path) -> None:
        from smm.week_pack import generate_week_pack

        paths = generate_week_pack(days=1, seed=42, out_dir=tmp_path / "pack")
        assert len(paths) >= 10
        for name, path in paths.items():
            assert path.exists(), f"{name} not found at {path}"

    def test_contains_key_files(self, tmp_path: Path) -> None:
        from smm.week_pack import generate_week_pack

        paths = generate_week_pack(days=1, seed=42, out_dir=tmp_path / "pack")
        assert "json" in paths
        assert "csv" in paths
        assert "markdown" in paths
        assert "biolink" in paths
        assert "readme" in paths

    def test_platform_directories(self, tmp_path: Path) -> None:
        from smm.week_pack import generate_week_pack

        paths = generate_week_pack(days=1, seed=42, out_dir=tmp_path / "pack")
        platform_keys = [k for k in paths if k.startswith("captions_")]
        assert len(platform_keys) == 3

    def test_readme_has_stats(self, tmp_path: Path) -> None:
        from smm.week_pack import generate_week_pack

        paths = generate_week_pack(days=1, seed=42, out_dir=tmp_path / "pack")
        readme = paths["readme"].read_text()
        assert "total_posts" in readme
        assert "9" in readme

    def test_scheduler_exports_present(self, tmp_path: Path) -> None:
        from smm.week_pack import generate_week_pack

        paths = generate_week_pack(days=1, seed=42, out_dir=tmp_path / "pack")
        scheduler_keys = [k for k in paths if k.startswith("scheduler_")]
        assert len(scheduler_keys) >= 4

    def test_video_scripts_generated(self, tmp_path: Path) -> None:
        from smm.week_pack import generate_week_pack

        paths = generate_week_pack(days=1, seed=42, out_dir=tmp_path / "pack")
        script_keys = [k for k in paths if k.startswith("scripts_")]
        assert len(script_keys) >= 1
        for key in script_keys:
            content = paths[key].read_text()
            assert "Script" in content

    def test_seed_reproducibility(self, tmp_path: Path) -> None:
        from smm.week_pack import generate_week_pack

        paths1 = generate_week_pack(days=1, seed=99, out_dir=tmp_path / "p1")
        paths2 = generate_week_pack(days=1, seed=99, out_dir=tmp_path / "p2")
        json1 = paths1["json"].read_text()
        json2 = paths2["json"].read_text()
        assert json1 == json2

    def test_ab_variants_included(self, tmp_path: Path) -> None:
        from smm.week_pack import generate_week_pack

        paths = generate_week_pack(days=1, seed=42, out_dir=tmp_path / "pack")
        assert "ab_json" in paths
        assert "ab_csv" in paths
        assert paths["ab_json"].exists()
        data = json.loads(paths["ab_json"].read_text())
        assert len(data) >= 1

    def test_hashtag_pools_included(self, tmp_path: Path) -> None:
        from smm.week_pack import generate_week_pack

        paths = generate_week_pack(days=1, seed=42, out_dir=tmp_path / "pack")
        assert "hashtag_pools" in paths
        content = paths["hashtag_pools"].read_text()
        assert "Cyber Security" in content
        assert "Machine Learning" in content

    def test_engagement_hooks_included(self, tmp_path: Path) -> None:
        from smm.week_pack import generate_week_pack

        paths = generate_week_pack(days=1, seed=42, out_dir=tmp_path / "pack")
        assert "engagement" in paths
        content = paths["engagement"].read_text()
        assert "ОПРОС:" in content
        assert "КВИЗ:" in content
        assert "ВОПРОС:" in content
        assert "THIS OR THAT:" in content


# --- A/B variant tests ---


class TestABVariants:
    def test_generates_correct_count(self) -> None:
        from smm.ab_variants import generate_ab_posts

        posts = generate_ab_posts(days=1, seed=42)
        assert len(posts) == 9

    def test_each_post_has_two_variants(self) -> None:
        from smm.ab_variants import generate_ab_posts

        posts = generate_ab_posts(days=1, seed=42)
        for p in posts:
            assert p.variant_a.variant == "A"
            assert p.variant_b.variant == "B"
            assert p.variant_a.caption != p.variant_b.caption

    def test_variants_have_different_hooks(self) -> None:
        from smm.ab_variants import generate_ab_posts

        posts = generate_ab_posts(days=1, seed=42)
        diff_count = sum(1 for p in posts if p.variant_a.hook != p.variant_b.hook)
        assert diff_count >= 5

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.ab_variants import export_ab_json, generate_ab_posts

        posts = generate_ab_posts(days=1, seed=42)
        path = export_ab_json(posts, tmp_path / "ab.json")
        data = json.loads(path.read_text())
        assert len(data) == 9
        assert "variant_a" in data[0]
        assert "variant_b" in data[0]

    def test_export_csv(self, tmp_path: Path) -> None:
        import csv as csv_mod

        from smm.ab_variants import export_ab_csv, generate_ab_posts

        posts = generate_ab_posts(days=1, seed=42)
        path = export_ab_csv(posts, tmp_path / "ab.csv")
        with path.open() as f:
            reader = csv_mod.reader(f)
            rows = list(reader)
        assert rows[0][-1] == "Winner"
        assert len(rows) == 10

    def test_export_markdown(self, tmp_path: Path) -> None:
        from smm.ab_variants import export_ab_markdown, generate_ab_posts

        posts = generate_ab_posts(days=1, seed=42)
        path = export_ab_markdown(posts, tmp_path / "ab.md")
        content = path.read_text()
        assert "Variant A" in content
        assert "Variant B" in content
        assert "Winner" in content

    def test_seed_reproducibility(self) -> None:
        from smm.ab_variants import generate_ab_posts

        posts1 = generate_ab_posts(days=1, seed=77)
        posts2 = generate_ab_posts(days=1, seed=77)
        for p1, p2 in zip(posts1, posts2, strict=True):
            assert p1.variant_a.caption == p2.variant_a.caption

    def test_summary(self) -> None:
        from smm.ab_variants import ab_summary, generate_ab_posts

        posts = generate_ab_posts(days=1, seed=42)
        summary = ab_summary(posts)
        assert "9" in summary
        assert "18" in summary

    def test_to_dict(self) -> None:
        from smm.ab_variants import generate_ab_posts

        posts = generate_ab_posts(days=1, seed=42)
        d = posts[0].to_dict()
        assert "variant_a" in d
        assert "caption" in d["variant_a"]


# --- Hashtag engine tests ---


class TestHashtagEngine:
    def test_generate_default_count(self) -> None:
        from smm.hashtag_engine import generate_hashtags

        hs = generate_hashtags("Cyber Security & Ethical Hacking", seed=42)
        assert hs.count == 15

    def test_generate_custom_count(self) -> None:
        from smm.hashtag_engine import generate_hashtags

        hs = generate_hashtags("Machine Learning & AI", count=10, seed=42)
        assert hs.count == 10

    def test_all_tags_are_hashtags(self) -> None:
        from smm.hashtag_engine import generate_hashtags

        hs = generate_hashtags("Red Team / Offensive Security", seed=42)
        for tag in hs.all_tags:
            assert tag.startswith("#"), f"{tag} is not a hashtag"

    def test_as_string(self) -> None:
        from smm.hashtag_engine import generate_hashtags

        hs = generate_hashtags("Blue Team / Defensive Security", count=5, seed=42)
        s = hs.as_string
        assert "#" in s
        assert len(s.split()) == 5

    def test_pools_cover_all_pillars(self) -> None:
        from smm.hashtag_engine import HASHTAG_POOLS

        assert len(HASHTAG_POOLS) >= 5
        for name, pool in HASHTAG_POOLS.items():
            assert "high" in pool, f"{name} missing high pool"
            assert "mid" in pool, f"{name} missing mid pool"
            assert "niche" in pool, f"{name} missing niche pool"
            assert len(pool["high"]) >= 10
            assert len(pool["mid"]) >= 10
            assert len(pool["niche"]) >= 10

    def test_no_duplicates_within_set(self) -> None:
        from smm.hashtag_engine import generate_hashtags

        hs = generate_hashtags("AliExpress - Гаджеты", count=15, seed=42)
        assert len(set(hs.all_tags)) == len(hs.all_tags)

    def test_report(self) -> None:
        from smm.hashtag_engine import hashtag_report

        report = hashtag_report("Cyber Security & Ethical Hacking")
        assert "Высокочастотные" in report
        assert "Нишевые" in report
        assert "Всего" in report

    def test_fallback_for_unknown_pillar(self) -> None:
        from smm.hashtag_engine import generate_hashtags

        hs = generate_hashtags("Unknown Pillar", count=10, seed=42)
        assert hs.count == 10

    def test_seed_reproducibility(self) -> None:
        from smm.hashtag_engine import generate_hashtags

        hs1 = generate_hashtags("Machine Learning & AI", seed=123)
        hs2 = generate_hashtags("Machine Learning & AI", seed=123)
        assert hs1.all_tags == hs2.all_tags

    def test_posts_use_engine_hashtags(self) -> None:
        from smm.hashtag_engine import HASHTAG_POOLS
        from smm.post_generator import generate_week_plan

        plan = generate_week_plan(days=1, seed=42)
        all_engine_tags = set()
        for pool in HASHTAG_POOLS.values():
            for tags in pool.values():
                all_engine_tags.update(tags)
        for slot in plan:
            if slot.pillar.name in HASHTAG_POOLS:
                assert any(t in all_engine_tags for t in slot.hashtags)


# --- Content calendar HTML tests ---


class TestContentCalendarHTML:
    def test_generates_html(self, tmp_path: Path) -> None:
        from smm.content_calendar_html import generate_calendar_file
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        path = generate_calendar_file(posts, tmp_path / "cal.html")
        assert path.exists()
        content = path.read_text()
        assert "<!DOCTYPE html>" in content
        assert "Контент-календарь" in content

    def test_contains_all_platforms(self, tmp_path: Path) -> None:
        from smm.content_calendar_html import generate_calendar_html
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        html_out = generate_calendar_html(posts)
        assert "IG" in html_out
        assert "TT" in html_out
        assert "YT" in html_out

    def test_pillar_colors_present(self, tmp_path: Path) -> None:
        from smm.content_calendar_html import generate_calendar_html
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        html_out = generate_calendar_html(posts)
        assert "#00ff41" in html_out

    def test_xss_prevention(self, tmp_path: Path) -> None:
        from smm.content_calendar_html import generate_calendar_html
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        html_out = generate_calendar_html(posts)
        assert "<script>" not in html_out

    def test_post_count_in_title(self, tmp_path: Path) -> None:
        from smm.content_calendar_html import generate_calendar_html
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        html_out = generate_calendar_html(posts)
        assert "9 постов" in html_out

    def test_weekday_names_russian(self, tmp_path: Path) -> None:
        from smm.content_calendar_html import generate_calendar_html
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=3, seed=42)
        html_out = generate_calendar_html(posts)
        has_russian_day = any(
            day in html_out
            for day in [
                "Понедельник",
                "Вторник",
                "Среда",
                "Четверг",
                "Пятница",
                "Суббота",
                "Воскресенье",
            ]
        )
        assert has_russian_day


# --- Engagement hooks tests ---


class TestEngagementHooks:
    def test_generate_poll(self) -> None:
        from smm.engagement_hooks import generate_poll

        hook = generate_poll("Cyber Security & Ethical Hacking", seed=42)
        assert hook.hook_type == "poll"
        assert len(hook.options) == 4
        assert hook.content
        assert hook.correct_index is None

    def test_generate_quiz(self) -> None:
        from smm.engagement_hooks import generate_quiz

        hook = generate_quiz("Machine Learning & AI", seed=42)
        assert hook.hook_type == "quiz"
        assert len(hook.options) == 4
        assert hook.correct_index is not None
        assert 0 <= hook.correct_index < len(hook.options)

    def test_generate_question(self) -> None:
        from smm.engagement_hooks import generate_question

        q = generate_question("Red Team / Offensive Security", seed=42)
        assert isinstance(q, str)
        assert len(q) > 10

    def test_generate_this_or_that(self) -> None:
        from smm.engagement_hooks import generate_this_or_that

        a, b = generate_this_or_that("AliExpress - Гаджеты", seed=42)
        assert isinstance(a, str)
        assert isinstance(b, str)
        assert a != b

    def test_all_pillars_covered(self) -> None:
        from smm.engagement_hooks import (
            POLLS_BY_PILLAR,
            QUESTIONS_BY_PILLAR,
            QUIZ_BY_PILLAR,
        )

        for pool in (POLLS_BY_PILLAR, QUIZ_BY_PILLAR, QUESTIONS_BY_PILLAR):
            assert len(pool) == 5

    def test_engagement_summary(self) -> None:
        from smm.engagement_hooks import engagement_summary

        summary = engagement_summary("Cyber Security & Ethical Hacking")
        assert "Опросы:" in summary
        assert "Квизы:" in summary
        assert "Вопросы:" in summary
        assert "Всего:" in summary

    def test_fallback_for_unknown_pillar(self) -> None:
        from smm.engagement_hooks import generate_poll

        hook = generate_poll("Unknown Pillar", seed=42)
        assert hook.hook_type == "poll"
        assert len(hook.options) == 4

    def test_seed_reproducibility(self) -> None:
        from smm.engagement_hooks import generate_poll

        h1 = generate_poll("Blue Team / Defensive Security", seed=99)
        h2 = generate_poll("Blue Team / Defensive Security", seed=99)
        assert h1.content == h2.content
        assert h1.options == h2.options


# --- Caption validator tests ---


class TestCaptionValidator:
    def test_all_posts_pass(self) -> None:
        from smm.caption_validator import validate_posts
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        report = validate_posts(posts)
        assert report.ok
        assert report.passed == report.total

    def test_no_unresolved_placeholders(self) -> None:
        from smm.caption_validator import validate_posts
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=7, seed=42)
        report = validate_posts(posts)
        placeholder_errors = [
            e for e in report.errors if "placeholder" in e.message.lower()
        ]
        assert len(placeholder_errors) == 0

    def test_summary_format(self) -> None:
        from smm.caption_validator import validate_posts
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        report = validate_posts(posts)
        summary = report.summary()
        assert "Проверено:" in summary
        assert "Прошло:" in summary

    def test_empty_list(self) -> None:
        from smm.caption_validator import validate_posts

        report = validate_posts([])
        assert report.ok
        assert report.total == 0

    def test_report_properties(self) -> None:
        from smm.caption_validator import validate_posts
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        report = validate_posts(posts)
        assert report.total == 9
        assert report.failed == report.total - report.passed

    def test_seven_days_all_pass(self) -> None:
        from smm.caption_validator import validate_posts
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=7, seed=42)
        report = validate_posts(posts)
        assert report.ok
        assert report.total == 63


class TestStoryGenerator:
    def test_generate_story_pack(self) -> None:
        from smm.story_generator import generate_story_pack

        pillar = PILLARS[0]
        pack = generate_story_pack(pillar, pillar.topics[0], seed=42)
        assert pack.pillar == pillar.name
        assert pack.topic == pillar.topics[0]
        assert len(pack.slides) >= 4

    def test_generate_story_packs(self) -> None:
        from smm.story_generator import generate_story_packs

        packs = generate_story_packs(count=5, seed=42)
        assert len(packs) == 5
        pillars_seen = {p.pillar for p in packs}
        assert len(pillars_seen) >= 2

    def test_slides_have_text(self) -> None:
        from smm.story_generator import generate_story_pack

        pack = generate_story_pack(PILLARS[0], PILLARS[0].topics[0], seed=42)
        for slide in pack.slides:
            assert slide.text.strip()
            assert slide.visual_note.strip()
            assert slide.number > 0

    def test_interactive_slides_present(self) -> None:
        from smm.story_generator import generate_story_pack

        pack = generate_story_pack(PILLARS[0], PILLARS[0].topics[0], seed=42)
        interactive = [s for s in pack.slides if s.interactive]
        assert len(interactive) >= 2

    def test_to_dict(self) -> None:
        from smm.story_generator import generate_story_pack

        pack = generate_story_pack(PILLARS[0], PILLARS[0].topics[0], seed=42)
        d = pack.to_dict()
        assert d["pillar"] == pack.pillar
        assert d["topic"] == pack.topic
        assert len(d["slides"]) == len(pack.slides)

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.story_generator import export_story_packs_json, generate_story_packs

        packs = generate_story_packs(count=3, seed=42)
        path = export_story_packs_json(packs, tmp_path / "stories.json")
        assert path.exists()
        data = json.loads(path.read_text())
        assert len(data) == 3

    def test_export_txt(self, tmp_path: Path) -> None:
        from smm.story_generator import export_story_packs_txt, generate_story_packs

        packs = generate_story_packs(count=3, seed=42)
        path = export_story_packs_txt(packs, tmp_path / "stories.txt")
        assert path.exists()
        text = path.read_text()
        assert "СТОРИС #1" in text
        assert "Слайд 1:" in text

    def test_story_summary(self) -> None:
        from smm.story_generator import generate_story_packs, story_summary

        packs = generate_story_packs(count=5, seed=42)
        summary = story_summary(packs)
        assert "Сторис-пакеты: 5" in summary
        assert "Всего слайдов:" in summary
        assert "С интерактивом:" in summary

    def test_seed_reproducibility(self) -> None:
        from smm.story_generator import generate_story_packs

        packs1 = generate_story_packs(count=3, seed=99)
        packs2 = generate_story_packs(count=3, seed=99)
        for p1, p2 in zip(packs1, packs2, strict=True):
            assert p1.pillar == p2.pillar
            assert p1.topic == p2.topic

    def test_week_pack_includes_stories(self, tmp_path: Path) -> None:
        from smm.week_pack import generate_week_pack

        paths = generate_week_pack(days=1, seed=42, out_dir=tmp_path / "wp")
        assert "stories_json" in paths
        assert "stories_txt" in paths
        assert paths["stories_json"].exists()

    def test_accent_colors_all_pillars(self) -> None:
        from smm.story_generator import ACCENT_COLORS

        for p in PILLARS:
            assert p.name in ACCENT_COLORS


class TestCarouselGenerator:
    def test_generate_carousel(self) -> None:
        from smm.carousel_generator import generate_carousel

        pillar = PILLARS[0]
        pack = generate_carousel(pillar, pillar.topics[0], seed=42)
        assert pack.pillar == pillar.name
        assert pack.topic == pillar.topics[0]
        assert len(pack.slides) >= 4

    def test_generate_carousels(self) -> None:
        from smm.carousel_generator import generate_carousels

        packs = generate_carousels(count=5, seed=42)
        assert len(packs) == 5

    def test_cover_and_cta_slides(self) -> None:
        from smm.carousel_generator import generate_carousel

        pack = generate_carousel(PILLARS[0], PILLARS[0].topics[0], seed=42)
        covers = [s for s in pack.slides if s.is_cover]
        ctas = [s for s in pack.slides if s.is_cta]
        assert len(covers) == 1
        assert len(ctas) == 1

    def test_to_dict(self) -> None:
        from smm.carousel_generator import generate_carousel

        pack = generate_carousel(PILLARS[0], PILLARS[0].topics[0], seed=42)
        d = pack.to_dict()
        assert d["framework"] in ("listicle", "tutorial", "comparison")
        assert len(d["slides"]) == len(pack.slides)

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.carousel_generator import export_carousels_json, generate_carousels

        packs = generate_carousels(count=3, seed=42)
        path = export_carousels_json(packs, tmp_path / "car.json")
        assert path.exists()
        data = json.loads(path.read_text())
        assert len(data) == 3

    def test_export_txt(self, tmp_path: Path) -> None:
        from smm.carousel_generator import export_carousels_txt, generate_carousels

        packs = generate_carousels(count=3, seed=42)
        path = export_carousels_txt(packs, tmp_path / "car.txt")
        assert path.exists()
        text = path.read_text()
        assert "КАРУСЕЛЬ #1" in text
        assert "[ОБЛОЖКА]" in text

    def test_carousel_summary(self) -> None:
        from smm.carousel_generator import carousel_summary, generate_carousels

        packs = generate_carousels(count=5, seed=42)
        summary = carousel_summary(packs)
        assert "Карусели: 5" in summary
        assert "Всего слайдов:" in summary

    def test_comparison_pairs_all_pillars(self) -> None:
        from smm.carousel_generator import COMPARISON_PAIRS

        for p in PILLARS:
            assert p.name in COMPARISON_PAIRS

    def test_listicle_points_all_pillars(self) -> None:
        from smm.carousel_generator import LISTICLE_POINTS

        for p in PILLARS:
            assert p.name in LISTICLE_POINTS

    def test_seed_reproducibility(self) -> None:
        from smm.carousel_generator import generate_carousels

        packs1 = generate_carousels(count=3, seed=99)
        packs2 = generate_carousels(count=3, seed=99)
        for p1, p2 in zip(packs1, packs2, strict=True):
            assert p1.pillar == p2.pillar
            assert p1.topic == p2.topic

    def test_week_pack_includes_carousels(self, tmp_path: Path) -> None:
        from smm.week_pack import generate_week_pack

        paths = generate_week_pack(days=1, seed=42, out_dir=tmp_path / "wp")
        assert "carousels_json" in paths
        assert "carousels_txt" in paths
        assert paths["carousels_json"].exists()


class TestContentRepurposer:
    def test_repurpose_single_post(self) -> None:
        from smm.content_repurposer import repurpose_post
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        result = repurpose_post(posts[0], Platform.TIKTOK)
        assert result.target_platform == "tiktok"
        assert result.adapted_caption

    def test_repurpose_batch(self) -> None:
        from smm.content_repurposer import repurpose_batch
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        results = repurpose_batch(posts)
        assert len(results) > 0
        targets_seen = {r.target_platform for r in results}
        assert len(targets_seen) >= 2

    def test_caption_trimming(self) -> None:
        from smm.content_repurposer import _trim_caption

        long_text = "A " * 2000
        trimmed = _trim_caption(long_text, 100)
        assert len(trimmed) <= 100
        assert trimmed.endswith("...")

    def test_caption_no_trim_needed(self) -> None:
        from smm.content_repurposer import _trim_caption

        short = "Hello world"
        assert _trim_caption(short, 100) == short

    def test_adapted_hashtags_within_limit(self) -> None:
        from smm.content_repurposer import repurpose_post
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        for post in posts:
            for target in Platform:
                result = repurpose_post(post, target)
                spec = PLATFORM_SPECS[target]
                assert len(result.adapted_hashtags) <= spec.hashtag_range[1]

    def test_format_adaptation(self) -> None:
        from smm.content_repurposer import _adapt_format

        assert _adapt_format("reels", Platform.TIKTOK) == "short_video"
        assert _adapt_format("reels", Platform.YOUTUBE) == "shorts"
        assert _adapt_format("static_post", Platform.INSTAGRAM) == "static_post"

    def test_visual_and_video_notes(self) -> None:
        from smm.content_repurposer import repurpose_post
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        result = repurpose_post(posts[0], Platform.TIKTOK)
        assert result.visual_note
        assert result.video_note

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.content_repurposer import export_repurposed_json, repurpose_batch
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        repurposed = repurpose_batch(posts[:3])
        path = export_repurposed_json(repurposed, tmp_path / "rep.json")
        assert path.exists()
        data = json.loads(path.read_text())
        assert len(data) == len(repurposed)

    def test_repurpose_summary(self) -> None:
        from smm.content_repurposer import repurpose_batch, repurpose_summary
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        repurposed = repurpose_batch(posts)
        summary = repurpose_summary(repurposed)
        assert "адаптаций" in summary

    def test_skip_same_platform(self) -> None:
        from smm.content_repurposer import repurpose_batch
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        results = repurpose_batch(posts)
        for r in results:
            assert r.original_platform != r.target_platform


class TestPostingScheduleOptimizer:
    def test_score_time_slot(self) -> None:
        from smm.posting_schedule_optimizer import score_time_slot

        score = score_time_slot(Platform.INSTAGRAM, 12, 2)
        assert 0 < score.final_score <= 1.5
        assert score.platform == "instagram"

    def test_best_times(self) -> None:
        from smm.posting_schedule_optimizer import best_times

        tops = best_times(Platform.INSTAGRAM, weekday=2, count=3)
        assert len(tops) == 3
        assert tops[0].final_score >= tops[1].final_score

    def test_recommend_schedule(self) -> None:
        from smm.posting_schedule_optimizer import recommend_schedule

        recs = recommend_schedule(start=date(2026, 1, 5), days=7)
        assert len(recs) == 7 * 3
        platforms = {r.platform for r in recs}
        assert platforms == {"instagram", "tiktok", "youtube"}

    def test_optimize_existing_posts(self) -> None:
        from smm.posting_schedule_optimizer import optimize_existing_posts
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        suggestions = optimize_existing_posts(posts)
        assert isinstance(suggestions, list)
        for s in suggestions:
            assert "improvement" in s
            assert "suggested_time" in s

    def test_schedule_heatmap(self) -> None:
        from smm.posting_schedule_optimizer import schedule_heatmap

        hm = schedule_heatmap(Platform.INSTAGRAM)
        assert "instagram" in hm
        assert "███" in hm
        assert "Легенда" in hm

    def test_optimizer_summary(self) -> None:
        from smm.posting_schedule_optimizer import (
            optimizer_summary,
            recommend_schedule,
        )

        recs = recommend_schedule(start=date(2026, 1, 5), days=3)
        summary = optimizer_summary(recs)
        assert "Оптимизация расписания" in summary
        assert "Средний скор" in summary

    def test_engagement_scores_all_platforms(self) -> None:
        from smm.posting_schedule_optimizer import ENGAGEMENT_SCORES

        for p in Platform:
            assert p.value in ENGAGEMENT_SCORES

    def test_weekday_multipliers_all_platforms(self) -> None:
        from smm.posting_schedule_optimizer import WEEKDAY_MULTIPLIERS

        for p in Platform:
            assert p.value in WEEKDAY_MULTIPLIERS
            assert len(WEEKDAY_MULTIPLIERS[p.value]) == 7


class TestContentSeries:
    def test_generate_series_returns_content_series(self) -> None:
        from smm.content_series import ContentSeries, generate_series

        series = generate_series(PILLARS[0], seed=42)
        assert isinstance(series, ContentSeries)
        assert series.pillar == PILLARS[0].name
        assert series.total_days == len(series.episodes)

    def test_generate_series_episode_numbering(self) -> None:
        from smm.content_series import generate_series

        series = generate_series(PILLARS[0], seed=42)
        for i, ep in enumerate(series.episodes, 1):
            assert ep.day == i

    def test_generate_series_first_episode_has_hook(self) -> None:
        from smm.content_series import generate_series

        series = generate_series(PILLARS[0], seed=42)
        first = series.episodes[0]
        assert len(first.caption) > 20

    def test_generate_series_last_episode_has_cta(self) -> None:
        from smm.content_series import generate_series

        series = generate_series(PILLARS[0], seed=42)
        last = series.episodes[-1]
        assert last.cta

    def test_generate_all_series_one_per_pillar(self) -> None:
        from smm.content_series import generate_all_series

        all_series = generate_all_series(seed=42)
        assert len(all_series) == len(PILLARS)
        pillar_names = {s.pillar for s in all_series}
        assert len(pillar_names) == len(PILLARS)

    def test_series_has_hashtags(self) -> None:
        from smm.content_series import generate_series

        series = generate_series(PILLARS[0], seed=42)
        for ep in series.episodes:
            assert ep.hashtags.startswith("#")

    def test_to_dict_structure(self) -> None:
        from smm.content_series import generate_series

        series = generate_series(PILLARS[0], seed=42)
        d = series.to_dict()
        assert "pillar" in d
        assert "series_name" in d
        assert "episodes" in d
        assert len(d["episodes"]) == series.total_days

    def test_export_series_json(self, tmp_path: Path) -> None:
        from smm.content_series import export_series_json, generate_all_series

        all_series = generate_all_series(seed=42)
        path = export_series_json(all_series, tmp_path / "series.json")
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data) == len(PILLARS)

    def test_export_series_txt(self, tmp_path: Path) -> None:
        from smm.content_series import export_series_txt, generate_all_series

        all_series = generate_all_series(seed=42)
        path = export_series_txt(all_series, tmp_path / "series.txt")
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "СЕРИЯ #1" in text

    def test_series_summary(self) -> None:
        from smm.content_series import generate_all_series, series_summary

        all_series = generate_all_series(seed=42)
        summary = series_summary(all_series)
        assert "Контент-серии" in summary
        assert "Всего эпизодов" in summary
        assert "По направлениям" in summary

    def test_series_templates_all_types_covered(self) -> None:
        from smm.content_series import SERIES_TEMPLATES

        types = {str(t["type"]) for t in SERIES_TEMPLATES}
        assert len(types) == len(SERIES_TEMPLATES)


class TestCompetitorAnalysis:
    def test_get_benchmark_known_pillar(self) -> None:
        from smm.competitor_analysis import get_benchmark

        b = get_benchmark("Cyber Security & Ethical Hacking")
        assert b.pillar == "Cyber Security & Ethical Hacking"
        assert b.avg_engagement_rate > 0

    def test_get_benchmark_unknown_pillar(self) -> None:
        from smm.competitor_analysis import get_benchmark

        b = get_benchmark("Unknown Niche")
        assert b.avg_engagement_rate == 2.0

    def test_get_competitors(self) -> None:
        from smm.competitor_analysis import get_competitors

        comps = get_competitors("Cyber Security & Ethical Hacking")
        assert len(comps) >= 2
        assert all(c.name for c in comps)

    def test_get_content_gaps(self) -> None:
        from smm.competitor_analysis import get_content_gaps

        gaps = get_content_gaps("Cyber Security & Ethical Hacking")
        assert len(gaps) >= 3

    def test_analyze_niche(self) -> None:
        from smm.competitor_analysis import analyze_niche

        analysis = analyze_niche("Cyber Security & Ethical Hacking")
        assert analysis.pillar == "Cyber Security & Ethical Hacking"
        assert len(analysis.gaps) > 0
        assert len(analysis.competitors) > 0
        assert len(analysis.recommendations) > 0

    def test_analyze_all_niches(self) -> None:
        from smm.competitor_analysis import analyze_all_niches

        all_analyses = analyze_all_niches()
        assert len(all_analyses) == len(PILLARS)

    def test_export_analysis_json(self, tmp_path: Path) -> None:
        from smm.competitor_analysis import analyze_all_niches, export_analysis_json

        analyses = analyze_all_niches()
        path = export_analysis_json(analyses, tmp_path / "analysis.json")
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data) == len(PILLARS)

    def test_export_analysis_txt(self, tmp_path: Path) -> None:
        from smm.competitor_analysis import analyze_all_niches, export_analysis_txt

        analyses = analyze_all_niches()
        path = export_analysis_txt(analyses, tmp_path / "analysis.txt")
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "АНАЛИЗ #1" in text

    def test_analysis_summary(self) -> None:
        from smm.competitor_analysis import analysis_summary, analyze_all_niches

        analyses = analyze_all_niches()
        summary = analysis_summary(analyses)
        assert "Анализ конкурентов" in summary
        assert "Контент-гэпов" in summary

    def test_benchmark_all_pillars_covered(self) -> None:
        from smm.competitor_analysis import NICHE_BENCHMARKS

        for p in PILLARS:
            assert p.name in NICHE_BENCHMARKS


class TestContentStrategy:
    def test_generate_pillar_strategies(self) -> None:
        from smm.content_strategy import generate_pillar_strategies

        strategies = generate_pillar_strategies()
        assert len(strategies) == len(PILLARS)
        assert strategies[0].priority == 1

    def test_pillar_strategy_shares_sum_to_one(self) -> None:
        from smm.content_strategy import generate_pillar_strategies

        strategies = generate_pillar_strategies()
        total = sum(s.content_share for s in strategies)
        assert abs(total - 1.0) < 0.01

    def test_generate_strategy(self) -> None:
        from smm.content_strategy import generate_strategy

        strategy = generate_strategy()
        assert strategy.total_posts_per_week == 63
        assert len(strategy.pillars) == len(PILLARS)
        assert len(strategy.priority_actions) > 0

    def test_content_mix_sums_to_one(self) -> None:
        from smm.content_strategy import CONTENT_MIX

        assert abs(sum(CONTENT_MIX.values()) - 1.0) < 0.01

    def test_format_distribution_all_platforms(self) -> None:
        from smm.content_strategy import FORMAT_DISTRIBUTION

        for p in Platform:
            assert p.value in FORMAT_DISTRIBUTION

    def test_growth_targets_periods(self) -> None:
        from smm.content_strategy import GROWTH_TARGETS

        assert "month_1" in GROWTH_TARGETS
        assert "month_3" in GROWTH_TARGETS
        assert "month_6" in GROWTH_TARGETS

    def test_export_strategy_json(self, tmp_path: Path) -> None:
        from smm.content_strategy import export_strategy_json, generate_strategy

        strategy = generate_strategy()
        path = export_strategy_json(strategy, tmp_path / "strategy.json")
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "pillars" in data

    def test_export_strategy_txt(self, tmp_path: Path) -> None:
        from smm.content_strategy import export_strategy_txt, generate_strategy

        strategy = generate_strategy()
        path = export_strategy_txt(strategy, tmp_path / "strategy.txt")
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "КОНТЕНТ-СТРАТЕГИЯ" in text

    def test_strategy_summary(self) -> None:
        from smm.content_strategy import generate_strategy, strategy_summary

        strategy = generate_strategy()
        summary = strategy_summary(strategy)
        assert "Контент-стратегия" in summary
        assert "63" in summary


class TestDashboard:
    def test_generate_dashboard_returns_path(self, tmp_path: Path) -> None:
        from smm.dashboard import generate_dashboard

        path = generate_dashboard(days=3, seed=42, output=tmp_path / "dash.html")
        assert isinstance(path, Path)
        assert path.exists()

    def test_dashboard_html_contains_key_sections(self, tmp_path: Path) -> None:
        from smm.dashboard import generate_dashboard

        path = generate_dashboard(days=3, seed=42, output=tmp_path / "dash.html")
        html = path.read_text(encoding="utf-8")
        assert "SMM Dashboard" in html
        assert "ShadowRigs" in html
        assert "Cyber Security" in html

    def test_dashboard_has_strategy_table(self, tmp_path: Path) -> None:
        from smm.dashboard import generate_dashboard

        path = generate_dashboard(days=3, seed=42, output=tmp_path / "dash.html")
        html = path.read_text(encoding="utf-8")
        assert "Стратегия по направлениям" in html

    def test_dashboard_has_competitor_cards(self, tmp_path: Path) -> None:
        from smm.dashboard import generate_dashboard

        path = generate_dashboard(days=3, seed=42, output=tmp_path / "dash.html")
        html = path.read_text(encoding="utf-8")
        assert "Конкуренты и гэпы" in html

    def test_dashboard_has_content_mix(self, tmp_path: Path) -> None:
        from smm.dashboard import generate_dashboard

        path = generate_dashboard(days=3, seed=42, output=tmp_path / "dash.html")
        html = path.read_text(encoding="utf-8")
        assert "Контент-микс" in html

    def test_dashboard_has_growth_targets(self, tmp_path: Path) -> None:
        from smm.dashboard import generate_dashboard

        path = generate_dashboard(days=3, seed=42, output=tmp_path / "dash.html")
        html = path.read_text(encoding="utf-8")
        assert "Цели роста" in html

    def test_dashboard_has_calendar(self, tmp_path: Path) -> None:
        from smm.dashboard import generate_dashboard

        path = generate_dashboard(days=3, seed=42, output=tmp_path / "dash.html")
        html = path.read_text(encoding="utf-8")
        assert "Контент-календарь" in html
        assert "cal-grid" in html

    def test_dashboard_summary(self, tmp_path: Path) -> None:
        from smm.dashboard import dashboard_summary, generate_dashboard

        path = generate_dashboard(days=3, seed=42, output=tmp_path / "dash.html")
        summary = dashboard_summary(path)
        assert "дашборд" in summary.lower()
        assert str(path) in summary

    def test_dashboard_default_output(self) -> None:
        from smm.dashboard import generate_dashboard

        path = generate_dashboard(days=2, seed=42)
        assert path.exists()
        assert path.name == "dashboard.html"
        path.unlink()


class TestConversionFunnel:
    def test_generate_funnel_posts_all_stages(self) -> None:
        from smm.conversion_funnel import generate_funnel_posts

        posts = generate_funnel_posts("Cyber Security & Ethical Hacking")
        stages = {p.stage for p in posts}
        assert stages == {"tofu", "mofu", "bofu"}

    def test_generate_funnel_posts_count(self) -> None:
        from smm.conversion_funnel import generate_funnel_posts

        posts = generate_funnel_posts("Cyber Security & Ethical Hacking")
        assert len(posts) == 15  # 5 hooks x 3 stages

    def test_generate_funnel_posts_unknown_pillar(self) -> None:
        from smm.conversion_funnel import generate_funnel_posts

        posts = generate_funnel_posts("Nonexistent")
        assert posts == []

    def test_generate_lead_magnets(self) -> None:
        from smm.conversion_funnel import generate_lead_magnets

        magnets = generate_lead_magnets("Red Team / Offensive Security")
        assert len(magnets) == 2
        assert all(m.pillar == "Red Team / Offensive Security" for m in magnets)

    def test_generate_pillar_funnel(self) -> None:
        from smm.conversion_funnel import generate_pillar_funnel

        funnel = generate_pillar_funnel("Machine Learning & AI")
        assert funnel.total_posts == 15
        assert len(funnel.tofu_posts) == 5
        assert len(funnel.mofu_posts) == 5
        assert len(funnel.bofu_posts) == 5

    def test_generate_all_funnels(self) -> None:
        from smm.conversion_funnel import generate_all_funnels

        funnels = generate_all_funnels()
        assert len(funnels) == len(PILLARS)

    def test_all_pillars_covered(self) -> None:
        from smm.conversion_funnel import PILLAR_FUNNELS

        for pillar in PILLARS:
            assert pillar.name in PILLAR_FUNNELS, f"Missing funnel for {pillar.name}"

    def test_export_funnel_json(self, tmp_path: Path) -> None:
        from smm.conversion_funnel import export_funnel_json, generate_all_funnels

        funnels = generate_all_funnels()
        path = export_funnel_json(funnels, tmp_path / "funnel.json")
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data) == len(PILLARS)

    def test_export_funnel_txt(self, tmp_path: Path) -> None:
        from smm.conversion_funnel import export_funnel_txt, generate_all_funnels

        funnels = generate_all_funnels()
        path = export_funnel_txt(funnels, tmp_path / "funnel.txt")
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "КОНВЕРСИОННАЯ ВОРОНКА" in text

    def test_funnel_summary(self) -> None:
        from smm.conversion_funnel import funnel_summary, generate_all_funnels

        funnels = generate_all_funnels()
        summary = funnel_summary(funnels)
        assert "Конверсионная воронка" in summary
        assert "лид-магнитов" in summary

    def test_funnel_post_has_cta(self) -> None:
        from smm.conversion_funnel import generate_funnel_posts

        posts = generate_funnel_posts("AliExpress - Гаджеты")
        assert all(p.cta for p in posts)


class TestUGCTemplates:
    def test_generate_ugc_templates(self) -> None:
        from smm.ugc_templates import generate_ugc_templates

        templates = generate_ugc_templates("Cyber Security & Ethical Hacking")
        assert len(templates) == 5  # 1 per UGC type

    def test_generate_ugc_templates_unknown_pillar(self) -> None:
        from smm.ugc_templates import generate_ugc_templates

        templates = generate_ugc_templates("Nonexistent")
        assert templates == []

    def test_generate_all_ugc_templates(self) -> None:
        from smm.ugc_templates import generate_all_ugc_templates

        templates = generate_all_ugc_templates()
        assert len(templates) == 25  # 5 pillars x 5 types

    def test_all_pillars_covered(self) -> None:
        from smm.ugc_templates import PILLAR_UGC

        for pillar in PILLARS:
            assert pillar.name in PILLAR_UGC, f"Missing UGC for {pillar.name}"

    def test_ugc_template_has_all_fields(self) -> None:
        from smm.ugc_templates import generate_ugc_templates

        templates = generate_ugc_templates("Red Team / Offensive Security")
        for t in templates:
            assert t.title
            assert t.prompt_text
            assert t.example
            assert t.hashtags
            assert t.cta

    def test_export_ugc_json(self, tmp_path: Path) -> None:
        from smm.ugc_templates import export_ugc_json, generate_all_ugc_templates

        templates = generate_all_ugc_templates()
        path = export_ugc_json(templates, tmp_path / "ugc.json")
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data) == 25

    def test_export_ugc_txt(self, tmp_path: Path) -> None:
        from smm.ugc_templates import export_ugc_txt, generate_all_ugc_templates

        templates = generate_all_ugc_templates()
        path = export_ugc_txt(templates, tmp_path / "ugc.txt")
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "UGC" in text

    def test_ugc_summary(self) -> None:
        from smm.ugc_templates import generate_all_ugc_templates, ugc_summary

        templates = generate_all_ugc_templates()
        summary = ugc_summary(templates)
        assert "UGC" in summary
        assert "25" in summary

    def test_ugc_types_all_present(self) -> None:
        from smm.ugc_templates import UGC_TYPES, generate_ugc_templates

        templates = generate_ugc_templates("Machine Learning & AI")
        types = {t.ugc_type for t in templates}
        assert types == set(UGC_TYPES)


class TestContentMixer:
    def test_generate_mixed_schedule(self) -> None:
        from smm.content_mixer import generate_mixed_schedule

        mixes = generate_mixed_schedule(days=3, seed=42)
        assert len(mixes) == 3

    def test_day_mix_has_posts(self) -> None:
        from smm.content_mixer import generate_mixed_schedule

        mixes = generate_mixed_schedule(days=2, seed=42)
        for dm in mixes:
            assert len(dm.posts) > 0

    def test_classify_post(self) -> None:
        from smm.content_mixer import classify_post
        from smm.ready_posts import generate_ready_posts

        posts = generate_ready_posts(days=1, seed=42)
        for p in posts:
            ctype = classify_post(p)
            assert ctype in {
                "educational",
                "entertaining",
                "promotional",
                "engagement",
                "social_proof",
            }

    def test_balance_score_range(self) -> None:
        from smm.content_mixer import generate_mixed_schedule

        mixes = generate_mixed_schedule(days=3, seed=42)
        for dm in mixes:
            assert 0.0 <= dm.balance_score <= 1.0

    def test_export_mix_json(self, tmp_path: Path) -> None:
        from smm.content_mixer import export_mix_json, generate_mixed_schedule

        mixes = generate_mixed_schedule(days=2, seed=42)
        path = export_mix_json(mixes, tmp_path / "mix.json")
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data) == 2

    def test_export_mix_txt(self, tmp_path: Path) -> None:
        from smm.content_mixer import export_mix_txt, generate_mixed_schedule

        mixes = generate_mixed_schedule(days=2, seed=42)
        path = export_mix_txt(mixes, tmp_path / "mix.txt")
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "КОНТЕНТ-МИКС" in text

    def test_mix_summary(self) -> None:
        from smm.content_mixer import generate_mixed_schedule, mix_summary

        mixes = generate_mixed_schedule(days=3, seed=42)
        summary = mix_summary(mixes)
        assert "Контент-микс" in summary
        assert "баланс" in summary.lower()

    def test_type_distribution_counts(self) -> None:
        from smm.content_mixer import generate_mixed_schedule

        mixes = generate_mixed_schedule(days=1, seed=42)
        for dm in mixes:
            total = sum(dm.type_distribution.values())
            assert total == len(dm.posts)


class TestViralHooks:
    def test_generate_hooks(self) -> None:
        from smm.viral_hooks import generate_hooks

        hooks = generate_hooks("Cyber Security & Ethical Hacking")
        assert len(hooks) > 0
        assert all(h.pillar == "Cyber Security & Ethical Hacking" for h in hooks)

    def test_generate_hooks_unknown_pillar(self) -> None:
        from smm.viral_hooks import generate_hooks

        hooks = generate_hooks("Nonexistent")
        assert hooks == []

    def test_generate_all_hooks(self) -> None:
        from smm.viral_hooks import generate_all_hooks

        hooks = generate_all_hooks()
        pillars = {h.pillar for h in hooks}
        assert len(pillars) == len(PILLARS)

    def test_all_pillars_covered(self) -> None:
        from smm.viral_hooks import PILLAR_HOOKS

        for pillar in PILLARS:
            assert pillar.name in PILLAR_HOOKS, f"Missing hooks for {pillar.name}"

    def test_hook_has_all_fields(self) -> None:
        from smm.viral_hooks import generate_hooks

        hooks = generate_hooks("Red Team / Offensive Security")
        for h in hooks:
            assert h.text
            assert h.thumbnail_text
            assert h.platform_best in ("instagram", "tiktok", "youtube")

    def test_pick_random_hooks(self) -> None:
        from smm.viral_hooks import pick_random_hooks

        hooks = pick_random_hooks(count=5, seed=42)
        assert len(hooks) == 5

    def test_pick_random_hooks_pillar(self) -> None:
        from smm.viral_hooks import pick_random_hooks

        hooks = pick_random_hooks(count=3, pillar="Machine Learning & AI", seed=42)
        assert len(hooks) == 3
        assert all(h.pillar == "Machine Learning & AI" for h in hooks)

    def test_export_hooks_json(self, tmp_path: Path) -> None:
        from smm.viral_hooks import export_hooks_json, generate_all_hooks

        hooks = generate_all_hooks()
        path = export_hooks_json(hooks, tmp_path / "hooks.json")
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data) == len(hooks)

    def test_export_hooks_txt(self, tmp_path: Path) -> None:
        from smm.viral_hooks import export_hooks_txt, generate_all_hooks

        hooks = generate_all_hooks()
        path = export_hooks_txt(hooks, tmp_path / "hooks.txt")
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "ВИРУСНЫЕ ХУКИ" in text

    def test_hooks_summary(self) -> None:
        from smm.viral_hooks import generate_all_hooks, hooks_summary

        hooks = generate_all_hooks()
        summary = hooks_summary(hooks)
        assert "Вирусные хуки" in summary

    def test_all_hook_types_present(self) -> None:
        from smm.viral_hooks import HOOK_TYPES, generate_hooks

        hooks = generate_hooks("AliExpress - Гаджеты")
        types = {h.hook_type for h in hooks}
        assert types == set(HOOK_TYPES)


# --- Cross-promo tests ---


class TestCrossPromo:
    def test_generate_all_promos(self) -> None:
        from smm.cross_promo import generate_cross_promos

        promos = generate_cross_promos(seed=42)
        assert len(promos) == 50  # 5 pillars * 10 routes

    def test_generate_single_pillar(self) -> None:
        from smm.cross_promo import generate_cross_promos

        promos = generate_cross_promos(
            pillar_name="Cyber Security & Ethical Hacking", seed=1
        )
        assert len(promos) == 10
        assert all(p.pillar == "Cyber Security & Ethical Hacking" for p in promos)

    def test_promo_fields_populated(self) -> None:
        from smm.cross_promo import generate_cross_promos

        promos = generate_cross_promos(seed=7)
        for p in promos:
            assert p.pillar
            assert p.source_platform in ("instagram", "tiktok", "youtube")
            assert p.target
            assert p.hook
            assert p.caption
            assert p.cta

    def test_caption_has_no_format_placeholders(self) -> None:
        from smm.cross_promo import generate_cross_promos

        promos = generate_cross_promos(seed=99)
        for p in promos:
            assert "{" not in p.caption, f"Unformatted placeholder in: {p.caption}"

    def test_seed_deterministic(self) -> None:
        from smm.cross_promo import generate_cross_promos

        a = generate_cross_promos(seed=42)
        b = generate_cross_promos(seed=42)
        assert [p.caption for p in a] == [p.caption for p in b]

    def test_routes_cover_all_targets(self) -> None:
        from smm.cross_promo import generate_cross_promos

        promos = generate_cross_promos(seed=1)
        targets = {p.target for p in promos}
        assert targets >= {"youtube", "instagram", "tiktok", "course", "referral"}

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.cross_promo import export_promos_json, generate_cross_promos

        promos = generate_cross_promos(seed=1)
        path = export_promos_json(promos, tmp_path / "promos.json")
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data) == 50

    def test_export_txt(self, tmp_path: Path) -> None:
        from smm.cross_promo import export_promos_txt, generate_cross_promos

        promos = generate_cross_promos(seed=1)
        path = export_promos_txt(promos, tmp_path / "promos.txt")
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "КРОСС-ПРОМО" in text

    def test_summary(self) -> None:
        from smm.cross_promo import generate_cross_promos, promos_summary

        promos = generate_cross_promos(seed=1)
        summary = promos_summary(promos)
        assert "Кросс-промо" in summary
        assert "Маршруты" in summary

    def test_unknown_pillar_returns_empty(self) -> None:
        from smm.cross_promo import generate_cross_promos

        promos = generate_cross_promos(pillar_name="Nonexistent")
        assert promos == []


# --- Email sequences tests ---


class TestEmailSequences:
    def test_generate_all_emails(self) -> None:
        from smm.email_sequences import generate_all_emails

        emails = generate_all_emails()
        assert len(emails) > 40

    def test_generate_single_pillar(self) -> None:
        from smm.email_sequences import generate_emails

        emails = generate_emails("Cyber Security & Ethical Hacking")
        assert len(emails) == 12
        assert all(e.pillar == "Cyber Security & Ethical Hacking" for e in emails)

    def test_all_sequence_types_present(self) -> None:
        from smm.email_sequences import SEQUENCE_TYPES, generate_emails

        emails = generate_emails("Red Team / Offensive Security")
        types = {e.sequence_type for e in emails}
        assert types == set(SEQUENCE_TYPES)

    def test_email_fields_populated(self) -> None:
        from smm.email_sequences import generate_all_emails

        for e in generate_all_emails():
            assert e.pillar
            assert e.sequence_type
            assert e.sequence_label
            assert e.day >= 0
            assert e.subject
            assert e.preview
            assert e.body_outline
            assert e.cta

    def test_unknown_pillar_returns_empty(self) -> None:
        from smm.email_sequences import generate_emails

        assert generate_emails("Nonexistent") == []

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.email_sequences import export_emails_json, generate_all_emails

        emails = generate_all_emails()
        path = export_emails_json(emails, tmp_path / "emails.json")
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data) == len(emails)

    def test_export_txt(self, tmp_path: Path) -> None:
        from smm.email_sequences import export_emails_txt, generate_all_emails

        emails = generate_all_emails()
        path = export_emails_txt(emails, tmp_path / "emails.txt")
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "EMAIL-ПОСЛЕДОВАТЕЛЬНОСТИ" in text

    def test_summary(self) -> None:
        from smm.email_sequences import emails_summary, generate_all_emails

        emails = generate_all_emails()
        summary = emails_summary(emails)
        assert "Email-последовательности" in summary
        assert "По типам серий" in summary

    def test_days_ascending_within_sequence(self) -> None:
        from smm.email_sequences import generate_emails

        emails = generate_emails("Machine Learning & AI")
        by_seq: dict[str, list[int]] = {}
        for e in emails:
            by_seq.setdefault(e.sequence_type, []).append(e.day)
        for days in by_seq.values():
            assert days == sorted(days)


# --- Content scoring tests ---


class TestContentScoring:
    def test_score_post_range(self) -> None:
        from smm.content_scoring import score_post

        s = score_post(
            "Бесплатный гайд по хакерским инструментам",
            "Cyber Security & Ethical Hacking",
            "tiktok",
            "reel",
            19,
        )
        assert 0 <= s.total_score <= 100
        assert s.grade in ("A", "B", "C", "D", "F")

    def test_generate_scored_batch(self) -> None:
        from smm.content_scoring import generate_scored_batch

        scored = generate_scored_batch(count=20, seed=42)
        assert len(scored) == 20
        scores = [s.total_score for s in scored]
        assert scores == sorted(scores, reverse=True)

    def test_seed_deterministic(self) -> None:
        from smm.content_scoring import generate_scored_batch

        a = generate_scored_batch(seed=7)
        b = generate_scored_batch(seed=7)
        assert [s.total_score for s in a] == [s.total_score for s in b]

    def test_grade_assignment(self) -> None:
        from smm.content_scoring import _grade

        assert _grade(85) == "A"
        assert _grade(70) == "B"
        assert _grade(55) == "C"
        assert _grade(40) == "D"
        assert _grade(20) == "F"

    def test_hook_score_capped(self) -> None:
        from smm.content_scoring import _hook_score

        score = _hook_score(
            "Бесплатный секрет: топ-5 ошибок хакеров при взломе нейросети"
        )
        assert score <= 30

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.content_scoring import export_scores_json, generate_scored_batch

        scored = generate_scored_batch(count=10, seed=1)
        path = export_scores_json(scored, tmp_path / "scores.json")
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data) == 10

    def test_export_txt(self, tmp_path: Path) -> None:
        from smm.content_scoring import export_scores_txt, generate_scored_batch

        scored = generate_scored_batch(count=10, seed=1)
        path = export_scores_txt(scored, tmp_path / "scores.txt")
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "СКОРИНГ" in text

    def test_summary(self) -> None:
        from smm.content_scoring import generate_scored_batch, scoring_summary

        scored = generate_scored_batch(count=15, seed=1)
        summary = scoring_summary(scored)
        assert "Скоринг контента" in summary
        assert "Средний балл" in summary

    def test_empty_summary(self) -> None:
        from smm.content_scoring import scoring_summary

        assert "0 постов" in scoring_summary([])


class TestCTALibrary:
    def test_generate_all(self) -> None:
        from smm.cta_library import generate_ctas

        ctas = generate_ctas()
        assert len(ctas) == 24

    def test_filter_by_stage(self) -> None:
        from smm.cta_library import generate_ctas

        tofu = generate_ctas(stage="tofu")
        assert all(c.stage == "tofu" for c in tofu)
        assert len(tofu) > 0

    def test_filter_by_platform(self) -> None:
        from smm.cta_library import generate_ctas

        ig = generate_ctas(platform="instagram")
        assert all(c.platform == "instagram" for c in ig)
        assert len(ig) == 8

    def test_filter_by_action(self) -> None:
        from smm.cta_library import generate_ctas

        saves = generate_ctas(action="save")
        assert all(c.action == "save" for c in saves)
        assert len(saves) > 0

    def test_cta_fields(self) -> None:
        from smm.cta_library import CTA, generate_ctas

        cta = generate_ctas()[0]
        assert isinstance(cta, CTA)
        assert cta.short_text
        assert cta.long_text
        assert cta.stage_label
        assert cta.action_label

    def test_pick_cta(self) -> None:
        from smm.cta_library import pick_cta

        cta = pick_cta(stage="bofu", platform="youtube", seed=42)
        assert cta.stage == "bofu"
        assert cta.platform == "youtube"

    def test_pick_cta_deterministic(self) -> None:
        from smm.cta_library import pick_cta

        a = pick_cta(seed=99)
        b = pick_cta(seed=99)
        assert a == b

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.cta_library import export_ctas_json, generate_ctas

        ctas = generate_ctas()
        p = export_ctas_json(ctas, tmp_path / "ctas.json")
        data = json.loads(p.read_text(encoding="utf-8"))
        assert len(data) == 24
        assert data[0]["stage"] == "tofu"

    def test_export_txt(self, tmp_path: Path) -> None:
        from smm.cta_library import export_ctas_txt, generate_ctas

        ctas = generate_ctas()
        p = export_ctas_txt(ctas, tmp_path / "ctas.txt")
        text = p.read_text(encoding="utf-8")
        assert "БИБЛИОТЕКА CTA" in text

    def test_summary(self) -> None:
        from smm.cta_library import cta_summary, generate_ctas

        ctas = generate_ctas()
        summary = cta_summary(ctas)
        assert "24 вариантов" in summary
        assert "По этапам воронки" in summary


class TestReferralAnalytics:
    def test_generate_metrics(self) -> None:
        from smm.referral_analytics import generate_campaign_metrics

        metrics = generate_campaign_metrics(seed=42)
        assert len(metrics) == 5 * 3 * 6  # 5 products * 3 platforms * 6 campaigns

    def test_deterministic(self) -> None:
        from smm.referral_analytics import generate_campaign_metrics

        a = generate_campaign_metrics(seed=42)
        b = generate_campaign_metrics(seed=42)
        assert a[0].impressions == b[0].impressions

    def test_metric_fields(self) -> None:
        from smm.referral_analytics import CampaignMetric, generate_campaign_metrics

        m = generate_campaign_metrics(seed=1)[0]
        assert isinstance(m, CampaignMetric)
        assert m.impressions > 0
        assert m.clicks > 0
        assert m.ctr > 0

    def test_summarize_by_product(self) -> None:
        from smm.referral_analytics import (
            generate_campaign_metrics,
            summarize_by_product,
        )

        metrics = generate_campaign_metrics(seed=1)
        summaries = summarize_by_product(metrics)
        assert len(summaries) == 5
        assert all(s.total_impressions > 0 for s in summaries)
        assert all(
            s.best_platform in ("instagram", "tiktok", "youtube") for s in summaries
        )

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.referral_analytics import (
            export_analytics_json,
            generate_campaign_metrics,
        )

        metrics = generate_campaign_metrics(seed=1)
        p = export_analytics_json(metrics, tmp_path / "analytics.json")
        data = json.loads(p.read_text(encoding="utf-8"))
        assert len(data) == 90
        assert "product_id" in data[0]

    def test_export_txt(self, tmp_path: Path) -> None:
        from smm.referral_analytics import (
            export_analytics_txt,
            generate_campaign_metrics,
        )

        metrics = generate_campaign_metrics(seed=1)
        p = export_analytics_txt(metrics, tmp_path / "analytics.txt")
        text = p.read_text(encoding="utf-8")
        assert "АНАЛИТИКА РЕФЕРАЛЬНЫХ КАМПАНИЙ" in text
        assert "ROAS" in text

    def test_summary(self) -> None:
        from smm.referral_analytics import analytics_summary, generate_campaign_metrics

        metrics = generate_campaign_metrics(seed=1)
        summary = analytics_summary(metrics)
        assert "90 кампаний" in summary
        assert "ROAS" in summary

    def test_empty_summary(self) -> None:
        from smm.referral_analytics import analytics_summary

        assert "0 кампаний" in analytics_summary([])

    def test_product_types(self) -> None:
        from smm.referral_analytics import generate_campaign_metrics

        metrics = generate_campaign_metrics(seed=1)
        types = {m.product_type for m in metrics}
        assert types == {"course", "referral"}


class TestTopicABTest:
    def test_generate_all(self) -> None:
        from smm.topic_ab_test import generate_ab_topics

        pairs = generate_ab_topics(seed=42)
        assert len(pairs) == 5 * 3 * 5  # 5 pillars * 3 platforms * 5 pairs each

    def test_deterministic(self) -> None:
        from smm.topic_ab_test import generate_ab_topics

        a = generate_ab_topics(seed=42)
        b = generate_ab_topics(seed=42)
        assert a[0].variant_a == b[0].variant_a

    def test_filter_by_pillar(self) -> None:
        from smm.topic_ab_test import generate_ab_topics

        pairs = generate_ab_topics(pillar="Machine Learning & AI", seed=1)
        assert all(p.pillar == "Machine Learning & AI" for p in pairs)
        assert len(pairs) == 15

    def test_filter_by_platform(self) -> None:
        from smm.topic_ab_test import generate_ab_topics

        pairs = generate_ab_topics(platform="tiktok", seed=1)
        assert all(p.platform == "tiktok" for p in pairs)
        assert len(pairs) == 25

    def test_pair_fields(self) -> None:
        from smm.topic_ab_test import TopicABPair, generate_ab_topics

        p = generate_ab_topics(seed=1)[0]
        assert isinstance(p, TopicABPair)
        assert p.variant_a
        assert p.variant_b
        assert p.test_id
        assert p.hypothesis

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.topic_ab_test import export_ab_topics_json, generate_ab_topics

        pairs = generate_ab_topics(seed=1)
        p = export_ab_topics_json(pairs, tmp_path / "topic_ab.json")
        data = json.loads(p.read_text(encoding="utf-8"))
        assert len(data) == 75
        assert "variant_a" in data[0]

    def test_export_txt(self, tmp_path: Path) -> None:
        from smm.topic_ab_test import export_ab_topics_txt, generate_ab_topics

        pairs = generate_ab_topics(seed=1)
        p = export_ab_topics_txt(pairs, tmp_path / "topic_ab.txt")
        text = p.read_text(encoding="utf-8")
        assert "A/B" in text

    def test_summary(self) -> None:
        from smm.topic_ab_test import ab_topics_summary, generate_ab_topics

        pairs = generate_ab_topics(seed=1)
        summary = ab_topics_summary(pairs)
        assert "75 пар" in summary

    def test_empty_summary(self) -> None:
        from smm.topic_ab_test import ab_topics_summary

        assert "0 пар" in ab_topics_summary([])


class TestAudiencePersonas:
    def test_generate_all(self) -> None:
        from smm.audience_personas import generate_personas

        personas = generate_personas()
        assert len(personas) == 5

    def test_filter_by_pillar(self) -> None:
        from smm.audience_personas import generate_personas

        personas = generate_personas(pillar="Machine Learning & AI")
        assert len(personas) == 1
        assert personas[0].pillar == "Machine Learning & AI"

    def test_persona_fields(self) -> None:
        from smm.audience_personas import Persona, generate_personas

        p = generate_personas()[0]
        assert isinstance(p, Persona)
        assert p.name
        assert len(p.pain_points) >= 2
        assert len(p.goals) >= 2
        assert len(p.buying_triggers) >= 2

    def test_pick_persona(self) -> None:
        from smm.audience_personas import pick_persona

        p = pick_persona("Cyber Security & Ethical Hacking", seed=42)
        assert p.pillar == "Cyber Security & Ethical Hacking"

    def test_content_brief(self) -> None:
        from smm.audience_personas import generate_content_brief, generate_personas

        p = generate_personas()[0]
        brief = generate_content_brief(p)
        assert "Бриф для" in brief
        assert "Боли аудитории" in brief
        assert "Триггеры покупки" in brief

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.audience_personas import export_personas_json, generate_personas

        personas = generate_personas()
        p = export_personas_json(personas, tmp_path / "personas.json")
        data = json.loads(p.read_text(encoding="utf-8"))
        assert len(data) == 5
        assert "pain_points" in data[0]

    def test_export_txt(self, tmp_path: Path) -> None:
        from smm.audience_personas import export_personas_txt, generate_personas

        personas = generate_personas()
        p = export_personas_txt(personas, tmp_path / "personas.txt")
        text = p.read_text(encoding="utf-8")
        assert "ПРОФИЛИ ЦЕЛЕВОЙ АУДИТОРИИ" in text

    def test_summary(self) -> None:
        from smm.audience_personas import generate_personas, personas_summary

        personas = generate_personas()
        summary = personas_summary(personas)
        assert "5 профилей" in summary

    def test_empty_summary(self) -> None:
        from smm.audience_personas import personas_summary

        assert "0 профилей" in personas_summary([])


class TestLeadMagnet:
    def test_generate_all(self) -> None:
        from smm.lead_magnet import generate_lead_magnets

        magnets = generate_lead_magnets()
        assert len(magnets) == 5

    def test_filter_by_pillar(self) -> None:
        from smm.lead_magnet import generate_lead_magnets

        magnets = generate_lead_magnets(pillar="Machine Learning & AI")
        assert len(magnets) == 1
        assert magnets[0].pillar == "Machine Learning & AI"

    def test_magnet_fields(self) -> None:
        from smm.lead_magnet import LeadMagnet, generate_lead_magnets

        m = generate_lead_magnets()[0]
        assert isinstance(m, LeadMagnet)
        assert m.title
        assert m.subtitle
        assert len(m.sections) >= 2
        assert m.cta

    def test_section_items(self) -> None:
        from smm.lead_magnet import generate_lead_magnets

        m = generate_lead_magnets()[0]
        for s in m.sections:
            assert s.heading
            assert len(s.items) >= 3

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.lead_magnet import export_lead_magnets_json, generate_lead_magnets

        magnets = generate_lead_magnets()
        p = export_lead_magnets_json(magnets, tmp_path / "lm.json")
        data = json.loads(p.read_text(encoding="utf-8"))
        assert len(data) == 5
        assert "sections" in data[0]

    def test_export_txt(self, tmp_path: Path) -> None:
        from smm.lead_magnet import export_lead_magnets_txt, generate_lead_magnets

        magnets = generate_lead_magnets()
        p = export_lead_magnets_txt(magnets, tmp_path / "lm.txt")
        text = p.read_text(encoding="utf-8")
        assert "ЛИД-МАГНИТЫ" in text

    def test_summary(self) -> None:
        from smm.lead_magnet import generate_lead_magnets, lead_magnets_summary

        magnets = generate_lead_magnets()
        summary = lead_magnets_summary(magnets)
        assert "5 материалов" in summary

    def test_empty_summary(self) -> None:
        from smm.lead_magnet import lead_magnets_summary

        assert "0 материалов" in lead_magnets_summary([])


class TestSocialProof:
    def test_generate_all_testimonials(self) -> None:
        from smm.social_proof import generate_testimonials

        testimonials = generate_testimonials()
        assert len(testimonials) == 10

    def test_filter_by_pillar(self) -> None:
        from smm.social_proof import generate_testimonials

        t = generate_testimonials(pillar="Machine Learning & AI")
        assert len(t) == 2
        assert all(x.pillar == "Machine Learning & AI" for x in t)

    def test_sample_count(self) -> None:
        from smm.social_proof import generate_testimonials

        t = generate_testimonials(count=3, seed=42)
        assert len(t) == 3

    def test_generate_pack(self) -> None:
        from smm.social_proof import SocialProofPack, generate_social_proof_pack

        pack = generate_social_proof_pack(seed=42)
        assert isinstance(pack, SocialProofPack)
        assert len(pack.testimonials) == 10
        assert len(pack.stats) == 6
        assert len(pack.trust_badges) == 6

    def test_testimonial_fields(self) -> None:
        from smm.social_proof import generate_testimonials

        t = generate_testimonials()[0]
        assert t.pillar
        assert t.name
        assert t.role
        assert t.text
        assert t.result

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.social_proof import (
            export_social_proof_json,
            generate_social_proof_pack,
        )

        pack = generate_social_proof_pack(seed=42)
        p = export_social_proof_json(pack, tmp_path / "sp.json")
        data = json.loads(p.read_text(encoding="utf-8"))
        assert "testimonials" in data
        assert "stats" in data
        assert "trust_badges" in data

    def test_export_txt(self, tmp_path: Path) -> None:
        from smm.social_proof import export_social_proof_txt, generate_social_proof_pack

        pack = generate_social_proof_pack(seed=42)
        p = export_social_proof_txt(pack, tmp_path / "sp.txt")
        text = p.read_text(encoding="utf-8")
        assert "СОЦИАЛЬНОЕ ДОКАЗАТЕЛЬСТВО" in text
        assert "ОТЗЫВЫ ВЫПУСКНИКОВ" in text

    def test_summary(self) -> None:
        from smm.social_proof import generate_social_proof_pack, social_proof_summary

        pack = generate_social_proof_pack(seed=42)
        summary = social_proof_summary(pack)
        assert "10 отзывов" in summary
        assert "6 метрик" in summary

    def test_seed_reproducibility(self) -> None:
        from smm.social_proof import generate_social_proof_pack

        pack1 = generate_social_proof_pack(seed=123)
        pack2 = generate_social_proof_pack(seed=123)
        assert pack1.stats == pack2.stats
        assert pack1.trust_badges == pack2.trust_badges


class TestContentPipeline:
    def test_run_pipeline(self) -> None:
        from smm.content_pipeline import run_pipeline

        result = run_pipeline(days=1, seed=42)
        assert result.total == 9
        assert result.avg_score > 0

    def test_enriched_posts_have_cta(self) -> None:
        from smm.content_pipeline import run_pipeline

        result = run_pipeline(days=1, seed=42)
        for e in result.posts:
            assert e.cta_short
            assert e.cta_long

    def test_funnel_stages_assigned(self) -> None:
        from smm.content_pipeline import run_pipeline

        result = run_pipeline(days=1, seed=42)
        stages = {e.funnel_stage for e in result.posts}
        assert stages == {"tofu", "mofu", "bofu"}

    def test_sorted_by_score(self) -> None:
        from smm.content_pipeline import run_pipeline

        result = run_pipeline(days=1, seed=42)
        scores = [e.score for e in result.posts]
        assert scores == sorted(scores, reverse=True)

    def test_by_platform(self) -> None:
        from smm.content_pipeline import run_pipeline

        result = run_pipeline(days=1, seed=42)
        assert sum(result.by_platform.values()) == result.total

    def test_top_posts(self) -> None:
        from smm.content_pipeline import run_pipeline

        result = run_pipeline(days=1, seed=42)
        assert len(result.top_posts) <= 10
        assert len(result.top_posts) <= result.total

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.content_pipeline import export_pipeline_json, run_pipeline

        result = run_pipeline(days=1, seed=42)
        p = export_pipeline_json(result, tmp_path / "pl.json")
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["total"] == 9
        assert "posts" in data

    def test_export_txt(self, tmp_path: Path) -> None:
        from smm.content_pipeline import export_pipeline_txt, run_pipeline

        result = run_pipeline(days=1, seed=42)
        p = export_pipeline_txt(result, tmp_path / "pl.txt")
        text = p.read_text(encoding="utf-8")
        assert "КОНТЕНТ-ПАЙПЛАЙН" in text

    def test_summary(self) -> None:
        from smm.content_pipeline import pipeline_summary, run_pipeline

        result = run_pipeline(days=1, seed=42)
        summary = pipeline_summary(result)
        assert "9 постов" in summary
        assert "скоринг" in summary


class TestRetargetingGuide:
    def test_generate_pixel_events_all(self) -> None:
        from smm.retargeting_guide import generate_pixel_events

        events = generate_pixel_events()
        assert len(events) == 17

    def test_filter_by_platform(self) -> None:
        from smm.retargeting_guide import generate_pixel_events

        events = generate_pixel_events(platform="meta")
        assert len(events) == 7
        assert all(e.platform == "meta" for e in events)

    def test_generate_audiences(self) -> None:
        from smm.retargeting_guide import generate_audiences

        audiences = generate_audiences()
        assert len(audiences) == 6

    def test_generate_guides(self) -> None:
        from smm.retargeting_guide import generate_retargeting_guides

        guides = generate_retargeting_guides()
        assert len(guides) == 3
        platforms = {g.platform for g in guides}
        assert platforms == {"meta", "tiktok", "youtube"}

    def test_guide_has_events(self) -> None:
        from smm.retargeting_guide import generate_retargeting_guides

        for g in generate_retargeting_guides():
            assert len(g.events) >= 5
            assert len(g.setup_steps) >= 6

    def test_event_fields(self) -> None:
        from smm.retargeting_guide import generate_pixel_events

        e = generate_pixel_events()[0]
        assert e.platform
        assert e.name
        assert e.trigger
        assert e.priority in ("high", "medium", "critical")

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.retargeting_guide import (
            export_retargeting_json,
            generate_audiences,
            generate_retargeting_guides,
        )

        guides = generate_retargeting_guides()
        audiences = generate_audiences()
        p = export_retargeting_json(guides, audiences, tmp_path / "rt.json")
        data = json.loads(p.read_text(encoding="utf-8"))
        assert "platforms" in data
        assert "audiences" in data

    def test_export_txt(self, tmp_path: Path) -> None:
        from smm.retargeting_guide import (
            export_retargeting_txt,
            generate_audiences,
            generate_retargeting_guides,
        )

        guides = generate_retargeting_guides()
        audiences = generate_audiences()
        p = export_retargeting_txt(guides, audiences, tmp_path / "rt.txt")
        text = p.read_text(encoding="utf-8")
        assert "РЕТАРГЕТИНГ" in text

    def test_summary(self) -> None:
        from smm.retargeting_guide import (
            generate_audiences,
            generate_retargeting_guides,
            retargeting_summary,
        )

        guides = generate_retargeting_guides()
        audiences = generate_audiences()
        summary = retargeting_summary(guides, audiences)
        assert "3 платформы" in summary
        assert "6 сегментов" in summary


class TestPricingCalculator:
    def test_generate_tiers(self) -> None:
        from smm.pricing_calculator import generate_tier_breakdowns

        tiers = generate_tier_breakdowns()
        assert len(tiers) == 3
        assert tiers[0].tier_id == "starter"
        assert tiers[2].tier_id == "pro"

    def test_tier_prices(self) -> None:
        from smm.pricing_calculator import generate_tier_breakdowns

        tiers = generate_tier_breakdowns()
        prices = [t.price_usd for t in tiers]
        assert prices == [97, 197, 397]

    def test_cost_per_post(self) -> None:
        from smm.pricing_calculator import generate_tier_breakdowns

        tiers = generate_tier_breakdowns()
        for t in tiers:
            assert t.cost_per_post > 0
            assert t.cost_per_post < t.price_usd

    def test_savings_positive(self) -> None:
        from smm.pricing_calculator import generate_tier_breakdowns

        tiers = generate_tier_breakdowns()
        for t in tiers:
            assert t.savings_vs_agency > 0

    def test_roi_projections(self) -> None:
        from smm.pricing_calculator import generate_roi_projections

        roi = generate_roi_projections()
        assert len(roi) == 3
        for r in roi:
            assert r.monthly_impressions > 0
            assert r.monthly_clicks > 0

    def test_roi_positive(self) -> None:
        from smm.pricing_calculator import generate_roi_projections

        roi = generate_roi_projections()
        for r in roi:
            assert r.roi_percent > 0

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.pricing_calculator import (
            export_pricing_json,
            generate_roi_projections,
            generate_tier_breakdowns,
        )

        tiers = generate_tier_breakdowns()
        roi = generate_roi_projections()
        p = export_pricing_json(tiers, roi, tmp_path / "pr.json")
        data = json.loads(p.read_text(encoding="utf-8"))
        assert "tiers" in data
        assert "roi_projections" in data
        assert "benchmarks" in data

    def test_export_txt(self, tmp_path: Path) -> None:
        from smm.pricing_calculator import (
            export_pricing_txt,
            generate_roi_projections,
            generate_tier_breakdowns,
        )

        tiers = generate_tier_breakdowns()
        roi = generate_roi_projections()
        p = export_pricing_txt(tiers, roi, tmp_path / "pr.txt")
        text = p.read_text(encoding="utf-8")
        assert "ROI" in text

    def test_summary(self) -> None:
        from smm.pricing_calculator import (
            generate_roi_projections,
            generate_tier_breakdowns,
            pricing_summary,
        )

        tiers = generate_tier_breakdowns()
        roi = generate_roi_projections()
        summary = pricing_summary(tiers, roi)
        assert "Starter" in summary
        assert "$97" in summary


class TestWebinarFunnel:
    def test_generate_all(self) -> None:
        from smm.webinar_funnel import generate_webinar_funnel

        messages = generate_webinar_funnel()
        assert len(messages) == 25

    def test_filter_by_pillar(self) -> None:
        from smm.webinar_funnel import generate_webinar_funnel

        messages = generate_webinar_funnel(pillar="Machine Learning & AI")
        assert len(messages) == 5
        assert all(m.pillar == "Machine Learning & AI" for m in messages)

    def test_stages_complete(self) -> None:
        from smm.webinar_funnel import FUNNEL_STAGES, generate_webinar_funnel

        messages = generate_webinar_funnel(pillar="Machine Learning & AI")
        stages = [m.stage for m in messages]
        assert stages == list(FUNNEL_STAGES)

    def test_message_fields(self) -> None:
        from smm.webinar_funnel import generate_webinar_funnel

        m = generate_webinar_funnel()[0]
        assert m.pillar
        assert m.stage
        assert m.stage_label
        assert m.webinar_title
        assert m.subject
        assert m.body

    def test_subject_contains_title(self) -> None:
        from smm.webinar_funnel import generate_webinar_funnel

        for m in generate_webinar_funnel():
            if m.stage == "invite":
                assert m.webinar_title in m.subject

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.webinar_funnel import export_webinar_json, generate_webinar_funnel

        messages = generate_webinar_funnel()
        p = export_webinar_json(messages, tmp_path / "wb.json")
        data = json.loads(p.read_text(encoding="utf-8"))
        assert len(data) == 25
        assert "subject" in data[0]

    def test_export_txt(self, tmp_path: Path) -> None:
        from smm.webinar_funnel import export_webinar_txt, generate_webinar_funnel

        messages = generate_webinar_funnel()
        p = export_webinar_txt(messages, tmp_path / "wb.txt")
        text = p.read_text(encoding="utf-8")
        assert "ВЕБИНАРНАЯ ВОРОНКА" in text

    def test_summary(self) -> None:
        from smm.webinar_funnel import generate_webinar_funnel, webinar_summary

        messages = generate_webinar_funnel()
        summary = webinar_summary(messages)
        assert "25 писем" in summary
        assert "5 направлений" in summary
        assert "5 этапов" in summary


class TestTelegramBotConfig:
    def test_generate_bot_config(self) -> None:
        from smm.telegram_bot_config import generate_bot_config

        config = generate_bot_config()
        assert len(config.commands) == 6
        assert len(config.course_messages) == 4
        assert len(config.faq_items) == 6
        assert len(config.notification_templates) == 3

    def test_commands_are_bot_command(self) -> None:
        from smm.telegram_bot_config import BotCommand, generate_bot_config

        config = generate_bot_config()
        for cmd in config.commands:
            assert isinstance(cmd, BotCommand)
            assert cmd.command.startswith("/")
            assert len(cmd.description) > 0

    def test_welcome_message_nonempty(self) -> None:
        from smm.telegram_bot_config import generate_bot_config

        config = generate_bot_config()
        assert len(config.welcome_message) > 50

    def test_course_messages_cover_pillars(self) -> None:
        from smm.telegram_bot_config import generate_bot_config

        config = generate_bot_config()
        expected = {
            "Cyber Security & Ethical Hacking",
            "Blue Team / Defensive Security",
            "Red Team / Offensive Security",
            "Machine Learning & AI",
        }
        assert set(config.course_messages.keys()) == expected

    def test_faq_items_are_faqitem(self) -> None:
        from smm.telegram_bot_config import FAQItem, generate_bot_config

        config = generate_bot_config()
        for item in config.faq_items:
            assert isinstance(item, FAQItem)
            assert len(item.question) > 0
            assert len(item.answer) > 0

    def test_notification_templates_have_placeholders(self) -> None:
        from smm.telegram_bot_config import generate_bot_config

        config = generate_bot_config()
        assert "{name}" in config.notification_templates["new_lead"]
        assert "{course}" in config.notification_templates["new_purchase"]
        assert "{magnet_name}" in config.notification_templates["lead_magnet_download"]

    def test_export_json(self, tmp_path: Path) -> None:
        from smm.telegram_bot_config import export_bot_config_json, generate_bot_config

        config = generate_bot_config()
        p = export_bot_config_json(config, tmp_path / "bot.json")
        assert p.exists()
        data = json.loads(p.read_text(encoding="utf-8"))
        assert len(data["commands"]) == 6
        assert len(data["faq"]) == 6

    def test_export_txt(self, tmp_path: Path) -> None:
        from smm.telegram_bot_config import export_bot_config_txt, generate_bot_config

        config = generate_bot_config()
        p = export_bot_config_txt(config, tmp_path / "bot.txt")
        assert p.exists()
        text = p.read_text(encoding="utf-8")
        assert "TELEGRAM-БОТ" in text
        assert "/start" in text

    def test_summary(self) -> None:
        from smm.telegram_bot_config import bot_config_summary, generate_bot_config

        config = generate_bot_config()
        summary = bot_config_summary(config)
        assert "6 команд" in summary
        assert "4 курсов" in summary
        assert "6 FAQ" in summary
        assert "3 уведомлений" in summary
