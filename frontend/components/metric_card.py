"""
Komponen metric card untuk Dashboard dan Calculator.
"""
import streamlit as st


def metric_card(label: str, value: str, sub: str = "", badge: str = "", badge_type: str = "green"):
    """
    Render metric card dengan styling kustom.
    badge_type: 'green' | 'blue'
    """
    badge_html = ""
    if badge:
        cls = "badge-green" if badge_type == "green" else "badge-blue"
        badge_html = f'<span class="badge {cls}">{badge}</span>'

    progress_html = ""
    # Jika sub berisi "/", tampilkan progress bar (misal "84/144")
    if "/" in sub:
        try:
            parts = sub.replace(" ", "").split("/")
            current_val = float(parts[0])
            max_val = float(parts[1])
            pct = min(int((current_val / max_val) * 100), 100)
            progress_html = f"""
            <div class="progress-bar-wrap">
                <div class="progress-bar-fill" style="width:{pct}%"></div>
            </div>
            """
        except Exception:
            pass

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}{badge_html}</div>
            <div class="sub">{sub}</div>
            {progress_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
