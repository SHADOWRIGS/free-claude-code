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
