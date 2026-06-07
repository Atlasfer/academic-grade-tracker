import streamlit as st

def init_state():
    """Inisialisasi semua session state yang dibutuhkan."""
    defaults = {
        "token": None,
        "mahasiswa_id": None,
        "mahasiswa_nim": "",
        "mahasiswa_nama": "",
        "mahasiswa_prodi": "",
        "mahasiswa_total_sks": 0,
        "semester_aktif_id": None,
        "semester_aktif_label": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def set_mahasiswa(data: dict):
    """Simpan data mahasiswa ke session state setelah login/pilih profil."""
    st.session_state.mahasiswa_id = data.get("id")
    st.session_state.mahasiswa_nim = data.get("nim", "")
    st.session_state.mahasiswa_nama = data.get("nama", "")
    st.session_state.mahasiswa_prodi = data.get("program_studi", "")
    st.session_state.mahasiswa_total_sks = data.get("total_sks_lulus", 0)


def clear_mahasiswa():
    """Reset semua data mahasiswa dari session state."""
    st.session_state.mahasiswa_id = None
    st.session_state.mahasiswa_nim = ""
    st.session_state.mahasiswa_nama = ""
    st.session_state.mahasiswa_prodi = ""
    st.session_state.mahasiswa_total_sks = 0
    st.session_state.semester_aktif_id = None
    st.session_state.semester_aktif_label = ""


def is_logged_in() -> bool:
    return st.session_state.get("mahasiswa_id") is not None
