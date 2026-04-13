"""
Erstellt die T.S.-Badge-Icons für die PWA.
Einmalig lokal ausführen: python create_icons.py
Benötigt Pillow (in requirements.txt enthalten).
"""
import os
from PIL import Image, ImageDraw, ImageFont


def create_badge(size: int) -> Image.Image:
    """Zeichnet den T.S.-Badge: Deep Olive Quadrat + Orange Ring + weißer Text."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Deep Olive Hintergrund – volles Quadrat (iOS schneidet selbst ab)
    draw.rectangle([0, 0, size - 1, size - 1], fill="#2D362E")

    # Muted Orange Ring (innen, als Dekoration)
    ring = max(4, size // 20)
    pad = ring * 2
    draw.ellipse(
        [pad, pad, size - 1 - pad, size - 1 - pad],
        outline="#D97706",
        width=ring,
    )

    # T.S. Text (weiß, zentriert, größer)
    font_size = int(size * 0.42)
    font_paths = [
        "/Library/Fonts/Arial Bold.ttf",                                  # macOS
        "/Library/Fonts/Arial Black.ttf",                                  # macOS Fallback
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",   # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",           # Linux Fallback
    ]
    font = None
    for fp in font_paths:
        try:
            font = ImageFont.truetype(fp, font_size)
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default(size=font_size)

    bbox = draw.textbbox((0, 0), "T.S.", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (size - tw) // 2 - bbox[0]
    y = (size - th) // 2 - bbox[1]
    draw.text((x, y), "T.S.", fill="#FFFFFF", font=font)

    return img


def main():
    os.makedirs("docs", exist_ok=True)
    for size in [180, 192, 512]:
        icon = create_badge(size)
        path = f"docs/icon-{size}.png"
        icon.save(path, "PNG")
        print(f"✅ {path} erstellt ({size}×{size}px)")
    print("Icons fertig!")


if __name__ == "__main__":
    main()
