from fastapi import APIRouter, HTTPException, Query
from models import MahasiswaCreate, SemesterCreate
from database import mahasiswa_db, semester_db, matakuliah_db, hitung_ips

router = APIRouter(prefix="/api/v1", tags=["Mahasiswa"])


@router.get("/mahasiswa")
def get_mahasiswa(page: int = Query(1), per_page: int = Query(10)):
    start = (page - 1) * per_page
    return {"data": mahasiswa_db[start:start + per_page]}


@router.post("/mahasiswa", status_code=201)
def create_mahasiswa(body: MahasiswaCreate):
    mahasiswa = {
        "id": len(mahasiswa_db) + 1,
        "nim": body.nim,
        "nama": body.nama,
        "program_studi": body.program_studi,
        "total_sks_lulus": 0,
    }
    mahasiswa_db.append(mahasiswa)
    return mahasiswa


@router.get("/mahasiswa/{mahasiswa_id}/ipk")
def get_ipk(mahasiswa_id: int):
    mahasiswa = next((m for m in mahasiswa_db if m["id"] == mahasiswa_id), None)
    if not mahasiswa:
        raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan.")

    sems = [s for s in semester_db if s["mahasiswa_id"] == mahasiswa_id]
    cumulative_mk = []
    for s in sems:
        mk_list = [mk for mk in matakuliah_db if mk["semester_id"] == s["id"]]
        ips, _ = hitung_ips(mk_list)
        s["ips"] = ips
        cumulative_mk.extend(mk_list)

    ipk, total_sks = hitung_ips(cumulative_mk)
    return {"ipk": ipk, "total_sks_kumulatif": total_sks, "semester": sems}


@router.get("/mahasiswa/{mahasiswa_id}/tren")
def get_tren(mahasiswa_id: int):
    sems = [s for s in semester_db if s["mahasiswa_id"] == mahasiswa_id]
    tren = []
    cumulative_mk = []
    for s in sems:
        mk_list = [mk for mk in matakuliah_db if mk["semester_id"] == s["id"]]
        ips, _ = hitung_ips(mk_list)
        cumulative_mk.extend(mk_list)
        ipk_kumulatif, _ = hitung_ips(cumulative_mk)
        tren.append({
            "label": f"{s['tahun_ajaran']} {s['semester']}",
            "ips": ips,
            "ipk_kumulatif": ipk_kumulatif,
        })
    return {"tren": tren}


@router.get("/mahasiswa/{mahasiswa_id}/semester")
def get_semesters(mahasiswa_id: int, page: int = Query(1), per_page: int = Query(50)):
    sems = [s for s in semester_db if s["mahasiswa_id"] == mahasiswa_id]
    start = (page - 1) * per_page
    return {"data": sems[start:start + per_page]}


@router.post("/mahasiswa/{mahasiswa_id}/semester", status_code=201)
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
        "ips": None,
    }
    semester_db.append(sem)
    return sem