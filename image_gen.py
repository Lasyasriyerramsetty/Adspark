import requests
import urllib.parse
from config import HF_API_KEY

TONE_STYLES = {
    "playful":  "bright colorful illustration, fun and energetic",
    "premium":  "photorealistic, sleek and elegant, studio lighting",
    "eco":      "soft watercolor painting, natural earthy tones",
    "bold":     "high-contrast graphic design, strong geometric shapes",
    "minimal":  "clean minimalist photography, white background, soft shadows",
}


def generate_image(product: str, audience: str, tone: str, tagline: str, retries=3) -> bytes:
    """Generate image via Pollinations.ai (free, no key needed). Returns raw image bytes."""
    style = TONE_STYLES.get(tone.lower(), f"{tone} aesthetic")
    prompt = (
        f"Campaign hero image for {product}. Style: {style}. "
        f"Product presented heroically, evoking {tagline}. "
        f"Centered composition, cinematic framing. "
        f"No text, no logos, no people. Mood: resonates with {audience}."
    )
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=576&nologo=true&enhance=true"

    for attempt in range(retries):
        try:
            resp = requests.get(
                url,
                timeout=60,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            resp.raise_for_status()
            if len(resp.content) < 1000:
                raise RuntimeError("Response too small, likely not a valid image")
            return resp.content
        except Exception as e:
            if attempt == retries - 1:
                raise RuntimeError(f"Image generation failed: {e}")
            import time
            time.sleep(2 ** attempt)
