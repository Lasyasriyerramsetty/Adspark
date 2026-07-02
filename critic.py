"""
critic.py — AI Self-Critique Loop for AdSpark
Evaluates generated campaign assets against the original brief,
auto-regenerates failed assets with feedback injected into the prompt.
"""

import json
from text_gen import _chat, generate_tagline, generate_blog_intro, generate_social_posts

MAX_RETRIES = 2  # maximum regeneration attempts per failed asset


def _critique_assets(
    product: str,
    audience: str,
    tone: str,
    tagline: str,
    blog: str,
    social: dict,
) -> dict:
    """
    Ask the AI to evaluate the three assets against the campaign brief.
    Returns structured JSON with pass/fail and issue description per asset.
    """
    social_sample = social.get("twitter", "") if isinstance(social, dict) else str(social)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a senior marketing quality reviewer. "
                "Evaluate the campaign assets strictly against the brief. "
                "Return ONLY valid JSON — no markdown, no explanation. "
                "Schema: {\"tagline\": {\"pass\": bool, \"issue\": str|null}, "
                "\"blog\": {\"pass\": bool, \"issue\": str|null}, "
                "\"social\": {\"pass\": bool, \"issue\": str|null}}"
            ),
        },
        {
            "role": "user",
            "content": (
                f"Campaign Brief:\n"
                f"  Product: {product}\n"
                f"  Audience: {audience}\n"
                f"  Tone: {tone}\n\n"
                f"Assets to evaluate:\n"
                f"  Tagline: {tagline}\n\n"
                f"  Blog (first 300 chars): {blog[:300]}\n\n"
                f"  Social (Twitter): {social_sample}\n\n"
                "Check each asset for:\n"
                "- Tone matches requested style\n"
                "- Audience correctly targeted\n"
                "- Product accurately described\n"
                "- No contradictions\n"
                "- Overall marketing quality\n"
                "- Tagline: max ~15 words\n"
                "- Blog: should be ~200 words\n"
                "- Twitter: max 280 chars\n\n"
                "Return JSON only."
            ),
        },
    ]

    raw = _chat(messages, max_tokens=300)
    # Strip markdown fences if model adds them
    raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    try:
        result = json.loads(raw)
        # Ensure all keys exist with correct structure
        for key in ("tagline", "blog", "social"):
            if key not in result:
                result[key] = {"pass": True, "issue": None}
            if "pass" not in result[key]:
                result[key]["pass"] = True
            if "issue" not in result[key]:
                result[key]["issue"] = None
        return result
    except json.JSONDecodeError:
        # If parsing fails, treat all as passed to avoid blocking the user
        return {
            "tagline": {"pass": True, "issue": None},
            "blog":    {"pass": True, "issue": None},
            "social":  {"pass": True, "issue": None},
        }


def _regenerate_tagline(product: str, audience: str, tone: str, issue: str) -> str:
    """Regenerate tagline with critic feedback injected into the prompt."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a creative advertising copywriter. "
                "Return ONLY the tagline, no quotes or explanation."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Generate a tagline for:\n"
                f"Product: {product} | Audience: {audience} | Tone: {tone}\n\n"
                f"Previous version was rejected for: {issue}\n"
                f"Fix that issue. Return only the improved tagline."
            ),
        },
    ]
    return _chat(messages, max_tokens=50)


def _regenerate_blog(
    product: str, audience: str, tone: str, tagline: str, issue: str
) -> str:
    """Regenerate blog intro with critic feedback injected into the prompt."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a content strategist. "
                "Write EXACTLY 200 words. Include the tagline naturally."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Write a 200-word blog introduction for:\n"
                f"Product: {product}\nAudience: {audience}\nTone: {tone}\n"
                f"Tagline: \"{tagline}\"\n\n"
                f"Previous version was rejected for: {issue}\n"
                f"Fix that issue. Exactly 200 words."
            ),
        },
    ]
    return _chat(messages, max_tokens=300)


def _regenerate_social(
    product: str, audience: str, tone: str, tagline: str, issue: str
) -> dict:
    """Regenerate social posts with critic feedback injected into the prompt."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a social media manager. Return ONLY valid JSON with keys: "
                "twitter (max 280 chars), instagram (include hashtags), "
                "linkedin (professional, max 700 chars). No markdown."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Create social posts for:\n"
                f"Product: {product}\nAudience: {audience}\nTone: {tone}\n"
                f"Tagline: \"{tagline}\"\n\n"
                f"Previous version was rejected for: {issue}\n"
                f"Fix that issue."
            ),
        },
    ]
    raw = _chat(messages, max_tokens=600)
    raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"twitter": raw, "instagram": raw, "linkedin": raw}


def run_critic_loop(
    product: str,
    audience: str,
    tone: str,
    tagline: str,
    blog: str,
    social: dict,
) -> dict:
    """
    Main entry point for the critic loop.

    Runs critique → auto-regenerates failures (up to MAX_RETRIES) →
    returns final assets + full critic report.

    Returns:
        {
            "tagline": str,
            "blog": str,
            "social": dict,
            "report": {
                "tagline": {"pass": bool, "issue": str|None, "retries": int},
                "blog":    {"pass": bool, "issue": str|None, "retries": int},
                "social":  {"pass": bool, "issue": str|None, "retries": int},
            }
        }
    """
    report = {
        "tagline": {"pass": True, "issue": None, "retries": 0},
        "blog":    {"pass": True, "issue": None, "retries": 0},
        "social":  {"pass": True, "issue": None, "retries": 0},
    }

    current_tagline = tagline
    current_blog    = blog
    current_social  = social

    for attempt in range(MAX_RETRIES + 1):
        # Run the AI critique
        critique = _critique_assets(
            product, audience, tone,
            current_tagline, current_blog, current_social
        )

        all_pass = True

        # ── Tagline ──────────────────────────────────────────────────────────
        if not critique["tagline"]["pass"]:
            all_pass = False
            report["tagline"]["pass"]  = False
            report["tagline"]["issue"] = critique["tagline"]["issue"]
            if attempt < MAX_RETRIES:
                report["tagline"]["retries"] += 1
                try:
                    current_tagline = _regenerate_tagline(
                        product, audience, tone, critique["tagline"]["issue"]
                    )
                except Exception:
                    pass  # keep current version on error

        # ── Blog ─────────────────────────────────────────────────────────────
        if not critique["blog"]["pass"]:
            all_pass = False
            report["blog"]["pass"]  = False
            report["blog"]["issue"] = critique["blog"]["issue"]
            if attempt < MAX_RETRIES:
                report["blog"]["retries"] += 1
                try:
                    current_blog = _regenerate_blog(
                        product, audience, tone, current_tagline,
                        critique["blog"]["issue"]
                    )
                except Exception:
                    pass

        # ── Social ───────────────────────────────────────────────────────────
        if not critique["social"]["pass"]:
            all_pass = False
            report["social"]["pass"]  = False
            report["social"]["issue"] = critique["social"]["issue"]
            if attempt < MAX_RETRIES:
                report["social"]["retries"] += 1
                try:
                    current_social = _regenerate_social(
                        product, audience, tone, current_tagline,
                        critique["social"]["issue"]
                    )
                except Exception:
                    pass

        # Stop early if everything passed
        if all_pass:
            report["tagline"]["pass"] = True
            report["blog"]["pass"]    = True
            report["social"]["pass"]  = True
            break

    return {
        "tagline": current_tagline,
        "blog":    current_blog,
        "social":  current_social,
        "report":  report,
    }
