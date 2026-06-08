from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from sqlalchemy.orm import Session
from database import get_db, Mahasiswa, Semester, MataKuliah, GRADE_POINTS, hitung_ips
from dependencies import get_current_user
import pdfplumber
import re
import io

router = APIRouter(prefix="/api/v1", tags=["Semester"])


# --- Routes ---

@router.delete("/semester/{semester_id}")
def delete_semester(
    semester_id: int,
    db: Session = Depends(get_db),
    current_user: Mahasiswa = Depends(get_current_user),
):
    sem = _get_semester_owned(semester_id, current_user, db)
    db.delete(sem)
    db.commit()
    return {"detail": "Semester berhasil dihapus."}


@router.get("/semester/{semester_id}/ips")
def get_ips(
    semester_id: int,
    db: Session = Depends(get_db),
    current_user: Mahasiswa = Depends(get_current_user),
):
    sem = _get_semester_owned(semester_id, current_user, db)
    mk_list = db.query(MataKuliah).filter(MataKuliah.semester_id == semester_id).all()
    ips, total_sks = hitung_ips(mk_list)
    return {
        "ips": ips,
        "total_sks_semester": total_sks,
        "mata_kuliah": [_fmt_mk(mk) for mk in mk_list],
    }


@router.get("/semester/{semester_id}/mata-kuliah")
def get_matakuliah(
    semester_id: int,
    db: Session = Depends(get_db),
    current_user: Mahasiswa = Depends(get_current_user),
):
    _get_semester_owned(semester_id, current_user, db)
    mk_list = db.query(MataKuliah).filter(MataKuliah.semester_id == semester_id).all()
    return {"data": [_fmt_mk(mk) for mk in mk_list]}


@router.post("/semester/{semester_id}/import-frs")
async def import_frs(
    semester_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Mahasiswa = Depends(get_current_user),
):
    sem = _get_semester_owned(semester_id, current_user, db)
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File harus berformat PDF.")

    content = await file.read()
    try:
        text = ""
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Gagal membaca PDF: {str(e)}")

    is_transcript = "TRANSKRIP" in text.upper() or "TRANSCRIPT" in text.upper()

    if not is_transcript:
        # Block FRS if no transcript has been imported yet
        has_transcript = db.query(MataKuliah).join(Semester).filter(
            Semester.mahasiswa_id == sem.mahasiswa_id,
            MataKuliah.nilai_huruf != None,
        ).first()
        if not has_transcript:
            raise HTTPException(
                status_code=400,
                detail="Impor transkrip terlebih dahulu sebelum mengimpor FRS."
            )

    if is_transcript:
        return _parse_transcript(text, sem.mahasiswa_id, db)
    else:
        return _parse_frs(text, semester_id, sem.mahasiswa_id, db)


# --- PDF Parsers ---

def _parse_frs(text: str, semester_id: int, mahasiswa_id: int, db: Session) -> dict:
    """FRS format: NO  KODE  NAMA MK  SKS  KELAS"""
    pattern = re.compile(
        r"^\s*\d+\s+([A-Z]{2}\d{6})\s+(.+?)\s+(\d+)\s+[A-Z]\s*$",
        re.MULTILINE
    )

    nrp_match = re.search(r"\b(\d{10})\b", text)
    nrp = nrp_match.group(1) if nrp_match else None

    sem_header = re.search(r"(Ganjil|Genap|Pendek)\s+(\d{4})", text, re.IGNORECASE)
    if sem_header:
        jenis_raw, tahun_str = sem_header.groups()
        jenis = jenis_raw.upper()
        tahun = int(tahun_str)

        # Tahun ajaran == tahun yang di mention
        tahun_ajaran = f"{tahun}/{tahun + 1}"

        # Block if existing semester already has graded courses
        existing = db.query(Semester).filter(
            Semester.mahasiswa_id == mahasiswa_id,
            Semester.tahun_ajaran == tahun_ajaran,
            Semester.semester == jenis,
        ).first()
        if existing:
            has_grades = db.query(MataKuliah).filter(
                MataKuliah.semester_id == existing.id,
                MataKuliah.nilai_huruf != None,
            ).first()
            if has_grades:
                raise HTTPException(
                    status_code=409,
                    detail=f"Semester {jenis} {tahun_ajaran} sudah memiliki nilai dari transkrip. "
                           f"FRS tidak dapat digabung dengan semester yang sudah dinilai."
                )

        target_sem = _get_or_create_semester(mahasiswa_id, tahun_ajaran, jenis, db)
        semester_id = target_sem.id

    berhasil, gagal, detail_gagal = 0, 0, []

    for i, match in enumerate(pattern.finditer(text), start=1):
        kode, nama, sks = match.groups()
        duplicate = db.query(MataKuliah).filter(
            MataKuliah.semester_id == semester_id,
            MataKuliah.kode_mk == kode,
        ).first()
        if duplicate:
            gagal += 1
            detail_gagal.append({"baris": i, "alasan": f"Kode '{kode}' sudah ada."})
            continue

        db.add(MataKuliah(
            semester_id=semester_id,
            kode_mk=kode,
            nama_mk=nama.strip(),
            sks=int(sks),
            nilai_huruf=None,
            nilai_bobot=None,
        ))
        berhasil += 1

    if berhasil == 0 and gagal == 0:
        raise HTTPException(status_code=422, detail="Tidak ada data mata kuliah yang dapat dikenali dari PDF ini.")

    db.commit()
    return {"berhasil": berhasil, "gagal": gagal, "detail_gagal": detail_gagal}


def _parse_transcript(text: str, mahasiswa_id: int, db: Session) -> dict:
    """Transcript format: NO  KODE  NAMA MK  SEM  SKS  NILAI"""
    pattern = re.compile(
        r"^\s*(\d+)\s+([A-Z]{2}\d{6})\s+(.+?)\s+(\d+)\s+(\d+)\s+(A|AB|B|BC|C|D|E)(?:\s|$)",
        re.MULTILINE
    )

    nrp_match = re.search(r"\b(\d{10})\b", text)
    nrp = nrp_match.group(1) if nrp_match else None
    entrance_year = _get_anchor_year(mahasiswa_id, db, fallback_nrp=nrp)

    sem_map: dict[int, list] = {}
    for i, match in enumerate(pattern.finditer(text), start=1):
        _, kode, nama, sem_num, sks, nilai = match.groups()
        sem_map.setdefault(int(sem_num), []).append({
            "kode": kode,
            "nama": nama.strip(),
            "sks": int(sks),
            "nilai": nilai,
            "baris": i,
        })

    if not sem_map:
        raise HTTPException(status_code=422, detail="Tidak ada data mata kuliah yang dapat dikenali dari PDF ini.")

    berhasil, gagal, detail_gagal = 0, 0, []

    for sem_num, courses in sorted(sem_map.items()):
        tahun_ajaran, jenis = _sem_num_to_tahun_ajaran(sem_num, entrance_year)
        sem = _get_or_create_semester(mahasiswa_id, tahun_ajaran, jenis, db)

        for course in courses:
            duplicate = db.query(MataKuliah).filter(
                MataKuliah.semester_id == sem.id,
                MataKuliah.kode_mk == course["kode"],
            ).first()
            if duplicate:
                gagal += 1
                detail_gagal.append({"baris": course["baris"], "alasan": f"Kode '{course['kode']}' sudah ada."})
                continue

            db.add(MataKuliah(
                semester_id=sem.id,
                kode_mk=course["kode"],
                nama_mk=course["nama"],
                sks=course["sks"],
                nilai_huruf=course["nilai"],
                nilai_bobot=GRADE_POINTS.get(course["nilai"]),
            ))
            berhasil += 1

    db.commit()
    return {"berhasil": berhasil, "gagal": gagal, "detail_gagal": detail_gagal}


# --- Semester Helpers ---

def _get_anchor_year(mahasiswa_id: int, db: Session, fallback_nrp: str = None) -> int:
    existing = db.query(Semester).filter(
        Semester.mahasiswa_id == mahasiswa_id
    ).order_by(Semester.tahun_ajaran.asc()).first()
    if existing:
        return int(existing.tahun_ajaran.split("/")[0])
    if fallback_nrp and len(fallback_nrp) >= 8:
        return 2000 + int(fallback_nrp[4:6])
    return 2024


def _sem_num_to_tahun_ajaran(sem_num: int, entrance_year: int) -> tuple[str, str]:
    year_offset = (sem_num - 1) // 2
    tahun_mulai = entrance_year + year_offset
    jenis = "GANJIL" if sem_num % 2 == 1 else "GENAP"
    return f"{tahun_mulai}/{tahun_mulai + 1}", jenis


def _get_or_create_semester(mahasiswa_id: int, tahun_ajaran: str, jenis: str, db: Session) -> Semester:
    sem = db.query(Semester).filter(
        Semester.mahasiswa_id == mahasiswa_id,
        Semester.tahun_ajaran == tahun_ajaran,
        Semester.semester == jenis,
    ).first()
    if not sem:
        sem = Semester(mahasiswa_id=mahasiswa_id, tahun_ajaran=tahun_ajaran, semester=jenis)
        db.add(sem)
        db.flush()
    return sem


def _get_semester_owned(semester_id: int, current_user: Mahasiswa, db: Session) -> Semester:
    sem = db.query(Semester).filter(Semester.id == semester_id).first()
    if not sem:
        raise HTTPException(status_code=404, detail="Semester tidak ditemukan.")
    if sem.mahasiswa_id != current_user.id:
        raise HTTPException(status_code=403, detail="Akses ditolak.")
    return sem


# --- Formatter ---

def _fmt_mk(mk: MataKuliah) -> dict:
    return {
        "id": mk.id,
        "semester_id": mk.semester_id,
        "kode_mk": mk.kode_mk,
        "nama_mk": mk.nama_mk,
        "sks": mk.sks,
        "nilai_huruf": mk.nilai_huruf,
        "nilai_bobot": mk.nilai_bobot,
    }