from fastapi import APIRouter, HTTPException, Depends
from database import get_db, Mahasiswa
from models import SimulasiRequest
from dependencies import get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1", tags=["Simulasi"])


@router.post("/simulasi/target-ipk")
def simulasi_target_ipk(
    body: SimulasiRequest,
    db: Session = Depends(get_db),
    current_user: Mahasiswa = Depends(get_current_user),
):
    if not (0 <= body.target_ipk <= 4.0):
        raise HTTPException(status_code=422, detail="Target IPK harus antara 0.00 dan 4.00.")
    if not (0 <= body.ipk_saat_ini <= 4.0):
        raise HTTPException(status_code=422, detail="IPK saat ini harus antara 0.00 dan 4.00.")
    if body.sisa_sks <= 0:
        raise HTTPException(status_code=422, detail="Sisa SKS harus lebih dari 0.")

    total_sks_akhir = body.total_sks_ditempuh + body.sisa_sks
    ips_minimum = round(
        (body.target_ipk * total_sks_akhir - body.ipk_saat_ini * body.total_sks_ditempuh)
        / body.sisa_sks, 2,
    )
    return {
        "ips_minimum_diperlukan": ips_minimum,
        "tercapai": ips_minimum <= 4.0,
        "sisa_sks": body.sisa_sks,
    }