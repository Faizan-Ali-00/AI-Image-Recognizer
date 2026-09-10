import streamlit as st
from groq import Groq
from PIL import Image
import base64
import io
import os
import re
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PixelSage — Image Analyzer",
    page_icon="🧙",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS — Live scanner theme + PixelSage branding
# ============================================================

st.markdown("""
<style>
    /* Animated background */
    .stApp {
        background:
            radial-gradient(circle at 20% 10%, #0e7490 0%, transparent 40%),
            radial-gradient(circle at 80% 90%, #10b98122 0%, transparent 45%),
            linear-gradient(180deg, #020617 0%, #0b0f14 100%);
        background-attachment: fixed;
    }
    #MainMenu, footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(2, 6, 23, 0.85);
        backdrop-filter: blur(20px);
        border-right: 1px solid #1e293b;
    }
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #f1f5f9;
        font-weight: 600;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] li {
        color: #94a3b8;
        font-size: 0.9rem;
    }

    /* Hero */
    .hero {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
        margin-bottom: 2rem;
    }
    .hero-mark {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #06b6d4 0%, #0891b2 60%, #065f46 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.4rem;
        margin: 0 auto 1.2rem auto;
        box-shadow:
            0 0 40px rgba(6, 182, 212, 0.5),
            0 0 80px rgba(16, 185, 129, 0.3);
        animation: radarPulse 3s ease-in-out infinite;
    }
    @keyframes radarPulse {
        0%, 100% {
            box-shadow: 0 0 40px rgba(6, 182, 212, 0.5),
                        0 0 80px rgba(16, 185, 129, 0.3);
            transform: scale(1);
        }
        50% {
            box-shadow: 0 0 60px rgba(6, 182, 212, 0.8),
                        0 0 120px rgba(16, 185, 129, 0.5);
            transform: scale(1.05);
        }
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 900;
        letter-spacing: -1.5px;
        background: linear-gradient(90deg, #06b6d4 0%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.1;
    }
    .hero-sub {
        font-size: 0.78rem;
        color: #64748b;
        letter-spacing: 3px;
        margin-top: 0.4rem;
        text-transform: uppercase;
    }
    .hero-tagline {
        font-size: 1rem;
        color: #94a3b8;
        letter-spacing: 3px;
        margin-top: 0.9rem;
        text-transform: uppercase;
        font-weight: 500;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.9rem;
        background: rgba(6, 182, 212, 0.1);
        border: 1px solid rgba(6, 182, 212, 0.4);
        border-radius: 999px;
        font-size: 0.75rem;
        color: #22d3ee;
        font-weight: 500;
        margin-top: 1.2rem;
    }
    .status-dot {
        width: 8px; height: 8px;
        background: #22d3ee;
        border-radius: 50%;
        box-shadow: 0 0 10px #22d3ee;
        animation: blink 1.5s ease-in-out infinite;
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    /* Section labels */
    .section-label {
        font-size: 0.72rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
        margin: 2rem 0 0.75rem 0;
    }

    /* Upload */
    div[data-testid="stFileUploader"] {
        background: rgba(15, 23, 42, 0.7);
        border: 1.5px dashed rgba(6, 182, 212, 0.3);
        border-radius: 16px;
        padding: 1rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #06b6d4;
        background: rgba(6, 182, 212, 0.05);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        padding: 0.85rem 1.6rem;
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
        width: 100%;
        box-shadow: 0 4px 20px rgba(6, 182, 212, 0.35);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #22d3ee 0%, #06b6d4 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(6, 182, 212, 0.55);
    }

    /* Scanning animation */
    .scanning {
        text-align: center;
        padding: 2rem;
        background: rgba(6, 182, 212, 0.05);
        border: 1px dashed rgba(6, 182, 212, 0.4);
        border-radius: 16px;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
    }
    .scanning::before {
        content: "";
        position: absolute;
        top: 0; left: -100%;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, transparent, #06b6d4, transparent);
        animation: scanLine 2s linear infinite;
    }
    @keyframes scanLine {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    .scanning-icon {
        font-size: 2.5rem;
        animation: rotate 2s linear infinite;
        display: inline-block;
    }
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .scanning-text {
        color: #22d3ee;
        font-size: 0.95rem;
        letter-spacing: 2px;
        margin-top: 1rem;
        text-transform: uppercase;
        font-weight: 600;
    }

    /* Result card */
    .result-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid #1e293b;
        border-left: 4px solid #06b6d4;
        border-radius: 16px;
        padding: 1.8rem 2rem;
        margin-top: 1rem;
        color: #e2e8f0;
        font-size: 1.05rem;
        line-height: 1.85;
        backdrop-filter: blur(10px);
    }
    .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 1rem;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 1.4rem;
    }
    .result-header-title {
        font-size: 0.72rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
    }
    .result-meta {
        font-size: 0.72rem;
        color: #475569;
    }

    /* Stats */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.85rem;
        margin-top: 1rem;
    }
    .stat-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        backdrop-filter: blur(10px);
        transition: all 0.2s ease;
        text-align: center;
    }
    .stat-card:hover {
        border-color: rgba(6, 182, 212, 0.4);
        transform: translateY(-2px);
    }
    .stat-label {
        font-size: 0.68rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 0.4rem;
        font-weight: 600;
    }
    .stat-value {
        font-size: 1rem;
        color: #f1f5f9;
        font-weight: 700;
    }

    /* Placeholder */
    .placeholder-card {
        background: rgba(15, 23, 42, 0.4);
        border: 1px dashed #1e293b;
        border-radius: 16px;
        padding: 3.5rem 2rem;
        text-align: center;
        color: #475569;
        backdrop-filter: blur(10px);
    }
    .placeholder-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }

    /* Image frame */
    div[data-testid="stImage"] img {
        border-radius: 14px;
        border: 1px solid rgba(6, 182, 212, 0.25);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
    }

    /* Text */
    p, span, div, label { color: #cbd5e1; }
    .stCaption, small { color: #64748b !important; }

    /* Spinner */
    .stSpinner > div { border-top-color: #06b6d4 !important; }

    /* Alerts */
    .stAlert {
        border-radius: 12px;
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid #1e293b;
    }

    hr { border-color: #1e293b; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# API KEY
# ============================================================

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("🔑 **Groq API key not found.**")
    st.info("Add `GROQ_API_KEY` to `.env` or Streamlit Secrets.")
    st.stop()

MODEL_NAME = "qwen/qwen3.6-27b"

# ============================================================
# CLIENT
# ============================================================

@st.cache_resource
def get_client():
    return Groq(api_key=GROQ_API_KEY)

client = get_client()

# ============================================================
# CLEAN RESPONSE
# ============================================================

META_STARTERS = [
    "Identify the", "Determine the", "Analyze the",
    "Let me ", "Okay, ", "Hmm, ", "Wait, ",
    "I need to ", "The user is asking", "The user wants",
    "Draft Response:", "Final decision:",
    "Let's ", "Actually, ", "Correction:",
    "Alternative:", "Refine:", "Check constraints",
    "Final Output", "Looking closely",
    "Wait, no", "Let's re-evaluate",
]

def clean_response(text):
    if not text:
        return ""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"</?think>", "", cleaned)
    lines = cleaned.split("\n")
    filtered = []
    for line in lines:
        stripped = line.strip()
        if any(stripped.startswith(m) for m in META_STARTERS):
            continue
        filtered.append(line)
    cleaned = "\n".join(filtered)
    if not cleaned.strip() and text:
        parts = text.strip().split("\n\n")
        cleaned = parts[-1] if parts else ""
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🧙 PixelSage")
    st.markdown(
        "<p style='font-size:0.8rem;color:#64748b;margin-top:-0.5rem;'>"
        "Image Analysis Engine</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    st.markdown("### ⚙️ Settings")
    detail_level = st.select_slider(
        "Detail level",
        options=["Brief", "Standard", "Detailed"],
        value="Standard"
    )

    st.markdown("---")
    st.markdown("### 🔍 Detects")
    st.markdown(
        """
        - People & actions
        - Objects & items
        - Background scenery
        - Environment & setting
        - Colors, shapes, materials
        - Lighting & atmosphere
        - Positions & layout
        - Small visible details
        """
    )

    st.markdown("---")
    st.markdown("### ⚡ Engine")
    st.markdown(f"**Model** · `{MODEL_NAME}`")
    st.markdown("**Status** · Online")

# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-mark">🧙</div>
        <h1 class="hero-title">PixelSage</h1>
        <div class="hero-sub">Image Analyzer</div>
        <div class="hero-tagline">Snap it · See it · Understand it</div>
        <div class="status-pill">
            <span class="status-dot"></span> Analyzer Ready
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# STEP 1 — UPLOAD
# ============================================================

st.markdown(
    '<div class="section-label">📸 01 · Upload Image</div>',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Upload image",
    type=["jpg", "jpeg", "png", "webp"],
    label_visibility="collapsed"
)

# ============================================================
# STEP 2 — PREVIEW
# ============================================================

if uploaded_file:
    try:
        image = Image.open(uploaded_file).convert("RGB")
    except Exception:
        st.error("Invalid image file.")
        st.stop()

    st.markdown(
        '<div class="section-label">🖼️ 02 · Preview</div>',
        unsafe_allow_html=True
    )

    st.image(image, use_container_width=True)

    # Image stats
    w, h = image.size
    st.markdown(
        f"""
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-label">Width</div>
                <div class="stat-value">{w} px</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Height</div>
                <div class="stat-value">{h} px</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Mode</div>
                <div class="stat-value">{image.mode}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")

    # Analyze button
    analyze_clicked = st.button("🔍  Analyze Image", use_container_width=True)

    # --------------------------------------------------
    # STEP 3 — RESULT
    # --------------------------------------------------
    st.markdown(
        '<div class="section-label">📝 03 · Analysis Result</div>',
        unsafe_allow_html=True
    )

    if analyze_clicked:
        # Scanning animation
        scan_placeholder = st.empty()
        scan_placeholder.markdown(
            """
            <div class="scanning">
                <div class="scanning-icon">📡</div>
                <div class="scanning-text">Scanning · Analyzing · Generating</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        try:
            # Preprocess
            img_copy = image.copy()
            img_copy.thumbnail((1024, 1024))
            buffered = io.BytesIO()
            img_copy.save(buffered, format="JPEG", quality=88)
            img_bytes = buffered.getvalue()
            base64_image = base64.b64encode(img_bytes).decode("utf-8")

            # Detail level mapping
            detail_map = {
                "Brief": "60 to 80 words",
                "Standard": "100 to 150 words",
                "Detailed": "180 to 250 words"
            }
            target_len = detail_map.get(detail_level, "100 to 150 words")

            # Prompt
            prompt = f"""Analyze the ENTIRE image carefully and describe what you see in ONE coherent paragraph of {target_len}.

Cover in this order:
1. Foreground objects (closest to viewer)
2. Middle ground objects
3. Background scenery
4. Edges and corners (any small details)
5. People and what they are doing (or say no people are visible)
6. Environment and setting
7. Colors, shapes, materials, lighting
8. Positions (left, right, center, etc.)

RULES:
- Describe only things actually visible.
- Do not guess or invent.
- Do not repeat information.
- Do not number your observations.
- Do NOT show reasoning, thinking, or step-by-step analysis.
- Do NOT use phrases like "Let me think", "Wait", "Looking closely".
- Write ONE natural paragraph, flowing smoothly from foreground to background.
- Respond ONLY with the final description."""

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=900,
                temperature=0.3
            )

            answer = response.choices[0].message.content
            answer = clean_response(answer)

            # Clear scanning
            scan_placeholder.empty()

            if not answer:
                st.warning("No description returned.")
            else:
                timestamp = datetime.now().strftime("%H:%M:%S")
                st.markdown(
                    f"""
                    <div class="result-card">
                        <div class="result-header">
                            <div class="result-header-title">🧙 PixelSage Says</div>
                            <div class="result-meta">{target_len} · {timestamp}</div>
                        </div>
                        {answer}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                with st.expander("📋 Copy as plain text"):
                    st.code(answer, language=None)

        except Exception as e:
            scan_placeholder.empty()
            st.error("⚠️ Analysis failed.")
            st.code(str(e))

    else:
        st.markdown(
            """
            <div class="placeholder-card">
                <div class="placeholder-icon">🔍</div>
                <div>Click <b>Analyze Image</b> to generate a description</div>
            </div>
            """,
            unsafe_allow_html=True
        )

else:
    st.markdown(
        """
        <div class="placeholder-card">
            <div class="placeholder-icon">📤</div>
            <div>Upload an image to begin analysis</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#475569;font-size:0.8rem;letter-spacing:1px;'>"
    "🧙 PixelSage · Snap it · See it · Understand it"
    "</p>",
    unsafe_allow_html=True
)
