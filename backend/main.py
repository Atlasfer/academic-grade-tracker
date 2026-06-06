from fastapi import APIRouter, FastAPI, Query, HTTPException, File, UploadFile
import re
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
router = APIRouter(prefix="/api/v1")


mahasiswa_db = [] # TODO real database later
matkuliah_db = []

GRADE_POINTS = {
    "A": 4.0, 
    "AB": 3.5, 
    "B": 3.0, 
    "BC": 2.5, 
    "C": 2.0, 
    "D": 1.0, 
    "E": 0.0
}

def _hitung_ips(mk_list: list):
    total_bobot = sum(
        mk["sks"] * GRADE_POINTS.get(mk.get("nilai_huruf", ""), 0)
        for mk in mk_list if mk.get("nilai_huruf")
    )
    total_sks = sum(mk["sks"] for mk in mk_list if mk.get("nilai_huruf"))
    ips = round(total_bobot / total_sks, 2) if total_sks else 0.0
    return ips, total_sks



# profil.py
class MahasiswaCreate(BaseModel):
    nim: str
    nama: str
    program_studi: str

@router.get("/mahasiswa")
def get_mahasiswa(page: int = Query(1), per_page: int = Query(10)):
    start = (page - 1) * per_page
    end = start + per_page
    return {"data": mahasiswa_db[start:end]}
    
@router.post("/mahasiswa")
def create_mahasiswa(body: MahasiswaCreate):
    mahasiswa = {
        "id": len(mahasiswa_db) + 1,
        "nim": body.nim,
        "nama": body.nama,
        "program_studi": body.prodi,
        "total_sks_lulus": 0,
    }
    mahasiswa_db.append(mahasiswa)
    return mahasiswa

#dashboard.py

@router.get("/mahasiswa/{mahasiswa_id}/ipk")
def get_ipk(mahasiswa_id: int):
    mahasiswa = next((m for m in mahasiswa_db if m["id"] == mahasiswa_id), None)
    if not mahasiswa:
        raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan")
    
    sems = [s for s in semester_db if s["mahasiswa_id"] == mahasiswa_id]
    all_mk = []
    for s in sems:
        mk_list = [mk for mk in matakuliah_db if mk["semester_id"] == s["id"]]
        ips, sks = _hitung_ips(mk_list)
        all_mk.extend(mk_list)
        s["ips"] = ips

    ipk, total_sks = _hitung_ips(all_mk)

    return {
        "ipk": ipk,
        "total_sks_kumulatif": total_sks,
        "semester": sems,
    }


@router.get("/mahasiswa/{mahasiswa_id}/tren")
def get_tren(mahasiswa_id: int):
    sems = [s for s in semester_db if s["mahasiswa_id"] == mahasiswa_id]
    tren = []
    cumulative_mk = []
    for s in sems:
        mk_list = [mk for mk in matakuliah_db if mk["semester_id"] == s["id"]]
        ips, _ = _hitung_ips(mk_list)
        cumulative_mk.extend(mk_list)
        ipk_kumulatif, _ = _hitung_ips(cumulative_mk)
        tren.append({
            "label": f"{s['tahun_ajaran']} {s['semester']}",
            "ips": ips,
            "ipk_kumulatif": ipk_kumulatif,
        })
    return {"tren": tren}


@router.get("/semester/{semester_id}/mata-kuliah")
def get_matakuliah(semester_id: int):
    mk_list = [mk for mk in matakuliah_db if mk["semester_id"] == semester_id]
    return {"data": mk_list}

@router.get("/")
def root():
    return {"status": "ok"}

# kalkulator.py

class SemesterCreate(BaseModel):
    tahun_ajaran: str
    semester: str  # GANJIL / GENAP / PENDEK

class MataKuliahCreate(BaseModel):
    kode_mk: str
    nama_mk: str
    sks: int
    nilai_huruf: str | None = None


# Semester ---

@router.get("/mahasiswa/{mahasiswa_id}/semester")
def get_semesters(mahasiswa_id: int, page: int = Query(1), per_page: int = Query(50)):
    sems = [s for s in semester_db if s["mahasiswa_id"] == mahasiswa_id]
    start = (page - 1) * per_page
    return {"data": sems[start:start + per_page]}


@router.post("/mahasiswa/{mahasiswa_id}/semester")
def create_semester(mahasiswa_id: int, body: SemesterCreate):

    duplicate = any(
        s["mahasiswa_id"] == mahasiswa_id
        and s["tahun_ajaran"] == body.tahun_ajaran
        and s["semester"] == body.semester
        for s in semester_db
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="Semester sudah ada.")

    sem = {
        "id": len(semester_db) + 1,
        "mahasiswa_id": mahasiswa_id,
        "tahun_ajaran": body.tahun_ajaran,
        "semester": body.semester,
    }
    semester_db.append(sem)
    return sem


@router.delete("/semester/{semester_id}")
def delete_semester(semester_id: int):
    global semester_db, matakuliah_db
    sem = next((s for s in semester_db if s["id"] == semester_id), None)
    if not sem:
        raise HTTPException(status_code=404, detail="Semester tidak ditemukan.")
    semester_db = [s for s in semester_db if s["id"] != semester_id]
    matakuliah_db = [mk for mk in matakuliah_db if mk["semester_id"] != semester_id]
    return {"detail": "Semester berhasil dihapus."}


@router.get("/semester/{semester_id}/ips")
def get_ips(semester_id: int):
    sem = next((s for s in semester_db if s["id"] == semester_id), None)
    if not sem:
        raise HTTPException(status_code=404, detail="Semester tidak ditemukan.")
    mk_list = [mk for mk in matakuliah_db if mk["semester_id"] == semester_id]
    ips, total_sks = _hitung_ips(mk_list)
    return {
        "ips": ips,
        "total_sks_semester": total_sks,
        "mata_kuliah": mk_list,
    }


# --- matkul

@router.post("/semester/{semester_id}/mata-kuliah")
def create_matakuliah(semester_id: int, body: MataKuliahCreate):
    sem = next((s for s in semester_db if s["id"] == semester_id), None)
    if not sem:
        raise HTTPException(status_code=404, detail="Semester tidak ditemukan.")

    duplicate = any(
        mk["semester_id"] == semester_id and mk["kode_mk"] == body.kode_mk
        for mk in matakuliah_db
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="Kode MK sudah ada di semester ini.")

    bobot = GRADE_POINTS.get(body.nilai_huruf) if body.nilai_huruf else None
    mk = {
        "id": len(matakuliah_db) + 1,
        "semester_id": semester_id,
        "kode_mk": body.kode_mk,
        "nama_mk": body.nama_mk,
        "sks": body.sks,
        "nilai_huruf": body.nilai_huruf,
        "nilai_bobot": bobot,
    }
    matakuliah_db.append(mk)
    return mk


@router.delete("/mata-kuliah/{mk_id}")
def delete_matakuliah(mk_id: int):
    global matakuliah_db
    mk = next((m for m in matakuliah_db if m["id"] == mk_id), None)
    if not mk:
        raise HTTPException(status_code=404, detail="Mata kuliah tidak ditemukan.")
    matakuliah_db = [m for m in matakuliah_db if m["id"] != mk_id]
    return {"detail": "Mata kuliah berhasil dihapus."}

# simulasi.py

class SimulasiRequest(BaseModel):
    ipk_saat_ini: float
    total_sks_ditempuh: int
    target_ipk: float
    sisa_sks: int


@router.post("/simulasi/target-ipk")
def simulasi_target_ipk(body: SimulasiRequest):
    total_sks_akhir = body.total_sks_ditempuh + body.sisa_sks
    ips_minimum = (
        body.target_ipk * total_sks_akhir - body.ipk_saat_ini * body.total_sks_ditempuh
    ) / body.sisa_sks
    ips_minimum = round(ips_minimum, 2)

    return {
        "ips_minimum_diperlukan": ips_minimum,
        "tercapai": ips_minimum <= 4.0,
        "sisa_sks": body.sisa_sks,
    }

#import_frs.py (pdfplumber)

@router.post("/semester/{semester_id}/import-frs")
async def import_frs(semester_id: int, file: UploadFile = File(...)):
    sem = next((s for s in semester_db if s["id"] == semester_id), None)
    if not sem:
        raise HTTPException(status_code=404, detail="Semester tidak ditemukan.")

    content = await file.read()
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File harus berformat PDF.")

    # TODO: Parse PDF

    berhasil = 0
    gagal = 0
    detail_gagal = []

    for i, match in enumerate(pattern.finditer(text), start=1):
        kode, nama, sks, nilai = match.groups()
        nilai_huruf = None if nilai == "-" else nilai

        # Skip duplicates
        duplicate = any(
            mk["semester_id"] == semester_id and mk["kode_mk"] == kode
            for mk in matakuliah_db
        )
        if duplicate:
            gagal += 1
            detail_gagal.append({"baris": i, "alasan": f"Kode '{kode}' sudah ada."})
            continue

        bobot = GRADE_POINTS.get(nilai_huruf) if nilai_huruf else None
        matakuliah_db.append({
            "id": len(matakuliah_db) + 1,
            "semester_id": semester_id,
            "kode_mk": kode,
            "nama_mk": nama.strip(),
            "sks": int(sks),
            "nilai_huruf": nilai_huruf,
            "nilai_bobot": bobot,
        })
        berhasil += 1

    if berhasil == 0 and gagal == 0:
        raise HTTPException(
            status_code=422,
            detail="Tidak ada data mata kuliah yang dapat dikenali dari PDF ini."
        )

    return {"berhasil": berhasil, "gagal": gagal, "detail_gagal": detail_gagal}

app.include_router(router)