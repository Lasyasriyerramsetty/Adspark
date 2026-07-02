"""
adapter.py — Multi-Channel Adaptation for AdSpark
Regenerates tagline, blog, and social posts for a specific platform channel.
Hero image and video are NOT affected — only text assets are adapted.
"""

import json
from text_gen import _chat

# Channel definitions — tone instructions injected into prompts
CHANNEL_PROFILES = {
    "B2B LinkedIn": {
        "label":       "B2B LinkedIn",
        "tone":        "professional, business-focused, corporate, data-driven",
        "style":       "formal tone, no slang, minimal emoji, highlight ROI and business value",
        "tagline_len": "under 12 words, professional",
        "blog_style":  "executive summary style, business benefits first, formal language",
        "social_note": "LinkedIn post: professional, 500-700 chars, 1-2 relevant hashtags, no casual language",
    },
    "Gen-Z TikTok": {
        "label":       "Gen-Z TikTok",
        "tone":        "energetic, trendy, fun, Gen-Z slang",
        "style":       "short punchy sentences, lots of emojis, viral hooks, FOMO-driven",
        "tagline_len": "under 8 words, catchy and memeable",
        "blog_style":  "casual conversational style, short sentences, trending references, relatable",
        "social_note": "TikTok caption: max 150 chars, 3-5 trending hashtags, lots of emojis, Gen-Z voice",
    },
    "Parents Facebook": {
        "label":       "Parents Facebook",
        "tone":        "warm, friendly, family-oriented, trust-building",
        "style":       "conversational, reassuring, focus on safety/family benefits, moderate emoji",
        "tagline_len": "under 12 words, warm and relatable",
        "blog_style":  "friendly storytelling style, parent-focused benefits, warm and trustworthy",
        "social_note": "Facebook post: 150-300 chars, family-friendly, 2-3 hashtags, warm emoji",
    },
}


def adapt_tagline(product: str, audience: str, channel: str) -> str:
    """Regenerate tagline adapted for the specified channel."""
    profile = CHANNEL_PROFILES[channel]
    messages = [
        {
            "role": "system",
            "content": (
                "You are a creative advertising copywriter. "
                "Return ONLY the tagline — no quotes, no explanation."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Write a tagline for:\n"
                f"Product: {product}\n"
                f"Audience: {audience}\n"
                f"Channel: {profile['label']}\n"
                f"Tone: {profile['tone']}\n"
                f"Style rules: {profile['style']}\n"
                f"Length: {profile['tagline_len']}\n\n"
                f"Return ONLY the tagline."
            ),
        },
    ]
    return _chat(messages, max_tokens=50)


def adapt_blog(product: str, audience: str, channel: str, tagline: str) -> str:
    """Regenerate blog intro adapted for the specified channel."""
    profile = CHANNEL_PROFILES[channel]
    messages = [
        {
            "role": "system",
            "content": (
                f"You are a content writer specialising in {profile['label']} content. "
                f"Write approximately 200 words. Include the tagline naturally."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Write a ~200-word blog introduction for:\n"
                f"Product: {product}\n"
                f"Audience: {audience}\n"
                f"Channel: {profile['label']}\n"
                f"Tone: {profile['tone']}\n"
                f"Writing style: {profile['blog_style']}\n"
                f"Tagline to include: \"{tagline}\"\n\n"
                f"Match the channel style throughout."
            ),
        },
    ]
    return _chat(messages, max_tokens=300)


def adapt_social(product: str, audience: str, channel: str, tagline: str) -> dict:
    """Regenerate social posts adapted for the specified channel."""
    profile = CHANNEL_PROFILES[channel]
    messages = [
        {
            "role": "system",
            "content": (
                "You are a social media strategist. "
                "Return ONLY valid JSON with keys: twitter, instagram, linkedin. "
                "No markdown, no explanation."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Create social media posts for:\n"
                f"Product: {product}\n"
                f"Audience: {audience}\n"
                f"Channel: {profile['label']}\n"
                f"Tone: {profile['tone']}\n"
                f"Style: {profile['style']}\n"
                f"Tagline: \"{tagline}\"\n\n"
                f"Special note: {profile['social_note']}\n\n"
                f"Return JSON only."
            ),
        },
    ]
    raw = _chat(messages, max_tokens=600)
    raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"twitter": raw, "instagram": raw, "linkedin": raw}


def adapt_for_channel(product: str, audience: str, channel: str) -> dict:
    """
    Full adaptation pipeline for a given channel.
    Generates adapted tagline first, then blog + social use it.

    Returns:
        {
            "channel":  str,
            "tagline":  str,
            "blog":     str,
            "social":   dict,
            "error":    str|None
        }
    """
    if channel not in CHANNEL_PROFILES:
        return {
            "channel": channel,
            "tagline": "",
            "blog":    "",
            "social":  {},
            "error":   f"Unknown channel: {channel}. Choose from: {list(CHANNEL_PROFILES.keys())}",
        }

    try:
        # Tagline first — blog and social depend on it
        tagline = adapt_tagline(product, audience, channel)

        # Blog and social in parallel
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=2) as executor:
            blog_f   = executor.submit(adapt_blog,   product, audience, channel, tagline)
            social_f = executor.submit(adapt_social, product, audience, channel, tagline)

        blog   = blog_f.result()
        social = social_f.result()

        return {
            "channel": channel,
            "tagline": tagline,
            "blog":    blog,
            "social":  social,
            "error":   None,
        }

    except Exception as e:
        return {
            "channel": channel,
            "tagline": "",
            "blog":    "",
            "social":  {},
            "error":   str(e),
        }
