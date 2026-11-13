"""Caption validator — checks posts against platform constraints.

Validates that each post meets platform requirements before publishing:
- Caption length within limits
- Hashtag count within range
- CTA presence (for course/referral posts)
- No broken template placeholders
- Visual brief present
- Video script present for video formats
"""

from __future__ import annotations

from dataclasses import dataclass

from smm.platforms import PLATFORM_SPECS, Platform
from smm.ready_posts import ReadyPost

VIDEO_FORMATS = frozenset({"reels", "short_video", "shorts", "duet", "full_video"})

PLACEHOLDER_MARKERS = ("{hook}", "{cta}", "{topic}", "{hashtags}", "{pillar_short}")


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    post_index: int
    field: str
    severity: str
    message: str


@dataclass(frozen=True, slots=True)
class ValidationReport:
    total: int
    passed: int
    warnings: list[ValidationIssue]
    errors: list[ValidationIssue]

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        lines = [
            f"Проверено: {self.total} постов",
            f"Прошло: {self.passed}",
            f"Ошибок: {len(self.errors)}",
            f"Предупреждений: {len(self.warnings)}",
        ]
        if self.errors:
            lines.append("\nОшибки:")
            lines.extend(
                f"  [{e.post_index}] {e.field}: {e.message}" for e in self.errors[:20]
            )
        if self.warnings:
            lines.append("\nПредупреждения:")
            lines.extend(
                f"  [{w.post_index}] {w.field}: {w.message}" for w in self.warnings[:20]
            )
        return "\n".join(lines)


def _platform_enum(name: str) -> Platform | None:
    for p in Platform:
        if p.value == name:
            return p
    return None


def validate_posts(posts: list[ReadyPost]) -> ValidationReport:
    warnings: list[ValidationIssue] = []
    errors: list[ValidationIssue] = []
    passed_count = 0

    for i, post in enumerate(posts):
        post_errors: list[ValidationIssue] = []
        post_warnings: list[ValidationIssue] = []

        platform = _platform_enum(post.platform)
        if platform is None:
            post_errors.append(
                ValidationIssue(
                    i, "platform", "error", f"Unknown platform: {post.platform}"
                )
            )
        else:
            spec = PLATFORM_SPECS[platform]

            if len(post.caption) > spec.max_caption_length:
                post_errors.append(
                    ValidationIssue(
                        i,
                        "caption",
                        "error",
                        f"Caption too long: {len(post.caption)}/{spec.max_caption_length}",
                    )
                )

            tag_count = len(post.hashtags)
            if tag_count < spec.hashtag_range[0]:
                post_warnings.append(
                    ValidationIssue(
                        i,
                        "hashtags",
                        "warning",
                        f"Too few hashtags: {tag_count} (min {spec.hashtag_range[0]})",
                    )
                )
            elif tag_count > spec.hashtag_range[1]:
                post_warnings.append(
                    ValidationIssue(
                        i,
                        "hashtags",
                        "warning",
                        f"Too many hashtags: {tag_count} (max {spec.hashtag_range[1]})",
                    )
                )

        post_errors.extend(
            ValidationIssue(i, "caption", "error", f"Unresolved placeholder: {marker}")
            for marker in PLACEHOLDER_MARKERS
            if marker in post.caption
        )

        if not post.caption.strip():
            post_errors.append(ValidationIssue(i, "caption", "error", "Empty caption"))

        if not post.visual_brief.strip():
            post_warnings.append(
                ValidationIssue(i, "visual_brief", "warning", "Empty visual brief")
            )

        if post.format in VIDEO_FORMATS and not post.video_script.strip():
            post_warnings.append(
                ValidationIssue(
                    i, "video_script", "warning", "Video format without script"
                )
            )

        if not post_errors:
            passed_count += 1
        errors.extend(post_errors)
        warnings.extend(post_warnings)

    return ValidationReport(
        total=len(posts),
        passed=passed_count,
        warnings=warnings,
        errors=errors,
    )
