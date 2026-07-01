import json
import time
from groq import Groq
from openai import OpenAI
from config import (
    GROQ_API_KEY, GROQ_MODEL,
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL,
    OPENROUTER_MODEL, OPENROUTER_FALLBACK_MODELS
)

groq_client = Groq(api_key=GROQ_API_KEY)
or_client   = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)


def _chat(messages, retries=2, **kwargs):
    """Try Groq first (fast & free), fall back to OpenRouter if it fails."""
    # 1. Try Groq
    if GROQ_API_KEY and GROQ_API_KEY != "YOUR_GROQ_API_KEY_HERE":
        for attempt in range(retries):
            try:
                resp = groq_client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=messages,
                    **kwargs
                )
                return resp.choices[0].message.content.strip()
            except Exception as e:
                err = str(e)
                if "401" in err or "invalid_api_key" in err.lower():
                    break  # bad key, skip Groq entirely
                if attempt < retries - 1:
                    time.sleep(1)

    # 2. Fall back to OpenRouter
    for model in [OPENROUTER_MODEL] + OPENROUTER_FALLBACK_MODELS:
        for attempt in range(retries):
            try:
                resp = or_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs
                )
                return resp.choices[0].message.content.strip()
            except Exception as e:
                err = str(e)
                if "404" in err or "No endpoints found" in err:
                    break  # dead model, try next
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)

    raise RuntimeError("All models failed. Add a free Groq key at console.groq.com for fast responses.")


def generate_tagline(product: str, audience: str, tone: str) -> str:
    """Generate a campaign tagline using few-shot prompting. Max 10 words."""
    messages = [
        {"role": "system", "content": "You are a creative advertising copywriter. Return ONLY the tagline, no quotes or explanation."},
        # Few-shot examples
        {"role": "user", "content": "Product: EcoBottle | Audience: eco-conscious millennials | Tone: eco"},
        {"role": "assistant", "content": "Sip sustainably. Protect the planet, one bottle at a time."},
        {"role": "user", "content": "Product: LuxWatch | Audience: high-net-worth professionals | Tone: premium"},
        {"role": "assistant", "content": "Time, perfected. For those who accept nothing less."},
        {"role": "user", "content": "Product: SnapToys | Audience: children aged 5-10 | Tone: playful"},
        {"role": "assistant", "content": "Snap, build, imagine — every day is an adventure!"},
        # Actual request
        {"role": "user", "content": f"Product: {product} | Audience: {audience} | Tone: {tone}"},
    ]
    return _chat(messages, max_tokens=50)


def generate_blog_intro(product: str, audience: str, tone: str, tagline: str) -> str:
    """Generate a 200-word blog introduction that includes the tagline."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a content strategist writing compelling blog introductions. "
                "Write EXACTLY 200 words. Include the provided tagline naturally within the text."
            )
        },
        {
            "role": "user",
            "content": (
                f"Write a 200-word blog introduction for:\n"
                f"Product: {product}\n"
                f"Target Audience: {audience}\n"
                f"Brand Tone: {tone}\n"
                f"Tagline to include: \"{tagline}\"\n\n"
                f"Exactly 200 words. Match the {tone} tone throughout."
            )
        }
    ]
    return _chat(messages, max_tokens=300)  # ~200 words = ~270 tokens


def generate_social_posts(product: str, audience: str, tone: str, tagline: str) -> dict:
    """Generate social posts for Twitter, Instagram, LinkedIn. Returns a parsed dict."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a social media manager. Return ONLY valid JSON with keys: "
                "twitter (max 280 chars), instagram (max 2200 chars, include hashtags), "
                "linkedin (max 700 chars, professional). No markdown, no explanation."
            )
        },
        {
            "role": "user",
            "content": (
                f"Create social media posts for:\n"
                f"Product: {product}\n"
                f"Target Audience: {audience}\n"
                f"Brand Tone: {tone}\n"
                f"Tagline: \"{tagline}\""
            )
        }
    ]
    raw = _chat(messages, max_tokens=600)
    # Strip markdown code fences if present
    raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: return raw text under each key
        return {"twitter": raw, "instagram": raw, "linkedin": raw}
