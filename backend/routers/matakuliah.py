from fastapi import APIRouter, HTTPException
from models import MataKuliahCreate
from database import semester_db, matakuliah_db, GRADE_POINTS

router = APIRouter(prefix="/api/v1", tags=["Mata Kuliah"])


@router.post("/semester/{semester_id}/mata-kuliah", status_code=201)
def create_matakuliah(semester_id: int, body: MataKuliahCreate):
    if not any(s["id"] == semester_id for s in semester_db):
        raise HTTPException(status_code=404, detail="Semester tidak ditemukan.")
    if any(mk["semester_id"] == semester_id and mk["kode_mk"] == body.kode_mk for mk in matakuliah_db):
        raise HTTPException(status_code=409, detail="Kode MK sudah ada di semester ini.")

    mk = {
        "id": len(matakuliah_db) + 1,
        "semester_id": semester_id,
        "kode_mk": body.kode_mk,
        "nama_mk": body.nama_mk,
        "sks": body.sks,
        "nilai_huruf": body.nilai_huruf,
        "nilai_bobot": GRADE_POINTS.get(body.nilai_huruf) if body.nilai_huruf else None,
    }
    matakuliah_db.append(mk)
    return mk


@router.delete("/mata-kuliah/{mk_id}")
def delete_matakuliah(mk_id: int):
    if not any(mk["id"] == mk_id for mk in matakuliah_db):
        raise HTTPException(status_code=404, detail="Mata kuliah tidak ditemukan.")
    matakuliah_db[:] = [mk for mk in matakuliah_db if mk["id"] != mk_id]
    return {"detail": "Mata kuliah berhasil dihapus."}