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
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS — Clean, professional analyzer UI
# ============================================================

st.markdown("""
<style>
    /* Base */
    .stApp {
        background: #0b0f14;
    }
    #MainMenu, footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #0f1419;
        border-right: 1px solid #1f2937;
    }
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #e5e7eb;
        font-weight: 600;
        letter-spacing: -0.3px;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] li {
        color: #9ca3af;
        font-size: 0.9rem;
    }

    /* Top bar */
    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.2rem 0 1.8rem 0;
        border-bottom: 1px solid #1f2937;
        margin-bottom: 2rem;
    }
    .brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .brand-mark {
        width: 42px;
        height: 42px;
        border-radius: 10px;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3);
    }
    .brand-text h1 {
        font-size: 1.35rem;
        font-weight: 700;
        color: #f9fafb;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .brand-text p {
        font-size: 0.78rem;
        color: #6b7280;
        margin: 0;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.4rem 0.85rem;
        background: #0f2a1f;
        border: 1px solid #14532d;
        border-radius: 999px;
        font-size: 0.78rem;
        color: #4ade80;
        font-weight: 500;
    }
    .status-dot {
        width: 8px; height: 8px;
        background: #4ade80;
        border-radius: 50%;
        box-shadow: 0 0 8px #4ade80;
    }

    /* Section headers */
    .section-label {
        font-size: 0.72rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin: 1.5rem 0 0.75rem 0;
    }

    /* Upload area */
    div[data-testid="stFileUploader"] {
        background: #0f1419;
        border: 1.5px dashed #1f2937;
        border-radius: 14px;
        padding: 1rem;
        transition: all 0.2s ease;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #3b82f6;
        background: #101822;
    }

    /* Buttons */
    .stButton > button {
        background: #3b82f6;
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.4rem;
        font-weight: 600;
        font-size: 0.92rem;
        letter-spacing: 0.2px;
        transition: all 0.15s ease;
        width: 100%;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.25);
    }
    .stButton > button:hover {
        background: #2563eb;
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(59, 130, 246, 0.4);
    }

    /* Result card */
    .result-card {
        background: #0f1419;
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 1.6rem 1.8rem;
        margin-top: 1rem;
        color: #e5e7eb;
        font-size: 1rem;
        line-height: 1.75;
    }
    .result-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 1rem;
        border-bottom: 1px solid #1f2937;
        margin-bottom: 1.2rem;
    }
    .result-header-title {
        font-size: 0.78rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin: 0;
    }
    .result-meta {
        font-size: 0.75rem;
        color: #4b5563;
    }

    /* Stat cards */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
        margin-top: 1rem;
    }
    .stat-card {
        background: #0f1419;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 0.85rem 1rem;
    }
    .stat-label {
        font-size: 0.7rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.3rem;
    }
    .stat-value {
        font-size: 0.95rem;
        color: #f9fafb;
        font-weight: 600;
    }

    /* Text colors */
    p, span, div, label { color: #d1d5db; }
    .stCaption, small { color: #6b7280 !important; }

    /* Image frame */
    div[data-testid="stImage"] img {
        border-radius: 12px;
        border: 1px solid #1f2937;
    }

    /* Spinner */
    .stSpinner > div { border-top-color: #3b82f6 !important; }

    /* Alerts */
    .stAlert {
        border-radius: 10px;
        background: #0f1419;
        border: 1px solid #1f2937;
    }

    /* Divider */
    hr { border-color: #1f2937; margin: 1.5rem 0; }
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

# ============================================================
# MODEL
# ============================================================

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
    "Final Output", "Top image:", "Second image",
    "Third image", "Bottom image", "Looking closely",
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
    st.markdown("## PixelSage")
    st.markdown(
        "<p style='font-size:0.8rem;color:#6b7280;margin-top:-0.5rem;'>"
        "Image analysis engine</p>",
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

    st.markdown("### 🔎 Detection")
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
    st.markdown(f"**Status** · Online")

# ============================================================
# TOP BAR
# ============================================================

st.markdown(
    """
    <div class="topbar">
        <div class="brand">
            <div class="brand-mark">🔎</div>
            <div class="brand-text">
                <h1>PixelSage</h1>
                <p>Image Analyzer</p>
            </div>
        </div>
        <div class="status-pill">
            <span class="status-dot"></span> Engine Online
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# MAIN LAYOUT — 2 columns
# ============================================================

col_left, col_right = st.columns([1, 1], gap="large")

# ------------------------------------------------------------
# LEFT: Upload + Preview
# ------------------------------------------------------------

with col_left:
    st.markdown('<div class="section-label">01 · Source Image</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload image",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        try:
            image = Image.open(uploaded_file).convert("RGB")
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
        except Exception:
            st.error("Invalid image file.")
            st.stop()

# ------------------------------------------------------------
# RIGHT: Analysis
# ------------------------------------------------------------

with col_right:
    st.markdown('<div class="section-label">02 · Analysis Result</div>', unsafe_allow_html=True)

    if uploaded_file:
        if st.button("▶  Analyze Image", use_container_width=True):
            with st.spinner("Analyzing image..."):
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

                    prompt = f"""Analyze the ENTIRE image carefully and describe what you see in ONE coherent paragraph of {target_len}.

Cover in order:
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
- Write ONE natural paragraph.
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

                    if not answer:
                        st.warning("No description returned.")
                    else:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        st.markdown(
                            f"""
                            <div class="result-card">
                                <div class="result-header">
                                    <div class="result-header-title">Description</div>
                                    <div class="result-meta">{target_len} · {timestamp}</div>
                                </div>
                                {answer}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # Copy-friendly expander
                        with st.expander("📋 View as plain text (copy)"):
                            st.code(answer, language=None)

                except Exception as e:
                    st.error("Analysis failed.")
                    st.code(str(e))
    else:
        st.markdown(
            """
            <div class="result-card" style="text-align:center;padding:3rem 2rem;color:#4b5563;">
                <div style="font-size:2.5rem;margin-bottom:0.8rem;">🔎</div>
                <div style="font-size:0.95rem;">Upload an image to begin analysis</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#4b5563;font-size:0.8rem;'>"
    "PixelSage · Image Analyzer · Snap it · See it · Understand it"
    "</p>",
    unsafe_allow_html=True
)
