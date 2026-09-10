import streamlit as st
from groq import Groq
from PIL import Image
import base64
import io
import os
import re
import json
from datetime import datetime
from pathlib import Path

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PixelSage — Image Analyzer",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# LOGO
# ============================================================

LOGO_SVG = """
<svg width="36" height="36" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="psGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#06b6d4"/>
      <stop offset="100%" stop-color="#10b981"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="36" height="36" rx="10" fill="url(#psGrad)"/>
  <circle cx="18" cy="18" r="8.5" fill="none" stroke="#ffffff" stroke-width="1.8"/>
  <circle cx="18" cy="18" r="3.2" fill="#ffffff"/>
  <line x1="24" y1="24" x2="29" y2="29" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>
  <line x1="9" y1="9" x2="13" y2="13" stroke="#ffffff" stroke-width="1.2" stroke-linecap="round" opacity="0.7"/>
  <line x1="27" y1="9" x2="23" y2="13" stroke="#ffffff" stroke-width="1.2" stroke-linecap="round" opacity="0.7"/>
</svg>
"""

LOGO_DATA_URI = "data:image/svg+xml;base64," + base64.b64encode(LOGO_SVG.encode("utf-8")).decode("utf-8")

# ============================================================
# STORAGE PATHS
# ============================================================

HISTORY_FILE = Path("history.json")
THUMBNAIL_DIR = Path("thumbnails")
THUMBNAIL_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = Path("settings.json")

DEFAULT_SETTINGS = {
    "detail_level": "Standard",
    "temperature": 0.4,
    "max_tokens": 900,
}

# ============================================================
# FILE HELPERS
# ============================================================

def load_history():
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Could not save history: {e}")

def save_thumbnail(image, entry_id):
    try:
        thumb = image.copy()
        thumb.thumbnail((300, 300))
        path = THUMBNAIL_DIR / f"{entry_id}.jpg"
        thumb.save(path, format="JPEG", quality=80)
        return str(path)
    except Exception:
        return ""

def add_history_entry(image, description, detail_level, model_name):
    entry_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    thumb_path = save_thumbnail(image, entry_id)
    entry = {
        "id": entry_id,
        "timestamp": datetime.now().strftime("%b %d, %Y · %H:%M"),
        "description": description,
        "detail_level": detail_level,
        "model": model_name,
        "thumbnail": thumb_path,
        "width": image.width,
        "height": image.height,
    }
    history = load_history()
    history.insert(0, entry)
    history = history[:30]
    save_history(history)
    return entry

def delete_history_entry(entry_id):
    history = load_history()
    history = [h for h in history if h["id"] != entry_id]
    save_history(history)
    thumb_path = THUMBNAIL_DIR / f"{entry_id}.jpg"
    if thumb_path.exists():
        try:
            thumb_path.unlink()
        except Exception:
            pass

def clear_history():
    history = load_history()
    for entry in history:
        thumb = Path(entry.get("thumbnail", ""))
        if thumb.exists():
            try:
                thumb.unlink()
            except Exception:
                pass
    save_history([])

def load_settings():
    if not SETTINGS_FILE.exists():
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = DEFAULT_SETTINGS.copy()
        merged.update(data)
        return merged
    except Exception:
        return DEFAULT_SETTINGS.copy()

def save_settings_file(settings):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        st.error(f"Could not save settings: {e}")

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "settings" not in st.session_state:
    st.session_state.settings = load_settings()

# Initialize temp settings widgets with current values
if "temp_detail" not in st.session_state:
    st.session_state.temp_detail = st.session_state.settings["detail_level"]
if "temp_temp" not in st.session_state:
    st.session_state.temp_temp = st.session_state.settings["temperature"]
if "temp_tokens" not in st.session_state:
    st.session_state.temp_tokens = st.session_state.settings["max_tokens"]
if "settings_saved_msg" not in st.session_state:
    st.session_state.settings_saved_msg = False
if "settings_reset_msg" not in st.session_state:
    st.session_state.settings_reset_msg = False

# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>
    .stApp { background: #08090c; }
    #MainMenu, footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent; height: 0;}
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 900px; }

    .app-nav {
        display: flex; align-items: center; justify-content: space-between;
        padding: 0.85rem 1.3rem;
        background: rgba(15, 17, 21, 0.9);
        border: 1px solid #1c1f26; border-radius: 14px;
        backdrop-filter: blur(20px); margin-bottom: 2rem;
    }
    .nav-left { display: flex; align-items: center; gap: 0.75rem; }
    .nav-logo { width: 36px; height: 36px; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 16px rgba(6, 182, 212, 0.35); }
    .nav-logo img { width: 36px; height: 36px; display: block; }
    .nav-brand { font-size: 1rem; font-weight: 700; color: #f1f5f9; letter-spacing: -0.3px; line-height: 1.1; }
    .nav-sub { font-size: 0.66rem; color: #64748b; letter-spacing: 0.6px; margin-top: 1px; }
    .nav-pill {
        display: inline-flex; align-items: center; gap: 0.4rem;
        padding: 0.32rem 0.7rem;
        background: rgba(6, 182, 212, 0.08);
        border: 1px solid rgba(6, 182, 212, 0.3);
        border-radius: 999px; font-size: 0.7rem; color: #67e8f9; font-weight: 600;
    }
    .nav-pill-dot {
        width: 6px; height: 6px; background: #22d3ee; border-radius: 50%;
        box-shadow: 0 0 8px #22d3ee; animation: blink 1.6s ease-in-out infinite;
    }
    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

    .page-hero { text-align: center; margin-bottom: 1.8rem; }
    .hero-logo {
        width: 68px; height: 68px; border-radius: 18px;
        margin: 0 auto 1rem auto;
        box-shadow: 0 10px 40px rgba(6, 182, 212, 0.35);
        animation: logoFloat 4s ease-in-out infinite;
        overflow: hidden;
    }
    .hero-logo img { width: 68px; height: 68px; display: block; }
    @keyframes logoFloat { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
    .page-title {
        font-size: 2.4rem; font-weight: 800; color: #f8fafc;
        letter-spacing: -1.2px; line-height: 1.05; margin: 0 0 0.6rem 0;
    }
    .page-title span {
        background: linear-gradient(90deg, #06b6d4 0%, #10b981 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .page-sub { font-size: 0.95rem; color: #94a3b8; margin: 0; }

    button[data-baseweb="tab"] {
        background: transparent !important; color: #64748b !important;
        font-weight: 600 !important; font-size: 0.85rem !important;
        padding: 0.6rem 1.1rem !important; border-radius: 8px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #f1f5f9 !important; background: rgba(28, 31, 38, 0.9) !important;
    }
    div[data-baseweb="tab-list"] {
        background: rgba(15, 17, 21, 0.6) !important;
        border: 1px solid #1c1f26 !important;
        border-radius: 12px !important;
        padding: 0.3rem !important;
        gap: 0.2rem !important;
        justify-content: center;
    }
    div[data-baseweb="tab-highlight"] { display: none !important; }
    div[data-baseweb="tab-border"] { display: none !important; }

    div[role="radiogroup"] {
        display: flex; justify-content: center; gap: 0.35rem;
        background: rgba(15, 17, 21, 0.6);
        border: 1px solid #1c1f26; border-radius: 12px;
        padding: 0.3rem; width: fit-content; margin: 0 auto 1.5rem auto;
    }
    div[role="radiogroup"] label {
        padding: 0.5rem 1.2rem !important; border-radius: 8px !important;
        font-size: 0.82rem !important; font-weight: 600 !important;
        color: #64748b !important; cursor: pointer; transition: all 0.2s ease;
    }
    div[role="radiogroup"] label:hover { color: #94a3b8 !important; }
    div[role="radiogroup"] label:has(input:checked) {
        background: #1c1f26 !important; color: #f1f5f9 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    div[role="radiogroup"] input {display: none;}

    div[data-testid="stFileUploader"] { background: transparent !important; border: none !important; padding: 0 !important; }
    div[data-testid="stFileUploader"] > label {display: none !important;}
    div[data-testid="stFileUploader"] section {
        background: #0f1115 !important; border: 2px dashed #2a2f3a !important;
        border-radius: 20px !important; padding: 3.5rem 2rem !important;
        transition: all 0.25s ease !important; min-height: 300px !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
    }
    div[data-testid="stFileUploader"] section:hover {
        border-color: #06b6d4 !important; background: #10161e !important;
        box-shadow: 0 0 40px rgba(6, 182, 212, 0.12) !important;
    }
    div[data-testid="stFileUploader"] section > div { flex-direction: column; text-align: center; }
    div[data-testid="stFileUploader"] section svg { width: 46px; height: 46px; color: #06b6d4; margin-bottom: 1rem; }
    div[data-testid="stFileUploader"] section small { color: #64748b; font-size: 0.82rem; }
    div[data-testid="stFileUploader"] section span { color: #e2e8f0; font-weight: 600; }
    div[data-testid="stFileUploader"] button {
        background: #1c1f26 !important; color: #e2e8f0 !important;
        border: 1px solid #2a2f3a !important; border-radius: 10px !important;
        padding: 0.55rem 1.2rem !important; font-weight: 600 !important;
        font-size: 0.85rem !important; margin-top: 1.1rem;
    }
    div[data-testid="stFileUploader"] button:hover { border-color: #06b6d4 !important; color: #22d3ee !important; }

    .stButton > button {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: #ffffff; border: none; border-radius: 12px;
        padding: 0.85rem 1.6rem; font-weight: 700; font-size: 0.92rem;
        letter-spacing: 0.3px; transition: all 0.2s ease; width: 100%;
        box-shadow: 0 4px 20px rgba(6, 182, 212, 0.35);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #22d3ee 0%, #06b6d4 100%);
        transform: translateY(-2px); box-shadow: 0 8px 30px rgba(6, 182, 212, 0.55);
    }

    .secondary-btn button {
        background: #1c1f26 !important; color: #e2e8f0 !important;
        border: 1px solid #2a2f3a !important; box-shadow: none !important;
        padding: 0.5rem 1rem !important; font-size: 0.8rem !important;
    }
    .secondary-btn button:hover {
        border-color: #06b6d4 !important; color: #22d3ee !important; transform: none !important;
    }

    div[data-testid="stImage"] img {
        border-radius: 16px; border: 1px solid #1c1f26;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    }

    .result-block {
        background: linear-gradient(135deg, rgba(6,182,212,0.06) 0%, rgba(16,185,129,0.03) 100%);
        border: 1px solid #1c1f26; border-radius: 20px;
        padding: 2rem 2.2rem; margin-top: 1.5rem;
        backdrop-filter: blur(20px); position: relative; overflow: hidden;
    }
    .result-block::before {
        content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #06b6d4 0%, #10b981 100%);
    }
    .result-top {
        display: flex; align-items: center; justify-content: space-between;
        padding-bottom: 1.2rem; border-bottom: 1px solid #1c1f26; margin-bottom: 1.5rem;
    }
    .result-label {
        display: flex; align-items: center; gap: 0.6rem;
        font-size: 0.72rem; color: #94a3b8; letter-spacing: 2px;
        text-transform: uppercase; font-weight: 700;
    }
    .result-label-dot {
        width: 8px; height: 8px; background: #10b981; border-radius: 50%;
        box-shadow: 0 0 10px #10b981;
    }
    .result-time { font-size: 0.72rem; color: #475569; }
    .result-text {
        color: #e2e8f0; font-size: 1.05rem; line-height: 1.9; letter-spacing: 0.1px;
    }

    .chips-row {
        display: flex; gap: 0.5rem; flex-wrap: wrap;
        margin-top: 1rem; justify-content: center;
    }
    .chip {
        display: inline-flex; align-items: center; gap: 0.4rem;
        padding: 0.35rem 0.75rem; background: rgba(15, 17, 21, 0.8);
        border: 1px solid #1c1f26; border-radius: 999px;
        font-size: 0.75rem; color: #94a3b8; font-weight: 500;
    }
    .chip strong {color: #e2e8f0; font-weight: 600;}

    .scanning-block {
        padding: 2.5rem; background: rgba(6, 182, 212, 0.04);
        border: 1px dashed rgba(6, 182, 212, 0.3); border-radius: 20px;
        text-align: center; position: relative; overflow: hidden;
    }
    .scanning-block::before {
        content: ""; position: absolute; top: 0; left: -100%;
        width: 100%; height: 2px;
        background: linear-gradient(90deg, transparent, #06b6d4, transparent);
        animation: scanline 2s linear infinite;
    }
    @keyframes scanline { 0% { left: -100%; } 100% { left: 100%; } }
    .scanning-block .icon { font-size: 2.5rem; animation: pulse 1.8s ease-in-out infinite; display: inline-block; }
    @keyframes pulse { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.15); opacity: 0.7; } }
    .scanning-block .label {
        color: #22d3ee; font-size: 0.85rem; letter-spacing: 3px;
        text-transform: uppercase; font-weight: 700; margin-top: 1rem;
    }

    .history-time { font-size: 0.72rem; color: #64748b; letter-spacing: 0.5px; font-weight: 600; }
    .history-tags { display: flex; gap: 0.35rem; flex-wrap: wrap; }
    .history-tag {
        padding: 0.15rem 0.5rem; background: rgba(6, 182, 212, 0.1);
        border: 1px solid rgba(6, 182, 212, 0.25); border-radius: 6px;
        font-size: 0.68rem; color: #67e8f9; font-weight: 600;
    }
    .history-text {
        font-size: 0.88rem; color: #cbd5e1; line-height: 1.55;
        display: -webkit-box; -webkit-line-clamp: 2;
        -webkit-box-orient: vertical; overflow: hidden;
    }

    .empty-state { text-align: center; padding: 3rem 2rem; }
    .empty-title { font-size: 0.95rem; color: #475569; font-weight: 500; }
    .empty-icon { font-size: 2.5rem; opacity: 0.4; margin-bottom: 0.8rem; }

    .settings-title {
        font-size: 0.72rem; color: #64748b; text-transform: uppercase;
        letter-spacing: 2px; font-weight: 700; margin-bottom: 1rem;
    }
    .settings-box {
        background: rgba(15, 17, 21, 0.7);
        border: 1px solid #1c1f26;
        border-radius: 14px;
        padding: 1.5rem 1.6rem;
        margin-bottom: 1.2rem;
    }

    .success-banner {
        background: linear-gradient(135deg, rgba(16,185,129,0.15) 0%, rgba(6,182,212,0.1) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 12px;
        padding: 0.9rem 1.2rem;
        color: #4ade80;
        font-weight: 600;
        font-size: 0.92rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    p, span, div, label { color: #cbd5e1; }
    .stCaption, small { color: #64748b !important; }
    .stSpinner > div { border-top-color: #06b6d4 !important; }
    .stAlert { border-radius: 12px; background: rgba(15, 17, 21, 0.8); border: 1px solid #1c1f26; }
    hr { border-color: #1c1f26; margin: 2rem 0; }

    .app-footer {
        display: flex; align-items: center; justify-content: center; gap: 0.5rem;
        padding: 2rem 0 1rem 0; color: #3f4551; font-size: 0.78rem; letter-spacing: 1px;
    }
    .app-footer img { width: 16px; height: 16px; border-radius: 4px; opacity: 0.8; }
    .app-footer strong {color: #64748b;}

    div[data-testid="stSlider"] > div > div > div > div {
        background: linear-gradient(90deg, #06b6d4 0%, #10b981 100%) !important;
    }
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

@st.cache_resource
def get_client():
    return Groq(api_key=GROQ_API_KEY)

client = get_client()

# ============================================================
# CLEAN RESPONSE
# ============================================================

REASONING_STARTERS = [
    "the user wants", "the user is asking", "the user asked",
    "the prompt asks", "the prompt says",
    "wait,", "wait ", "looking closer", "looking at",
    "let me ", "let's ", "actually,", "hmm,", "okay,",
    "first,", "first ", "i need to", "i should", "i will", "i can", "i'll ",
    "so i", "so,", "now,", "next,", "then,", "however,",
    "but wait", "let me re-evaluate", "let me look", "let me count",
    "draft", "final decision", "refine", "correction", "alternative",
    "check constraints", "the image appears", "the image is a",
    "the image provided", "the image features", "the image shows",
    "top section", "top crop", "top part",
    "middle section", "middle crop", "middle part",
    "bottom section", "bottom crop", "bottom part",
    "panel 1", "panel 2", "panel 3",
    "subject:", "attire:", "setting:", "word count",
]

def clean_response(text):
    if not text:
        return ""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"</?think>", "", cleaned).strip()

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", cleaned) if p.strip()]
    if not paragraphs:
        return ""

    clean_paragraphs = []
    for p in paragraphs:
        lower = p.lower().strip()
        if any(lower.startswith(r) for r in REASONING_STARTERS):
            continue
        if len(p) < 40:
            continue
        markers = lower.count("wait") + lower.count("actually") + lower.count("let me")
        if markers >= 2:
            continue
        clean_paragraphs.append(p)

    if not clean_paragraphs and paragraphs:
        candidate = paragraphs[-1]
        if len(candidate) > 800:
            sentences = re.split(r"(?<=[.!?])\s+", candidate)
            candidate = " ".join(sentences[-3:])
        return candidate.strip()

    result = max(clean_paragraphs, key=len)
    result = re.sub(r"\s+", " ", result).strip()
    result = re.sub(r"^(Final answer|Answer|Description)\s*[:•\-]\s*", "", result, flags=re.IGNORECASE)
    return result

# ============================================================
# NAV
# ============================================================

st.markdown(
    f"""
    <div class="app-nav">
        <div class="nav-left">
            <div class="nav-logo"><img src="{LOGO_DATA_URI}" alt="PixelSage logo" /></div>
            <div>
                <div class="nav-brand">PixelSage</div>
                <div class="nav-sub">IMAGE ANALYSIS STUDIO</div>
            </div>
        </div>
        <div class="nav-pill"><span class="nav-pill-dot"></span> Engine Ready</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# HERO
# ============================================================

st.markdown(
    f"""
    <div class="page-hero">
        <div class="hero-logo"><img src="{LOGO_DATA_URI}" alt="PixelSage logo" /></div>
        <h1 class="page-title">See what's <span>really</span> in your photo.</h1>
        <p class="page-sub">Drop an image and PixelSage describes every detail — foreground to background.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# TABS
# ============================================================

tab_analyze, tab_history, tab_settings = st.tabs([
    "📸  Analyze",
    "📚  History",
    "⚙️  Settings"
])

# ============================================================
# TAB 1 — ANALYZE
# ============================================================

with tab_analyze:
    detail_level = st.radio(
        "Detail level",
        options=["Brief", "Standard", "Detailed"],
        index=["Brief", "Standard", "Detailed"].index(st.session_state.settings["detail_level"]),
        horizontal=True,
        label_visibility="collapsed",
        key="analyze_detail_level"
    )

    uploaded_file = st.file_uploader(
        "Upload image",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
        key="analyze_upload"
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

        analyze_clicked = st.button("🔍  Analyze Image", use_container_width=True, key="analyze_btn")

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

                system_prompt = """You are a professional image analyst. Output ONLY the final description of the image — nothing else.

ABSOLUTE RULES:
1. Write ONE continuous paragraph in plain English.
2. NEVER write your thinking, reasoning, or planning.
3. NEVER start with "The user", "Wait", "Let me", "Looking at", "The image is a", "The prompt", or any meta phrase.
4. NEVER mention the prompt, the user, panels, sections, or word count.
5. NEVER use numbered lists, bullets, or headings.
6. Just describe what is visible, in a natural human voice.
7. Flow: foreground → middle ground → background → edges → people → environment → colors → positions.
8. Start directly with the scene, like: "A smiling doctor in a white coat stands..."

Output format:
<one clean paragraph>

That's it. No preamble, no thinking, no explanation."""

                user_prompt = f"""Describe this image in {target_len}. Output ONLY one paragraph — no reasoning, no meta commentary."""

                try:
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
                        max_tokens=st.session_state.settings["max_tokens"],
                        temperature=st.session_state.settings["temperature"],
                        extra_body={"reasoning_effort": "none"}
                    )
                except Exception:
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
                        max_tokens=st.session_state.settings["max_tokens"],
                        temperature=st.session_state.settings["temperature"]
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

                    add_history_entry(image, answer, detail_level, MODEL_NAME)
                    st.success("✅ Saved to history")

            except Exception as e:
                scan_placeholder.empty()
                st.error("⚠️ Analysis failed.")
                st.code(str(e))

    else:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-title">Upload an image above to get started</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ============================================================
# TAB 2 — HISTORY
# ============================================================

with tab_history:
    history = load_history()

    if not history:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">📚</div>
                <div class="empty-title">No analyses yet</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.markdown(
                f"<p style='color:#94a3b8;font-size:0.85rem;margin-top:0.5rem;'>"
                f"<strong style='color:#e2e8f0;'>{len(history)}</strong> saved analysis"
                f"{'es' if len(history) != 1 else ''}</p>",
                unsafe_allow_html=True
            )
        with col_b:
            if st.button("🗑️ Clear All", key="clear_all_history_btn", use_container_width=True):
                clear_history()
                st.rerun()

        st.markdown("")

        for idx, entry in enumerate(history):
            thumb_path = entry.get("thumbnail", "")
            thumb_exists = Path(thumb_path).exists()

            col_thumb, col_info, col_actions = st.columns([1, 4, 1])

            with col_thumb:
                if thumb_exists:
                    st.image(thumb_path, use_container_width=True)
                else:
                    st.markdown(
                        "<div style='width:80px;height:80px;background:#1c1f26;"
                        "border-radius:10px;display:flex;align-items:center;"
                        "justify-content:center;color:#475569;'>🖼️</div>",
                        unsafe_allow_html=True
                    )

            with col_info:
                st.markdown(
                    f"""
                    <div style="padding-top:0.3rem;">
                        <div class="history-time">🕐 {entry['timestamp']}</div>
                        <div class="history-tags" style="margin-top:0.5rem;">
                            <span class="history-tag">{entry['detail_level']}</span>
                            <span class="history-tag">{entry['width']} × {entry['height']}</span>
                        </div>
                        <div class="history-text" style="margin-top:0.6rem;">{entry['description']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col_actions:
                with st.expander("👁️ View"):
                    st.markdown(
                        f"<div style='font-size:0.9rem;color:#cbd5e1;"
                        f"line-height:1.7;'>{entry['description']}</div>",
                        unsafe_allow_html=True
                    )
                    st.code(entry['description'], language=None)

                if st.button("🗑️ Delete", key=f"del_hist_{idx}_{entry['id']}", use_container_width=True):
                    delete_history_entry(entry['id'])
                    st.rerun()

            st.markdown("---")

# ============================================================
# TAB 3 — SETTINGS
# ============================================================

with tab_settings:

    # Success message (persists across one rerun)
    if st.session_state.settings_saved_msg:
        st.markdown(
            '<div class="success-banner">✅ Settings saved successfully</div>',
            unsafe_allow_html=True
        )
        st.session_state.settings_saved_msg = False

    if st.session_state.settings_reset_msg:
        st.markdown(
            '<div class="success-banner">✅ Reset to defaults</div>',
            unsafe_allow_html=True
        )
        st.session_state.settings_reset_msg = False

    # ---- Analysis preferences ----
    st.markdown('<div class="settings-title">⚙️ Analysis Preferences</div>', unsafe_allow_html=True)

    st.markdown("**Default detail level**")
    selected_detail = st.radio(
        "Default detail level",
        options=["Brief", "Standard", "Detailed"],
        index=["Brief", "Standard", "Detailed"].index(st.session_state.settings["detail_level"]),
        horizontal=True,
        label_visibility="collapsed",
        key="settings_detail_radio"
    )

    st.markdown("")
    st.markdown("**Creativity (temperature)**")
    st.caption("Lower = more focused. Higher = more creative.")
    selected_temp = st.slider(
        "Temperature",
        min_value=0.0, max_value=1.0,
        value=float(st.session_state.settings["temperature"]),
        step=0.05,
        label_visibility="collapsed",
        key="settings_temp_slider"
    )
    st.caption(f"Current: **{selected_temp}**")

    st.markdown("")
    st.markdown("**Maximum response length (tokens)**")
    st.caption("Higher = longer output.")
    selected_tokens = st.slider(
        "Max tokens",
        min_value=300, max_value=2000,
        value=int(st.session_state.settings["max_tokens"]),
        step=100,
        label_visibility="collapsed",
        key="settings_tokens_slider"
    )
    st.caption(f"Current: **{selected_tokens}** tokens")

    st.markdown("")

    # ---- Action buttons ----
    col_save, col_reset = st.columns(2)

    with col_save:
        if st.button("💾  Save Settings", use_container_width=True, key="btn_save_settings"):
            new_settings = {
                "detail_level": selected_detail,
                "temperature": selected_temp,
                "max_tokens": selected_tokens,
            }
            st.session_state.settings = new_settings
            save_settings_file(new_settings)
            st.session_state.settings_saved_msg = True
            st.rerun()

    with col_reset:
        if st.button("↺  Reset to Defaults", use_container_width=True, key="btn_reset_settings"):
            st.session_state.settings = DEFAULT_SETTINGS.copy()
            save_settings_file(DEFAULT_SETTINGS)
            st.session_state.settings_reset_msg = True
            st.rerun()

    st.markdown("---")

    # ---- Current saved settings display ----
    st.markdown('<div class="settings-title">📋 Currently Saved</div>', unsafe_allow_html=True)

    current = st.session_state.settings
    st.markdown(
        f"""
        <div class="settings-box">
            <div style="display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid #1c1f26;">
                <span style="color:#94a3b8;">Detail level</span>
                <strong style="color:#e2e8f0;">{current['detail_level']}</strong>
            </div>
            <div style="display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid #1c1f26;">
                <span style="color:#94a3b8;">Temperature</span>
                <strong style="color:#e2e8f0;">{current['temperature']}</strong>
            </div>
            <div style="display:flex;justify-content:space-between;padding:0.5rem 0;">
                <span style="color:#94a3b8;">Max tokens</span>
                <strong style="color:#e2e8f0;">{current['max_tokens']}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # ---- About ----
    st.markdown('<div class="settings-title">ℹ️ About</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        **PixelSage** — Image Analysis Studio

        - **Model:** `{MODEL_NAME}`
        - **Engine:** Groq API
        - **History:** Last 30 analyses
        - **Storage:** Local JSON files
        """
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    f"""
    <div class="app-footer">
        <img src="{LOGO_DATA_URI}" alt="PixelSage" />
        <strong>PixelSage</strong> · Snap it · See it · Understand it
    </div>
    """,
    unsafe_allow_html=True
)
