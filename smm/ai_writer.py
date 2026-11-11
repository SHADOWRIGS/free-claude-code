"""AI-powered content writer that turns PostSlot plans into ready-to-publish posts."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import httpx

from smm.generator import GeneratorConfig
from smm.post_generator import PostSlot


@dataclass(frozen=True, slots=True)
class ReadyPost:
    slot: PostSlot
    caption: str
    visual_brief: str
    script: str
    alt_hooks: list[str]


WRITER_SYSTEM = """\
You are an expert SMM copywriter for cybersecurity, ethical hacking, \
machine learning, and tech gadgets content in Russian.
Always respond with valid JSON only, no markdown fences."""

POST_PROMPT = """\
Write a complete social media post in Russian.

Platform: {platform}
Format: {fmt}
Content pillar: {pillar}
Topic: {topic}

Use this hook as a starting point: {hook}
Call to action: {cta}
Hashtags to include: {hashtags}
{referral_line}

Return JSON:
{{
  "caption": "full post text with emojis, line breaks, hashtags at the end",
  "visual_brief": "2-3 sentences describing the ideal visual/thumbnail",
  "script": "if video format, provide a 30-60 second script; otherwise empty string",
  "alt_hooks": ["hook variant 1", "hook variant 2", "hook variant 3"]
}}"""


@dataclass(slots=True)
class AIWriter:
    config: GeneratorConfig = field(default_factory=GeneratorConfig)

    async def _call(self, prompt: str) -> dict[str, Any]:
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        if self.config.api_key:
            headers["x-api-key"] = self.config.api_key

        payload = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "system": WRITER_SYSTEM,
            "messages": [{"role": "user", "content": prompt}],
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

    async def write_post(self, slot: PostSlot) -> ReadyPost:
        referral_line = ""
        if slot.referral_url:
            referral_line = f"Referral link to include: {slot.referral_url}"

        prompt = POST_PROMPT.format(
            platform=slot.platform.value,
            fmt=slot.format,
            pillar=slot.pillar.name,
            topic=slot.topic,
            hook=slot.hook,
            cta=slot.cta,
            hashtags=" ".join(slot.hashtags),
            referral_line=referral_line,
        )

        result = await self._call(prompt)
        return ReadyPost(
            slot=slot,
            caption=result.get("caption", ""),
            visual_brief=result.get("visual_brief", ""),
            script=result.get("script", ""),
            alt_hooks=result.get("alt_hooks", []),
        )

    async def write_batch(self, slots: list[PostSlot]) -> list[ReadyPost]:
        results: list[ReadyPost] = []
        for slot in slots:
            results.append(await self.write_post(slot))  # noqa: PERF401
        return results
