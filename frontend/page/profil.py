import streamlit as st
from utils import api_client
from utils.api_client import APIError
from utils.state import set_mahasiswa
from utils.auth import save_token


def render():
    st.markdown("## 🎓 Selamat Datang di Academic Grade Tracker")
    st.markdown(
        "<div class='section-sub'>"
        "Masuk dengan NIM dan password, atau daftar jika belum punya akun."
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
 
    tab_login, tab_register = st.tabs(["Masuk", "Daftar"])
 
    with tab_login:
        _form_login()
 
    with tab_register:
        _form_register()
    
def _form_login():
    with st.form("form_login"):
        nim = st.text_input("NIM", placeholder="Contoh: 5053241001", max_chars=20)
        password = st.text_input("Password", type="password", placeholder="Masukkan password Anda")
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
            st.error(f"Gagal login: {e.message}")
        except Exception as e:
            st.error(f"Koneksi ke backend gagal. ({e})")

def _form_register():
    with st.form("form_register"):
        nim = st.text_input("NIM", placeholder="Contoh: 220194532", max_chars=20)
        nama = st.text_input("Nama Lengkap", placeholder="Contoh: Cecep Budiman", max_chars=200)
        prodi = st.text_input("Program Studi", placeholder="Contoh: Teknik Informatika", max_chars=100)

        password = st.text_input("Password", type="password", placeholder="Buat password yang kuat")
        password_confirm = st.text_input("Konfirmasi Password", type="password", placeholder="Masukkan ulang password")
        submitted = st.form_submit_button("Daftar →", type="primary", use_container_width=True)
    
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
            for e in errors:
                st.error(e)
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
            st.success(f"Profil berhasil dibuat. Selamat datang, {nama}!")
            st.session_state.current_page = "Dashboard"
            st.rerun()
        except APIError as e:
            st.error(f"Gagal daftar: {e.message}")
        except Exception as e:
            st.error(f"Koneksi ke backend gagal.({e})")
