import streamlit as st
from utils import api_client
from utils.api_client import APIError
from utils.state import set_mahasiswa
from utils.auth import save_token

AUTH_PAGE_CSS = """
<style>
/* Sembunyikan sidebar di halaman auth */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* Full-page centering */
.auth-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 80vh;
    padding: 2rem 1rem;
}

/* Branding */
.auth-brand {
    text-align: center;
    margin-bottom: 2rem;
}
.auth-brand-title {
    font-size: 2rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.5px;
    line-height: 1.1;
}
.auth-brand-title span {
    color: #0f172a;
}
.auth-brand-sub {
    font-size: 0.88rem;
    color: #64748b;
    margin-top: 0.35rem;
}

/* Card container */
.auth-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 2rem 2.25rem;
    width: 100%;
    max-width: 420px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
}

/* Tab styling override */
.auth-card .stTabs [data-baseweb="tab-list"] {
    background: #f1f5f9;
    border-radius: 8px;
    padding: 3px;
    gap: 2px;
}
.auth-card .stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.88rem;
    padding: 0.45rem 1.25rem;
    color: #64748b;
}
.auth-card .stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #0f172a !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.auth-card .stTabs [data-baseweb="tab-highlight"] {
    display: none;
}
.auth-card .stTabs [data-baseweb="tab-border"] {
    display: none;
}

/* Footer */
.auth-footer {
    text-align: center;
    margin-top: 1.5rem;
    font-size: 0.78rem;
    color: #94a3b8;
}
</style>
"""


def render():
    st.markdown(AUTH_PAGE_CSS, unsafe_allow_html=True)

    # Branding
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(
            """
            <div class="auth-brand">
                <div class="auth-brand-title">Academic<br><span>Grade Tracker</span></div>
                <div class="auth-brand-sub">Pantau IPK dan progres akademikmu dengan mudah</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            tab_login, tab_register = st.tabs(["  Masuk  ", "  Daftar  "])
            with tab_login:
                st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
                _form_login()
            with tab_register:
                st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
                _form_register()

        st.markdown(
            "<div class='auth-footer'>Academic Grade Tracker &copy; 2025</div>",
            unsafe_allow_html=True,
        )


def _form_login():
    with st.form("form_login"):
        st.markdown("#### Masuk ke Akun")
        st.markdown(
            "<div style='font-size:0.82rem;color:#64748b;margin-bottom:1rem;margin-top:-0.25rem'>"
            "Masukkan NIM dan password kamu untuk melanjutkan."
            "</div>",
            unsafe_allow_html=True,
        )
        nim = st.text_input("NIM", placeholder="Contoh: 5053241001", max_chars=20)
        password = st.text_input("Password", type="password", placeholder="Masukkan password kamu")
        submitted = st.form_submit_button("Masuk →", type="primary", use_container_width=True)

    if submitted:
        if not nim.strip() or not password:
            st.error("NIM dan password wajib diisi.")
            return
        try:
            result = api_client.post("/auth/login", {"nim": nim.strip(), "password": password})
            save_token(result.get("token"))
            set_mahasiswa(result.get("mahasiswa", {}))
            st.success(f"Selamat datang kembali, {result['mahasiswa']['nama']}!")
            st.session_state.current_page = "Dashboard"
            st.rerun()
        except APIError as e:
            st.error(f"Login gagal: {e.message}")
        except Exception as e:
            st.error(f"Koneksi ke backend gagal. ({e})")


def _form_register():
    with st.form("form_register"):
        st.markdown("#### Buat Akun Baru")
        st.markdown(
            "<div style='font-size:0.82rem;color:#64748b;margin-bottom:1rem;margin-top:-0.25rem'>"
            "Isi data diri kamu untuk membuat akun."
            "</div>",
            unsafe_allow_html=True,
        )
        nim = st.text_input("NIM", placeholder="Contoh: 5053241001", max_chars=20)
        nama = st.text_input("Nama Lengkap", placeholder="Contoh: Budi Santoso", max_chars=200)
        prodi = st.text_input("Program Studi", placeholder="Contoh: Teknik Informatika", max_chars=100)
        st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
        password = st.text_input("Password", type="password", placeholder="Buat password yang kuat")
        password_confirm = st.text_input("Konfirmasi Password", type="password", placeholder="Ulangi password kamu")
        submitted = st.form_submit_button("Buat Akun →", type="primary", use_container_width=True)

    if submitted:
        errors = []
        if not nim.strip():
            errors.append("NIM wajib diisi.")
        if not nama.strip():
            errors.append("Nama wajib diisi.")
        if not prodi.strip():
            errors.append("Program studi wajib diisi.")
        if not password:
            errors.append("Password wajib diisi.")
        elif password != password_confirm:
            errors.append("Password tidak cocok.")

        if errors:
            for err in errors:
                st.error(err)
            return
        try:
            result = api_client.post("/auth/register", {
                "nim": nim.strip(),
                "nama": nama.strip(),
                "program_studi": prodi.strip(),
                "password": password,
            })
            save_token(result.get("token"))
            set_mahasiswa(result["mahasiswa"])
            st.success(f"Akun berhasil dibuat. Selamat datang, {nama}!")
            st.session_state.current_page = "Dashboard"
            st.rerun()
        except APIError as e:
            st.error(f"Registrasi gagal: {e.message}")
        except Exception as e:
            st.error(f"Koneksi ke backend gagal. ({e})")
