"""Media library — image/video specs, canvas templates, stock resources.

Generates structured media configs:
- Platform image/video size specifications
- Canvas templates per content type
- Stock resource directories (free sources)
- File naming conventions
- Asset organization structure
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

IMAGE_SPECS: list[dict[str, str | int]] = [
    {
        "platform": "Instagram",
        "type": "post_square",
        "width": 1080,
        "height": 1080,
        "aspect": "1:1",
        "format": "JPG/PNG",
        "max_size_mb": 30,
    },
    {
        "platform": "Instagram",
        "type": "post_portrait",
        "width": 1080,
        "height": 1350,
        "aspect": "4:5",
        "format": "JPG/PNG",
        "max_size_mb": 30,
    },
    {
        "platform": "Instagram",
        "type": "story",
        "width": 1080,
        "height": 1920,
        "aspect": "9:16",
        "format": "JPG/PNG",
        "max_size_mb": 30,
    },
    {
        "platform": "Instagram",
        "type": "carousel",
        "width": 1080,
        "height": 1080,
        "aspect": "1:1",
        "format": "JPG/PNG",
        "max_size_mb": 30,
    },
    {
        "platform": "TikTok",
        "type": "video_cover",
        "width": 1080,
        "height": 1920,
        "aspect": "9:16",
        "format": "JPG/PNG",
        "max_size_mb": 10,
    },
    {
        "platform": "YouTube",
        "type": "thumbnail",
        "width": 1280,
        "height": 720,
        "aspect": "16:9",
        "format": "JPG/PNG",
        "max_size_mb": 2,
    },
    {
        "platform": "YouTube",
        "type": "banner",
        "width": 2560,
        "height": 1440,
        "aspect": "16:9",
        "format": "JPG/PNG",
        "max_size_mb": 6,
    },
    {
        "platform": "Telegram",
        "type": "post_image",
        "width": 1280,
        "height": 720,
        "aspect": "16:9",
        "format": "JPG/PNG",
        "max_size_mb": 10,
    },
]

VIDEO_SPECS: list[dict[str, str | int]] = [
    {
        "platform": "Instagram",
        "type": "reels",
        "width": 1080,
        "height": 1920,
        "aspect": "9:16",
        "max_duration_sec": 90,
        "format": "MP4",
        "fps": 30,
    },
    {
        "platform": "TikTok",
        "type": "standard",
        "width": 1080,
        "height": 1920,
        "aspect": "9:16",
        "max_duration_sec": 180,
        "format": "MP4",
        "fps": 30,
    },
    {
        "platform": "YouTube",
        "type": "standard",
        "width": 1920,
        "height": 1080,
        "aspect": "16:9",
        "max_duration_sec": 3600,
        "format": "MP4",
        "fps": 30,
    },
    {
        "platform": "YouTube",
        "type": "shorts",
        "width": 1080,
        "height": 1920,
        "aspect": "9:16",
        "max_duration_sec": 60,
        "format": "MP4",
        "fps": 30,
    },
]

CANVAS_TEMPLATES: list[dict[str, str]] = [
    {
        "name": "Терминал-пост",
        "description": "Тёмный фон с кодом/командами для хакерской эстетики",
        "size": "1080x1080",
        "elements": "фон #0D1117, текст #3FB950, лого, CTA-полоса",
        "best_for": "Cyber Security, Red Team",
    },
    {
        "name": "Инфографика-карусель",
        "description": "Серия слайдов с пошаговым объяснением",
        "size": "1080x1080",
        "elements": "нумерация, иконки, прогресс-бар, CTA на последнем",
        "best_for": "Все курсы",
    },
    {
        "name": "До/После",
        "description": "Сравнение до и после обучения (сплит-экран)",
        "size": "1080x1350",
        "elements": "два блока, стрелка, статистика, CTA",
        "best_for": "ML, Cyber Security",
    },
    {
        "name": "Товарная карточка",
        "description": "Фото товара + описание + цена + ссылка",
        "size": "1080x1080",
        "elements": "фото, цена, рейтинг, кнопка Купить",
        "best_for": "AliExpress — Гаджеты",
    },
    {
        "name": "Цитата-мотиватор",
        "description": "Цитата на тематическом фоне для вовлечения",
        "size": "1080x1080",
        "elements": "фон, кавычки, текст цитаты, автор, лого",
        "best_for": "Все направления",
    },
    {
        "name": "YouTube-превью",
        "description": "Яркий thumbnail с лицом, текстом и эмоцией",
        "size": "1280x720",
        "elements": "фото/лицо, крупный текст (3-5 слов), стрелка/рамка",
        "best_for": "Все видео",
    },
]

STOCK_SOURCES: list[dict[str, str]] = [
    {
        "name": "Unsplash",
        "url": "https://unsplash.com",
        "type": "Фото",
        "license": "Бесплатно для коммерческого использования",
        "best_for": "Фоны, технологии, ноутбуки",
    },
    {
        "name": "Pexels",
        "url": "https://pexels.com",
        "type": "Фото + Видео",
        "license": "Бесплатно для коммерческого использования",
        "best_for": "Фоны, люди за компьютерами",
    },
    {
        "name": "Flaticon",
        "url": "https://flaticon.com",
        "type": "Иконки",
        "license": "Бесплатно с указанием автора",
        "best_for": "Иконки для инфографик",
    },
    {
        "name": "Canva",
        "url": "https://canva.com",
        "type": "Шаблоны + Элементы",
        "license": "Бесплатный план / Pro",
        "best_for": "Быстрое создание постов",
    },
    {
        "name": "Remove.bg",
        "url": "https://remove.bg",
        "type": "Инструмент",
        "license": "Бесплатно (лимиты)",
        "best_for": "Удаление фона с фото",
    },
]

NAMING_CONVENTION: dict[str, str] = {
    "pattern": "{platform}_{type}_{pillar}_{date}_{version}.{ext}",
    "example": "ig_post_cybersec_20261116_v1.png",
    "platform_codes": "ig=Instagram, tt=TikTok, yt=YouTube, tg=Telegram",
    "type_codes": "post, story, reel, thumb, banner, carousel, cover",
}


@dataclass(frozen=True, slots=True)
class ImageSpec:
    platform: str
    type: str
    width: int
    height: int
    aspect: str
    format: str
    max_size_mb: int


@dataclass(frozen=True, slots=True)
class VideoSpec:
    platform: str
    type: str
    width: int
    height: int
    aspect: str
    max_duration_sec: int
    format: str
    fps: int


@dataclass(frozen=True, slots=True)
class CanvasTemplate:
    name: str
    description: str
    size: str
    elements: str
    best_for: str


@dataclass(frozen=True, slots=True)
class StockSource:
    name: str
    url: str
    type: str
    license: str
    best_for: str


@dataclass(frozen=True, slots=True)
class MediaLibrary:
    image_specs: tuple[ImageSpec, ...]
    video_specs: tuple[VideoSpec, ...]
    canvas_templates: tuple[CanvasTemplate, ...]
    stock_sources: tuple[StockSource, ...]
    naming_pattern: str
    naming_example: str


def generate_media_library() -> MediaLibrary:
    return MediaLibrary(
        image_specs=tuple(
            ImageSpec(
                platform=s["platform"],
                type=s["type"],
                width=int(s["width"]),
                height=int(s["height"]),
                aspect=s["aspect"],
                format=s["format"],
                max_size_mb=int(s["max_size_mb"]),
            )
            for s in IMAGE_SPECS
        ),
        video_specs=tuple(
            VideoSpec(
                platform=s["platform"],
                type=s["type"],
                width=int(s["width"]),
                height=int(s["height"]),
                aspect=s["aspect"],
                max_duration_sec=int(s["max_duration_sec"]),
                format=s["format"],
                fps=int(s["fps"]),
            )
            for s in VIDEO_SPECS
        ),
        canvas_templates=tuple(
            CanvasTemplate(
                name=t["name"],
                description=t["description"],
                size=t["size"],
                elements=t["elements"],
                best_for=t["best_for"],
            )
            for t in CANVAS_TEMPLATES
        ),
        stock_sources=tuple(
            StockSource(
                name=s["name"],
                url=s["url"],
                type=s["type"],
                license=s["license"],
                best_for=s["best_for"],
            )
            for s in STOCK_SOURCES
        ),
        naming_pattern=NAMING_CONVENTION["pattern"],
        naming_example=NAMING_CONVENTION["example"],
    )


def export_media_json(ml: MediaLibrary, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "image_specs": [
            {
                "platform": s.platform,
                "type": s.type,
                "width": s.width,
                "height": s.height,
                "aspect": s.aspect,
                "format": s.format,
                "max_size_mb": s.max_size_mb,
            }
            for s in ml.image_specs
        ],
        "video_specs": [
            {
                "platform": s.platform,
                "type": s.type,
                "width": s.width,
                "height": s.height,
                "aspect": s.aspect,
                "max_duration_sec": s.max_duration_sec,
                "format": s.format,
                "fps": s.fps,
            }
            for s in ml.video_specs
        ],
        "canvas_templates": [
            {
                "name": t.name,
                "description": t.description,
                "size": t.size,
                "elements": t.elements,
                "best_for": t.best_for,
            }
            for t in ml.canvas_templates
        ],
        "stock_sources": [
            {
                "name": s.name,
                "url": s.url,
                "type": s.type,
                "license": s.license,
                "best_for": s.best_for,
            }
            for s in ml.stock_sources
        ],
        "naming": {
            "pattern": ml.naming_pattern,
            "example": ml.naming_example,
        },
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_media_txt(ml: MediaLibrary, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "=" * 60,
        "МЕДИА-БИБЛИОТЕКА — СПЕЦИФИКАЦИИ И ШАБЛОНЫ",
        "=" * 60,
        "\n📐 РАЗМЕРЫ ИЗОБРАЖЕНИЙ",
        "━" * 50,
    ]
    lines.extend(
        f"  {s.platform} / {s.type}: {s.width}x{s.height} ({s.aspect})"
        f" | {s.format} ≤{s.max_size_mb}MB"
        for s in ml.image_specs
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("🎬 РАЗМЕРЫ ВИДЕО")
    lines.append("━" * 50)
    lines.extend(
        f"  {s.platform} / {s.type}: {s.width}x{s.height} ({s.aspect})"
        f" | {s.format} {s.fps}fps ≤{s.max_duration_sec}с"
        for s in ml.video_specs
    )

    lines.append(f"\n{'━' * 50}")
    lines.append("🎨 ШАБЛОНЫ КАНВАСОВ")
    lines.append("━" * 50)
    for t in ml.canvas_templates:
        lines.append(f"\n  [{t.name}] {t.size}")
        lines.append(f"    {t.description}")
        lines.append(f"    Элементы: {t.elements}")
        lines.append(f"    Для: {t.best_for}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📸 СТОКОВЫЕ РЕСУРСЫ")
    lines.append("━" * 50)
    for s in ml.stock_sources:
        lines.append(f"\n  [{s.name}] {s.url}")
        lines.append(f"    Тип: {s.type} | Лицензия: {s.license}")
        lines.append(f"    Для: {s.best_for}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📁 ИМЕНОВАНИЕ ФАЙЛОВ")
    lines.append("━" * 50)
    lines.append(f"  Паттерн: {ml.naming_pattern}")
    lines.append(f"  Пример: {ml.naming_example}")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def media_library_summary(ml: MediaLibrary) -> str:
    return (
        f"Медиа-библиотека: "
        f"{len(ml.image_specs)} спеков изображений, "
        f"{len(ml.video_specs)} спеков видео, "
        f"{len(ml.canvas_templates)} шаблонов, "
        f"{len(ml.stock_sources)} стоковых ресурсов"
    )
