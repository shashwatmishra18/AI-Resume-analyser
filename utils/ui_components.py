"""
Reusable Streamlit UI components for displaying analysis results.
"""

import streamlit as st


def render_ats_score(score: int, breakdown: dict = None, label: str = "ATS Compatibility Score"):
    """Display the ATS compatibility score with a visual gauge.

    Args:
        score: ATS score from 0-100.
        breakdown: Optional dict with sub-scores for detailed view.
        label: Header label for the score card.
    """
    # Color based on score range
    if score >= 80:
        color = "#00C851"
        status = "Excellent"
        emoji = "🟢"
    elif score >= 60:
        color = "#ffbb33"
        status = "Good"
        emoji = "🟡"
    elif score >= 40:
        color = "#ff8800"
        status = "Needs Work"
        emoji = "🟠"
    else:
        color = "#ff4444"
        status = "Poor"
        emoji = "🔴"

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        border: 1px solid {color}33;
        box-shadow: 0 0 30px {color}22;
    ">
        <p style="font-size: 13px; color: #8892b0; margin-bottom: 8px; letter-spacing: 2px; text-transform: uppercase;">
            {label}
        </p>
        <h1 style="
            font-size: 64px;
            font-weight: 800;
            color: {color};
            margin: 0;
            line-height: 1;
            text-shadow: 0 0 20px {color}44;
        ">{score}</h1>
        <p style="font-size: 13px; color: #8892b0; margin-top: 4px;">out of 100</p>
        <p style="
            font-size: 16px;
            color: {color};
            font-weight: 600;
            margin-top: 8px;
        ">{emoji} {status}</p>
    </div>
    """, unsafe_allow_html=True)

    # Score breakdown
    if breakdown:
        st.markdown("#### 📊 Score Breakdown")
        cols = st.columns(4)
        breakdown_labels = {
            "keyword_relevance": ("🔑", "Keywords"),
            "experience_match": ("💼", "Experience"),
            "skills_alignment": ("🎯", "Skills"),
            "formatting_clarity": ("📝", "Formatting"),
        }
        for i, (key, (icon, lbl)) in enumerate(breakdown_labels.items()):
            value = breakdown.get(key, 0)
            with cols[i]:
                st.metric(label=f"{icon} {lbl}", value=f"{value}/25")


def render_section(title: str, items: list, icon: str = "•", color: str = "#64ffda"):
    """Display a section with bullet points.

    Args:
        title: Section heading.
        items: List of strings to display as bullet points.
        icon: Emoji/character to use as bullet.
        color: Accent color for the section header.
    """
    st.markdown(f"""
    <h3 style="
        color: {color};
        border-bottom: 2px solid {color}33;
        padding-bottom: 8px;
        margin-top: 24px;
    ">{title}</h3>
    """, unsafe_allow_html=True)

    for item in items:
        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{icon}&nbsp; {item}")


def render_summary(summary: str):
    """Display the overall assessment summary.

    Args:
        summary: Summary text from the AI analysis.
    """
    st.markdown("""
    <h3 style="
        color: #c792ea;
        border-bottom: 2px solid #c792ea33;
        padding-bottom: 8px;
        margin-top: 24px;
    ">📋 Overall Assessment</h3>
    """, unsafe_allow_html=True)

    st.info(summary)
