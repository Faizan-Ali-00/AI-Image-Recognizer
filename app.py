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
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    .main-title {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem; font-weight: 800; text-align: center;
        padding: 1rem 0 0.5rem 0; margin-bottom: 0;
    }
    .subtitle { text-align: center; color: #a0a0b0; font-size: 1.1rem; margin-bottom: 2rem; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        display: block !important;
    }
    section[data-testid="stSidebar"] h2 { color: #667eea; }

    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; border-radius: 10px;
        padding: 0.5rem 1rem; font-weight: 600;
        transition: all 0.3s ease; width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }

    .description-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-left: 4px solid #667eea;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        font-size: 1.05rem;
        line-height: 1.7;
    }

    .stAlert { border-radius: 10px; background: rgba(255, 255, 255, 0.05); }
    p, h1, h2, h3, h4, h5, h6, span, div { color: #e0e0e8; }
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

    # Remove  thinking... blocks
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"</?think>", "", cleaned)

    # Remove meta reasoning lines
    lines = cleaned.split("\n")
    filtered = []
    for line in lines:
        stripped = line.strip()
        if any(stripped.startswith(m) for m in META_STARTERS):
            continue
        filtered.append(line)
    cleaned = "\n".join(filtered)

    # Fallback: if everything was stripped, use last paragraph
    if not cleaned.strip() and text:
        parts = text.strip().split("\n\n")
        cleaned = parts[-1] if parts else ""

    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()

# ============================================================
# HEADER
# ============================================================

st.markdown('<h1 class="main-title">🧙 PixelSage</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Snap it. See it. Understand it.</p>',
    unsafe_allow_html=True
)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## ℹ️ About PixelSage")
    st.markdown(
        "PixelSage uses a powerful vision-language model to "
        "understand and describe uploaded images in natural language."
    )

    st.markdown("### 🔍 What it detects")
    st.markdown(
        """
        - 👤 People & actions
        - 📦 Main objects
        - 🌄 Background & scenery
        - 📍 Object positions
        - 🏞️ Environment & setting
        - 🎨 Colors, shapes, materials
        - 💡 Lighting & atmosphere
        - 🔎 Small visible details
        """
    )

    st.markdown("---")
    st.markdown("### ⚡ Powered by")
    st.markdown(f"**Model:** `{MODEL_NAME}`")

# ============================================================
# UPLOAD IMAGE
# ============================================================

uploaded_file = st.file_uploader(
    "📤 Upload an image",
    type=["jpg", "jpeg", "png", "webp"]
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

    col1, col2 = st.columns([1, 1])

    with col1:
        st.image(image, caption="Uploaded Image", use_container_width=True)

    with col2:
        st.markdown("### 🧠 Analysis")
        st.markdown(
            "Click **Analyze Image** below to generate a description "
            "of the entire scene."
        )

        if st.button("🔍 Analyze Image", use_container_width=True):
            with st.spinner("PixelSage is analyzing the image..."):
                try:
                    # Resize for API (max 1024px)
                    image.thumbnail((1024, 1024))

                    # Convert to base64
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG", quality=85)
                    img_bytes = buffered.getvalue()
                    base64_image = base64.b64encode(img_bytes).decode("utf-8")

                    # Vision prompt
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

                    # Groq API call with vision
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
                        max_tokens=500,
                        temperature=0.3
                    )

                    answer = response.choices[0].message.content
                    answer = clean_response(answer)

                    if not answer:
                        st.warning("The model returned no description.")
                    else:
                        st.markdown(
                            f'<div class="description-box">{answer}</div>',
                            unsafe_allow_html=True
                        )

                except Exception as e:
                    st.error("⚠️ PixelSage could not analyze the image.")
                    st.code(str(e))

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#667eea; font-size:0.85rem;">'
    '🧙 PixelSage · Snap it. See it. Understand it.'
    '</p>',
    unsafe_allow_html=True
)
