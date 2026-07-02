# ⚡ AdSpark — Content Engine Pro

> *Ignite your campaign in seconds.*

AdSpark is an AI-powered campaign engine that transforms a simple product brief into a complete marketing launch — tagline, blog introduction, social media posts, hero image, animated preview, voiceover, and multi-channel adaptation. No agency. No waiting. Just spark.

---

## ✨ Features

### Core
- 🏷️ **Tagline Generator** — punchy, on-brand campaign taglines via few-shot prompting
- 📰 **Blog Introduction** — 200-word blog intro matched to your brand tone
- 📱 **Social Media Posts** — ready-to-post copy for Twitter, Instagram, and LinkedIn
- 🖼️ **Hero Image** — AI-generated campaign visual via Pollinations.ai
- 🎬 **Animated Preview** — GIF animation of your hero image for social use

### Pro
- 🔍 **AI Critic Loop** — auto-evaluates every asset against your brief, regenerates failures (up to 2 retries), displays full pass/fail report
- 🎙️ **Voiceover Generation** — converts blog intro into narration-ready script, generates downloadable MP3 via gTTS
- 📡 **Channel Adaptation** — one-click re-adaptation for B2B LinkedIn, Gen-Z TikTok, or Parents Facebook

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/Lasyasriyerramsetty/Adspark.git
cd Adspark
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your API keys

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
HF_API_KEY=your_hf_key_here
```

| Key | Where to get it | Required |
|-----|----------------|----------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) — free | ✅ Yes (fast text gen) |
| `OPENROUTER_API_KEY` | [openrouter.ai](https://openrouter.ai) — free tier | Fallback |
| `HF_API_KEY` | [huggingface.co](https://huggingface.co) — free | Optional |

### 4. Run the app

```bash
python -m streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| Text AI | Groq (LLaMA 3.1 8B) + OpenRouter fallback |
| Image AI | Pollinations.ai |
| Animation | Pillow (GIF generation) |
| Voiceover | gTTS (Google Text-to-Speech) |
| Critic | LLM-based JSON evaluation loop |

---

## 📁 Project Structure

```
Adspark/
├── app.py            # Streamlit UI — all panels
├── text_gen.py       # Tagline, blog, social post generation
├── image_gen.py      # Hero image (Pollinations.ai)
├── video_gen.py      # Animated GIF preview
├── critic.py         # AI self-critique loop with auto-regeneration
├── voiceover.py      # Script adapter + MP3 generation (gTTS)
├── adapter.py        # Multi-channel content adaptation
├── config.py         # API keys and model config
├── requirements.txt  # Python dependencies
└── .env              # Your API keys (local only, not committed)
```

---

## 🔍 AI Critic Loop

Every generated asset is automatically evaluated against your campaign brief before display. If an asset fails quality checks, it is regenerated with the critic's feedback injected into the prompt — up to 2 retries. A full pass/fail report is shown in the UI.

## 🎙️ Voiceover

The blog introduction is adapted into a narration-ready script (breathing pauses, dramatic ellipses, max 15 words per sentence, no visual references), then converted to MP3 using gTTS. Play in-browser or download.

## 📡 Channel Adaptation

Select a channel from the sidebar dropdown to regenerate tagline, blog, and social posts in the platform's native style. Hero image and GIF are never regenerated.

| Channel | Style |
|---------|-------|
| B2B LinkedIn | Professional, corporate, data-driven, minimal emoji |
| Gen-Z TikTok | Energetic, trendy, Gen-Z slang, lots of emojis |
| Parents Facebook | Warm, friendly, family-oriented, trust-building |

---

## ⚡ Powered by AdSpark
