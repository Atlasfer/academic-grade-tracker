GLOBAL_CSS = """
<style>
/* GLOBAL & LAYOUT */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1100px;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #1a2332;
    border-right: none;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: none;
    color: #94a3b8 !important;
    font-size: 0.9rem;
    text-align: left;
    width: 100%;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    transition: background 0.2s;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.08);
    color: #fff !important;
}

/* METRIC CARDS */
.metric-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.metric-card .label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 0.35rem;
}

.metric-card .value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.1;
}

.metric-card .sub {
    font-size: 0.78rem;
    color: #64748b;
    margin-top: 0.3rem;
}

.metric-card .badge-green {
    display: inline-block;
    background: #dcfce7;
    color: #16a34a;
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-left: 6px;
}

.metric-card .badge-blue {
    display: inline-block;
    background: #dbeafe;
    color: #2563eb;
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-left: 6px;
}

/* SECTION HEADERS */
.section-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.25rem;
}

.section-sub {
    font-size: 0.82rem;
    color: #64748b;
    margin-bottom: 1rem;
}

/* TABEL KUSTOM */
.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
}

.custom-table th {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #64748b;
    padding: 0.6rem 0.75rem;
    border-bottom: 1px solid #e2e8f0;
    text-align: left;
}

.custom-table td {
    padding: 0.75rem 0.75rem;
    border-bottom: 1px solid #f1f5f9;
    color: #1e293b;
    vertical-align: middle;
}

.custom-table tr:last-child td {
    border-bottom: none;
}

.custom-table tr:hover td {
    background: #f8fafc;
}

/* BADGE STATUS */
.badge {
    display: inline-block;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 600;
}

.badge-passed   { background: #dcfce7; color: #16a34a; }
.badge-core     { background: #dcfce7; color: #15803d; }
.badge-elective { background: #e0e7ff; color: #4338ca; }
.badge-ongoing  { background: #fef9c3; color: #92400e; }
.badge-grade    {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px; height: 32px;
    border-radius: 50%;
    font-weight: 700;
    font-size: 0.82rem;
}
.grade-a    { background: #dcfce7; color: #16a34a; }
.grade-ab   { background: #d1fae5; color: #059669; }
.grade-b    { background: #dbeafe; color: #2563eb; }
.grade-bc   { background: #e0e7ff; color: #4338ca; }
.grade-c    { background: #fef9c3; color: #92400e; }
.grade-d    { background: #fee2e2; color: #dc2626; }
.grade-e    { background: #fecaca; color: #b91c1c; }

/* SEMESTER ACCORDION */
.semester-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.semester-card-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.semester-number {
    background: #1e293b;
    color: #fff;
    border-radius: 6px;
    width: 32px; height: 32px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.9rem;
    flex-shrink: 0;
}

/* SIMULATION RESULT CARD */
.sim-result-card {
    background: #1a2332;
    color: #fff;
    border-radius: 12px;
    padding: 1.75rem;
    text-align: center;
}

.sim-result-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 0.5rem;
}

.sim-result-value {
    font-size: 3.5rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1;
    margin-bottom: 0.75rem;
}

.sim-result-desc {
    font-size: 0.82rem;
    color: #94a3b8;
    margin-bottom: 1.25rem;
}

.sim-badge-achievable {
    display: inline-block;
    background: #16a34a;
    color: #fff;
    border-radius: 20px;
    padding: 0.4rem 1.25rem;
    font-size: 0.85rem;
    font-weight: 600;
}

.sim-badge-not-achievable {
    display: inline-block;
    background: #dc2626;
    color: #fff;
    border-radius: 20px;
    padding: 0.4rem 1.25rem;
    font-size: 0.85rem;
    font-weight: 600;
}

/* INSIGHT CARD (Simulation tips) */
.insight-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem 1.1rem;
    height: 100%;
}

.insight-card .insight-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 0.4rem;
}

.insight-card .insight-body {
    font-size: 0.8rem;
    color: #64748b;
    line-height: 1.5;
}

/* PROFILE BOX (Sidebar) */
.profile-box {
    background: rgba(255,255,255,0.07);
    border-radius: 8px;
    padding: 0.65rem 0.85rem;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.profile-avatar {
    width: 36px; height: 36px;
    border-radius: 50%;
    background: #334155;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    color: #e2e8f0;
    flex-shrink: 0;
}

.profile-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: #f1f5f9;
}

.profile-nim {
    font-size: 0.72rem;
    color: #94a3b8;
}

/* PROGRESS BAR CUSTOM */
.progress-bar-wrap {
    background: #e2e8f0;
    border-radius: 4px;
    height: 6px;
    width: 100%;
    margin-top: 0.4rem;
}

.progress-bar-fill {
    height: 6px;
    border-radius: 4px;
    background: #16a34a;
}

/* UPLOAD ZONE */
.upload-zone {
    border: 2px dashed #cbd5e1;
    border-radius: 12px;
    padding: 2.5rem;
    text-align: center;
    background: #f8fafc;
    color: #64748b;
    font-size: 0.9rem;
}

.upload-zone .upload-icon {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

/* NOTIFICATION BARS */
.notif-success {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    color: #166534;
    font-size: 0.88rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.notif-warning {
    background: #fff7ed;
    border: 1px solid #fdba74;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    color: #9a3412;
    font-size: 0.88rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

/* DIVIDER */
.divider {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 1.25rem 0;
}

/* HIDE STREAMLIT BRANDING */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
[data-testid="stDecoration"] {display: none;}
[data-testid="stStatusWidget"] {visibility: hidden;}
[data-testid="collapsedControl"] {
    visibility: visible !important;
    display: flex !important;
}

[data-testid="stSidebar"][aria-expanded="false"] {
    margin-left: 0 !important;
    transform: none !important;
    min-width: 15rem !important;
    width: 15rem !important;
}

[data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
    width: 15rem !important;
}
</style>
"""


def grade_css_class(nilai_huruf: str | None) -> str:
    """Kembalikan CSS class untuk badge nilai huruf."""
    mapping = {
        "A": "grade-a", "AB": "grade-ab", "B": "grade-b",
        "BC": "grade-bc", "C": "grade-c", "D": "grade-d", "E": "grade-e",
    }
    return mapping.get(nilai_huruf or "", "grade-a")
