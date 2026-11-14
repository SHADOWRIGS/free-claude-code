"""Carousel generator — ready-to-post Instagram carousel packs.

Assembles 4-5 slide carousels from CAROUSEL_FRAMEWORKS in content_bank,
enriched with pillar-specific content, hooks, CTAs, and comparisons.

Output: complete carousel scripts with slide text, visual directions,
and cover/CTA slides.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from smm.content_bank import CAROUSEL_FRAMEWORKS, get_ctas, get_hooks
from smm.content_pillars import PILLARS, ContentPillar

COMPARISON_PAIRS: dict[str, list[tuple[str, str]]] = {
    "Cyber Security & Ethical Hacking": [
        ("Kali Linux", "Parrot OS"),
        ("Burp Suite", "OWASP ZAP"),
        ("Bug Bounty", "Пентест по контракту"),
        ("CEH", "OSCP"),
    ],
    "Blue Team / Defensive Security": [
        ("Splunk", "ELK Stack"),
        ("EDR", "Антивирус"),
        ("SOC in-house", "SOC аутсорс"),
        ("SIEM", "XDR"),
    ],
    "Red Team / Offensive Security": [
        ("Metasploit", "Cobalt Strike"),
        ("Nmap", "Masscan"),
        ("Фишинг", "Vishing"),
        ("HackTheBox", "TryHackMe"),
    ],
    "Machine Learning & AI": [
        ("PyTorch", "TensorFlow"),
        ("GPT", "LLaMA"),
        ("Supervised", "Unsupervised"),
        ("Python", "R"),
    ],
    "AliExpress - Гаджеты": [
        ("WiFi Pineapple", "ESP8266"),
        ("Flipper Zero", "HackRF"),
        ("USB Rubber Ducky", "Bash Bunny"),
        ("Alfa AWUS036ACH", "TP-Link WN722N"),
    ],
}

LISTICLE_POINTS: dict[str, list[str]] = {
    "Cyber Security & Ethical Hacking": [
        "Nmap — сканируй сеть за минуту",
        "Wireshark — анализ трафика в реалтайме",
        "Hashcat — взлом хешей на GPU",
        "Burp Suite — перехват HTTP как профи",
        "John the Ripper — брутфорс паролей",
        "SQLmap — автоматизация SQL-инъекций",
    ],
    "Blue Team / Defensive Security": [
        "Zeek — мониторинг сетевого трафика",
        "YARA — детект малвари по сигнатурам",
        "Volatility — форензика оперативной памяти",
        "Suricata — IDS/IPS нового поколения",
        "TheHive — платформа реагирования",
        "Velociraptor — endpoint-мониторинг",
    ],
    "Red Team / Offensive Security": [
        "BloodHound — картография Active Directory",
        "Impacket — атаки на протоколы Windows",
        "Responder — перехват NTLM-хешей",
        "CrackMapExec — автоматизация атак",
        "Covenant — C2-фреймворк на .NET",
        "Rubeus — атаки на Kerberos",
    ],
    "Machine Learning & AI": [
        "Jupyter — интерактивные эксперименты",
        "Hugging Face — модели за 3 строки кода",
        "Pandas — манипуляция данными",
        "Scikit-learn — классические алгоритмы",
        "Weights & Biases — трекинг экспериментов",
        "LangChain — цепочки для LLM",
    ],
    "AliExpress - Гаджеты": [
        "WiFi-адаптер с режимом мониторинга",
        "USB Rubber Ducky — автоматизация атак",
        "Сетевой хаб для практики MITM",
        "Raspberry Pi — мини-лаборатория",
        "SDR-приёмник для анализа радио",
        "Lockpick-набор для физической безопасности",
    ],
}


@dataclass(frozen=True, slots=True)
class CarouselSlide:
    number: int
    text: str
    visual_note: str
    is_cover: bool
    is_cta: bool


@dataclass(frozen=True, slots=True)
class CarouselPack:
    pillar: str
    topic: str
    framework: str
    slides: list[CarouselSlide]

    def to_dict(self) -> dict[str, object]:
        return {
            "pillar": self.pillar,
            "topic": self.topic,
            "framework": self.framework,
            "slides": [
                {
                    "number": s.number,
                    "text": s.text,
                    "visual_note": s.visual_note,
                    "is_cover": s.is_cover,
                    "is_cta": s.is_cta,
                }
                for s in self.slides
            ],
        }


def _get_comparison(pillar: ContentPillar) -> tuple[str, str]:
    pairs = COMPARISON_PAIRS.get(pillar.name)
    if pairs:
        return random.choice(pairs)
    return ("Вариант A", "Вариант B")


def _get_listicle_points(pillar: ContentPillar, count: int = 3) -> list[str]:
    points = LISTICLE_POINTS.get(pillar.name, [])
    if not points:
        return [f"Пункт {i}" for i in range(1, count + 1)]
    random.shuffle(points)
    return points[:count]


def generate_carousel(
    pillar: ContentPillar,
    topic: str,
    seed: int | None = None,
) -> CarouselPack:
    if seed is not None:
        random.seed(seed)

    fw = random.choice(CAROUSEL_FRAMEWORKS)
    hooks = get_hooks(pillar.name.split("/")[0].strip().split("&")[0].strip(), count=2)
    ctas = get_ctas("referral" if pillar.product == "referral" else "course", count=1)
    option_a, option_b = _get_comparison(pillar)
    points = _get_listicle_points(pillar, count=3)
    topic_lower = topic.lower() if topic[0].isupper() else topic

    subs = {
        "hook": hooks[0],
        "cta": ctas[0],
        "topic": topic,
        "topic_lower": topic_lower,
        "option_a": option_a,
        "option_b": option_b,
        "num_1": "1",
        "num_2": "2",
        "num_3": "3",
        "point_1": points[0],
        "point_2": points[1] if len(points) > 1 else points[0],
        "point_3": points[2] if len(points) > 2 else points[0],
    }

    slides: list[CarouselSlide] = []
    slide_keys = [k for k in fw if k != "name"]
    for i, key in enumerate(slide_keys, 1):
        text = fw[key]
        for k, v in subs.items():
            text = text.replace(f"{{{k}}}", v)

        is_cover = key == "cover"
        is_cta = key == "cta_slide"

        if is_cover:
            visual = "Обложка: крупный шрифт, яркий фон, привлекающий внимание"
        elif is_cta:
            visual = "Финальный слайд: CTA + стрелка «ссылка в био»"
        else:
            visual = f"Информационный слайд: тёмный фон, иконки, факт по теме {topic}"

        slides.append(
            CarouselSlide(
                number=i,
                text=text,
                visual_note=visual,
                is_cover=is_cover,
                is_cta=is_cta,
            )
        )

    return CarouselPack(
        pillar=pillar.name,
        topic=topic,
        framework=fw["name"],
        slides=slides,
    )


def generate_carousels(
    count: int = 5,
    seed: int | None = None,
) -> list[CarouselPack]:
    if seed is not None:
        random.seed(seed)

    packs: list[CarouselPack] = []
    all_topics = [(t, p) for p in PILLARS for t in p.topics]
    random.shuffle(all_topics)

    for i in range(min(count, len(all_topics))):
        topic, pillar = all_topics[i]
        pack = generate_carousel(pillar, topic)
        packs.append(pack)

    return packs


def export_carousels_json(packs: list[CarouselPack], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [p.to_dict() for p in packs]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_carousels_txt(packs: list[CarouselPack], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for i, pack in enumerate(packs, 1):
        lines.append(f"{'=' * 50}")
        lines.append(f"КАРУСЕЛЬ #{i} | {pack.framework}")
        lines.append(f"Тема: {pack.topic}")
        lines.append(f"Направление: {pack.pillar}")
        lines.append(f"{'=' * 50}")
        for slide in pack.slides:
            role = ""
            if slide.is_cover:
                role = " [ОБЛОЖКА]"
            elif slide.is_cta:
                role = " [CTA]"
            lines.append(f"\n  Слайд {slide.number}{role}:")
            lines.append(f"    Текст: {slide.text}")
            lines.append(f"    Визуал: {slide.visual_note}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def carousel_summary(packs: list[CarouselPack]) -> str:
    by_pillar: dict[str, int] = {}
    by_fw: dict[str, int] = {}
    total_slides = 0
    for p in packs:
        by_pillar[p.pillar] = by_pillar.get(p.pillar, 0) + 1
        by_fw[p.framework] = by_fw.get(p.framework, 0) + 1
        total_slides += len(p.slides)

    lines = [
        f"Карусели: {len(packs)} шт.",
        f"Всего слайдов: {total_slides}",
        "\nПо направлениям:",
    ]
    for name, count in sorted(by_pillar.items()):
        lines.append(f"  {name}: {count}")
    lines.append("\nПо фреймворкам:")
    for name, count in sorted(by_fw.items()):
        lines.append(f"  {name}: {count}")
    return "\n".join(lines)
