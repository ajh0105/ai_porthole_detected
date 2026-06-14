"""
YOLOv11 기반 도로 파손 탐지 모듈.
CUDA C:\cuda 환경 사용.
"""

import logging
import os
import torch
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO

from gps_mapper import get_gps, load_gps_csv
from db_client import get_connection

logger = logging.getLogger(__name__)

os.environ["CUDA_PATH"] = r"C:\cuda"

MODEL_PATH = Path(__file__).parent / "models" / "rdd2022-yolo12s-best.pt"

# rezzzq/yolo12s-road-damage-rdd2022 (YOLOv12s, RDD2022 전체 47,420장 학습)
_RDD_CLASS_NAMES = {
    0: "D00",
    1: "D10",
    2: "D20",
    3: "D40",
    4: "Repair",
}

_DAMAGE_TYPE_MAP = {
    "D00":    "crack",
    "D10":    "crack",
    "D20":    "crack",
    "D40":    "pothole",
    "Repair": "crack",
    # 구형 모델 호환
    "pothole": "pothole",
    "crack":   "crack",
}

LABEL_MAP = {0: "pothole", 1: "crack"}  # 구형 2-클래스 모델용 fallback


def _resolve_damage_type(cls_id: int, model_names: dict | None) -> str:
    """모델 클래스 ID → damage_type(pothole/crack) 변환."""
    if model_names:
        class_name = model_names.get(cls_id, "")
        return _DAMAGE_TYPE_MAP.get(class_name, "crack")
    return LABEL_MAP.get(cls_id, "crack")


def load_model() -> YOLO:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"모델 파일이 없습니다: {MODEL_PATH}\n"
            "train_yolo.py를 먼저 실행하거나 models/ 폴더에 pothole-crack.pt를 배치하세요."
        )
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info("YOLO 디바이스: %s", device)
    model = YOLO(str(MODEL_PATH))
    model.to(device)
    return model


def detect_images(
    image_paths: list[str],
    gps_csv: str | None = None,
    conf_threshold: float = 0.4,
    batch_id: int | None = None,
) -> list[dict]:
    """
    이미지 목록에서 도로 파손을 탐지하고 PostGIS에 저장.
    GPS가 없는 이미지는 탐지 결과만 반환하고 DB 저장은 건너뜀.
    """
    model   = load_model()
    # 모델에 등록된 클래스 이름 조회 (RDD2022 7클래스 또는 구형 2클래스)
    model_names: dict | None = getattr(model, "names", None)
    gps_map = load_gps_csv(gps_csv) if gps_csv and Path(gps_csv).exists() else {}

    results_all: list[dict] = []
    saved_count = 0

    conn = get_connection()
    cur  = conn.cursor()

    for img_path in image_paths:
        try:
            results = model.predict(img_path, conf=conf_threshold, verbose=False)
        except Exception as e:
            logger.warning("이미지 탐지 실패 [%s]: %s", img_path, e)
            _update_batch_progress(cur, conn, batch_id)
            continue

        gps = get_gps(img_path, gps_map)
        if gps is None:
            logger.debug("GPS 정보 없음 — DB 저장 건너뜀: %s", img_path)

        for result in results:
            boxes = result.boxes
            if boxes is None or len(boxes) == 0:
                continue

            for box in boxes:
                cls_id      = int(box.cls[0])
                conf        = float(box.conf[0])
                damage_type = _resolve_damage_type(cls_id, model_names)
                xywhn       = box.xywhn[0].tolist()

                record: dict = {
                    "damage_type": damage_type,
                    "confidence":  conf,
                    "image_path":  str(img_path),
                    "bbox_x": xywhn[0],
                    "bbox_y": xywhn[1],
                    "bbox_w": xywhn[2],
                    "bbox_h": xywhn[3],
                    "latitude":  gps[0] if gps else None,
                    "longitude": gps[1] if gps else None,
                    "detected_at": datetime.now().isoformat(),
                }
                results_all.append(record)

                if gps:
                    try:
                        cur.execute("""
                            INSERT INTO road_damage
                                (damage_type, confidence, location, image_path,
                                 bbox_x, bbox_y, bbox_w, bbox_h, detected_at)
                            VALUES (%s, %s,
                                ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                                %s, %s, %s, %s, %s, NOW())
                        """, (
                            damage_type, conf,
                            gps[1], gps[0],
                            str(img_path),
                            xywhn[0], xywhn[1], xywhn[2], xywhn[3],
                        ))
                        conn.commit()
                        saved_count += 1
                    except Exception as e:
                        conn.rollback()
                        logger.error("DB 저장 실패 [%s]: %s", img_path, e)

        _update_batch_progress(cur, conn, batch_id)

    cur.close()
    conn.close()

    logger.info(
        "탐지 완료: 처리=%d장, 탐지=%d건, DB저장=%d건",
        len(image_paths), len(results_all), saved_count,
    )
    return results_all


def _update_batch_progress(cur, conn, batch_id: int | None):
    if batch_id:
        try:
            cur.execute(
                "UPDATE detection_batch SET processed = processed + 1 WHERE id = %s",
                (batch_id,),
            )
            conn.commit()
        except Exception:
            conn.rollback()


def main():
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="YOLOv11 도로 파손 탐지")
    parser.add_argument("images", nargs="+", help="탐지할 이미지 경로")
    parser.add_argument("--gps-csv", default=None, help="GPS CSV 파일 경로")
    parser.add_argument("--conf",    type=float, default=0.4, help="신뢰도 임계값")
    args = parser.parse_args()

    results = detect_images(args.images, gps_csv=args.gps_csv, conf_threshold=args.conf)
    for r in results:
        print(f"  [{r['damage_type']}] conf={r['confidence']:.3f}  gps=({r['latitude']}, {r['longitude']})")


if __name__ == "__main__":
    main()
