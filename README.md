# ⚡ AdSpark

> *Ignite your campaign in seconds.*

AdSpark is an AI-powered campaign engine that transforms a simple product brief into a complete marketing launch — tagline, blog introduction, social media posts, hero image, and animated preview. No agency. No waiting. Just spark.

---

## ✨ Features

- 🏷️ **Tagline Generator** — punchy, on-brand campaign taglines via few-shot prompting
- 📰 **Blog Introduction** — 200-word blog intro matched to your brand tone
- 📱 **Social Media Posts** — ready-to-post copy for Twitter, Instagram, and LinkedIn
- 🖼️ **Hero Image** — AI-generated campaign visual via Pollinations.ai
- 🎬 **Animated Preview** — GIF animation of your hero image for social use

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add your API keys in `config.py`

| Key | Where to get it | Required |
|-----|----------------|----------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) — free | ✅ Yes (for fast text gen) |
| `OPENROUTER_API_KEY` | [openrouter.ai](https://openrouter.ai) — free tier | Fallback |
| `HF_API_KEY` | [huggingface.co](https://huggingface.co) — free | Optional |

### 3. Run the app

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

---

## 📁 Project Structure

```
image gen/
├── app.py          # Streamlit UI
├── text_gen.py     # Tagline, blog, social post generation
├── image_gen.py    # Hero image generation (Pollinations.ai)
├── video_gen.py    # Animated GIF preview
├── config.py       # API keys and model config
└── requirements.txt
```

---

## ⚡ Powered by AdSpark
"# Adspark" 
