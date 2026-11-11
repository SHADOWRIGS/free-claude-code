"""Tests for the smm automation toolkit."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from smm.platforms import PLATFORM_SPECS, Platform
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
