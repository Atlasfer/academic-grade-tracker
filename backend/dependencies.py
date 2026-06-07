from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db, Mahasiswa
from routers.auth import decode_token
from typing import Optional


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Mahasiswa:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token tidak ditemukan.")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    mahasiswa_id = int(payload.get("sub"))
    mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.id == mahasiswa_id).first()
    if not mahasiswa:
        raise HTTPException(status_code=401, detail="User tidak ditemukan.")
    return mahasiswa