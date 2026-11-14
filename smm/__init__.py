"""SMM automation toolkit — AI-powered content generation and scheduling.

Standalone tool that uses the free-claude-code proxy (or any Anthropic-
compatible endpoint) to generate, format, and schedule social-media
content for Instagram, TikTok, and YouTube.
"""

from smm.analytics import WeeklyReport, create_tracking_template
from smm.content_bank import get_ctas, get_hooks, get_story_framework
from smm.content_pillars import PILLARS, ContentPillar
from smm.hashtag_engine import generate_hashtags, hashtag_report
from smm.platforms import Platform
from smm.post_generator import PostSlot, generate_week_plan
from smm.preview import render_preview, render_preview_file
from smm.ready_posts import ReadyPost, generate_ready_posts
from smm.story_generator import StoryPack, generate_story_packs

__all__ = [
    "PILLARS",
    "ContentPillar",
    "Platform",
    "PostSlot",
    "ReadyPost",
    "StoryPack",
    "WeeklyReport",
    "create_tracking_template",
    "generate_hashtags",
    "generate_ready_posts",
    "generate_story_packs",
    "generate_week_plan",
    "get_ctas",
    "get_hooks",
    "get_story_framework",
    "hashtag_report",
    "render_preview",
    "render_preview_file",
]
