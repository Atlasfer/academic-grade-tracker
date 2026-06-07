from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db, Semester, MataKuliah, GRADE_POINTS
from models import MataKuliahCreate

router = APIRouter(prefix="/api/v1", tags=["Mata Kuliah"])


@router.post("/semester/{semester_id}/mata-kuliah", status_code=201)
def create_matakuliah(semester_id: int, body: MataKuliahCreate, db: Session = Depends(get_db)):
    sem = db.query(Semester).filter(Semester.id == semester_id).first()
    if not sem:
        raise HTTPException(status_code=404, detail="Semester tidak ditemukan.")

    duplicate = db.query(MataKuliah).filter(
        MataKuliah.semester_id == semester_id,
        MataKuliah.kode_mk == body.kode_mk,
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Kode MK sudah ada di semester ini.")

    mk = MataKuliah(
        semester_id=semester_id,
        kode_mk=body.kode_mk,
        nama_mk=body.nama_mk,
        sks=body.sks,
        nilai_huruf=body.nilai_huruf,
        nilai_bobot=GRADE_POINTS.get(body.nilai_huruf) if body.nilai_huruf else None,
    )
    db.add(mk)
    db.commit()
    db.refresh(mk)
    return {
        "id": mk.id,
        "semester_id": mk.semester_id,
        "kode_mk": mk.kode_mk,
        "nama_mk": mk.nama_mk,
        "sks": mk.sks,
        "nilai_huruf": mk.nilai_huruf,
        "nilai_bobot": mk.nilai_bobot,
    }


@router.delete("/mata-kuliah/{mk_id}")
def delete_matakuliah(mk_id: int, db: Session = Depends(get_db)):
    mk = db.query(MataKuliah).filter(MataKuliah.id == mk_id).first()
    if not mk:
        raise HTTPException(status_code=404, detail="Mata kuliah tidak ditemukan.")
    db.delete(mk)
    db.commit()
    return {"detail": "Mata kuliah berhasil dihapus."}