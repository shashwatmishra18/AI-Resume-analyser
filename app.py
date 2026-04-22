"""
AI Resume Analyzer & Enhancer
=============================
A Streamlit-based web application that analyzes resumes using Google Gemini AI
and provides ATS compatibility scores, strengths, missing skills, and
actionable improvement suggestions.

Usage:
    streamlit run app.py
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv

from utils.parser import extract_text
from utils.analyzer import analyze_resume, configure_gemini, compute_ats_score
from utils.ui_components import render_ats_score, render_section, render_summary

# ---------------------------------------------------------------------------
# 1. Load environment variables FIRST — before any Streamlit calls
# ---------------------------------------------------------------------------
# Try loading from .env in the project root
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Read API key from environment (set by .env or system env)
ENV_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# ---------------------------------------------------------------------------
# 2. Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="auto",
)

# ---------------------------------------------------------------------------
# 3. Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* ---- Global Overrides ---- */
    .stApp {
        background: linear-gradient(180deg, #0a192f 0%, #0d1b30 50%, #112240 100%);
    }

    /* Header */
    .main-header {
        text-align: center;
        padding: 20px 0 10px 0;
    }
    .main-header h1 {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #64ffda 0%, #48c9b0 50%, #c792ea 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0;
    }
    .main-header p {
        color: #8892b0;
        font-size: 1.05rem;
        margin-top: 6px;
    }

    /* Divider */
    .gradient-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #64ffda, transparent);
        margin: 10px 0 30px 0;
        border: none;
    }

    /* Upload area */
    [data-testid="stFileUploader"] {
        border-radius: 12px;
    }

    /* Buttons — enabled state */
    .stButton > button {
        background: linear-gradient(135deg, #64ffda 0%, #48c9b0 100%) !important;
        color: #0a192f !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.6rem 2rem !important;
        border: none !important;
        border-radius: 8px !important;
        width: 100%;
        transition: all 0.3s ease !important;
        letter-spacing: 0.5px;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(100, 255, 218, 0.3) !important;
    }
    /* Buttons — disabled state */
    .stButton > button:disabled {
        background: #233554 !important;
        color: #8892b0 !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: #1a1a2e;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        border: 1px solid #233554;
    }

    /* API key status badge */
    .api-status {
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
        margin-top: 4px;
    }
    .api-connected {
        background: #00C85122;
        color: #00C851;
        border: 1px solid #00C85155;
    }
    .api-missing {
        background: #ff444422;
        color: #ff4444;
        border: 1px solid #ff444455;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 4. Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>📄 AI Resume Analyzer</h1>
    <p>Upload your resume and get instant AI-powered feedback to boost your job application</p>
</div>
<div class="gradient-divider"></div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 5. API Key Resolution — .env first, sidebar fallback
# ---------------------------------------------------------------------------
def get_api_key() -> str:
    """Resolve the API key with priority: .env > sidebar input.

    Returns the active API key string (may be empty if none provided).
    """
    # Priority 1: .env / system environment variable
    if ENV_API_KEY:
        return ENV_API_KEY

    # Priority 2: Sidebar input (stored in session state)
    return st.session_state.get("sidebar_api_key", "")


with st.sidebar:
    st.markdown("### ⚙️ Settings")

    if ENV_API_KEY:
        # Key loaded from .env — show confirmation, no need for manual input
        st.markdown(
            '<span class="api-status api-connected">✅ API key loaded from .env</span>',
            unsafe_allow_html=True,
        )
        st.caption("To change, update `GEMINI_API_KEY` in your `.env` file.")
    else:
        # No .env key — show input field
        st.markdown(
            '<span class="api-status api-missing">⚠️ No API key in .env</span>',
            unsafe_allow_html=True,
        )
        st.text_input(
            "Enter Gemini API Key",
            type="password",
            key="sidebar_api_key",
            help="Get your free API key from https://aistudio.google.com/apikey",
        )
        st.markdown(
            "[🔑 Get a free Gemini API key](https://aistudio.google.com/apikey)",
        )

    st.markdown("---")
    st.markdown("Built with ❤️ using **Streamlit** & **Google Gemini**")

# Resolve the active key
active_api_key = get_api_key()
has_api_key = bool(active_api_key)

# ---------------------------------------------------------------------------
# 6. Main Input Form
# ---------------------------------------------------------------------------
col1, col2 = st.columns([3, 2])

with col1:
    uploaded_file = st.file_uploader(
        "📎 Upload your Resume",
        type=["pdf", "docx"],
        help="Supported formats: PDF, DOCX (max 10 MB)",
    )

with col2:
    job_role = st.text_input(
        "🎯 Target Job Role",
        placeholder="e.g., Software Engineer, Data Analyst",
        help="Enter the role you're applying for",
    )

# Show warning if no API key — but don't break the app
if not has_api_key:
    st.warning(
        "⚠️ **No API key detected.** Add `GEMINI_API_KEY` to a `.env` file "
        "in the project root, or enter it in the sidebar. "
        "[Get a free key →](https://aistudio.google.com/apikey)"
    )

# ---------------------------------------------------------------------------
# 7. Analyze Button — disabled when no API key
# ---------------------------------------------------------------------------
analyze_clicked = st.button(
    "🚀 Analyze Resume",
    use_container_width=True,
    disabled=not has_api_key,
)

if analyze_clicked:
    # --- Validation ---
    if not uploaded_file:
        st.warning("⚠️ Please upload your resume first.")
        st.stop()
    if not job_role.strip():
        st.warning("⚠️ Please enter a target job role.")
        st.stop()

    # --- Configure Gemini once ---
    configure_gemini(active_api_key)

    # --- Step 1: Extract Text ---
    with st.spinner("📖 Extracting text from resume..."):
        try:
            resume_text = extract_text(uploaded_file)
        except Exception as e:
            st.error(f"❌ Failed to extract text: {e}")
            st.stop()

        if not resume_text.strip():
            st.error(
                "❌ No text could be extracted from the file. "
                "It may be scanned/image-based."
            )
            st.stop()

    st.success(f"✅ Extracted **{len(resume_text.split())}** words from resume.")

    # --- Step 2: Local ATS Keyword Score ---
    with st.spinner("🔑 Computing ATS keyword score..."):
        ats_local = compute_ats_score(resume_text, job_role.strip())

    # --- Step 3: AI Analysis ---
    with st.spinner("🤖 Running AI analysis with Gemini..."):
        try:
            results = analyze_resume(resume_text, job_role.strip())
        except Exception as e:
            st.error(f"❌ AI analysis failed. Please check your API key or try again.\n\n{e}")
            st.stop()

    # -----------------------------------------------------------------
    # DISPLAY RESULTS
    # -----------------------------------------------------------------
    st.markdown("---")
    st.markdown(
        "<h2 style='text-align:center; color:#ccd6f6;'>📊 Analysis Results</h2>",
        unsafe_allow_html=True,
    )
    st.markdown("")

    # --- ATS Scores (AI + Local) ---
    score_col1, score_col2 = st.columns(2)

    with score_col1:
        render_ats_score(
            score=results.get("ats_score", 0),
            breakdown=results.get("score_breakdown"),
            label="AI ATS Score",
        )

    with score_col2:
        render_ats_score(
            score=ats_local["score"],
            label="Keyword Match Score",
        )

    st.markdown("")

    # --- Local keyword details ---
    with st.expander(f"🔑 Keyword Match Details — {len(ats_local['matched'])} matched, {len(ats_local['missing'])} missing"):
        kw_col1, kw_col2 = st.columns(2)
        with kw_col1:
            st.markdown("**✅ Matched Keywords:**")
            for kw in ats_local["matched"]:
                st.markdown(f"&nbsp;&nbsp;• {kw}")
        with kw_col2:
            st.markdown("**❌ Missing Keywords:**")
            for kw in ats_local["missing"]:
                st.markdown(f"&nbsp;&nbsp;• {kw}")

    st.markdown("")

    # --- Summary ---
    if results.get("summary"):
        render_summary(results["summary"])

    # --- Strengths & Missing Skills ---
    col_left, col_right = st.columns(2)

    with col_left:
        render_section(
            title="💪 Key Strengths",
            items=results.get("key_strengths", ["No strengths identified."]),
            icon="✅",
            color="#64ffda",
        )

    with col_right:
        render_section(
            title="⚠️ Missing Skills",
            items=results.get("missing_skills", ["No missing skills identified."]),
            icon="❌",
            color="#ff6b6b",
        )

    # --- Improvement Suggestions ---
    render_section(
        title="💡 Improvement Suggestions",
        items=results.get("improvement_suggestions", ["No suggestions."]),
        icon="➡️",
        color="#ffbb33",
    )

    # --- Expandable: Raw Resume Text ---
    with st.expander("📝 View Extracted Resume Text"):
        st.text(resume_text)
