from pathlib import Path

from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "chaimaa.jpeg"
OUTPUT_DIR = ROOT / "assets"
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT = OUTPUT_DIR / "chaimaa-share.png"


def make_cover_image(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    resized = img.resize((int(src_w * scale), int(src_h * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def main() -> None:
    img = Image.open(SOURCE).convert("RGBA")

    canvas_size = (1200, 630)
    bg = make_cover_image(img, canvas_size).filter(ImageFilter.GaussianBlur(18))
    bg = ImageEnhance.Brightness(bg).enhance(0.78)
    bg = ImageEnhance.Contrast(bg).enhance(0.95)

    canvas = bg.copy()
    overlay = Image.new("RGBA", canvas_size, (22, 0, 0, 70))
    canvas = Image.alpha_composite(canvas, overlay)

    # Add a soft vignette to keep the focus centered.
    vignette = Image.new("L", canvas_size, 0)
    vignette_draw = ImageDraw.Draw(vignette)
    vignette_draw.ellipse((-80, -80, 1280, 710), fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(90))
    dark = Image.new("RGBA", canvas_size, (0, 0, 0, 90))
    canvas = Image.composite(canvas, Image.alpha_composite(canvas, dark), vignette)

    # Center the original invitation image, cropped to a pleasant portrait card.
    card_h = 560
    card_w = int(card_h * img.width / img.height)
    card = ImageOps.contain(img, (card_w, card_h), method=Image.Resampling.LANCZOS)

    # Shadow behind the card.
    shadow = Image.new("RGBA", (card.width + 40, card.height + 40), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((16, 16, shadow.width - 16, shadow.height - 16), radius=34, fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))

    x = (canvas_size[0] - shadow.width) // 2
    y = (canvas_size[1] - shadow.height) // 2
    canvas.alpha_composite(shadow, (x, y))

    card_bg = Image.new("RGBA", (card.width + 28, card.height + 28), (253, 246, 240, 255))
    card_mask = Image.new("L", card_bg.size, 0)
    ImageDraw.Draw(card_mask).rounded_rectangle((0, 0, card_bg.width, card_bg.height), radius=32, fill=255)
    card_bg.putalpha(card_mask)
    card_bg.alpha_composite(card, (14, 14))

    canvas.alpha_composite(card_bg, ((canvas_size[0] - card_bg.width) // 2, (canvas_size[1] - card_bg.height) // 2))

    canvas.convert("RGB").save(OUTPUT, quality=92, optimize=True)
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
