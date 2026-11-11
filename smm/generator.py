"""Content generation via Anthropic-compatible API.

Sends structured prompts to the proxy (or any Anthropic endpoint) and
returns parsed JSON content ready for scheduling and posting.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

import httpx

from smm.platforms import PLATFORM_SPECS, Platform
from smm.referral import ReferralRegistry
from smm.templates import ROLE_TEMPLATES


@dataclass(slots=True)
class GeneratorConfig:
    api_base: str = field(
        default_factory=lambda: os.environ.get("SMM_API_BASE", "http://localhost:4444")
    )
    api_key: str = field(default_factory=lambda: os.environ.get("SMM_API_KEY", ""))
    model: str = field(
        default_factory=lambda: os.environ.get("SMM_MODEL", "claude-sonnet-4-20250514")
    )
    max_tokens: int = 4096


@dataclass(slots=True)
class ContentGenerator:
    config: GeneratorConfig = field(default_factory=GeneratorConfig)
    referrals: ReferralRegistry = field(default_factory=ReferralRegistry)

    async def _call_api(self, system: str, user_prompt: str) -> dict[str, Any]:
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        if self.config.api_key:
            headers["x-api-key"] = self.config.api_key

        payload = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user_prompt}],
        }

        async with httpx.AsyncClient(
            base_url=self.config.api_base, timeout=120
        ) as client:
            resp = await client.post("/v1/messages", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        text = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                text += block["text"]

        text = text.strip()
        if text.startswith("```"):
            first_nl = text.index("\n")
            text = text[first_nl + 1 :]
            if text.endswith("```"):
                text = text[:-3]

        return json.loads(text)

    async def generate_plan(
        self,
        *,
        days: int = 7,
        platforms: list[Platform] | None = None,
        pillars: list[str] | None = None,
        posts_per_day: int = 3,
    ) -> list[dict[str, Any]]:
        platforms = platforms or list(Platform)
        pillars = pillars or [
            "AI tool reviews and tutorials",
            "AI industry news",
            "Success cases and applications",
            "Tips and productivity hacks",
        ]

        template = ROLE_TEMPLATES["strategist"]
        prompt = template.format(
            days=days,
            platforms=", ".join(p.value for p in platforms),
            pillars="\n".join(f"- {p}" for p in pillars),
            posts_per_day=posts_per_day,
            referral_context=self.referrals.context_string(),
        )
        result = await self._call_api(
            "You are a content strategist. Respond only with valid JSON.",
            prompt,
        )
        return result if isinstance(result, list) else result.get("plan", [result])

    async def generate_post(
        self,
        *,
        platform: Platform,
        fmt: str,
        topic: str,
        cta_goal: str = "link click",
    ) -> dict[str, Any]:
        spec = PLATFORM_SPECS[platform]
        referral_line = ""
        ref_links = self.referrals.for_platform(platform.value)
        if ref_links:
            referral_line = f"\nInclude this referral link naturally: {ref_links[0].build_url(platform.value)}"

        template = ROLE_TEMPLATES["copywriter"]
        prompt = template.format(
            platform=spec.name,
            format=fmt,
            topic=topic,
            cta_goal=cta_goal,
            hashtag_min=spec.hashtag_range[0],
            hashtag_max=spec.hashtag_range[1],
            referral_line=referral_line,
        )
        return await self._call_api(
            "You are a social media copywriter. Respond only with valid JSON.",
            prompt,
        )

    async def generate_script(
        self,
        *,
        topic: str,
        duration: int = 60,
    ) -> dict[str, Any]:
        mid = max(10, duration - 15)
        referral_line = ""
        ref_links = self.referrals.links
        if ref_links:
            referral_line = (
                f"\nMention this link in the CTA: {ref_links[0].build_url('video')}"
            )

        template = ROLE_TEMPLATES["scriptwriter"]
        prompt = template.format(
            topic=topic,
            duration=duration,
            mid=mid,
            referral_line=referral_line,
        )
        return await self._call_api(
            "You are a video scriptwriter. Respond only with valid JSON.",
            prompt,
        )

    async def generate_visual_brief(
        self,
        *,
        topic: str,
        platform: Platform,
        format_type: str,
    ) -> dict[str, Any]:
        template = ROLE_TEMPLATES["visual"]
        prompt = template.format(
            topic=topic,
            platform=PLATFORM_SPECS[platform].name,
            format_type=format_type,
        )
        return await self._call_api(
            "You are a visual director. Respond only with valid JSON.",
            prompt,
        )

    async def analyze_trends(
        self,
        *,
        platforms: list[Platform] | None = None,
        pillars: list[str] | None = None,
    ) -> dict[str, Any]:
        platforms = platforms or list(Platform)
        pillars = pillars or [
            "AI tool reviews",
            "AI industry news",
            "AI tutorials",
        ]
        template = ROLE_TEMPLATES["analyst"]
        prompt = template.format(
            pillars=", ".join(pillars),
            platforms=", ".join(p.value for p in platforms),
        )
        return await self._call_api(
            "You are a trend analyst. Respond only with valid JSON.",
            prompt,
        )
