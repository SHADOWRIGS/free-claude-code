"""SMM automation toolkit — AI-powered content generation and scheduling.

Standalone tool that uses the free-claude-code proxy (or any Anthropic-
compatible endpoint) to generate, format, and schedule social-media
content for Instagram, TikTok, and YouTube.
"""

from smm.analytics import WeeklyReport, create_tracking_template
from smm.content_pillars import PILLARS, ContentPillar
from smm.platforms import Platform
from smm.post_generator import PostSlot, generate_week_plan
from smm.preview import render_preview, render_preview_file
from smm.ready_posts import ReadyPost, generate_ready_posts

__all__ = [
    "PILLARS",
    "ContentPillar",
    "Platform",
    "PostSlot",
    "ReadyPost",
    "WeeklyReport",
    "create_tracking_template",
    "generate_ready_posts",
    "generate_week_plan",
    "render_preview",
    "render_preview_file",
]
