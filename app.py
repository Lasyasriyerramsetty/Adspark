"""
app.py — AdSpark: AI-Powered Campaign Engine
Generates a complete marketing campaign from a single product brief.

New in Content Engine Pro:
  - AI Critic Panel: auto-evaluates and regenerates failing assets
  - Voiceover Panel: narration script + downloadable MP3
  - Channel Adaptation Panel: B2B LinkedIn / Gen-Z TikTok / Parents Facebook
"""

import streamlit as st
from concurrent.futures import ThreadPoolExecutor

# ── Existing modules ──────────────────────────────────────────────────────────
from text_gen import generate_tagline, generate_blog_intro, generate_social_posts
from image_gen import generate_image
from video_gen import generate_video

# ── New Pro modules ───────────────────────────────────────────────────────────
from critic    import run_critic_loop
from voiceover import generate_voiceover_package
from adapter   import adapt_for_channel, CHANNEL_PROFILES

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="AdSpark", page_icon="⚡", layout="wide")
st.title("⚡ AdSpark")
st.caption(
    "Ignite your campaign in seconds. "
    "Transform a product brief into a complete marketing launch — "
    "tagline, blog, social posts, hero image, and animated preview."
)

# ── Sidebar inputs ────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Product Brief")
    product  = st.text_input("Product Name",    placeholder="e.g. EcoBottle Pro")
    audience = st.text_input("Target Audience", placeholder="e.g. eco-conscious millennials")
    tone     = st.selectbox("Brand Tone", ["playful", "premium", "eco", "bold", "minimal"])

    st.divider()

    # Pro feature toggles
    st.subheader("⚙️ Pro Features")
    enable_critic   = st.toggle("🔍 AI Critic",         value=True,  help="Auto-evaluate and fix failing assets")
    enable_voice    = st.toggle("🎙️ Voiceover",         value=True,  help="Generate MP3 narration from blog")
    enable_channels = st.toggle("📡 Channel Adaptation", value=True,  help="Adapt content per platform")

    st.divider()
    generate = st.button("✨ Generate Campaign", type="primary", use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
left, right = st.columns([1, 1], gap="large")

if generate:
    # Input validation
    if not product or not audience:
        st.warning("Please fill in both Product Name and Target Audience.")
        st.stop()

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 1 — CAMPAIGN COPY (existing feature, unchanged)
    # ═══════════════════════════════════════════════════════════════════════
    with left:
        st.subheader("📝 Campaign Copy")

        # Tagline — generated first as others depend on it
        with st.spinner("Generating tagline…"):
            try:
                tagline = generate_tagline(product, audience, tone)
            except Exception as e:
                st.error(f"Tagline failed: {e}")
                st.stop()

        # Blog + social posts in parallel (both need tagline)
        with st.spinner("Writing blog & social posts…"):
            with ThreadPoolExecutor(max_workers=2) as executor:
                blog_f  = executor.submit(generate_blog_intro,  product, audience, tone, tagline)
                posts_f = executor.submit(generate_social_posts, product, audience, tone, tagline)

            try:
                blog = blog_f.result()
            except Exception as e:
                blog = f"⚠️ Blog generation failed: {e}"

            try:
                posts = posts_f.result()
            except Exception as e:
                posts = {"twitter": f"Error: {e}", "instagram": f"Error: {e}", "linkedin": f"Error: {e}"}

        # ═══════════════════════════════════════════════════════════════════
        # SECTION 2 — AI CRITIC PANEL (new Pro feature)
        # ═══════════════════════════════════════════════════════════════════
        if enable_critic:
            with st.spinner("🔍 AI Critic evaluating assets…"):
                try:
                    critic_result = run_critic_loop(
                        product, audience, tone, tagline, blog, posts
                    )
                    # Replace assets with critic-approved versions
                    tagline = critic_result["tagline"]
                    blog    = critic_result["blog"]
                    posts   = critic_result["social"]
                    report  = critic_result["report"]
                except Exception as e:
                    report = None
                    st.warning(f"⚠️ Critic loop failed (showing original): {e}")

            # Display Critic Report
            if report:
                with st.expander("🔍 AI Critic Report", expanded=False):
                    st.caption("Assets were automatically evaluated against your campaign brief.")

                    for asset_name, label in [("tagline", "🏷️ Tagline"), ("blog", "📰 Blog"), ("social", "📱 Social")]:
                        r = report[asset_name]
                        col_status, col_detail = st.columns([1, 3])
                        with col_status:
                            if r["pass"]:
                                st.success(f"{label}: ✅ Pass")
                            else:
                                st.error(f"{label}: ❌ Fail")
                        with col_detail:
                            if r["issue"]:
                                st.caption(f"Issue: {r['issue']}")
                            if r["retries"] > 0:
                                st.caption(f"🔄 Regenerated {r['retries']}x")

                    # Overall verdict
                    all_passed = all(report[k]["pass"] for k in ("tagline", "blog", "social"))
                    if all_passed:
                        st.success("✅ All assets passed quality review.")
                    else:
                        st.warning("⚠️ Some assets still have issues after retries — showing best available version.")

        # Display final campaign copy
        st.markdown(f"### 🏷️ Tagline\n> *{tagline}*")
        st.divider()

        st.markdown("### 📰 Blog Introduction")
        st.write(blog)
        st.divider()

        st.markdown("### 📱 Social Media Posts")
        tab_tw, tab_ig, tab_li = st.tabs(["𝕏 Twitter", "📸 Instagram", "💼 LinkedIn"])
        with tab_tw:
            st.write(posts.get("twitter", ""))
            st.caption(f"{len(posts.get('twitter', ''))} / 280 chars")
        with tab_ig:
            st.write(posts.get("instagram", ""))
        with tab_li:
            st.write(posts.get("linkedin", ""))

        st.divider()

        # ═══════════════════════════════════════════════════════════════════
        # SECTION 3 — VOICEOVER PANEL (new Pro feature)
        # ═══════════════════════════════════════════════════════════════════
        if enable_voice:
            st.subheader("🎙️ Voiceover")

            with st.spinner("Generating narration script & MP3…"):
                try:
                    vo = generate_voiceover_package(blog, product, tone)
                except Exception as e:
                    vo = {"script": None, "mp3": None, "error": str(e)}

            if vo["error"]:
                st.error(f"Voiceover failed: {vo['error']}")
            else:
                with st.expander("📄 Narration Script", expanded=False):
                    st.write(vo["script"])

                if vo["mp3"]:
                    st.audio(vo["mp3"], format="audio/mp3")
                    st.download_button(
                        "⬇️ Download MP3",
                        data=vo["mp3"],
                        file_name="campaign_voiceover.mp3",
                        mime="audio/mpeg",
                    )

        # ═══════════════════════════════════════════════════════════════════
        # SECTION 4 — CHANNEL ADAPTATION PANEL (new Pro feature)
        # ═══════════════════════════════════════════════════════════════════
        if enable_channels:
            st.divider()
            st.subheader("📡 Channel Adaptation")
            st.caption("Regenerates tagline, blog, and social posts for a specific platform. Image and video are unchanged.")

            channel = st.selectbox(
                "Select Target Channel",
                options=list(CHANNEL_PROFILES.keys()),
                index=0,
            )

            if st.button("🔄 Adapt for Channel", use_container_width=True):
                with st.spinner(f"Adapting content for {channel}…"):
                    try:
                        adapted = adapt_for_channel(product, audience, channel)
                    except Exception as e:
                        adapted = {"error": str(e)}

                if adapted.get("error"):
                    st.error(f"Adaptation failed: {adapted['error']}")
                else:
                    st.success(f"✅ Adapted for {channel}")

                    st.markdown(f"#### 🏷️ Adapted Tagline\n> *{adapted['tagline']}*")
                    st.divider()

                    st.markdown("#### 📰 Adapted Blog")
                    st.write(adapted["blog"])
                    st.divider()

                    st.markdown("#### 📱 Adapted Social Posts")
                    soc = adapted["social"]
                    a_tw, a_ig, a_li = st.tabs(["𝕏 Twitter", "📸 Instagram", "💼 LinkedIn"])
                    with a_tw:
                        st.write(soc.get("twitter", ""))
                        st.caption(f"{len(soc.get('twitter', ''))} / 280 chars")
                    with a_ig:
                        st.write(soc.get("instagram", ""))
                    with a_li:
                        st.write(soc.get("linkedin", ""))

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 5 — VISUALS (existing feature, unchanged)
    # ═══════════════════════════════════════════════════════════════════════
    with right:
        st.subheader("🎨 Visuals")
        image_bytes = None

        with st.spinner("Generating hero image…"):
            try:
                image_bytes = generate_image(product, audience, tone, tagline)
            except Exception as e:
                st.error(f"Image generation failed: {e}")

        if image_bytes:
            st.markdown("### 🖼️ Campaign Hero Image")
            st.image(image_bytes, use_container_width=True)
            st.download_button("⬇️ Download Image", image_bytes, "hero_image.png", "image/png")
            st.divider()

            with st.spinner("Generating animated preview…"):
                try:
                    gif_bytes = generate_video(image_bytes, product)
                except Exception as e:
                    gif_bytes = None
                    st.error(f"Animation generation failed: {e}")

            if gif_bytes:
                st.markdown("### 🎬 Animated Preview")
                st.image(gif_bytes, use_container_width=True)
                st.download_button("⬇️ Download GIF", gif_bytes, "campaign_preview.gif", "image/gif")

else:
    with left:
        st.info("Fill in the sidebar and click **✨ Generate Campaign** to create your full campaign.")
    with right:
        st.empty()
