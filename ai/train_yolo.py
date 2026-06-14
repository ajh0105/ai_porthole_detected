"""
YOLOv11 도로 파손 탐지 모델 학습 스크립트.
데이터셋: RDD2022 (47,420장, 7클래스) — setup_dataset.py로 다운로드
CUDA C:\cuda 환경 사용.

클래스:
  0: D00_Longitudinal_Crack (종방향 균열)
  1: D10_Transverse_Crack   (횡방향 균열)
  2: D20_Alligator_Crack    (그물망 균열)
  3: D40_Pothole            (포트홀)
  4: D44_Other_Corruption   (기타 손상)
  5: D50_Block_Crack        (블록 균열)
  6: D10D40_Repair          (보수 흔적)

실행 예시:
  python train_yolo.py                       # 기본 100 epochs
  python train_yolo.py --epochs 200 --model yolo11s.pt   # small 모델
  python train_yolo.py --validate            # 학습 후 검증 포함
"""

import argparse
import os
import shutil
import torch
from pathlib import Path

os.environ["CUDA_PATH"] = r"C:\cuda"

DATASET_YAML = Path(__file__).parent / "data" / "dataset" / "data.yaml"
OUTPUT_DIR   = Path(__file__).parent / "models"

# 권장 모델 크기: n(최소)→s→m→l→x(최대)
# VRAM 6GB 이상: yolo11m.pt, 이하: yolo11s.pt, CPU only: yolo11n.pt
DEFAULT_MODEL = "yolo11s.pt"


def train(
    epochs: int = 100,
    imgsz: int = 640,
    batch: int = 16,
    patience: int = 30,
    model_name: str = DEFAULT_MODEL,
):
    from ultralytics import YOLO

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[train_yolo] 디바이스: {device}")
    if device == "cuda":
        vram = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"[train_yolo] GPU VRAM: {vram:.1f} GB")
        # VRAM 부족 시 batch 자동 조정
        if vram < 6 and batch > 8:
            batch = 8
            print(f"[train_yolo] VRAM < 6GB → batch={batch}으로 조정")

    if not DATASET_YAML.exists():
        raise FileNotFoundError(
            f"데이터셋 YAML이 없습니다: {DATASET_YAML}\n"
            "먼저 실행하세요: python setup_dataset.py"
        )

    model = YOLO(model_name)
    print(f"[train_yolo] 모델: {model_name}  데이터: {DATASET_YAML}")

    results = model.train(
        data=str(DATASET_YAML),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        patience=patience,
        device=device,
        project=str(OUTPUT_DIR / "runs"),
        name="pothole-crack",
        exist_ok=True,
        # ── 데이터 증강 (도로 촬영 환경 고려) ────────────────────────────
        hsv_h=0.015,   # 색조 변화 (날씨/조명 차이)
        hsv_s=0.7,     # 채도
        hsv_v=0.4,     # 명도 (야간/터널 대응)
        degrees=5.0,   # 회전 (카메라 각도 차이)
        translate=0.1,
        scale=0.5,
        flipud=0.1,    # 상하 반전 (언덕 구간)
        fliplr=0.5,    # 좌우 반전
        mosaic=1.0,    # 모자이크 증강 (소물체 탐지 향상)
        mixup=0.15,    # 믹스업
        copy_paste=0.1,
        # ── 학습 하이퍼파라미터 ───────────────────────────────────────────
        lr0=0.01,
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3,
        box=7.5,       # bbox loss gain
        cls=0.5,       # classification loss gain
        dfl=1.5,       # distribution focal loss
        # ── 저장 설정 ─────────────────────────────────────────────────────
        save=True,
        save_period=10,   # 10 epoch마다 체크포인트 저장
        plots=True,
        verbose=True,
    )

    # 최적 가중치 → models/pothole-crack.pt 복사
    best = OUTPUT_DIR / "runs" / "pothole-crack" / "weights" / "best.pt"
    if best.exists():
        dest = OUTPUT_DIR / "pothole-crack.pt"
        shutil.copy(best, dest)
        print(f"[train_yolo] 최적 가중치 저장: {dest}")
    else:
        print("[train_yolo] 경고: best.pt를 찾을 수 없습니다.")

    return results


def validate(model_path: str | None = None):
    from ultralytics import YOLO

    pt = Path(model_path) if model_path else OUTPUT_DIR / "pothole-crack.pt"
    if not pt.exists():
        raise FileNotFoundError(f"모델 파일 없음: {pt}")

    model  = YOLO(str(pt))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    metrics = model.val(data=str(DATASET_YAML), device=device)

    print("\n[검증 결과]")
    print(f"  mAP@50    : {metrics.box.map50:.4f}")
    print(f"  mAP@50-95 : {metrics.box.map:.4f}")
    print(f"  Precision  : {metrics.box.mp:.4f}")
    print(f"  Recall     : {metrics.box.mr:.4f}")
    return metrics


def main():
    parser = argparse.ArgumentParser(description="YOLOv11 도로 파손 탐지 모델 학습")
    parser.add_argument("--epochs",    type=int,   default=100,         help="학습 epochs 수")
    parser.add_argument("--imgsz",     type=int,   default=640,         help="입력 이미지 크기")
    parser.add_argument("--batch",     type=int,   default=16,          help="배치 크기 (VRAM 부족 시 8로 줄임)")
    parser.add_argument("--patience",  type=int,   default=30,          help="Early stopping patience")
    parser.add_argument("--model",     type=str,   default=DEFAULT_MODEL, help="기본 모델 (yolo11n/s/m/l/x.pt)")
    parser.add_argument("--validate",  action="store_true",             help="학습 완료 후 검증 실행")
    parser.add_argument("--val-only",  type=str,   default=None,        help="학습 없이 해당 .pt 파일 검증만")
    args = parser.parse_args()

    if args.val_only:
        validate(args.val_only)
    else:
        train(args.epochs, args.imgsz, args.batch, args.patience, args.model)
        if args.validate:
            validate()


if __name__ == "__main__":
    main()
