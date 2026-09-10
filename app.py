import streamlit as st
from groq import Groq
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
import os
import re
import time

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PagePulse — Website Scanner",
    page_icon="📡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS — Live scanner theme (cyan/emerald on deep navy)
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
        font-size: 2.6rem;
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
        letter-spacing: 2px;
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
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Input */
    .stTextInput input {
        background: rgba(15, 23, 42, 0.7) !important;
        border: 1.5px solid #1e293b !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        padding: 0.85rem 1.1rem !important;
        font-size: 1rem !important;
        backdrop-filter: blur(10px);
    }
    .stTextInput input:focus {
        border-color: #06b6d4 !important;
        box-shadow: 0 0 0 4px rgba(6, 182, 212, 0.15) !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 1.6rem;
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

    /* Score card */
    .score-card {
        background: linear-gradient(135deg, rgba(6,182,212,0.08) 0%, rgba(16,185,129,0.05) 100%);
        border: 1px solid rgba(6, 182, 212, 0.3);
        border-radius: 20px;
        padding: 2.5rem 2rem;
        text-align: center;
        margin: 1rem 0;
        backdrop-filter: blur(20px);
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.05),
            0 20px 60px rgba(0, 0, 0, 0.4);
    }
    .score-value {
        font-size: 5rem;
        font-weight: 900;
        line-height: 1;
        background: linear-gradient(135deg, #06b6d4 0%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 4px 20px rgba(6, 182, 212, 0.4));
    }
    .score-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-top: 0.8rem;
        font-weight: 600;
    }
    .score-note {
        font-size: 1.05rem;
        color: #22d3ee;
        margin-top: 1.2rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Metric bars */
    .metric-row {
        margin: 1.1rem 0;
    }
    .metric-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    .metric-name { color: #cbd5e1; font-weight: 500; }
    .metric-value { color: #22d3ee; font-variant-numeric: tabular-nums; font-weight: 600; }
    .metric-bar {
        width: 100%;
        height: 10px;
        background: rgba(30, 41, 59, 0.8);
        border-radius: 999px;
        overflow: hidden;
        position: relative;
    }
    .metric-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #06b6d4 0%, #10b981 100%);
        box-shadow: 0 0 12px rgba(6, 182, 212, 0.6);
        transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Info grid */
    .info-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.85rem;
        margin-top: 1rem;
    }
    .info-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        backdrop-filter: blur(10px);
        transition: all 0.2s ease;
    }
    .info-card:hover {
        border-color: rgba(6, 182, 212, 0.4);
        transform: translateY(-2px);
    }
    .info-label {
        font-size: 0.68rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 0.4rem;
        font-weight: 600;
    }
    .info-value {
        font-size: 1rem;
        color: #f1f5f9;
        font-weight: 700;
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

    /* Suggestion list */
    .suggestion-item {
        background: rgba(15, 23, 42, 0.7);
        border-left: 3px solid #10b981;
        padding: 1rem 1.3rem;
        margin: 0.7rem 0;
        border-radius: 10px;
        color: #e2e8f0;
        font-size: 0.98rem;
        backdrop-filter: blur(10px);
        transition: all 0.2s ease;
        line-height: 1.6;
    }
    .suggestion-item:hover {
        border-left-color: #22d3ee;
        transform: translateX(4px);
        background: rgba(15, 23, 42, 0.95);
    }
    .suggestion-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: #ffffff;
        font-weight: 800;
        font-size: 0.75rem;
        width: 22px;
        height: 22px;
        border-radius: 6px;
        margin-right: 0.75rem;
        box-shadow: 0 2px 8px rgba(6, 182, 212, 0.4);
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
# SCRAPER + ANALYZER
# ============================================================

def normalize_url(url):
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response

def analyze_html(html, url):
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    meta_desc = ""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        meta_desc = meta["content"]

    h1_count = len(soup.find_all("h1"))
    h2_count = len(soup.find_all("h2"))
    h3_count = len(soup.find_all("h3"))

    images = soup.find_all("img")
    total_images = len(images)
    images_with_alt = sum(1 for img in images if img.get("alt"))

    links = soup.find_all("a")
    total_links = len(links)
    internal_links = sum(
        1 for a in links
        if a.get("href", "").startswith(("/", "#")) or urlparse(url).netloc in a.get("href", "")
    )
    external_links = total_links - internal_links

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    body_text = soup.get_text(separator=" ", strip=True)
    word_count = len(body_text.split())

    html_tag = soup.find("html")
    lang = html_tag.get("lang", "unknown") if html_tag else "unknown"

    viewport = soup.find("meta", attrs={"name": "viewport"})
    og_title = soup.find("meta", property="og:title")
    og_desc = soup.find("meta", property="og:description")

    return {
        "url": url,
        "title": title,
        "title_length": len(title),
        "meta_description": meta_desc,
        "meta_desc_length": len(meta_desc),
        "h1_count": h1_count,
        "h2_count": h2_count,
        "h3_count": h3_count,
        "total_images": total_images,
        "images_with_alt": images_with_alt,
        "total_links": total_links,
        "internal_links": internal_links,
        "external_links": external_links,
        "word_count": word_count,
        "lang": lang,
        "has_viewport": bool(viewport),
        "has_og_title": bool(og_title),
        "has_og_desc": bool(og_desc),
        "body_preview": body_text[:1500]
    }

def calculate_scores(data):
    scores = {}

    seo = 100
    if not data["title"]: seo -= 25
    elif data["title_length"] < 30 or data["title_length"] > 60: seo -= 10
    if not data["meta_description"]: seo -= 25
    elif data["meta_desc_length"] < 120 or data["meta_desc_length"] > 160: seo -= 10
    if data["h1_count"] == 0: seo -= 20
    elif data["h1_count"] > 1: seo -= 10
    if not data["has_og_title"]: seo -= 5
    if not data["has_og_desc"]: seo -= 5
    scores["SEO"] = max(0, min(100, seo))

    content = 100
    wc = data["word_count"]
    if wc < 300: content -= 40
    elif wc < 600: content -= 20
    if data["h2_count"] < 2: content -= 15
    if data["h3_count"] < 1: content -= 10
    scores["Content"] = max(0, min(100, content))

    accessibility = 100
    if data["total_images"] > 0:
        alt_ratio = data["images_with_alt"] / data["total_images"]
        accessibility = int(alt_ratio * 100)
    if data["lang"] == "unknown": accessibility -= 10
    scores["Accessibility"] = max(0, min(100, accessibility))

    mobile = 100
    if not data["has_viewport"]: mobile -= 50
    scores["Mobile"] = max(0, min(100, mobile))

    links_score = 100
    if data["total_links"] < 5: links_score -= 20
    if data["internal_links"] == 0: links_score -= 30
    if data["external_links"] == 0: links_score -= 20
    scores["Links"] = max(0, min(100, links_score))

    scores["Overall"] = int(sum(scores.values()) / len(scores))
    return scores

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 📡 PagePulse")
    st.markdown(
        "<p style='font-size:0.8rem;color:#64748b;margin-top:-0.5rem;'>"
        "Website Scanner</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    st.markdown("### 🔎 What It Scans")
    st.markdown(
        """
        - Title & meta description
        - Heading structure
        - Image alt tags
        - Internal / external links
        - Word count & depth
        - Mobile viewport
        - Open Graph tags
        - Language attribute
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
        <div class="hero-mark">📡</div>
        <h1 class="hero-title">PagePulse</h1>
        <div class="hero-sub">Website Scanner</div>
        <div class="hero-tagline">Scan it · Analyze it · Improve it</div>
        <div class="status-pill">
            <span class="status-dot"></span> Scanner Ready
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# STEP 1 — URL INPUT
# ============================================================

st.markdown(
    '<div class="section-label">📡 01 · Target URL</div>',
    unsafe_allow_html=True
)

url_input = st.text_input(
    "URL",
    placeholder="https://example.com",
    label_visibility="collapsed"
)

scan_clicked = st.button("📡  Scan Website", use_container_width=True)

# ============================================================
# STEP 2 — ANALYSIS
# ============================================================

if scan_clicked and url_input.strip():
    url = normalize_url(url_input)

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
        response = fetch_page(url)
        html = response.text
        data = analyze_html(html, url)
        scores = calculate_scores(data)

        # Clear scanning animation
        scan_placeholder.empty()

        # --------------------------------------------------
        # Section 02 · Report
        # --------------------------------------------------
        st.markdown(
            '<div class="section-label">📊 02 · Report</div>',
            unsafe_allow_html=True
        )

        # Score card
        overall = scores["Overall"]
        if overall >= 85: note = "Excellent · Well optimized"
        elif overall >= 70: note = "Good · Minor improvements needed"
        elif overall >= 50: note = "Average · Needs improvement"
        else: note = "Poor · Significant work needed"

        st.markdown(
            f"""
            <div class="score-card">
                <div class="score-value">{overall}</div>
                <div class="score-label">Overall Score</div>
                <div class="score-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # --------------------------------------------------
        # Score breakdown
        # --------------------------------------------------
        st.markdown(
            '<div class="section-label">📈 Score Breakdown</div>',
            unsafe_allow_html=True
        )

        metrics_html = ""
        for name in ["SEO", "Content", "Accessibility", "Mobile", "Links"]:
            val = scores[name]
            metrics_html += f"""
            <div class="metric-row">
                <div class="metric-header">
                    <span class="metric-name">{name}</span>
                    <span class="metric-value">{val}/100</span>
                </div>
                <div class="metric-bar">
                    <div class="metric-fill" style="width:{val}%;"></div>
                </div>
            </div>
            """
        st.markdown(metrics_html, unsafe_allow_html=True)

        # --------------------------------------------------
        # Page info
        # --------------------------------------------------
        st.markdown(
            '<div class="section-label">🔍 Page Details</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="info-grid">
                <div class="info-card">
                    <div class="info-label">Title Length</div>
                    <div class="info-value">{data['title_length']} chars</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Meta Desc</div>
                    <div class="info-value">{data['meta_desc_length']} chars</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Word Count</div>
                    <div class="info-value">{data['word_count']:,}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Images</div>
                    <div class="info-value">{data['total_images']}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Links</div>
                    <div class="info-value">{data['total_links']}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Language</div>
                    <div class="info-value">{data['lang']}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # --------------------------------------------------
        # AI Analysis
        # --------------------------------------------------
        st.markdown(
            '<div class="section-label">🤖 AI Analysis</div>',
            unsafe_allow_html=True
        )

        with st.spinner("Generating AI insights..."):
            analysis_prompt = f"""You are an expert web analyst. Analyze the following page and give a professional report.

PAGE DATA:
- URL: {data['url']}
- Title: "{data['title']}" ({data['title_length']} chars)
- Meta description: "{data['meta_description']}" ({data['meta_desc_length']} chars)
- H1 count: {data['h1_count']}
- H2 count: {data['h2_count']}
- H3 count: {data['h3_count']}
- Images: {data['total_images']} (with alt: {data['images_with_alt']})
- Total links: {data['total_links']} (internal: {data['internal_links']}, external: {data['external_links']})
- Word count: {data['word_count']}
- Language: {data['lang']}
- Viewport meta: {data['has_viewport']}
- Open Graph title: {data['has_og_title']}
- Open Graph description: {data['has_og_desc']}
- Content preview: "{data['body_preview']}"

Write a report in EXACTLY this format (no extra sections):

SUMMARY:
<2-3 sentences describing the page and its overall quality.>

TOP 5 IMPROVEMENTS:
1. <specific, actionable improvement>
2. <specific, actionable improvement>
3. <specific, actionable improvement>
4. <specific, actionable improvement>
5. <specific, actionable improvement>

RULES:
- Do NOT show reasoning or thinking.
- Do NOT use phrases like "Let me", "Okay", "Wait".
- Only output the SUMMARY and TOP 5 IMPROVEMENTS sections.
- Be specific and practical."""

            response_ai = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=900,
                temperature=0.3
            )

            ai_text = response_ai.choices[0].message.content
            ai_text = clean_response(ai_text)

            summary_match = re.search(
                r"SUMMARY:\s*(.+?)(?=TOP 5 IMPROVEMENTS:|$)",
                ai_text, re.DOTALL | re.IGNORECASE
            )
            improvements_match = re.search(
                r"TOP 5 IMPROVEMENTS:\s*(.+?)$",
                ai_text, re.DOTALL | re.IGNORECASE
            )

            summary = summary_match.group(1).strip() if summary_match else ai_text
            improvements_raw = improvements_match.group(1).strip() if improvements_match else ""

            # Summary card
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.markdown(
                f"""
                <div class="result-card">
                    <div class="result-header">
                        <div class="result-header-title">📝 Summary</div>
                        <div class="result-meta">{timestamp}</div>
                    </div>
                    {summary}
                </div>
                """,
                unsafe_allow_html=True
            )

            # Improvements
            if improvements_raw:
                st.markdown(
                    '<div class="section-label">💡 Top 5 Improvements</div>',
                    unsafe_allow_html=True
                )

                improvements = re.split(r"\n(?=\d+\.)", improvements_raw)
                for item in improvements:
                    item = item.strip()
                    if not item:
                        continue
                    match = re.match(r"(\d+)\.\s*(.+)", item, re.DOTALL)
                    if match:
                        num, text = match.groups()
                        text = re.sub(r"\s+", " ", text).strip()
                        st.markdown(
                            f'<div class="suggestion-item">'
                            f'<span class="suggestion-num">{num}</span>{text}'
                            f'</div>',
                            unsafe_allow_html=True
                        )

            # Copy option
            with st.expander("📋 View full report as plain text"):
                st.code(ai_text, language=None)

    except requests.exceptions.Timeout:
        scan_placeholder.empty()
        st.error("⏱️ Request timed out. The site took too long to respond.")
    except requests.exceptions.ConnectionError:
        scan_placeholder.empty()
        st.error("🌐 Could not connect. Check the URL.")
    except requests.exceptions.HTTPError as e:
        scan_placeholder.empty()
        st.error(f"❌ HTTP error: {e.response.status_code}")
    except Exception as e:
        scan_placeholder.empty()
        st.error("⚠️ Analysis failed.")
        st.code(str(e))

elif scan_clicked and not url_input.strip():
    st.warning("Please enter a URL first.")

else:
    st.markdown(
        """
        <div class="placeholder-card">
            <div class="placeholder-icon">📡</div>
            <div>Paste a URL above and click <b>Scan Website</b> to start</div>
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
    "📡 PagePulse · Scan it · Analyze it · Improve it"
    "</p>",
    unsafe_allow_html=True
)
