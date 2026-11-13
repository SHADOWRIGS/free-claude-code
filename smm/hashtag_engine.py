"""Smart hashtag engine with niche-optimized tag pools.

Generates balanced hashtag sets mixing high-frequency (reach),
medium-frequency (discoverability), and low-frequency/niche (engagement)
tags. Each pillar has its own curated pool.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

HASHTAG_POOLS: dict[str, dict[str, list[str]]] = {
    "Cyber Security & Ethical Hacking": {
        "high": [
            "#cybersecurity",
            "#hacking",
            "#infosec",
            "#security",
            "#tech",
            "#programming",
            "#coding",
            "#linux",
            "#python",
            "#developer",
        ],
        "mid": [
            "#ethicalhacking",
            "#pentesting",
            "#bugbounty",
            "#cybersec",
            "#hackerlife",
            "#ctf",
            "#kalilinux",
            "#osint",
            "#malware",
            "#vulnerability",
        ],
        "niche": [
            "#burpsuite",
            "#metasploit",
            "#nmap",
            "#wireshark",
            "#hackthebox",
            "#tryhackme",
            "#owasp",
            "#zerodayexploit",
            "#reverseengineering",
            "#forensics",
        ],
    },
    "Blue Team / Defensive Security": {
        "high": [
            "#cybersecurity",
            "#infosec",
            "#security",
            "#tech",
            "#cloud",
            "#devops",
            "#IT",
            "#networking",
            "#sysadmin",
            "#linux",
        ],
        "mid": [
            "#blueteam",
            "#soc",
            "#siem",
            "#threatdetection",
            "#incidentresponse",
            "#dfir",
            "#malwareanalysis",
            "#threatintel",
            "#zerotrust",
            "#compliance",
        ],
        "niche": [
            "#splunk",
            "#elastic",
            "#crowdstrike",
            "#sentinelone",
            "#yara",
            "#sigma",
            "#mitre",
            "#socanalyst",
            "#threatmodeling",
            "#endpointsecurity",
        ],
    },
    "Red Team / Offensive Security": {
        "high": [
            "#cybersecurity",
            "#hacking",
            "#infosec",
            "#security",
            "#linux",
            "#python",
            "#tech",
            "#programming",
            "#coding",
            "#developer",
        ],
        "mid": [
            "#redteam",
            "#pentesting",
            "#offensive",
            "#exploit",
            "#bugbounty",
            "#ctf",
            "#hackerlife",
            "#socialengineering",
            "#phishing",
            "#privilegeescalation",
        ],
        "niche": [
            "#cobalt_strike",
            "#mimikatz",
            "#bloodhound",
            "#hashcat",
            "#responder",
            "#c2framework",
            "#lateralmovement",
            "#adattack",
            "#shellcode",
            "#redteamtools",
        ],
    },
    "Machine Learning & AI": {
        "high": [
            "#ai",
            "#machinelearning",
            "#datascience",
            "#python",
            "#tech",
            "#programming",
            "#coding",
            "#deeplearning",
            "#technology",
            "#innovation",
        ],
        "mid": [
            "#neuralnetwork",
            "#nlp",
            "#computervision",
            "#tensorflow",
            "#pytorch",
            "#gpt",
            "#llm",
            "#chatgpt",
            "#generativeai",
            "#mlops",
        ],
        "niche": [
            "#rag",
            "#finetuning",
            "#huggingface",
            "#transformers",
            "#langchain",
            "#promptengineering",
            "#aiagent",
            "#embeddings",
            "#vectordb",
            "#localllm",
        ],
    },
    "AliExpress - Гаджеты": {
        "high": [
            "#gadgets",
            "#tech",
            "#aliexpress",
            "#unboxing",
            "#review",
            "#technology",
            "#techreview",
            "#cool",
            "#musthave",
            "#budget",
        ],
        "mid": [
            "#hackergadgets",
            "#techgadgets",
            "#aliexpressfinds",
            "#cheaptech",
            "#budgettech",
            "#gadgetreview",
            "#techtips",
            "#bestgadgets",
            "#cooltech",
            "#affordable",
        ],
        "niche": [
            "#flipperzero",
            "#wifiadapter",
            "#hackrf",
            "#esp32",
            "#raspberrypi",
            "#arduino",
            "#hackingtools",
            "#networkhardware",
            "#sdr",
            "#pentest_gadgets",
        ],
    },
}


@dataclass(frozen=True, slots=True)
class HashtagSet:
    high: list[str]
    mid: list[str]
    niche: list[str]

    @property
    def all_tags(self) -> list[str]:
        return self.high + self.mid + self.niche

    @property
    def as_string(self) -> str:
        return " ".join(self.all_tags)

    @property
    def count(self) -> int:
        return len(self.all_tags)


def generate_hashtags(
    pillar_name: str,
    count: int = 15,
    high_ratio: float = 0.3,
    mid_ratio: float = 0.4,
    niche_ratio: float = 0.3,
    seed: int | None = None,
) -> HashtagSet:
    if seed is not None:
        random.seed(seed)

    pool = HASHTAG_POOLS.get(pillar_name)
    if pool is None:
        for key in HASHTAG_POOLS:
            if key.lower().startswith(pillar_name.lower()[:10]):
                pool = HASHTAG_POOLS[key]
                break
    if pool is None:
        pool = HASHTAG_POOLS["Cyber Security & Ethical Hacking"]

    n_high = max(1, round(count * high_ratio))
    n_niche = max(1, round(count * niche_ratio))
    n_mid = count - n_high - n_niche

    high = random.sample(pool["high"], min(n_high, len(pool["high"])))
    mid = random.sample(pool["mid"], min(n_mid, len(pool["mid"])))
    niche = random.sample(pool["niche"], min(n_niche, len(pool["niche"])))

    return HashtagSet(high=high, mid=mid, niche=niche)


def hashtag_report(pillar_name: str) -> str:
    pool = HASHTAG_POOLS.get(pillar_name)
    if pool is None:
        return f"Нет пула хештегов для «{pillar_name}»"

    lines = [f"Хештег-пул для «{pillar_name}»:\n"]
    for tier, tags in pool.items():
        label = {
            "high": "Высокочастотные",
            "mid": "Среднечастотные",
            "niche": "Нишевые",
        }
        lines.append(f"  {label.get(tier, tier)} ({len(tags)}):")
        lines.append(f"    {' '.join(tags)}")
    lines.append(f"\n  Всего: {sum(len(t) for t in pool.values())} тегов")
    return "\n".join(lines)
