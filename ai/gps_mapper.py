"""
이미지 EXIF 또는 별도 GPS 파일에서 위경도를 추출하는 모듈.
GPS 파일 형식: CSV (filename, latitude, longitude)
"""

import os
import csv
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from pathlib import Path


def _get_exif_data(image_path: str) -> dict:
    img = Image.open(image_path)
    exif_data = img._getexif()
    if not exif_data:
        return {}
    result = {}
    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag == "GPSInfo":
            gps = {}
            for gps_id, gps_val in value.items():
                gps_tag = GPSTAGS.get(gps_id, gps_id)
                gps[gps_tag] = gps_val
            result["GPSInfo"] = gps
        else:
            result[tag] = value
    return result


def _dms_to_decimal(dms, ref: str) -> float:
    degrees = float(dms[0])
    minutes = float(dms[1])
    seconds = float(dms[2])
    decimal = degrees + minutes / 60 + seconds / 3600
    if ref in ("S", "W"):
        decimal = -decimal
    return decimal


def extract_gps_from_exif(image_path: str) -> tuple[float, float] | None:
    """EXIF에서 위경도 추출. 반환: (latitude, longitude) 또는 None."""
    exif = _get_exif_data(image_path)
    gps_info = exif.get("GPSInfo")
    if not gps_info:
        return None

    lat = _dms_to_decimal(gps_info["GPSLatitude"], gps_info["GPSLatitudeRef"])
    lng = _dms_to_decimal(gps_info["GPSLongitude"], gps_info["GPSLongitudeRef"])
    return lat, lng


def load_gps_csv(csv_path: str) -> dict[str, tuple[float, float]]:
    """CSV 파일에서 {filename: (lat, lng)} 딕셔너리 로드."""
    gps_map = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename = Path(row["filename"]).name
            gps_map[filename] = (float(row["latitude"]), float(row["longitude"]))
    return gps_map


def get_gps(image_path: str, gps_map: dict | None = None) -> tuple[float, float] | None:
    """
    EXIF → CSV gps_map 순으로 GPS 좌표 탐색.
    반환: (latitude, longitude) 또는 None
    """
    coords = extract_gps_from_exif(image_path)
    if coords:
        return coords

    if gps_map:
        key = Path(image_path).name
        return gps_map.get(key)

    return None
