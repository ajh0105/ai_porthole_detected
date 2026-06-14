"""
RDD2022 도로 파손 탐지 데이터셋 다운로드 및 환경 구성 스크립트.

다운로드 방법 우선순위:
  1. Kaggle API (kaggle.json 있을 때) — 47,420장 YOLO 포맷 직접 수신
  2. Figshare 직접 다운로드    — 동일 데이터, VOC XML → YOLO 자동 변환 포함

실행:
  python setup_dataset.py                   # 자동 선택
  python setup_dataset.py --method kaggle   # Kaggle 강제
  python setup_dataset.py --method figshare # Figshare 강제
  python setup_dataset.py --verify-only     # 폴더 구조만 검증
"""

import argparse
import json
import os
import shutil
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
import requests
from tqdm import tqdm

# ── 경로 상수 ─────────────────────────────────────────────────────────────────
AI_DIR      = Path(__file__).parent
DATA_DIR    = AI_DIR / "data"
DATASET_DIR = DATA_DIR / "dataset"
DOWNLOAD_DIR = DATA_DIR / "_download_cache"

# ── RDD2022 클래스 정의 ────────────────────────────────────────────────────────
# 7개 원본 클래스 → 우리 시스템의 pothole / crack 으로 매핑
RDD_CLASSES = [
    "D00_Longitudinal_Crack",
    "D10_Transverse_Crack",
    "D20_Alligator_Crack",
    "D40_Pothole",
    "D44_Other_Corruption",
    "D50_Block_Crack",
    "D10D40_Repair",
]

# VOC XML에서 사용하는 원본 레이블 이름
VOC_LABEL_MAP = {
    "D00": 0, "D01": 0,
    "D10": 1, "D11": 1,
    "D20": 2, "D21": 2,
    "D40": 3,
    "D44": 4,
    "D50": 5,
    "D43": 6,
}

# detect_road.py에서 pothole / crack 으로 축약할 매핑
DAMAGE_TYPE_MAP = {
    "D00_Longitudinal_Crack": "crack",
    "D10_Transverse_Crack":   "crack",
    "D20_Alligator_Crack":    "crack",
    "D40_Pothole":            "pothole",
    "D44_Other_Corruption":   "crack",
    "D50_Block_Crack":        "crack",
    "D10D40_Repair":          "crack",
}

KAGGLE_DATASET = "sreekaraditya/rdd2022-yolo-crackscan-v2"

FIGSHARE_URL = (
    "https://figshare.com/ndownloader/articles/21431547/versions/1"
)


# ── 유틸리티 ──────────────────────────────────────────────────────────────────

def _download_file(url: str, dest: Path, desc: str = "다운로드"):
    dest.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    with open(dest, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=desc) as bar:
        for chunk in resp.iter_content(chunk_size=65536):
            f.write(chunk)
            bar.update(len(chunk))


def _check_kaggle_creds() -> bool:
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if kaggle_json.exists():
        return True
    # 환경변수 방식
    return bool(os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY"))


# ── Kaggle 다운로드 ────────────────────────────────────────────────────────────

def download_kaggle():
    print("[Kaggle] RDD2022 YOLO 데이터셋 다운로드 시작...")
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    import subprocess
    zip_path = DOWNLOAD_DIR / "rdd2022-yolo-crackscan-v2.zip"
    if not zip_path.exists():
        subprocess.run(
            ["python", "-m", "kaggle", "datasets", "download",
             "-d", KAGGLE_DATASET, "-p", str(DOWNLOAD_DIR)],
            check=True,
        )
    else:
        print(f"[Kaggle] 캐시 존재: {zip_path}")

    print("[Kaggle] 압축 해제 중...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(DOWNLOAD_DIR / "rdd2022_yolo")

    _organize_kaggle(DOWNLOAD_DIR / "rdd2022_yolo")


def _organize_kaggle(src: Path):
    """Kaggle 다운로드 폴더 구조를 DATASET_DIR로 정리."""
    DATASET_DIR.mkdir(parents=True, exist_ok=True)

    # Kaggle 패키지에 따라 폴더 구조가 다를 수 있음
    for split in ("train", "valid", "test"):
        for sub in ("images", "labels"):
            # 여러 가능한 경로 패턴 탐색
            candidates = [
                src / split / sub,
                src / "RDD2022" / split / sub,
                src / "dataset" / split / sub,
            ]
            found = next((c for c in candidates if c.exists()), None)
            if found:
                dest = DATASET_DIR / split / sub
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(found, dest)
                count = len(list(dest.glob("*")))
                print(f"  복사: {found} → {dest}  ({count}개 파일)")

    _write_data_yaml()


# ── Figshare 다운로드 + VOC 변환 ───────────────────────────────────────────────

def download_figshare():
    print("[Figshare] RDD2022 데이터셋 다운로드 시작 (VOC XML 포맷, 약 3~4GB)...")
    zip_path = DOWNLOAD_DIR / "RDD2022_figshare.zip"
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    if not zip_path.exists():
        _download_file(FIGSHARE_URL, zip_path, "RDD2022 다운로드")
    else:
        print(f"[Figshare] 캐시 존재: {zip_path}")

    extract_dir = DOWNLOAD_DIR / "RDD2022_extracted"
    if not extract_dir.exists():
        print("[Figshare] 압축 해제 중 (시간이 걸릴 수 있습니다)...")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extract_dir)

    _convert_voc_to_yolo(extract_dir)
    _write_data_yaml()


def _convert_voc_to_yolo(src_root: Path):
    """VOC XML 어노테이션 → YOLO .txt 형식으로 변환."""
    import random
    print("[변환] VOC XML → YOLO 형식 변환 중...")

    all_samples: list[tuple[Path, Path]] = []  # (image_path, xml_path)

    # 다양한 국가별 폴더 순회
    for country_dir in src_root.rglob("annotations/xmls"):
        xml_dir = country_dir
        img_dir = country_dir.parent.parent / "images"
        if not img_dir.exists():
            img_dir = country_dir.parent / "images"
        for xml_file in xml_dir.glob("*.xml"):
            img_file = (img_dir / xml_file.stem).with_suffix(".jpg")
            if not img_file.exists():
                img_file = (img_dir / xml_file.stem).with_suffix(".png")
            if img_file.exists():
                all_samples.append((img_file, xml_file))

    if not all_samples:
        raise RuntimeError(f"VOC XML 파일을 찾을 수 없습니다: {src_root}")

    print(f"  총 샘플: {len(all_samples)}개")

    # 8:1:1 분할
    random.seed(42)
    random.shuffle(all_samples)
    n = len(all_samples)
    splits = {
        "train": all_samples[:int(n * 0.8)],
        "valid": all_samples[int(n * 0.8):int(n * 0.9)],
        "test":  all_samples[int(n * 0.9):],
    }

    for split, samples in splits.items():
        img_dest = DATASET_DIR / split / "images"
        lbl_dest = DATASET_DIR / split / "labels"
        img_dest.mkdir(parents=True, exist_ok=True)
        lbl_dest.mkdir(parents=True, exist_ok=True)

        for img_path, xml_path in tqdm(samples, desc=f"  {split}"):
            shutil.copy(img_path, img_dest / img_path.name)
            yolo_txt = _parse_voc_xml(xml_path)
            (lbl_dest / xml_path.stem).with_suffix(".txt").write_text(yolo_txt)

    for split, samples in splits.items():
        print(f"  {split}: {len(samples)}장")


def _parse_voc_xml(xml_path: Path) -> str:
    """VOC XML → YOLO .txt 변환. 좌표를 0~1 정규화."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    size = root.find("size")
    w = int(size.findtext("width", "0") or "1")
    h = int(size.findtext("height", "0") or "1")
    if w == 0 or h == 0:
        return ""

    lines = []
    for obj in root.findall("object"):
        name = (obj.findtext("name") or "").strip()
        cls_id = VOC_LABEL_MAP.get(name)
        if cls_id is None:
            continue
        bndbox = obj.find("bndbox")
        if bndbox is None:
            continue
        xmin = float(bndbox.findtext("xmin", "0") or "0")
        ymin = float(bndbox.findtext("ymin", "0") or "0")
        xmax = float(bndbox.findtext("xmax", str(w)) or str(w))
        ymax = float(bndbox.findtext("ymax", str(h)) or str(h))

        cx = ((xmin + xmax) / 2) / w
        cy = ((ymin + ymax) / 2) / h
        bw = (xmax - xmin) / w
        bh = (ymax - ymin) / h
        lines.append(f"{cls_id} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")

    return "\n".join(lines)


# ── data.yaml 생성 ─────────────────────────────────────────────────────────────

def _write_data_yaml():
    yaml_path = DATASET_DIR / "data.yaml"
    content = f"""# RDD2022 Road Damage Detection Dataset
# 7 damage classes — mapped to pothole/crack at inference in detect_road.py

path: {DATASET_DIR.as_posix()}
train: train/images
val:   valid/images
test:  test/images

nc: 7
names:
  0: D00_Longitudinal_Crack
  1: D10_Transverse_Crack
  2: D20_Alligator_Crack
  3: D40_Pothole
  4: D44_Other_Corruption
  5: D50_Block_Crack
  6: D10D40_Repair

# detect_road.py 에서 damage_type 으로 변환 매핑
# D00/D10/D20/D44/D50/D10D40 -> crack
# D40                         -> pothole
"""
    yaml_path.write_text(content, encoding="utf-8")
    print(f"[YAML] data.yaml 생성: {yaml_path}")


# ── 검증 ──────────────────────────────────────────────────────────────────────

def verify():
    ok = True
    for split in ("train", "valid"):
        img_dir = DATASET_DIR / split / "images"
        lbl_dir = DATASET_DIR / split / "labels"
        n_img = len(list(img_dir.glob("*.jpg"))) + len(list(img_dir.glob("*.png"))) if img_dir.exists() else 0
        n_lbl = len(list(lbl_dir.glob("*.txt"))) if lbl_dir.exists() else 0
        status = "OK" if n_img > 0 and n_lbl > 0 else "MISSING"
        print(f"  [{status}] {split}: images={n_img}  labels={n_lbl}")
        if status == "MISSING":
            ok = False

    yaml_path = DATASET_DIR / "data.yaml"
    print(f"  [{'OK' if yaml_path.exists() else 'MISSING'}] data.yaml: {yaml_path}")
    if not yaml_path.exists():
        ok = False

    if ok:
        print("\n데이터셋 준비 완료. 학습 실행:")
        print("  python train_yolo.py --epochs 100 --imgsz 640 --batch 16")
    else:
        print("\n데이터셋이 준비되지 않았습니다. setup_dataset.py를 실행하세요.")
    return ok


# ── 메인 ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="RDD2022 데이터셋 다운로드 및 셋업")
    parser.add_argument("--method", choices=["kaggle", "figshare", "auto"],
                        default="auto", help="다운로드 방법 선택")
    parser.add_argument("--verify-only", action="store_true",
                        help="다운로드 없이 폴더 구조만 검증")
    args = parser.parse_args()

    if args.verify_only:
        verify()
        return

    print("=" * 60)
    print("  RDD2022 도로 파손 탐지 데이터셋 셋업")
    print("=" * 60)

    method = args.method
    if method == "auto":
        method = "kaggle" if _check_kaggle_creds() else "figshare"
        print(f"[auto] 감지된 방법: {method}")

    if method == "kaggle":
        if not _check_kaggle_creds():
            print("""
[ERROR] Kaggle 자격증명이 없습니다.

설정 방법:
  1. https://www.kaggle.com/settings > API > Create New Token
  2. 다운로드된 kaggle.json을 C:\\Users\\<사용자명>\\.kaggle\\kaggle.json 에 복사
  3. 다시 실행

또는 Figshare로 자동 다운로드:
  python setup_dataset.py --method figshare
""")
            return
        download_kaggle()
    elif method == "figshare":
        download_figshare()

    print("\n[검증]")
    verify()


if __name__ == "__main__":
    main()
