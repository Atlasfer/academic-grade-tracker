import streamlit as st
from utils import api_client
from utils.api_client import APIError

def render():
    st.markdown(
        "<div class='section-header'>Reverse Target Simulation</div>"
        "<div class='section-sub'>"
        "Hitung IPS minimum yang harus kamu raih di sisa semester untuk mencapai target IPK kelulusan."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col_params, col_result = st.columns([5, 4], gap="large")

    with col_params:
        st.markdown(
            "<div style='background:#fff;border:1px solid #e2e8f0;border-radius:12px;"
            "padding:1.5rem;'>",
            unsafe_allow_html=True,
        )
        st.markdown("**⚙️ Parameters**")

        ipk_saat_ini = st.slider(
            "IPK Saat Ini",
            min_value=0.0, max_value=4.0, value=3.25, step=0.01,
            format="%.2f", key="sim_ipk",
        )
        st.markdown(
            f"<div style='text-align:right;margin-top:-0.5rem;font-size:0.78rem;"
            f"color:#64748b;'>{ipk_saat_ini:.2f}</div>",
            unsafe_allow_html=True,
        )

        total_sks = st.slider(
            "Total SKS yang Sudah Ditempuh",
            min_value=0, max_value=160, value=84, step=1,
            key="sim_sks",
        )
        st.markdown(
            f"<div style='text-align:right;margin-top:-0.5rem;font-size:0.78rem;"
            f"color:#64748b;'>{total_sks} SKS</div>",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            target_ipk = st.number_input(
                "Target IPK Akhir",
                min_value=0.0, max_value=4.0, value=3.50, step=0.01,
                format="%.2f", key="sim_target",
            )
        with c2:
            sisa_sks = st.number_input(
                "Sisa SKS",
                min_value=1, max_value=200, value=60, step=1,
                key="sim_sisa",
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # Tombol hitung
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        if st.button("Hitung IPS Minimum", type="primary", use_container_width=True, key="btn_sim"):
            _run_simulasi(ipk_saat_ini, total_sks, float(target_ipk), int(sisa_sks))

    with col_result:
        _render_result_card()

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Insight cards
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="insight-card">
                <div class="insight-title">Academic Load</div>
                <div class="insight-body">
                    Prioritaskan untuk mengambil mata kuliah dengan bobot SKS yang lebih tinggi terlebih dahulu agar IPK kamu stabil lebih cepat
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="insight-card">
                <div class="insight-title">Optimisasi</div>
                <div class="insight-body">
                    Meningkatkan nilai kamu, bahkan dalam mata kuliah 2 SKS, dapat memberikan dampak jangka panjang yang signifikan terhadap IPK akhir kamu.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        result = st.session_state.get("sim_result")
        ips_min = result.get("ips_minimum_diperlukan", 0) if result else 0
        insight_text = (
            "Target ini dapat dicapai dengan mempertahankan performa akademik saat ini."
            if ips_min and ips_min <= 4.0
            else "Jika nilai IPS yang dibutuhkan di atas 4.0, pertimbangkan untuk mengikuti kelas remedial untuk mata kuliah-mata kuliah sebelumnya yang nilainya rendah."
        )
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">Simulation Insight</div>
                <div class="insight-body">{insight_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _run_simulasi(ipk_saat_ini, total_sks, target_ipk, sisa_sks):
    """Kirim request simulasi ke backend dan simpan hasil ke session state."""
    if target_ipk < 0 or target_ipk > 4.0:
        st.error("Target IPK harus antara 0.00 dan 4.00.")
        return
    if ipk_saat_ini < 0 or ipk_saat_ini > 4.0:
        st.error("IPK saat ini harus antara 0.00 dan 4.00.")
        return
    if sisa_sks <= 0:
        st.error("Sisa SKS harus lebih dari 0.")
        return

    try:
        result = api_client.post("/simulasi/target-ipk", {
            "ipk_saat_ini": ipk_saat_ini,
            "total_sks_ditempuh": total_sks,
            "target_ipk": target_ipk,
            "sisa_sks": sisa_sks,
        })
        st.session_state.sim_result = result
        st.rerun()
    except APIError as e:
        st.error(f"Gagal: {e.message}")
    except Exception as e:
        st.error(f"Koneksi ke backend gagal: {e}")


def _render_result_card():
    """Tampilkan card hasil simulasi."""
    result = st.session_state.get("sim_result")

    if not result:
        st.markdown(
            """
            <div class="sim-result-card" style="height:100%;min-height:220px;
                 display:flex;flex-direction:column;align-items:center;justify-content:center;">
                <div class="sim-result-label">REQUIRED AVERAGE GPA</div>
                <div class="sim-result-value" style="color:#475569;">—</div>
                <div class="sim-result-desc">Isi parameter dan klik Hitung</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    ips_min = result.get("ips_minimum_diperlukan", 0)
    tercapai = result.get("tercapai", False)
    sisa = result.get("sisa_sks", 0)

    badge_html = (
        '<span class="sim-badge-achievable">Target Tercapai</span>'
        if tercapai
        else '<span class="sim-badge-not-achievable">Target Tidak Realistis</span>'
    )

    desc = (
        f"Pertahankan IPS ≥ {ips_min:.2f} di {sisa} SKS sisa untuk mencapai target."
        if tercapai
        else f"IPS minimum {ips_min:.2f} melebihi skala maksimum 4.00. Pertimbangkan revisi target."
    )

    st.markdown(
        f"""
        <div class="sim-result-card">
            <div class="sim-result-label">REQUIRED AVERAGE GPA (IPS)</div>
            <div class="sim-result-value">{ips_min:.2f}</div>
            <div class="sim-result-desc">{desc}</div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
