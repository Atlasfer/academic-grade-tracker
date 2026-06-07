import streamlit as st


def save_token(token: str):
    st.session_state.token = token


def get_token() -> str | None:
    return st.session_state.get("token")


def logout():
    st.session_state.token = None
    st.session_state.mahasiswa_id = None
    st.session_state.mahasiswa_nim = ""
    st.session_state.mahasiswa_nama = ""
    st.session_state.mahasiswa_prodi = ""
    st.session_state.mahasiswa_total_sks = 0
    st.session_state.semester_aktif_id = None
    st.session_state.semester_aktif_label = ""
    st.session_state.current_page = "Dashboard"


def is_authenticated() -> bool:
    return bool(get_token())