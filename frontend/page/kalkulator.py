import streamlit as st
from utils import api_client
from utils.api_client import APIError
from utils.helpers import (
    NILAI_HURUF_LIST, SKS_LIST, format_ipk, semester_label,
    ipk_status_label
)
from components.metric_card import metric_card


def render():
    mahasiswa_id = st.session_state.mahasiswa_id

    st.markdown(
        "<div class='section-header'>Kalkulator IPS/IPK</div>"
        "<div class='section-sub'>Input mata kuliah per semester dan lihat kalkulasi otomatis</div>",
        unsafe_allow_html=True,
    )

    # Pilih / Buat Semester
    semesters = _get_semesters(mahasiswa_id)
    sem_options = {
        semester_label(s["tahun_ajaran"], s["semester"]): s
        for s in semesters
    }

    col_sem, col_new = st.columns([3, 1])
    with col_sem:
        if sem_options:
            selected_label = st.selectbox(
                "Pilih Semester", list(sem_options.keys()), key="sel_semester"
            )
            active_semester = sem_options[selected_label]
        else:
            st.info("Belum ada semester. Buat semester baru di sebelah kanan.")
            active_semester = None

    with col_new:
        st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
        if st.button("➕ Semester Baru", key="btn_new_sem", use_container_width=True):
            st.session_state.show_new_sem_form = True

    # Form buat semester baru
    if st.session_state.get("show_new_sem_form"):
        _form_buat_semester(mahasiswa_id)

    if not active_semester:
        return

    semester_id = active_semester["id"]

    # Metric summary semester aktif
    ips_data = _get_ips(semester_id)
    ips_val = ips_data.get("ips") if ips_data else None
    total_sks_sem = ips_data.get("total_sks_semester", 0) if ips_data else 0
    mk_list = ips_data.get("mata_kuliah", []) if ips_data else []
    jumlah_mk = len(mk_list)

    # Hitung distribusi nilai
    grade_dist = {}
    for mk in mk_list:
        n = mk.get("nilai_huruf")
        if n:
            grade_dist[n] = grade_dist.get(n, 0) + 1
    primary_grade = max(grade_dist, key=grade_dist.get) if grade_dist else "-"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        label_ips = ipk_status_label(ips_val).replace("🏆 ", "").replace("⭐ ", "") if ips_val else ""
        metric_card(
            "IPS SEMESTER INI", format_ipk(ips_val),
            badge=label_ips if label_ips else "",
            badge_type="green",
        )
    with c2:
        metric_card("TOTAL SKS", str(total_sks_sem), sub="SKS semester ini")
    with c3:
        metric_card("MK TERCATAT", f"{jumlah_mk:02d}", sub=selected_label)
    with c4:
        metric_card("DISTRIBUSI NILAI", "", sub=f"Dominan: Grade {primary_grade}")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Layout 2 kolom: Form input | Tabel coursework
    col_form, col_table = st.columns([4, 6], gap="large")

    with col_form:
        _form_tambah_mk(semester_id)

    with col_table:
        _tabel_coursework(semester_id, mk_list, ips_val)

    # Hapus semester
    with st.expander("⚙️ Pengaturan Semester", expanded=False):
        st.warning(
            f"Menghapus semester **{selected_label}** akan menghapus semua mata kuliah di dalamnya."
        )
        if st.button("🗑️ Hapus Semester Ini", key="btn_del_sem", type="secondary"):
            st.session_state.confirm_del_sem = semester_id

        if st.session_state.get("confirm_del_sem") == semester_id:
            st.error("Yakin ingin menghapus? Tindakan ini tidak dapat dibatalkan.")
            c_yes, c_no = st.columns(2)
            with c_yes:
                if st.button("Ya, Hapus", key="btn_del_sem_confirm", type="primary"):
                    _hapus_semester(semester_id)
            with c_no:
                if st.button("Batal", key="btn_del_sem_cancel"):
                    st.session_state.confirm_del_sem = None
                    st.rerun()


# Sub-komponen
def _form_buat_semester(mahasiswa_id: str):
    st.markdown(
        "<div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;"
        "padding:1rem 1.25rem;margin-bottom:1rem;'>",
        unsafe_allow_html=True,
    )
    st.markdown("**Buat Semester Baru**")
    with st.form("form_new_semester"):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            tahun_mulai = st.text_input("Tahun Mulai", placeholder="2023", max_chars=4)
        with col2:
            jenis = st.selectbox("Jenis Semester", ["GANJIL", "GENAP", "PENDEK"])
        with col3:
            st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Buat", type="primary")

    if submitted:
        if not tahun_mulai.strip().isdigit() or len(tahun_mulai.strip()) != 4:
            st.error("Tahun mulai harus berupa 4 digit angka, contoh: 2023")
        else:
            tahun_ajaran = f"{tahun_mulai}/{int(tahun_mulai)+1}"
            try:
                api_client.post(f"/mahasiswa/{mahasiswa_id}/semester", {
                    "tahun_ajaran": tahun_ajaran,
                    "semester": jenis,
                })
                st.success(f"Semester {jenis} {tahun_ajaran} berhasil dibuat!")
                st.session_state.show_new_sem_form = False
                st.rerun()
            except APIError as e:
                if e.status_code == 409:
                    st.error(f"Semester {jenis} {tahun_ajaran} sudah ada.")
                else:
                    st.error(f"Gagal: {e.message}")

    st.markdown("</div>", unsafe_allow_html=True)


def _form_tambah_mk(semester_id: str):
    st.markdown(
        "<div style='background:#fff;border:1px solid #e2e8f0;border-radius:12px;"
        "padding:1.25rem;'>",
        unsafe_allow_html=True,
    )
    st.markdown("**Course Intake**")

    with st.form("form_tambah_mk", clear_on_submit=True):
        kode = st.text_input("Kode Mata Kuliah", placeholder="Contoh: IF4021", max_chars=20)
        nama = st.text_input("Nama Mata Kuliah", placeholder="Contoh: Pemrograman Web", max_chars=200)
        c1, c2 = st.columns(2)
        with c1:
            sks = st.selectbox("SKS", SKS_LIST, index=2)
        with c2:
            nilai_options = ["(Belum ada nilai)"] + NILAI_HURUF_LIST
            nilai_sel = st.selectbox("Nilai", nilai_options)

        st.markdown(
            "<div style='background:#f8fafc;border-radius:6px;padding:0.6rem 0.75rem;"
            "font-size:0.79rem;color:#64748b;margin-top:0.25rem;'>"
            "ℹ️ IPS dihitung dengan mengalikan bobot nilai tiap mata kuliah dengan SKS-nya, "
            "dijumlahkan, dan dibagi total SKS."
            "</div>",
            unsafe_allow_html=True,
        )

        submitted = st.form_submit_button("➕ Catat Mata Kuliah", type="primary", use_container_width=True)

    if submitted:
        errors = []
        if not kode.strip():
            errors.append("Kode mata kuliah wajib diisi.")
        if not nama.strip():
            errors.append("Nama mata kuliah wajib diisi.")
        if errors:
            for e in errors:
                st.error(e)
        else:
            nilai_huruf = None if nilai_sel == "(Belum ada nilai)" else nilai_sel
            try:
                api_client.post(f"/semester/{semester_id}/mata-kuliah", {
                    "kode_mk": kode.strip(),
                    "nama_mk": nama.strip(),
                    "sks": sks,
                    "nilai_huruf": nilai_huruf,
                })
                st.success(f"Mata kuliah '{kode}' berhasil ditambahkan!")
                st.rerun()
            except APIError as e:
                if e.status_code == 409:
                    st.error(f"Kode '{kode}' sudah ada di semester ini.")
                else:
                    st.error(f"Gagal: {e.message}")

    st.markdown("</div>", unsafe_allow_html=True)


def _tabel_coursework(semester_id: str, mk_list: list, ips_val: float | None):
    if not mk_list:
        st.info("Belum ada mata kuliah. Tambahkan di form kiri.")
        return

    rows = [
        {
            "Kode MK": mk.get("kode_mk", ""),
            "Nama Mata Kuliah": mk.get("nama_mk", ""),
            "SKS": mk.get("sks", ""),
            "Nilai": mk.get("nilai_huruf") or "-",
            "Bobot": mk.get("nilai_bobot") if mk.get("nilai_bobot") is not None else "-",
        }
        for mk in mk_list
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)

    # Academic Status card
    if ips_val is not None:
        status = ipk_status_label(ips_val)
        diff_to_perfect = round(4.0 - ips_val, 2)
        st.markdown(
            f"""
            <div style="background:#1a2332;border-radius:10px;padding:1rem 1.25rem;
                        margin-top:0.75rem;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:0.68rem;font-weight:600;letter-spacing:0.08em;
                                color:#64748b;text-transform:uppercase;">ACADEMIC STATUS</div>
                    <div style="font-size:1rem;font-weight:700;color:#fff;margin:0.2rem 0;">
                        {status}
                    </div>
                    <div style="font-size:0.78rem;color:#94a3b8;">
                        Kamu {diff_to_perfect:.2f} poin dari IPS sempurna (4.0)
                    </div>
                </div>
                <div style="background:#334155;border-radius:8px;width:44px;height:44px;
                            display:flex;align-items:center;justify-content:center;
                            font-size:1.25rem;font-weight:800;color:#fff;">
                    {"A" if ips_val >= 3.75 else "B" if ips_val >= 3.0 else "C"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)
    with st.expander("🗑️ Hapus mata kuliah", expanded=False):
        for mk in mk_list:
            label_mk = f"{mk.get('kode_mk')} — {mk.get('nama_mk')}"
            if st.button(f"Hapus: {label_mk}", key=f"del_mk_{mk['id']}"):
                _hapus_mk(mk["id"])


def _hapus_semester(semester_id: str):
    try:
        api_client.delete(f"/semester/{semester_id}")
        st.success("Semester berhasil dihapus.")
        st.session_state.confirm_del_sem = None
        st.rerun()
    except APIError as e:
        st.error(f"Gagal menghapus: {e.message}")


def _hapus_mk(mk_id: str):
    try:
        api_client.delete(f"/mata-kuliah/{mk_id}")
        st.success("Mata kuliah berhasil dihapus.")
        st.rerun()
    except APIError as e:
        st.error(f"Gagal menghapus: {e.message}")


def _get_semesters(mahasiswa_id: str) -> list:
    try:
        result = api_client.get(f"/mahasiswa/{mahasiswa_id}/semester",
                                params={"page": 1, "per_page": 50})
        return result.get("data", []) if result else []
    except Exception:
        return []


def _get_ips(semester_id: str) -> dict | None:
    try:
        return api_client.get(f"/semester/{semester_id}/ips")
    except APIError as e:
        if e.status_code == 422:
            return None
        return None
    except Exception:
        return None
