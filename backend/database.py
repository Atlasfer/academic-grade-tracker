from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") 

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# --- orm model

class Mahasiswa(Base):
    __tablename__ = "mahasiswa"

    id              = Column(Integer, primary_key=True, index=True)
    nim             = Column(String(20), unique=True, nullable=False)
    nama            = Column(String(200), nullable=False)
    program_studi   = Column(String(100), nullable=False)
    total_sks_lulus = Column(Integer, default=0)

    semesters = relationship("Semester", back_populates="mahasiswa", cascade="all, delete")


class Semester(Base):
    __tablename__ = "semester"

    id           = Column(Integer, primary_key=True, index=True)
    mahasiswa_id = Column(Integer, ForeignKey("mahasiswa.id", ondelete="CASCADE"), nullable=False)
    tahun_ajaran = Column(String(10), nullable=False)
    semester     = Column(String(10), nullable=False)

    mahasiswa   = relationship("Mahasiswa", back_populates="semesters")
    mata_kuliah = relationship("MataKuliah", back_populates="semester", cascade="all, delete")


class MataKuliah(Base):
    __tablename__ = "mata_kuliah"

    id          = Column(Integer, primary_key=True, index=True)
    semester_id = Column(Integer, ForeignKey("semester.id", ondelete="CASCADE"), nullable=False)
    kode_mk     = Column(String(20), nullable=False)
    nama_mk     = Column(String(200), nullable=False)
    sks         = Column(Integer, nullable=False)
    nilai_huruf = Column(String(2), nullable=True)
    nilai_bobot = Column(Float, nullable=True)

    semester = relationship("Semester", back_populates="mata_kuliah")

#----utils


GRADE_POINTS: dict = {
    "A": 4.0, "AB": 3.5, "B": 3.0,
    "BC": 2.5, "C": 2.0, "D": 1.0, "E": 0.0,
}


def hitung_ips(mk_list) -> tuple[float, int]:
    total_bobot = 0.0
    total_sks = 0
    for mk in mk_list:
        nilai = mk.nilai_huruf if hasattr(mk, "nilai_huruf") else mk.get("nilai_huruf")
        sks   = mk.sks        if hasattr(mk, "sks")         else mk.get("sks", 0)
        if nilai and nilai in GRADE_POINTS:
            total_bobot += sks * GRADE_POINTS[nilai]
            total_sks   += sks
    ips = round(total_bobot / total_sks, 2) if total_sks else 0.0
    return ips, total_sks


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)