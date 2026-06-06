from html import escape as _escape

def h(value) -> str:
    """Escape nilai untuk dimasukkan ke dalam HTML string (mencegah XSS)."""
    return _escape(str(value)) if value is not None else ""


NILAI_HURUF_LIST = ["A", "AB", "B", "BC", "C", "D", "E"]
SKS_LIST = [1, 2, 3, 4, 5, 6]

KONVERSI_NILAI = {
    "A": 4.0,
    "AB": 3.5,
    "B": 3.0,
    "BC": 2.5,
    "C": 2.0,
    "D": 1.0,
    "E": 0.0,
}

SEMESTER_ORDER = {"GANJIL": 1, "GENAP": 2, "PENDEK": 3}
SEMESTER_LABEL = {"GANJIL": "Ganjil", "GENAP": "Genap", "PENDEK": "Pendek"}


def format_ipk(value: float | None) -> str:
    """Format nilai IPK/IPS menjadi string 2 desimal."""
    if value is None:
        return "-"
    return f"{value:.2f}"


def ipk_badge_color(ipk: float | None) -> str:
    """Kembalikan warna CSS berdasarkan range IPK."""
    if ipk is None:
        return "#888"
    if ipk >= 3.75:
        return "#16a34a"
    if ipk >= 3.5:
        return "#2563eb"
    if ipk >= 3.0:
        return "#d97706"
    return "#dc2626"


def ipk_status_label(ipk: float | None) -> str:
    """Label predikat kelulusan berdasarkan IPK."""
    if ipk is None:
        return ""
    if ipk >= 3.75:
        return "Cum Laude"
    if ipk >= 3.5:
        return "Sangat Memuaskan"
    if ipk >= 3.0:
        return "Memuaskan"
    return "Perlu Ditingkatkan"


def goal_progress_pct(ipk_saat_ini: float | None, target: float = 3.75) -> float:
    """Hitung persentase kemajuan menuju target IPK."""
    if ipk_saat_ini is None:
        return 0.0
    return min(round((ipk_saat_ini / target) * 100, 1), 100.0)


def semester_label(tahun_ajaran: str, semester: str) -> str:
    """Format label semester: 'Ganjil 2023/2024'."""
    return f"{SEMESTER_LABEL.get(semester, semester)} {tahun_ajaran}"


def format_tahun_ajaran(raw: str) -> str:
    """Validasi dan format tahun ajaran dari input '2023' -> '2023/2024'."""
    try:
        year = int(raw)
        return f"{year}/{year + 1}"
    except ValueError:
        return raw
