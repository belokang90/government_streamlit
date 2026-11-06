"""기존 정부광고 데이터 저장소에서 CSV 5개를 내려받아 검증합니다.
실행: python setup_data.py
"""
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import quote
import hashlib

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)

SOURCE = "https://raw.githubusercontent.com/belokang90/government-ad-execution-2022-2026/main/data/"
FILES = {
    2022: ("2022년도_정부광고집행내역_260930 기준.csv", "5fc806e0696f26a5569e78f47e64c9be1a68ff65"),
    2023: ("2023년도_정부광고집행내역_260930 기준.csv", "0070ad995ae501b86f405cf2841fbc4be7442ec5"),
    2024: ("2024년도_정부광고집행내역_260930 기준.csv", "f7accb8acd218a84422b80b85eea373c5595e953"),
    2025: ("2025년도_정부광고집행내역_260930 기준.csv", "ccbd986cb797c88f9df52c94361ad607ab6b8e97"),
    2026: ("2026년도_정부광고집행내역_260930 기준.csv", "ea356557e5d97f676b13f107cc2e58e3e082c44a"),
}

def git_sha(path):
    h = hashlib.sha1()
    h.update(f"blob {path.stat().st_size}\0".encode())
    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

for year, (filename, expected) in FILES.items():
    target = DATA / filename
    if target.exists():
        if git_sha(target) == expected:
            print(f"{year}: 검증 완료 (기존 파일)")
        else:
            print(f"{year}: 다른 버전의 CSV가 이미 있습니다. 덮어쓰지 않고 유지합니다.")
        continue
    url = SOURCE + quote(filename)
    print(f"{year}: 데이터 다운로드 시작")
    temp = DATA / (filename + ".partial")
    try:
        with urlopen(Request(url, headers={"User-Agent":"government-streamlit-data-setup"}), timeout=60) as response, temp.open("wb") as out:
            while chunk := response.read(1024 * 1024):
                out.write(chunk)
        if git_sha(temp) != expected:
            raise ValueError(f"{year}년 원본 검증 실패")
        temp.replace(target)
        print(f"{year}: 다운로드 및 Git SHA-1 검사 완료")
    except Exception:
        temp.unlink(missing_ok=True)
        raise
print("데이터 준비를 마쳤습니다.")
