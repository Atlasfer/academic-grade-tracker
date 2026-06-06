from fastapi import APIRouter, HTTPException, File, UploadFile
from database import semester_db, matakuliah_db, GRADE_POINTS, hitung_ips
import re
import io

router = APIRouter(prefix="/api/v1", tags=["Semester"])


@router.delete("/semester/{semester_id}")
def delete_semester(semester_id: int):
    global semester_db, matakuliah_db
    if not any(s["id"] == semester_id for s in semester_db):
        raise HTTPException(status_code=404, detail="Semester tidak ditemukan.")
    semester_db[:] = [s for s in semester_db if s["id"] != semester_id]
    matakuliah_db[:] = [mk for mk in matakuliah_db if mk["semester_id"] != semester_id]
    return {"detail": "Semester berhasil dihapus."}


@router.get("/semester/{semester_id}/ips")
def get_ips(semester_id: int):
    if not any(s["id"] == semester_id for s in semester_db):
        raise HTTPException(status_code=404, detail="Semester tidak ditemukan.")
    mk_list = [mk for mk in matakuliah_db if mk["semester_id"] == semester_id]
    ips, total_sks = hitung_ips(mk_list)
    return {"ips": ips, "total_sks_semester": total_sks, "mata_kuliah": mk_list}


@router.get("/semester/{semester_id}/mata-kuliah")
def get_matakuliah(semester_id: int):
    mk_list = [mk for mk in matakuliah_db if mk["semester_id"] == semester_id]
    return {"data": mk_list}


@router.post("/semester/{semester_id}/import-frs")
async def import_frs(semester_id: int, file: UploadFile = File(...)):
    if not any(s["id"] == semester_id for s in semester_db):
        raise HTTPException(status_code=404, detail="Semester tidak ditemukan.")
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File harus berformat PDF.")

    content = await file.read()
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Gagal membaca PDF: {str(e)}")

    pattern = re.compile(
        r"([A-Z]{2}\d{4})\s+(.+?)\s+(\d)\s+([A-E]{1,2}|-)\s*$",
        re.MULTILINE
    )
    berhasil, gagal, detail_gagal = 0, 0, []

    for i, match in enumerate(pattern.finditer(text), start=1):
        kode, nama, sks, nilai = match.groups()
        nilai_huruf = None if nilai == "-" else nilai

        if any(mk["semester_id"] == semester_id and mk["kode_mk"] == kode for mk in matakuliah_db):
            gagal += 1
            detail_gagal.append({"baris": i, "alasan": f"Kode '{kode}' sudah ada."})
            continue

        matakuliah_db.append({
            "id": len(matakuliah_db) + 1,
            "semester_id": semester_id,
            "kode_mk": kode,
            "nama_mk": nama.strip(),
            "sks": int(sks),
            "nilai_huruf": nilai_huruf,
            "nilai_bobot": GRADE_POINTS.get(nilai_huruf) if nilai_huruf else None,
        })
        berhasil += 1

    if berhasil == 0 and gagal == 0:
        raise HTTPException(
            status_code=422,
            detail="Tidak ada data mata kuliah yang dapat dikenali dari PDF ini."
        )
    return {"berhasil": berhasil, "gagal": gagal, "detail_gagal": detail_gagal}