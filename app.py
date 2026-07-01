import streamlit as st
from text_gen import generate_tagline, generate_blog_intro, generate_social_posts
from image_gen import generate_image
from video_gen import generate_video

st.set_page_config(page_title="AdSpark", page_icon="⚡", layout="wide")
st.title("⚡ AdSpark")
st.caption("Ignite your campaign in seconds. Transform a product brief into a complete marketing launch — tagline, blog, social posts, hero image, and animated preview.")

# ── Sidebar inputs ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Product Brief")
    product  = st.text_input("Product Name", placeholder="e.g. EcoBottle Pro")
    audience = st.text_input("Target Audience", placeholder="e.g. eco-conscious millennials")
    tone     = st.selectbox("Brand Tone", ["playful", "premium", "eco", "bold", "minimal"])
    generate = st.button("✨ Generate", type="primary", use_container_width=True)

left, right = st.columns([1, 1], gap="large")

if generate:
    if not product or not audience:
        st.warning("Please fill in both Product Name and Target Audience.")
        st.stop()

    # ── TEXT (tagline first, then blog + social in parallel) ─────────────────
    with left:
        st.subheader("📝 Campaign Copy")

        with st.spinner("Generating tagline…"):
            try:
                tagline = generate_tagline(product, audience, tone)
            except Exception as e:
                st.error(f"Tagline failed: {e}")
                st.stop()

        st.markdown(f"### 🏷️ Tagline\n> *{tagline}*")
        st.divider()

        # Run blog intro and social posts in parallel
        from concurrent.futures import ThreadPoolExecutor
        with st.spinner("Writing blog & social posts…"):
            with ThreadPoolExecutor(max_workers=2) as executor:
                blog_future  = executor.submit(generate_blog_intro, product, audience, tone, tagline)
                posts_future = executor.submit(generate_social_posts, product, audience, tone, tagline)
            try:
                blog = blog_future.result()
            except Exception as e:
                blog = f"⚠️ Blog generation failed: {e}"
            try:
                posts = posts_future.result()
            except Exception as e:
                posts = {"twitter": f"Error: {e}", "instagram": f"Error: {e}", "linkedin": f"Error: {e}"}

        st.markdown("### 📱 Social Media Posts")
        tab_tw, tab_ig, tab_li = st.tabs(["𝕏 Twitter", "📸 Instagram", "💼 LinkedIn"])
        with tab_tw:
            st.write(posts.get("twitter", ""))
            st.caption(f"{len(posts.get('twitter', ''))} / 280 chars")
        with tab_ig:
            st.write(posts.get("instagram", ""))
        with tab_li:
            st.write(posts.get("linkedin", ""))

    # ── VISUALS ───────────────────────────────────────────────────────────────
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
        st.info("Fill in the sidebar and click **✨ Generate** to create your campaign.")
    with right:
        st.empty()
