"""Referral and course link integration for SMM content.

Maintains a registry of referral links and course landing pages so that
every generated post can include the right monetisation touchpoint.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class ReferralLink:
    label: str
    url: str
    utm_source: str = ""
    utm_medium: str = "social"
    utm_campaign: str = ""
    platforms: list[str] = field(default_factory=list)

    def build_url(self, platform: str = "") -> str:
        parts = [self.url]
        params: list[str] = []
        if self.utm_source:
            params.append(f"utm_source={self.utm_source}")
        elif platform:
            params.append(f"utm_source={platform}")
        if self.utm_medium:
            params.append(f"utm_medium={self.utm_medium}")
        if self.utm_campaign:
            params.append(f"utm_campaign={self.utm_campaign}")
        if params:
            sep = "&" if "?" in self.url else "?"
            parts.append(sep)
            parts.append("&".join(params))
        return "".join(parts)


@dataclass(slots=True)
class ReferralRegistry:
    links: list[ReferralLink] = field(default_factory=list)

    def add(self, link: ReferralLink) -> None:
        self.links.append(link)

    def for_platform(self, platform: str) -> list[ReferralLink]:
        return [
            lnk for lnk in self.links if not lnk.platforms or platform in lnk.platforms
        ]

    def context_string(self, platform: str = "") -> str:
        relevant = self.for_platform(platform) if platform else self.links
        if not relevant:
            return "No referral links configured."
        lines = [f"- {lnk.label}: {lnk.build_url(platform)}" for lnk in relevant]
        return "\n".join(lines)

    def save(self, path: Path) -> None:
        data = [
            {
                "label": lnk.label,
                "url": lnk.url,
                "utm_source": lnk.utm_source,
                "utm_medium": lnk.utm_medium,
                "utm_campaign": lnk.utm_campaign,
                "platforms": lnk.platforms,
            }
            for lnk in self.links
        ]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    @classmethod
    def load(cls, path: Path) -> ReferralRegistry:
        if not path.exists():
            return cls()
        data = json.loads(path.read_text())
        registry = cls()
        for entry in data:
            registry.add(ReferralLink(**entry))
        return registry
