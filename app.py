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
    page_title="PixelSage",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CSS — Real app look
# ============================================================

st.markdown("""
<style>
    .stApp { background: #08090c; }
    #MainMenu, footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent; height: 0;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 960px;
    }

    /* Top nav */
    .app-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.9rem 1.5rem;
        background: rgba(15, 17, 21, 0.85);
        border: 1px solid #1c1f26;
        border-radius: 16px;
        backdrop-filter: blur(20px);
        margin-bottom: 2.5rem;
    }
    .nav-left { display: flex; align-items: center; gap: 0.85rem; }
    .nav-logo {
        width: 36px; height: 36px;
        border-radius: 10px;
        background: linear-gradient(135deg, #06b6d4 0%, #10b981 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
        box-shadow: 0 4px 14px rgba(6, 182, 212, 0.35);
    }
    .nav-brand {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f1f5f9;
        letter-spacing: -0.3px;
        line-height: 1.1;
    }
    .nav-sub {
        font-size: 0.68rem;
        color: #64748b;
        letter-spacing: 0.5px;
        margin-top: 1px;
    }
    .nav-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.75rem;
        background: rgba(6, 182, 212, 0.08);
        border: 1px solid rgba(6, 182, 212, 0.3);
        border-radius: 999px;
        font-size: 0.72rem;
        color: #67e8f9;
        font-weight: 600;
    }
    .nav-pill-dot {
        width: 7px; height: 7px;
        background: #22d3ee;
        border-radius: 50%;
        box-shadow: 0 0 8px #22d3ee;
        animation: blink 1.6s ease-in-out infinite;
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    /* Hero */
    .page-hero { text-align: center; margin-bottom: 2.5rem; }
    .page-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -1.2px;
        line-height: 1.05;
        margin: 0 0 0.6rem 0;
    }
    .page-title span {
        background: linear-gradient(90deg, #06b6d4 0%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .page-sub {
        font-size: 1rem;
        color: #94a3b8;
        letter-spacing: 0.2px;
        margin: 0;
    }

    /* Tabs */
    .tabs-row {
        display: flex;
        gap: 0.4rem;
        background: rgba(15, 17, 21, 0.6);
        border: 1px solid #1c1f26;
        border-radius: 12px;
        padding: 0.35rem;
        margin-bottom: 2rem;
        width: fit-content;
        margin-left: auto;
        margin-right: auto;
    }
    .tab-item {
        padding: 0.5rem 1.1rem;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748b;
        letter-spacing: 0.3px;
    }
    .tab-active {
        background: #1c1f26;
        color: #f1f5f9;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }

    /* Drop zone */
    div[data-testid="stFileUploader"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    div[data-testid="stFileUploader"] > label {display: none;}
    div[data-testid="stFileUploader"] section {
        background: #0f1115 !important;
        border: 2px dashed #2a2f3a !important;
        border-radius: 20px !important;
        padding: 3.5rem 2rem !important;
        transition: all 0.25s ease !important;
        min-height: 300px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div[data-testid="stFileUploader"] section:hover {
        border-color: #06b6d4 !important;
        background: #10161e !important;
        box-shadow: 0 0 40px rgba(6, 182, 212, 0.15) !important;
    }
    div[data-testid="stFileUploader"] section > div {
        flex-direction: column;
        text-align: center;
    }
    div[data-testid="stFileUploader"] section svg {
        width: 42px;
        height: 42px;
        color: #06b6d4;
        margin-bottom: 1rem;
    }
    div[data-testid="stFileUploader"] section small { color: #64748b; font-size: 0.85rem; }
    div[data-testid="stFileUploader"] section span { color: #e2e8f0; font-weight: 600; }
    div[data-testid="stFileUploader"] button {
        background: #1c1f26 !important;
        color: #e2e8f0 !important;
        border: 1px solid #2a2f3a !important;
        border-radius: 10px !important;
        padding: 0.55rem 1.1rem !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        margin-top: 1rem;
    }
    div[data-testid="stFileUploader"] button:hover {
        border-color: #06b6d4 !important;
        color: #22d3ee !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        padding: 0.9rem 1.8rem;
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
        transition: all 0.2s ease;
        width: 100%;
        box-shadow: 0 4px 20px rgba(6, 182, 212, 0.35);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #22d3ee 0%, #06b6d4 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(6, 182, 212, 0.55);
    }

    /* Image preview */
    div[data-testid="stImage"] img {
        border-radius: 16px;
        border: 1px solid #1c1f26;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    }

    /* Result block */
    .result-block {
        background: linear-gradient(135deg, rgba(6,182,212,0.06) 0%, rgba(16,185,129,0.03) 100%);
        border: 1px solid #1c1f26;
        border-radius: 20px;
        padding: 2rem 2.2rem;
        margin-top: 1.5rem;
        backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
    }
    .result-block::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #06b6d4 0%, #10b981 100%);
    }
    .result-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 1.2rem;
        border-bottom: 1px solid #1c1f26;
        margin-bottom: 1.5rem;
    }
    .result-label {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.72rem;
        color: #94a3b8;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 700;
    }
    .result-label-dot {
        width: 8px; height: 8px;
        background: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 10px #10b981;
    }
    .result-time { font-size: 0.72rem; color: #475569; }
    .result-text {
        color: #e2e8f0;
        font-size: 1.05rem;
        line-height: 1.9;
        letter-spacing: 0.1px;
    }

    /* Chips */
    .chips-row {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-top: 1.2rem;
    }
    .chip {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.75rem;
        background: rgba(15, 17, 21, 0.8);
        border: 1px solid #1c1f26;
        border-radius: 999px;
        font-size: 0.75rem;
        color: #94a3b8;
        font-weight: 500;
    }
    .chip strong {color: #e2e8f0; font-weight: 600;}

    /* Empty */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: rgba(15, 17, 21, 0.5);
        border: 1px dashed #1c1f26;
        border-radius: 20px;
    }
    .empty-icon { font-size: 3rem; margin-bottom: 1rem; opacity: 0.4; }
    .empty-title { font-size: 1.1rem; color: #94a3b8; font-weight: 600; margin-bottom: 0.3rem; }
    .empty-sub { font-size: 0.85rem; color: #475569; }

    /* Scanning */
    .scanning-block {
        padding: 2.5rem;
        background: rgba(6, 182, 212, 0.04);
        border: 1px dashed rgba(6, 182, 212, 0.3);
        border-radius: 20px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .scanning-block::before {
        content: "";
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 2px;
        background: linear-gradient(90deg, transparent, #06b6d4, transparent);
        animation: scanline 2s linear infinite;
    }
    @keyframes scanline {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    .scanning-block .icon {
        font-size: 2.5rem;
        animation: pulse 1.8s ease-in-out infinite;
        display: inline-block;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.15); opacity: 0.7; }
    }
    .scanning-block .label {
        color: #22d3ee;
        font-size: 0.85rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        font-weight: 700;
        margin-top: 1rem;
    }

    /* Text */
    p, span, div, label { color: #cbd5e1; }
    .stCaption, small { color: #64748b !important; }

    /* Spinner */
    .stSpinner > div { border-top-color: #06b6d4 !important; }

    /* Alerts */
    .stAlert {
        border-radius: 12px;
        background: rgba(15, 17, 21, 0.8);
        border: 1px solid #1c1f26;
    }

    hr { border-color: #1c1f26; margin: 2rem 0; }

    /* Footer */
    .app-footer {
        text-align: center;
        padding: 2.5rem 0 1rem 0;
        color: #3f4551;
        font-size: 0.78rem;
        letter-spacing: 1px;
    }
    .app-footer strong {color: #64748b;}
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

def clean_response(text):
    if not text:
        return ""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"</?think>", "", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()

# ============================================================
# APP NAV
# ============================================================

st.markdown(
    """
    <div class="app-nav">
        <div class="nav-left">
            <div class="nav-logo">PS</div>
            <div>
                <div class="nav-brand">PixelSage</div>
                <div class="nav-sub">IMAGE ANALYSIS STUDIO</div>
            </div>
        </div>
        <div class="nav-pill">
            <span class="nav-pill-dot"></span> Engine Ready
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="page-hero">
        <h1 class="page-title">Analyze any image <span>instantly.</span></h1>
        <p class="page-sub">Upload a photo and PixelSage will describe every detail — from the foreground to the corners.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# TABS (visual only)
# ============================================================

st.markdown(
    """
    <div class="tabs-row">
        <div class="tab-item tab-active">📸 Analyze</div>
        <div class="tab-item">📚 History</div>
        <div class="tab-item">⚙️ Settings</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# DETAIL LEVEL
# ============================================================

detail_level = st.radio(
    "Detail level",
    options=["Brief", "Standard", "Detailed"],
    index=1,
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("")

# ============================================================
# UPLOAD / PREVIEW / RESULT
# ============================================================

uploaded_file = st.file_uploader(
    "Upload image",
    type=["jpg", "jpeg", "png", "webp"],
    label_visibility="collapsed"
)

if uploaded_file:
    try:
        image = Image.open(uploaded_file).convert("RGB")
    except Exception:
        st.error("Invalid image file.")
        st.stop()

    st.markdown("")
    st.image(image, use_container_width=True)

    w, h = image.size
    file_size = len(uploaded_file.getvalue()) / 1024
    st.markdown(
        f"""
        <div class="chips-row">
            <div class="chip">📐 <strong>{w} × {h}</strong></div>
            <div class="chip">🎨 <strong>{image.mode}</strong></div>
            <div class="chip">💾 <strong>{file_size:.0f} KB</strong></div>
            <div class="chip">⚙️ <strong>{detail_level}</strong></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")

    analyze_clicked = st.button("🔍  Analyze Image", use_container_width=True)

    if analyze_clicked:
        scan_placeholder = st.empty()
        scan_placeholder.markdown(
            """
            <div class="scanning-block">
                <div class="icon">📸</div>
                <div class="label">Analyzing image</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        try:
            img_copy = image.copy()
            img_copy.thumbnail((1024, 1024))
            buffered = io.BytesIO()
            img_copy.save(buffered, format="JPEG", quality=88)
            img_bytes = buffered.getvalue()
            base64_image = base64.b64encode(img_bytes).decode("utf-8")

            detail_map = {
                "Brief": "60 to 80 words",
                "Standard": "100 to 150 words",
                "Detailed": "180 to 250 words"
            }
            target_len = detail_map.get(detail_level, "100 to 150 words")

            # System prompt: forces natural, remembering-style output
            system_prompt = """You are a professional image analyst. Write your descriptions as a single, natural, flowing paragraph — exactly like a human expert looking at a photo would describe it out loud.

CRITICAL STYLE RULES:
- Write as ONE continuous paragraph, no bullet points, no numbered lists.
- Do NOT show any reasoning, thinking, or meta-commentary.
- Do NOT use phrases like "Let me", "Okay", "First, I'll look at...", "Wait".
- Do NOT reference instructions, prompts, or the user.
- Just describe what is visible, in order from foreground to background.
- Remember the ENTIRE image — including edges and corners — and weave small details in naturally.
- Sound confident and clear, like a professional analyst."""

            user_prompt = f"""Describe this image in {target_len}.

Flow your description naturally in this order:
foreground → middle ground → background → edges and corners → people (or note their absence) → environment → colors, shapes, materials, lighting → positions.

Write as ONE smooth paragraph. Just the final description, nothing else."""

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
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
                temperature=0.4
            )

            answer = response.choices[0].message.content
            answer = clean_response(answer)

            scan_placeholder.empty()

            if not answer:
                st.warning("No description returned.")
            else:
                timestamp = datetime.now().strftime("%H:%M")
                st.markdown(
                    f"""
                    <div class="result-block">
                        <div class="result-top">
                            <div class="result-label">
                                <span class="result-label-dot"></span> Description · {detail_level}
                            </div>
                            <div class="result-time">{timestamp}</div>
                        </div>
                        <div class="result-text">{answer}</div>
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
        <div class="empty-state">
            <div class="empty-icon">🖼️</div>
            <div class="empty-title">No image yet</div>
            <div class="empty-sub">Upload an image above to get started</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="app-footer"><strong>PixelSage</strong> · Snap it · See it · Understand it</div>',
    unsafe_allow_html=True
)
