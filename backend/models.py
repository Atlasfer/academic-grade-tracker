from pydantic import BaseModel

class MahasiswaCreate(BaseModel):
    nim: str
    nama: str
    program_studi: str


class SemesterCreate(BaseModel):
    tahun_ajaran: str
    semester: str  # GANJIL / GENAP / PENDEK


class MataKuliahCreate(BaseModel):
    kode_mk: str
    nama_mk: str
    sks: int
    nilai_huruf: str | None = None


class SimulasiRequest(BaseModel):
    ipk_saat_ini: float
    total_sks_ditempuh: int
    target_ipk: float
    sisa_sks: int