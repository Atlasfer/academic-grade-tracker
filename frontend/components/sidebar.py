"""
Komponen sidebar yang tampil di semua halaman.
"""
import streamlit as st
from utils.state import is_logged_in
from utils.helpers import format_ipk, h
from utils.auth import logout


def render_sidebar():
    """Render sidebar navigasi dengan profil mahasiswa."""
    with st.sidebar:
        # Branding
        st.markdown(
            """
            <div style="padding: 1rem 0 0.5rem 0;">
                <div style="font-size:1.6rem;font-weight:800;color:#f1f5f9;letter-spacing:-0.5px;">ACADEMIC</div>
                <div style="font-size:0.75rem;color:#64748b;margin-top:-2px;">Grade Tracker</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<hr style='border-color:#2d3f54;margin:0.5rem 0;'>", unsafe_allow_html=True)

        # Profil mahasiswa
        if is_logged_in():
            nama = st.session_state.mahasiswa_nama
            nim = st.session_state.mahasiswa_nim
            inisial = "".join([w[0].upper() for w in nama.split()[:2]])
            st.markdown(
                f"""
                <div style="background:rgba(255,255,255,0.07);border-radius:8px;
                            padding:0.65rem 0.85rem;margin-bottom:1rem;
                            display:flex;align-items:center;gap:0.6rem;">
                    <div style="width:36px;height:36px;border-radius:50%;
                                background:#334155;display:flex;align-items:center;
                                justify-content:center;font-size:0.9rem;
                                color:#e2e8f0;font-weight:700;flex-shrink:0;">
                        {h(inisial)}
                    </div>
                    <div>
                        <div style="font-size:0.85rem;font-weight:600;color:#f1f5f9;">{h(nama)}</div>
                        <div style="font-size:0.72rem;color:#94a3b8;">NIM: {h(nim)}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="background:rgba(255,255,255,0.05);border-radius:8px;
                            padding:0.65rem 0.85rem;margin-bottom:1rem;color:#64748b;
                            font-size:0.82rem;">
                    Belum ada profil dipilih
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Menu navigasi
        st.markdown(
            "<div style='font-size:0.68rem;font-weight:600;letter-spacing:0.08em;"
            "color:#475569;text-transform:uppercase;margin-bottom:0.4rem;'>"
            "MENU</div>",
            unsafe_allow_html=True,
        )

        pages = {
            "DASHBOARD": "Dashboard",
            "KALKULATOR": "Kalkulator",
            "SIMULASI": "Simulasi",
            "IMPORT FRS": "Import",
        }

        current = st.session_state.get("current_page", "Dashboard")

        for label, page_key in pages.items():
            is_active = current == page_key
            btn_style = (
                "background:rgba(255,255,255,0.12);color:#fff;font-weight:600;"
                if is_active
                else "background:transparent;color:#94a3b8;"
            )
            if st.button(
                label,
                key=f"nav_{page_key}",
                use_container_width=True,
            ):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("<hr style='border-color:#2d3f54;margin:1rem 0 0.5rem 0;'>", unsafe_allow_html=True)

        # Tombol tambah mata kuliah (di bawah navigasi)
        if is_logged_in():
            if st.button("➕  Tambah Mata Kuliah", use_container_width=True, key="nav_add_mk"):
                st.session_state.current_page = "Kalkulator"
                st.session_state.focus_add_mk = True
                st.rerun()
            if st.button("🚪  Logout", use_container_width=True, key="nav_logout"):
                logout()
                st.session_state.current_page = "Profil"
                st.rerun()

        st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
