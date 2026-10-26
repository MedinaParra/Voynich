#!/usr/bin/env python3
"""Make a context-and-crop comparison with explicit modern annotations."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def render(source, metadata, output):
    meta = json.loads(metadata.read_text())
    if hashlib.sha256(source.read_bytes()).hexdigest() != meta["source_sha256"]:
        raise ValueError("Source image differs from frozen evidence")
    im = Image.open(source)
    if list(im.size) != meta["image_size"]:
        raise ValueError("Unexpected source dimensions")
    out = Image.new("RGB", (1120, 900), "#f5f7f8")
    d = ImageDraw.Draw(out)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 25)
    d.text((24, 18), "f73r: dos posiciones con lectura ZL «otaly»", font=b, fill="#152c3a")
    thumb = im.copy()
    thumb.thumbnail((565, 760))
    out.paste(thumb, (20, 76))
    scale = thumb.width / im.width
    for i, occurrence in enumerate(meta["occurrences"]):
        x0, y0, x1, y1 = occurrence["crop_pixels"]
        if not (0 <= x0 < x1 <= im.width and 0 <= y0 < y1 <= im.height):
            raise ValueError("Invalid crop")
        coords = (20 + x0 * scale, 76 + y0 * scale, 20 + x1 * scale, 76 + y1 * scale)
        d.rectangle(coords, outline="#007f91", width=3)
        d.text((coords[2] + 5, coords[1] - 12), occurrence["marker"], font=b, fill="#007f91")
        crop = im.crop(occurrence["crop_pixels"])
        crop.thumbnail((465, 300))
        if crop.width * 2 <= 465:
            crop = crop.resize((crop.width * 2, crop.height * 2))
        top = 110 + i * 340
        d.text((610, top - 30), f"{occurrence['marker']}: locus f73r.{occurrence['locus']}", font=f, fill="#152c3a")
        out.paste(crop, (610, top + 15))
    d.text((24, 840), "Cajas y letras A/B modernas. Recortes sin realce; no son cifras del original.", font=f, fill="#526672")
    output.parent.mkdir(parents=True, exist_ok=True)
    out.save(output, quality=88)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--metadata", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    render(a.source, a.metadata, a.output)
