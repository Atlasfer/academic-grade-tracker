import streamlit as st
from utils import api_client
from utils.api_client import APIError
from utils.helpers import format_ipk, semester_label, h


def render():
    mahasiswa_id = st.session_state.mahasiswa_id

    st.markdown(
        "<div class='section-header'>Import Academic Data</div>"
        "<div class='section-sub'>"
        "Upload file PDF FRS/SIAKAD untuk mengimpor data nilai secara otomatis."
        "</div>",
        unsafe_allow_html=True,
    )

    # Check if transcript has been imported
    has_transcript = _has_graded_courses(mahasiswa_id)

    if not has_transcript:
        st.warning(
            "⚠️ Impor transkrip akademik terlebih dahulu sebelum mengimpor FRS. "
            "Upload file transkrip PDF dari SIAKAD untuk memulai."
        )

    # Pilih semester tujuan import
    semesters = _get_semesters(mahasiswa_id)
    sem_options = {
        semester_label(s["tahun_ajaran"], s["semester"]): s
        for s in semesters
    }

    if not sem_options and not has_transcript:
        st.info("Belum ada semester. Impor transkrip untuk membuat semester otomatis.")
        _render_upload_zone(mahasiswa_id, semester_id=None, allow_frs=False)
        return

    if not sem_options:
        st.warning("Belum ada semester. Buat semester terlebih dahulu di halaman Kalkulator.")
        return

    selected_label = st.selectbox(
        "Pilih Semester Tujuan Import", list(sem_options.keys()), key="import_sem_sel"
    )
    target_semester = sem_options[selected_label]
    semester_id = target_semester["id"]

    _render_upload_zone(mahasiswa_id, semester_id=semester_id, allow_frs=has_transcript)

    import_result = st.session_state.get("last_import_result")
    if import_result:
        berhasil = import_result.get("berhasil", 0)
        gagal = import_result.get("gagal", 0)
        st.markdown(
            f"""
            <div class="notif-success">
                ✅ Berhasil mengimpor <b>{berhasil}</b> mata kuliah dari semester ini.
            </div>
            """,
            unsafe_allow_html=True,
        )
        if gagal > 0:
            detail_gagal = import_result.get("detail_gagal", [])
            for item in detail_gagal:
                st.markdown(
                    f"""
                    <div class="notif-warning">
                        ⚠️ Baris {h(item.get('baris','-'))}: {h(item.get('alasan',''))}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    _render_academic_history(mahasiswa_id)


def _render_upload_zone(mahasiswa_id: str, semester_id, allow_frs: bool):
    st.markdown(
        """
        <div class="upload-zone">
            <div class="upload-icon">📄</div>
            <div style="font-weight:600;color:#1e293b;margin-bottom:0.25rem;">
                Drag and drop file di sini
            </div>
            <div style="font-size:0.78rem;">Maks. 10 MB • PDF</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Pilih file PDF",
        type=["pdf"],
        label_visibility="collapsed",
        key="import_uploader",
    )

    if uploaded:
        content = uploaded.read()
        if len(content) > 10 * 1024 * 1024:
            st.error("Ukuran file melebihi 10 MB. Silakan kompres PDF terlebih dahulu.")
            return

        st.markdown(
            f"<div style='font-size:0.82rem;color:#475569;margin-top:0.25rem;'>"
            f"📎 <b>{h(uploaded.name)}</b> ({len(content)/1024:.1f} KB)</div>",
            unsafe_allow_html=True,
        )

        if not allow_frs:
            st.info("File ini akan diproses sebagai transkrip. Semester akan dibuat otomatis.")

        if st.button("📥 Import Sekarang", type="primary", key="btn_import"):
            target_id = semester_id
            if target_id is None:
                try:
                    result = api_client.post(f"/mahasiswa/{mahasiswa_id}/semester", {
                        "tahun_ajaran": "2024/2025",
                        "semester": "GANJIL",
                    })
                    target_id = result.get("id")
                except Exception:
                    pass
            if target_id:
                _do_import(target_id, uploaded.name, content)


def _do_import(semester_id: str, filename: str, content: bytes):
    """Kirim file PDF ke backend."""
    try:
        with st.spinner("Memproses PDF..."):
            result = api_client.post(
                f"/semester/{semester_id}/import-frs",
                files={"file": (filename, content, "application/pdf")},
            )
        st.session_state.last_import_result = result
        st.rerun()
    except APIError as e:
        if e.status_code == 400:
            st.error(f"File tidak valid: {e.message}")
        elif e.status_code == 422:
            st.error(f"Format PDF tidak dapat diproses. {e.message} — Coba input manual di halaman Kalkulator.")
        else:
            st.error(f"Gagal import: {e.message}")
    except Exception as e:
        st.error(f"Koneksi ke backend gagal: {e}")


def _has_graded_courses(mahasiswa_id: str) -> bool:
    """Check if any graded courses exist — indicates transcript has been imported."""
    try:
        result = api_client.get(f"/mahasiswa/{mahasiswa_id}/ipk")
        semesters = result.get("semester", []) if result else []
        for sem in semesters:
            mk_list = api_client.get(f"/semester/{sem['id']}/mata-kuliah")
            data = mk_list.get("data", []) if mk_list else []
            if any(mk.get("nilai_huruf") for mk in data):
                return True
        return False
    except Exception:
        return False


def _render_academic_history(mahasiswa_id: str):
    """Tampilkan riwayat akademik semua semester dengan accordion."""
    try:
        ipk_data = api_client.get(f"/mahasiswa/{mahasiswa_id}/ipk")
    except Exception:
        ipk_data = None

    ipk_val = ipk_data.get("ipk", 0.0) if ipk_data else 0.0
    semesters = ipk_data.get("semester", []) if ipk_data else []

    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.markdown(
            "<div class='section-header'>Academic History</div>"
            "<div class='section-sub'>Riwayat performa akademik seluruh semester</div>",
            unsafe_allow_html=True,
        )
    with col_right:
        st.markdown(
            f"<div style='text-align:right;padding-top:8px;'>"
            f"<span style='font-size:0.72rem;color:#64748b;font-weight:600;"
            f"text-transform:uppercase;letter-spacing:0.06em;'>CUMULATIVE GPA</span><br>"
            f"<span style='font-size:1.8rem;font-weight:800;color:#0f172a;'>{format_ipk(ipk_val)}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    if not semesters:
        st.info("Belum ada data semester.")
        return

    for i, sem in enumerate(reversed(semesters)):
        sem_label = semester_label(sem.get("tahun_ajaran", ""), sem.get("semester", ""))
        ips = sem.get("ips")
        is_current = i == 0

        status_text = "CURRENT SEMESTER" if is_current else "COMPLETED"
        status_color = "#16a34a" if is_current else "#64748b"
        num = len(semesters) - i

        with st.expander(
            f"Semester {num} — {sem_label}  |  IPS: {format_ipk(ips)}",
            expanded=is_current,
        ):
            st.markdown(
                f"""
                <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem;">
                    <div style="background:#1e293b;color:#fff;border-radius:6px;
                                width:32px;height:32px;display:flex;align-items:center;
                                justify-content:center;font-weight:700;">{num}</div>
                    <div>
                        <div style="font-weight:700;font-size:1rem;color:#0f172a;">{h(sem_label)}</div>
                        <div style="font-size:0.72rem;font-weight:600;color:{status_color};">
                            {status_text}
                        </div>
                    </div>
                    <div style="margin-left:auto;text-align:right;">
                        <div style="font-size:0.68rem;color:#64748b;font-weight:600;">IPS</div>
                        <div style="font-size:1.4rem;font-weight:800;color:#16a34a;">{format_ipk(ips)}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            mk_list = _get_mk_semester(sem["id"])
            if mk_list:
                rows = [
                    {
                        "Kode MK": mk.get("kode_mk", ""),
                        "Nama Mata Kuliah": mk.get("nama_mk", ""),
                        "SKS": mk.get("sks", ""),
                        "Nilai": mk.get("nilai_huruf") or "-",
                        "Status": "Selesai" if mk.get("nilai_huruf") else "Berjalan",
                    }
                    for mk in mk_list
                ]
                st.dataframe(rows, use_container_width=True, hide_index=True)
            else:
                st.info("Belum ada mata kuliah di semester ini.")


def _get_semesters(mahasiswa_id: str) -> list:
    try:
        result = api_client.get(f"/mahasiswa/{mahasiswa_id}/semester",
                                params={"page": 1, "per_page": 50})
        return result.get("data", []) if result else []
    except Exception:
        return []


def _get_mk_semester(semester_id: str) -> list:
    try:
        result = api_client.get(f"/semester/{semester_id}/mata-kuliah",
                                params={"page": 1, "per_page": 50})
        return result.get("data", []) if result else []
    except Exception:
        return []