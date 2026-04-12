"""
Erstellt die T.S.-Badge-Icons für die PWA.
Einmalig lokal ausführen: python create_icons.py
Benötigt Pillow (in requirements.txt enthalten).
"""
import os
from PIL import Image, ImageDraw, ImageFont


def create_badge(size: int) -> Image.Image:
    """Zeichnet den T.S.-Badge: Deep Olive Kreis + Orange Ring + weißer Text."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Deep Olive Hintergrundkreis
    draw.ellipse([0, 0, size - 1, size - 1], fill="#2D362E")

    # Muted Orange Ring (außen)
    ring = max(2, size // 30)
    draw.ellipse(
        [ring, ring, size - 1 - ring, size - 1 - ring],
        outline="#D97706",
        width=ring,
    )

    # T.S. Text (weiß, zentriert)
    font_size = size // 4
    font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    try:
        font = ImageFont.truetype(font_path, font_size)
    except OSError:
        # Fallback: Standard-Font
        font = ImageFont.load_default()

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
