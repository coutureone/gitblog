#!/usr/bin/env python3
"""Optimize repository-hosted blog images.

This is meant for the current writing flow:

1. Write in Typora.
2. PicGo uploads images into this repository's img/ directory.
3. GitHub Actions runs this script and commits optimized images back.

It only affects images stored in img/. Images pasted directly into GitHub
Issues as github.com/user-attachments URLs cannot be optimized here.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = ROOT / "img"
PHOTO_EXTS = {".jpg", ".jpeg"}
PNG_EXTS = {".png"}
DEFAULT_PHOTO_MAX_SIDE = 2048
DEFAULT_PNG_MAX_SIDE = 2560
DEFAULT_JPEG_QUALITY = 82


def resize_to_max_side(image: Image.Image, max_side: int) -> Image.Image:
    width, height = image.size
    longest = max(width, height)
    if longest <= max_side:
        return image

    ratio = max_side / longest
    size = (round(width * ratio), round(height * ratio))
    return image.resize(size, Image.Resampling.LANCZOS)


def save_jpeg(image: Image.Image, out: Path, quality: int) -> None:
    image = ImageOps.exif_transpose(image)
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")
    image.save(out, "JPEG", quality=quality, optimize=True, progressive=True)


def save_png(image: Image.Image, out: Path) -> None:
    image.save(out, "PNG", optimize=True)


def optimize_image(
    path: Path,
    photo_max_side: int,
    png_max_side: int,
    jpeg_quality: int,
    dry_run: bool,
) -> tuple[int, int, str]:
    before = path.stat().st_size
    ext = path.suffix.lower()
    if ext not in PHOTO_EXTS | PNG_EXTS:
        return before, before, "skipped"

    with Image.open(path) as image:
        if ext in PHOTO_EXTS:
            original_max = max(image.size)
            image = resize_to_max_side(image, photo_max_side)
            action = f"jpeg q{jpeg_quality}"
            if original_max > photo_max_side:
                action += f" max{photo_max_side}"
            saver = lambda out: save_jpeg(image, out, jpeg_quality)
        else:
            original_max = max(image.size)
            image = resize_to_max_side(image, png_max_side)
            action = "png optimize"
            if original_max > png_max_side:
                action += f" max{png_max_side}"
            saver = lambda out: save_png(image, out)

        if dry_run:
            return before, before, action

        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        try:
            saver(temp_path)
            after = temp_path.stat().st_size
            if after < before:
                temp_path.replace(path)
                return before, after, action
            return before, before, f"{action} kept-original"
        finally:
            temp_path.unlink(missing_ok=True)


def iter_images() -> list[Path]:
    return sorted(
        path
        for path in IMG_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in PHOTO_EXTS | PNG_EXTS
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--photo-max-side", type=int, default=DEFAULT_PHOTO_MAX_SIDE)
    parser.add_argument("--png-max-side", type=int, default=DEFAULT_PNG_MAX_SIDE)
    parser.add_argument("--jpeg-quality", type=int, default=DEFAULT_JPEG_QUALITY)
    args = parser.parse_args()

    rows = [
        (
            *optimize_image(
                path,
                args.photo_max_side,
                args.png_max_side,
                args.jpeg_quality,
                args.dry_run,
            ),
            path.relative_to(ROOT),
        )
        for path in iter_images()
    ]

    before_total = sum(row[0] for row in rows)
    after_total = sum(row[1] for row in rows)
    saved = before_total - after_total
    mode = "dry-run " if args.dry_run else ""
    print(f"{mode}processed={len(rows)} before={before_total} after={after_total} saved={saved}")

    for before, after, action, relpath in sorted(rows, key=lambda row: row[0] - row[1], reverse=True)[:30]:
        print(f"{before - after:>9} {before:>9}->{after:<9} {action:<24} {relpath}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
