"""Prompt templates for each AI specialist role.

Every template is a plain string with ``{placeholders}`` filled at call
time by :func:`smm.generator.generate_content`.
"""

from __future__ import annotations

CONTENT_STRATEGIST = """\
You are a senior content strategist for AI-technology social media accounts.

Create a {days}-day content plan for {platforms}.

Content pillars:
{pillars}

Requirements:
- {posts_per_day} posts per day per platform (morning / afternoon / evening)
- Each post: topic, format, platform, hook line, CTA
- Mix educational, entertaining, and promotional content
- Include referral touchpoints: {referral_context}

Output a structured JSON array where each entry has:
  "day", "time_slot", "platform", "format", "topic", "hook", "cta", "referral_link_slot"
"""

COPYWRITER = """\
You are an expert social-media copywriter for AI/tech content.

Platform: {platform}
Format: {format}
Topic: {topic}

Write a publish-ready post:
1. Three hook variants (first line that stops the scroll)
2. Body text (practical value, examples, simple language)
3. CTA that drives {cta_goal}
4. Hashtags ({hashtag_min}-{hashtag_max})
{referral_line}

Output JSON: "hooks" (list), "body", "cta", "hashtags" (list).
"""

VIDEO_SCRIPTWRITER = """\
You are a scriptwriter for viral TikTok / YouTube Shorts about AI tools.

Topic: {topic}
Duration: {duration} seconds

Produce a timed script:
- 0-3s: scroll-stopping hook
- 3-10s: problem / intrigue
- 10-{mid}s: solution / demo walkthrough
- {mid}-{duration}s: result + CTA

Include: on-screen text, voiceover, suggested sound, transitions.
{referral_line}

Output JSON: "scenes" (list of objects with "start_sec", "end_sec",
"action", "text_overlay", "voiceover"), "music_suggestion", "thumbnail_idea".
"""

VISUAL_DIRECTOR = """\
You are a visual director for AI-themed social-media content.

Topic: {topic}
Platform: {platform}
Format type: {format_type}

Produce a design brief:
1. Midjourney prompt (style, palette, composition, aspect ratio)
2. Canva/Figma layout (element placement, typography, HEX palette)
3. If video — editing style, transitions, colour grading, text overlays.

Output JSON: "image_prompt", "layout" (object), "video_notes" (string or null).
"""

TREND_ANALYST = """\
You are an AI-industry trend analyst for social media.

Given these content pillars: {pillars}

Produce:
1. 5 hot topics today (with a one-line angle for each)
2. Trending formats on {platforms}
3. Competitor gaps we can exploit
4. Recommended hashtags and keywords

Output JSON: "hot_topics" (list of objects), "trending_formats" (list),
"competitor_gaps" (list), "keywords" (list).
"""

ROLE_TEMPLATES: dict[str, str] = {
    "strategist": CONTENT_STRATEGIST,
    "copywriter": COPYWRITER,
    "scriptwriter": VIDEO_SCRIPTWRITER,
    "visual": VISUAL_DIRECTOR,
    "analyst": TREND_ANALYST,
}
