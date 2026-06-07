from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from database import get_db, Mahasiswa, Semester, MataKuliah, hitung_ips
from models import MahasiswaCreate, SemesterCreate

router = APIRouter(prefix="/api/v1", tags=["Mahasiswa"])


@router.get("/mahasiswa")
def get_mahasiswa(page: int = Query(1), per_page: int = Query(10), db: Session = Depends(get_db)):
    offset = (page - 1) * per_page
    rows = db.query(Mahasiswa).offset(offset).limit(per_page).all()
    return {"data": [_fmt_mahasiswa(m) for m in rows]}


@router.post("/mahasiswa", status_code=201)
def create_mahasiswa(body: MahasiswaCreate, db: Session = Depends(get_db)):
    mahasiswa = Mahasiswa(
        nim=body.nim,
        nama=body.nama,
        program_studi=body.program_studi,
        total_sks_lulus=0,
    )
    db.add(mahasiswa)
    db.commit()
    db.refresh(mahasiswa)
    return _fmt_mahasiswa(mahasiswa)


@router.get("/mahasiswa/{mahasiswa_id}/ipk")
def get_ipk(mahasiswa_id: int, db: Session = Depends(get_db)):
    mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.id == mahasiswa_id).first()
    if not mahasiswa:
        raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan.")

    sems = db.query(Semester).filter(Semester.mahasiswa_id == mahasiswa_id).all()
    cumulative_mk = []
    sem_list = []
    for s in sems:
        mk_list = db.query(MataKuliah).filter(MataKuliah.semester_id == s.id).all()
        ips, _ = hitung_ips(mk_list)
        cumulative_mk.extend(mk_list)
        sem_list.append({**_fmt_semester(s), "ips": ips})

    ipk, total_sks = hitung_ips(cumulative_mk)
    return {"ipk": ipk, "total_sks_kumulatif": total_sks, "semester": sem_list}


@router.get("/mahasiswa/{mahasiswa_id}/tren")
def get_tren(mahasiswa_id: int, db: Session = Depends(get_db)):
    sems = db.query(Semester).filter(Semester.mahasiswa_id == mahasiswa_id).all()
    tren = []
    cumulative_mk = []
    for s in sems:
        mk_list = db.query(MataKuliah).filter(MataKuliah.semester_id == s.id).all()
        ips, _ = hitung_ips(mk_list)
        cumulative_mk.extend(mk_list)
        ipk_kumulatif, _ = hitung_ips(cumulative_mk)
        tren.append({
            "label": f"{s.tahun_ajaran} {s.semester}",
            "ips": ips,
            "ipk_kumulatif": ipk_kumulatif,
        })
    return {"tren": tren}


@router.get("/mahasiswa/{mahasiswa_id}/semester")
def get_semesters(mahasiswa_id: int, page: int = Query(1), per_page: int = Query(50), db: Session = Depends(get_db)):
    offset = (page - 1) * per_page
    sems = db.query(Semester).filter(Semester.mahasiswa_id == mahasiswa_id).offset(offset).limit(per_page).all()
    return {"data": [_fmt_semester(s) for s in sems]}


@router.post("/mahasiswa/{mahasiswa_id}/semester", status_code=201)
def create_semester(mahasiswa_id: int, body: SemesterCreate, db: Session = Depends(get_db)):
    duplicate = db.query(Semester).filter(
        Semester.mahasiswa_id == mahasiswa_id,
        Semester.tahun_ajaran == body.tahun_ajaran,
        Semester.semester == body.semester,
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Semester sudah ada.")

    sem = Semester(mahasiswa_id=mahasiswa_id, tahun_ajaran=body.tahun_ajaran, semester=body.semester)
    db.add(sem)
    db.commit()
    db.refresh(sem)
    return _fmt_semester(sem)


# --- forrmating

def _fmt_mahasiswa(m: Mahasiswa) -> dict:
    return {
        "id": m.id,
        "nim": m.nim,
        "nama": m.nama,
        "program_studi": m.program_studi,
        "total_sks_lulus": m.total_sks_lulus,
    }

def _fmt_semester(s: Semester) -> dict:
    return {
        "id": s.id,
        "mahasiswa_id": s.mahasiswa_id,
        "tahun_ajaran": s.tahun_ajaran,
        "semester": s.semester,
    }