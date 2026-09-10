import streamlit as st
from groq import Groq
from PIL import Image
import base64
import io
import os
import re

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PixelSage",
    page_icon="🧙",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CUSTOM CSS — Teal + Amber Theme
# ============================================================

st.markdown("""
<style>
    /* Background */
    .stApp {
        background:
            radial-gradient(circle at 20% 0%, #0e7490 0%, transparent 45%),
            radial-gradient(circle at 80% 100%, #f59e0b22 0%, transparent 50%),
            linear-gradient(180deg, #042f2e 0%, #0f172a 100%);
    }
    #MainMenu, footer, header {visibility: hidden;}

    /* Hero title */
    .sage-hero {
        text-align: center;
        padding: 3rem 1rem 1rem 1rem;
    }
    .sage-icon {
        font-size: 4rem;
        line-height: 1;
        filter: drop-shadow(0 0 20px #06b6d4aa);
    }
    .sage-title {
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #06b6d4 0%, #fbbf24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.3rem 0;
    }
    .sage-tagline {
        color: #94a3b8;
        font-size: 1.05rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }

    /* Upload card */
    div[data-testid="stFileUploader"] {
        background: rgba(6, 182, 212, 0.06);
        border: 1.5px dashed #06b6d466;
        border-radius: 18px;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #fbbf24;
        background: rgba(251, 191, 36, 0.05);
    }

    /* Buttons — pill style */
    .stButton > button {
        background: linear-gradient(90deg, #06b6d4 0%, #0891b2 100%);
        color: #042f2e;
        border: none;
        border-radius: 999px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.25);
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #fbbf24 0%, #f59e0b 100%);
        color: #042f2e;
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(251, 191, 36, 0.4);
    }

    /* Result card */
    .sage-result {
        background: linear-gradient(135deg, rgba(6,182,212,0.08) 0%, rgba(251,191,36,0.06) 100%);
        border: 1px solid rgba(6, 182, 212, 0.25);
        border-left: 4px solid #06b6d4;
        border-radius: 18px;
        padding: 1.8rem 2rem;
        margin: 1.5rem 0;
        backdrop-filter: blur(12px);
        font-size: 1.08rem;
        line-height: 1.8;
        color: #e2e8f0;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        position: relative;
    }
    .sage-result::before {
        content: "🧙 PixelSage says:";
        display: block;
        font-size: 0.85rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #06b6d4;
        margin-bottom: 0.8rem;
        font-weight: 700;
    }

    /* Divider */
    hr { border-color: rgba(6, 182, 212, 0.15); margin: 1.5rem 0; }

    /* Captions and text */
    .stCaption, small { color: #64748b !important; }
    p, span, div { color: #cbd5e1; }

    /* Uploaded image frame */
    div[data-testid="stImage"] img {
        border-radius: 14px;
        border: 1px solid rgba(6, 182, 212, 0.2);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
    }

    /* Spinner */
    .stSpinner > div { border-top-color: #06b6d4 !important; }

    /* Alerts */
    .stAlert {
        border-radius: 12px;
        background: rgba(6, 182, 212, 0.08);
        border: 1px solid rgba(6, 182, 212, 0.2);
    }

    /* Footer */
    .sage-footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #64748b;
        font-size: 0.85rem;
        letter-spacing: 1px;
    }
    .sage-footer span { color: #06b6d4; }
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
# HERO HEADER
# ============================================================

st.markdown(
    """
    <div class="sage-hero">
        <div class="sage-icon">🧙</div>
        <div class="sage-title">PixelSage</div>
        <div class="sage-tagline">Snap it · See it · Understand it</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# UPLOAD IMAGE
# ============================================================

uploaded_file = st.file_uploader(
    "Drop an image here",
    type=["jpg", "jpeg", "png", "webp"],
    label_visibility="collapsed"
)

# ============================================================
# IMAGE ANALYSIS
# ============================================================

if uploaded_file:
    try:
        image = Image.open(uploaded_file).convert("RGB")
    except Exception:
        st.error("The uploaded file is not a valid image.")
        st.stop()

    # Display image centered
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image(image, use_container_width=True)

    st.markdown("")

    # Analyze button
    if st.button("🔍  Reveal the Scene", use_container_width=True):
        with st.spinner("PixelSage is reading the image..."):
            try:
                image.thumbnail((1024, 1024))
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG", quality=85)
                img_bytes = buffered.getvalue()
                base64_image = base64.b64encode(img_bytes).decode("utf-8")

                prompt = """Analyze the ENTIRE image carefully. Describe what you see in ONE coherent paragraph of about 80 to 150 words.

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
- Do not copy these instructions.
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
                    st.warning("The model returned no description.")
                else:
                    st.markdown(
                        f'<div class="sage-result">{answer}</div>',
                        unsafe_allow_html=True
                    )

            except Exception as e:
                st.error("⚠️ PixelSage could not analyze the image.")
                st.code(str(e))

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="sage-footer">'
    '🧙 <span>PixelSage</span> · Snap it · See it · Understand it'
    '</div>',
    unsafe_allow_html=True
)
