from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db, Mahasiswa
from models import RegisterRequest, LoginRequest
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "changethisinproduction")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(mahasiswa_id: int, nim: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(
        {"sub": str(mahasiswa_id), "nim": nim, "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Token tidak valid atau sudah expired.")


@router.post("/register", status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Mahasiswa).filter(Mahasiswa.nim == body.nim).first()
    if existing:
        raise HTTPException(status_code=409, detail="NIM sudah terdaftar.")

    mahasiswa = Mahasiswa(
        nim=body.nim,
        nama=body.nama,
        program_studi=body.program_studi,
        total_sks_lulus=0,
        password_hash=hash_password(body.password),
    )
    db.add(mahasiswa)
    db.commit()
    db.refresh(mahasiswa)

    token = create_token(mahasiswa.id, mahasiswa.nim)
    return {
        "token": token,
        "mahasiswa": {
            "id": mahasiswa.id,
            "nim": mahasiswa.nim,
            "nama": mahasiswa.nama,
            "program_studi": mahasiswa.program_studi,
            "total_sks_lulus": mahasiswa.total_sks_lulus,
        }
    }


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.nim == body.nim).first()
    if not mahasiswa or not verify_password(body.password, mahasiswa.password_hash):
        raise HTTPException(status_code=401, detail="NIM atau password salah.")

    token = create_token(mahasiswa.id, mahasiswa.nim)
    return {
        "token": token,
        "mahasiswa": {
            "id": mahasiswa.id,
            "nim": mahasiswa.nim,
            "nama": mahasiswa.nama,
            "program_studi": mahasiswa.program_studi,
            "total_sks_lulus": mahasiswa.total_sks_lulus,
        }
    }