import io
from PIL import Image


def generate_video(image_bytes: bytes, product: str) -> bytes:
    """
    Create an animated GIF from the hero image using a slow Ken Burns zoom effect.
    Returns raw GIF bytes. No external API — runs fully locally with Pillow.
    """
    source = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    w, h = source.size

    frames = []
    num_frames = 20          # 20 frames × 80 ms ≈ 1.6-second loop
    max_crop = 0.10          # zoom in up to 10 % of the shortest edge

    for i in range(num_frames):
        t = i / (num_frames - 1)          # 0.0 → 1.0
        # Compute crop border that grows from 0 to max_crop
        border_x = int(w * max_crop * t)
        border_y = int(h * max_crop * t)

        left   = border_x
        top    = border_y
        right  = w - border_x
        bottom = h - border_y

        cropped = source.crop((left, top, right, bottom)).resize((w, h), Image.LANCZOS)
        frames.append(cropped.convert("P", palette=Image.ADAPTIVE, colors=256))

    buf = io.BytesIO()
    frames[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        loop=0,          # loop forever
        duration=80,     # ms per frame
        optimize=True,
    )
    return buf.getvalue()
