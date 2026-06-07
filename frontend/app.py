from dotenv import load_dotenv
import streamlit as st

load_dotenv()
from utils.state import init_state, is_logged_in
from utils.styles import GLOBAL_CSS
from components.sidebar import render_sidebar
from page import profil, dashboard, kalkulator, simulasi, import_frs


# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Academic Grade Tracker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject CSS global
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# Inisialisasi session state
init_state()

# Sidebar
if is_logged_in():
    render_sidebar()

# Router halaman
current_page = st.session_state.get("current_page", "Dashboard")
if not is_logged_in():
    profil.render()
else:
    if current_page == "Dashboard":
        dashboard.render()
    elif current_page == "Kalkulator":
        kalkulator.render()
    elif current_page == "Simulasi":
        simulasi.render()
    elif current_page == "Import":
        import_frs.render()
    else:
        dashboard.render()