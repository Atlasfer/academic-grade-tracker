import streamlit as st
from utils import api_client
from utils.api_client import APIError
from utils.state import set_mahasiswa


def render():
    _try_auto_load()
    st.markdown("## 🎓 Selamat Datang di Academic Grade Tracker")
    st.markdown(
        "<div class='section-sub'>"
        "Isi profil kamu sekali saja untuk memulai. Data ini tidak akan diminta lagi."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("form_setup_profil"):
        nim = st.text_input("NIM", placeholder="Contoh: 220194532", max_chars=20)
        nama = st.text_input("Nama Lengkap", placeholder="Contoh: Julian Walters", max_chars=200)
        prodi = st.text_input(
            "Program Studi", placeholder="Contoh: Teknik Informatika", max_chars=100
        )
        submitted = st.form_submit_button("Mulai Gunakan Aplikasi →", type="primary", use_container_width=True)

    if submitted:
        errors = []
        if not nim.strip():
            errors.append("NIM wajib diisi.")
        if not nama.strip():
            errors.append("Nama wajib diisi.")
        if not prodi.strip():
            errors.append("Program studi wajib diisi.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            _buat_profil(nim.strip(), nama.strip(), prodi.strip())


def _try_auto_load():
    try:
        result = api_client.get("/mahasiswa", params={"page": 1, "per_page": 1})
        data_list = result.get("data", []) if result else []
        if data_list:
            set_mahasiswa(data_list[0])
            st.session_state.current_page = "Dashboard"
            st.rerun()
    except Exception:
        pass


def _buat_profil(nim: str, nama: str, prodi: str):
    try:
        result = api_client.post("/mahasiswa", {
            "nim": nim,
            "nama": nama,
            "program_studi": prodi,
        })
        set_mahasiswa(result)
        st.session_state.current_page = "Dashboard"
        st.success(f"Profil berhasil dibuat. Selamat datang, {nama}!")
        st.rerun()
    except APIError as e:
        st.error(f"Gagal menyimpan profil: {e.message}")
    except Exception as e:
        st.error(f"Koneksi ke backend gagal. Pastikan backend sudah berjalan. ({e})")
