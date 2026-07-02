"""
voiceover.py — Script Adapter + TTS Voiceover for AdSpark
Converts blog intro into a narration-ready script,
then generates an MP3 voiceover using gTTS (free, no API key).
"""

import io
import re
from gtts import gTTS
from text_gen import _chat


def adapt_script(blog: str, product: str, tone: str) -> str:
    """
    Convert a blog introduction into a narration-ready voiceover script.

    Rules applied:
    - Max 15 words per sentence
    - Commas added for natural breathing pauses
    - Ellipses added for dramatic pauses
    - Visual references removed (e.g. "as you can see", "shown below")
    - Conversational, natural narration style
    - Original meaning preserved
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional voiceover scriptwriter. "
                "Convert the blog text into a narration-ready script following these rules:\n"
                "1. Maximum 15 words per sentence — split longer ones\n"
                "2. Add commas where a speaker would naturally pause to breathe\n"
                "3. Add ellipses (...) before dramatic or impactful phrases\n"
                "4. Remove all visual references (e.g. 'as you can see', 'shown here', 'below')\n"
                "5. Keep language natural and conversational — suitable for spoken audio\n"
                "6. Preserve the original meaning and key messages\n"
                "7. Output ONLY the narration script — no headings, no labels, no explanation"
            ),
        },
        {
            "role": "user",
            "content": (
                f"Convert this blog intro into a voiceover script:\n\n"
                f"{blog}\n\n"
                f"Product: {product}\nTone: {tone}\n\n"
                f"Return only the narration script."
            ),
        },
    ]
    return _chat(messages, max_tokens=400)


def generate_voiceover(script: str, lang: str = "en") -> bytes:
    """
    Generate an MP3 voiceover from the narration script using gTTS.
    Returns raw MP3 bytes ready for download or audio player.

    Args:
        script: Narration-ready text
        lang:   Language code (default 'en')

    Returns:
        MP3 bytes
    """
    # Clean up any markdown or special chars that would sound odd when spoken
    clean = re.sub(r"[*_`#>]", "", script)          # remove markdown symbols
    clean = re.sub(r"\n{2,}", ". ", clean)           # double newlines → sentence break
    clean = re.sub(r"\n", ", ", clean)               # single newlines → pause
    clean = clean.strip()

    tts = gTTS(text=clean, lang=lang, slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


def generate_voiceover_package(blog: str, product: str, tone: str) -> dict:
    """
    Full pipeline: blog → narration script → MP3 bytes.

    Returns:
        {
            "script": str,      # narration-ready script
            "mp3":    bytes,    # MP3 audio bytes
            "error":  str|None  # error message if TTS failed
        }
    """
    # Step 1: Adapt blog to narration script
    try:
        script = adapt_script(blog, product, tone)
    except Exception as e:
        return {"script": blog, "mp3": None, "error": f"Script adaptation failed: {e}"}

    # Step 2: Generate MP3 from script
    try:
        mp3_bytes = generate_voiceover(script)
    except Exception as e:
        return {"script": script, "mp3": None, "error": f"TTS generation failed: {e}"}

    return {"script": script, "mp3": mp3_bytes, "error": None}
