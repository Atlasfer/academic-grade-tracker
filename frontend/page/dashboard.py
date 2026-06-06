import streamlit as st
import plotly.graph_objects as go
from utils import api_client
from utils.api_client import APIError
from utils.helpers import format_ipk, semester_label, h
from components.metric_card import metric_card


def render():
    mahasiswa_id = st.session_state.mahasiswa_id
    nama = st.session_state.mahasiswa_nama

    st.markdown(
        "<div class='section-header'>Dashboard Overview</div>"
        f"<div class='section-sub'>Selamat datang kembali, {h(nama)}!</div>",
        unsafe_allow_html=True,
    )

    # Ambil data dari backend
    ipk_data = _get_ipk(mahasiswa_id)
    tren_data = _get_tren(mahasiswa_id)

    ipk_val = ipk_data.get("ipk", 0.0) if ipk_data else 0.0
    total_sks = ipk_data.get("total_sks_kumulatif", 0) if ipk_data else 0
    semesters = ipk_data.get("semester", []) if ipk_data else []

    # IPS semester terakhir
    ips_terakhir = None
    label_terakhir = ""
    if semesters:
        last_sem = semesters[-1]
        ips_terakhir = last_sem.get("ips")
        label_terakhir = semester_label(
            last_sem.get("tahun_ajaran", ""), last_sem.get("semester", "")
        )

    # Rata-rata IPS dari semua semester
    ips_list = [s.get("ips") for s in semesters if s.get("ips") is not None]
    rata_ips = round(sum(ips_list) / len(ips_list), 2) if ips_list else None
    jumlah_semester = len(semesters)

    # 4 Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(
            "TOTAL GPA (IPK)", format_ipk(ipk_val),
            sub="Performa kumulatif",
            badge="↑" if ipk_val and ipk_val > 0 else "",
            badge_type="green",
        )
    with c2:
        metric_card(
            "SEMESTER GPA (IPS)", format_ipk(ips_terakhir),
            sub=label_terakhir or "Belum ada data",
            badge="Latest" if ips_terakhir else "",
            badge_type="blue",
        )
    with c3:
        metric_card(
            "TOTAL CREDITS", str(total_sks),
            sub=f"{total_sks} / 144 SKS",
        )
    with c4:
        metric_card(
            "RATA-RATA IPS", format_ipk(rata_ips),
            sub=f"Dari {jumlah_semester} semester" if jumlah_semester > 0 else "Belum ada semester",
        )

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Grade Trend Visualization
    st.markdown(
        "<div class='section-header'>Grade Trend Visualization</div>"
        "<div class='section-sub'>Perbandingan IPK kumulatif dan IPS per semester</div>",
        unsafe_allow_html=True,
    )

    tren_list = tren_data.get("tren", []) if tren_data else []
    if tren_list:
        labels = [t["label"] for t in tren_list]
        ips_vals = [t.get("ips") or 0 for t in tren_list]
        ipk_vals = [t.get("ipk_kumulatif") or 0 for t in tren_list]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=labels, y=ipk_vals, mode="lines+markers",
            name="IPK", line=dict(color="#0f172a", width=2.5),
            marker=dict(size=7, color="#0f172a"),
        ))
        fig.add_trace(go.Scatter(
            x=labels, y=ips_vals, mode="lines+markers",
            name="IPS", line=dict(color="#16a34a", width=2, dash="dot"),
            marker=dict(size=7, color="#16a34a"),
        ))
        fig.update_layout(
            height=280,
            margin=dict(l=0, r=0, t=10, b=10),
            paper_bgcolor="white",
            plot_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False, tickfont=dict(size=11)),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", range=[0, 4.2],
                       tickfont=dict(size=11)),
            font=dict(family="Inter, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Belum ada data tren. Tambahkan semester dan mata kuliah untuk melihat grafik.")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Latest Course Entries
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown(
            "<div class='section-header'>Latest Course Entries</div>",
            unsafe_allow_html=True,
        )
    with col_right:
        st.markdown(
            "<div style='text-align:right;padding-top:4px;'>"
            "<span style='font-size:0.82rem;color:#2563eb;cursor:pointer;'>Lihat Semua →</span>"
            "</div>",
            unsafe_allow_html=True,
        )

    # Ambil mata kuliah dari semester terakhir
    latest_mk = _get_latest_mk(mahasiswa_id, semesters)
    if latest_mk:
        rows = [
            {
                "Kode MK": mk.get("kode_mk", ""),
                "Nama Mata Kuliah": mk.get("nama_mk", ""),
                "SKS": mk.get("sks", ""),
                "Nilai": mk.get("nilai_huruf") or "-",
                "Status": "Selesai" if mk.get("nilai_huruf") else "Berjalan",
            }
            for mk in latest_mk[:8]
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada mata kuliah. Tambahkan di halaman Kalkulator.")


# Helper functions
def _get_ipk(mahasiswa_id: str) -> dict | None:
    try:
        return api_client.get(f"/mahasiswa/{mahasiswa_id}/ipk")
    except APIError:
        return None
    except Exception:
        st.warning("⚠️ Tidak dapat terhubung ke backend.")
        return None


def _get_tren(mahasiswa_id: str) -> dict | None:
    try:
        return api_client.get(f"/mahasiswa/{mahasiswa_id}/tren")
    except APIError:
        return None
    except Exception:
        return None


def _get_latest_mk(mahasiswa_id: str, semesters: list) -> list:
    if not semesters:
        return []
    last_id = semesters[-1].get("id")
    if not last_id:
        return []
    try:
        result = api_client.get(f"/semester/{last_id}/mata-kuliah")
        return result.get("data", []) if result else []
    except Exception:
        return []
