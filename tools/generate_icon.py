from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "aura.ico"
OUT.parent.mkdir(parents=True, exist_ok=True)

def render(size: int) -> Image.Image:
    scale = size / 512
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    def p(v): return int(round(v * scale))
    d.rounded_rectangle((p(0), p(0), p(512), p(512)), radius=p(112), fill="#0c0a12")
    # Ring with a small gap for a cleaner silhouette
    d.arc((p(82), p(82), p(430), p(430)), start=215, end=505, fill="#b76cff", width=p(18))
    d.arc((p(82), p(82), p(430), p(430)), start=25, end=210, fill="#ff3b91", width=p(18))
    # A monogram, drawn with thick rounded strokes
    d.line((p(143), p(365), p(244), p(142), p(268), p(142), p(369), p(365)),
           fill="#ff3b91", width=p(52), joint="curve")
    d.line((p(207), p(285), p(305), p(285)), fill="#f8f1fa", width=p(18))
    return im

image = render(256)
image.save(OUT, format="ICO", sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])
print(f"Created {OUT}")
