"""
PostGIS → GeoJSON/Shapefile export 스크립트.
QGIS에서 직접 실행하거나, 독립 실행 가능.

사용법:
  python export_to_geojson.py --layer road_damage --output ./output/road_damage.geojson
  python export_to_geojson.py --layer blackice_risk --output ./output/blackice.geojson
  python export_to_geojson.py --all --output-dir ./output

QGIS Python Console에서 실행:
  exec(open('export_to_geojson.py').read())
"""

import json
import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# PostGIS 접속 정보 (환경변수 우선)
DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     int(os.getenv("DB_PORT", 5432)),
    "dbname":   os.getenv("DB_NAME",     "roadgis"),
    "user":     os.getenv("DB_USER",     "roadgis"),
    "password": os.getenv("DB_PASSWORD", "roadgis1234"),
}

# 레이어 정의
LAYER_QUERIES = {
    "road_damage": {
        "query": """
            SELECT
                id,
                damage_type,
                confidence,
                road_name,
                district,
                to_char(detected_at, 'YYYY-MM-DD HH24:MI') AS detected_at,
                ST_AsGeoJSON(location)::json AS geometry
            FROM road_damage
            ORDER BY detected_at DESC
        """,
        "style": {
            "pothole": {"marker-color": "#c62828", "marker-size": "medium"},
            "crack":   {"marker-color": "#e65100", "marker-size": "small"},
        },
    },
    "blackice_risk": {
        "query": """
            SELECT
                b.id,
                b.station_id,
                w.station_name,
                b.risk_level,
                b.risk_label,
                b.temperature,
                b.humidity,
                b.precipitation,
                b.wind_speed,
                to_char(b.predicted_at, 'YYYY-MM-DD HH24:MI') AS predicted_at,
                ST_AsGeoJSON(b.location)::json AS geometry
            FROM blackice_risk b
            LEFT JOIN weather_station w ON w.station_id = b.station_id
            ORDER BY b.predicted_at DESC
        """,
        "style": {
            0: {"marker-color": "#90a4ae"},
            1: {"marker-color": "#ffd54f"},
            2: {"marker-color": "#ff9800"},
            3: {"marker-color": "#c62828"},
        },
    },
}


def get_connection():
    import psycopg2
    return psycopg2.connect(**DB_CONFIG)


def export_layer(layer_name: str, output_path: str) -> int:
    """레이어를 GeoJSON 파일로 내보냄. 반환: 피처 수."""
    if layer_name not in LAYER_QUERIES:
        raise ValueError(f"알 수 없는 레이어: {layer_name}. 사용 가능: {list(LAYER_QUERIES)}")

    config = LAYER_QUERIES[layer_name]
    conn   = get_connection()
    cur    = conn.cursor()

    cur.execute(config["query"])
    columns = [desc[0] for desc in cur.description]
    rows    = cur.fetchall()
    cur.close()
    conn.close()

    features = []
    for row in rows:
        record = dict(zip(columns, row))
        geometry = record.pop("geometry")

        # 스타일 정보 추가
        style_key = record.get("damage_type") or record.get("risk_level")
        style_info = config["style"].get(style_key, {})
        record.update(style_info)

        features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": record,
        })

    geojson = {
        "type": "FeatureCollection",
        "name": layer_name,
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4326"}},
        "features": features,
        "metadata": {
            "exported_at": datetime.now().isoformat(),
            "feature_count": len(features),
            "layer": layer_name,
        },
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2, default=str)

    logger.info("GeoJSON 저장 완료: %s (%d개 피처)", output, len(features))
    return len(features)


def export_all(output_dir: str):
    """모든 레이어를 일괄 export."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    total = 0
    for layer_name in LAYER_QUERIES:
        count = export_layer(layer_name, str(out / f"{layer_name}.geojson"))
        total += count
    logger.info("전체 export 완료: %d개 피처", total)


def load_to_qgis(geojson_path: str, layer_name: str):
    """
    QGIS Python API를 통해 레이어를 직접 로드.
    QGIS Python Console 또는 Processing에서 실행할 때 사용.
    """
    try:
        from qgis.core import QgsVectorLayer, QgsProject
    except ImportError:
        logger.warning("QGIS 환경이 아닙니다. GeoJSON 파일을 QGIS에서 직접 열어주세요: %s", geojson_path)
        return

    layer = QgsVectorLayer(geojson_path, layer_name, "ogr")
    if not layer.isValid():
        logger.error("레이어 로드 실패: %s", geojson_path)
        return

    QgsProject.instance().addMapLayer(layer)
    logger.info("QGIS 레이어 추가 완료: %s", layer_name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="PostGIS → GeoJSON export")
    group  = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--layer",      choices=list(LAYER_QUERIES), help="내보낼 레이어 이름")
    group.add_argument("--all",        action="store_true", help="모든 레이어 내보내기")

    parser.add_argument("--output",     default=None, help="출력 파일 경로 (--layer 전용)")
    parser.add_argument("--output-dir", default="./qgis_output", help="출력 디렉터리 (--all 전용)")
    parser.add_argument("--load-qgis",  action="store_true", help="QGIS에 레이어 자동 로드")
    args = parser.parse_args()

    if args.all:
        export_all(args.output_dir)
    else:
        out = args.output or f"./qgis_output/{args.layer}.geojson"
        count = export_layer(args.layer, out)
        print(f"완료: {out} ({count}개 피처)")
        if args.load_qgis:
            load_to_qgis(out, args.layer)
