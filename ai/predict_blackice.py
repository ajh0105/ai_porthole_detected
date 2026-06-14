"""
블랙아이스 위험도 실시간 예측 모듈.
기상청 초단기실황(getUltraSrtNcst) API로 실시간 기상 데이터를 수집해 예측하고 PostGIS에 저장.

초단기실황 API 특성:
  - 매시간 정시 갱신, 정시+10분 이후 조회 가능
  - 격자 좌표(nx, ny) 사용 → 위경도를 Lambert Conformal Conic 변환으로 변환
  - 응답 카테고리: T1H(기온), REH(습도), RN1(강수량), WSD(풍속), PTY(강수형태)
"""

import logging
import math
import os
import joblib
import requests
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from db_client import get_connection

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
load_dotenv()  # ai/.env도 함께 로드 (로컬 오버라이드용)
logger = logging.getLogger(__name__)

MODEL_PATH  = Path(__file__).parent / "models" / "blackice_model.pkl"
SCALER_PATH = Path(__file__).parent / "models" / "blackice_scaler.pkl"
API_KEY     = os.getenv("WEATHER_API_KEY", "")
NCST_URL    = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
ASOS_URL    = "http://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList"

RISK_LABELS = {0: "안전", 1: "관심", 2: "주의", 3: "위험"}

# 관측소 정보: station_id, 위도, 경도
STATIONS = [
    {"id": "108", "name": "서울", "lat": 37.5714, "lon": 126.9658},
    {"id": "119", "name": "수원", "lat": 37.2636, "lon": 126.9831},
    {"id": "133", "name": "대전", "lat": 36.3714, "lon": 127.3718},
    {"id": "143", "name": "대구", "lat": 35.8831, "lon": 128.6189},
    {"id": "156", "name": "광주", "lat": 35.1722, "lon": 126.8914},
    {"id": "159", "name": "부산", "lat": 35.1044, "lon": 129.0317},
]
STATION_IDS = [s["id"] for s in STATIONS]
_STATION_MAP = {s["id"]: s for s in STATIONS}


# ── 좌표 변환 ────────────────────────────────────────────────────────────────

def latlon_to_grid(lat: float, lon: float) -> tuple[int, int]:
    """위경도 → 기상청 격자 좌표 (Lambert Conformal Conic 투영)."""
    RE, GRID = 6371.00877, 5.0
    SLAT1, SLAT2 = 30.0, 60.0
    OLON, OLAT = 126.0, 38.0
    XO, YO = 43, 136
    D = math.pi / 180.0

    sn = math.log(math.cos(SLAT1 * D) / math.cos(SLAT2 * D)) / \
         math.log(math.tan(math.pi / 4 + SLAT2 * D / 2) /
                  math.tan(math.pi / 4 + SLAT1 * D / 2))
    sf = math.pow(math.tan(math.pi / 4 + SLAT1 * D / 2), sn) * math.cos(SLAT1 * D) / sn
    re = RE / GRID
    ro = re * sf / math.pow(math.tan(math.pi / 4 + OLAT * D / 2), sn)
    ra = re * sf / math.pow(math.tan(math.pi / 4 + lat * D / 2), sn)
    theta = (lon - OLON) * D * sn

    nx = int(ra * math.sin(theta) + XO + 0.5)
    ny = int(ro - ra * math.cos(theta) + YO + 0.5)
    return nx, ny


# ── 기준 시각 계산 ───────────────────────────────────────────────────────────

def _resolve_base_time() -> tuple[str, str]:
    """
    초단기실황 base_date, base_time 계산.
    - 정시+10분 이후부터 해당 시각 데이터 조회 가능
    - 시스템 시계가 API 데이터 범위(~현재 실제 날짜)를 초과하면
      1일씩 후퇴하며 최대 3번 시도 후 포기
    """
    now = datetime.now()
    if now.minute < 10:
        now -= timedelta(hours=1)
    return now.strftime("%Y%m%d"), now.strftime("%H") + "00"


# ── 초단기실황 API 호출 ──────────────────────────────────────────────────────

def _fetch_ncst(nx: int, ny: int) -> dict | None:
    """
    초단기실황 단일 격자 조회.
    데이터 없으면 1시간씩 최대 3회 후퇴 후 None 반환.
    """
    now = datetime.now()
    if now.minute < 10:
        now -= timedelta(hours=1)

    for attempt in range(4):
        target = now - timedelta(hours=attempt)
        base_date = target.strftime("%Y%m%d")
        base_time = target.strftime("%H") + "00"

        params = {
            "serviceKey": API_KEY,
            "pageNo":     1,
            "numOfRows":  10,
            "dataType":   "JSON",
            "base_date":  base_date,
            "base_time":  base_time,
            "nx":         nx,
            "ny":         ny,
        }
        try:
            resp = requests.get(NCST_URL, params=params, timeout=15)
            # 403: API 키 미승인 → 재시도 의미 없음
            if resp.status_code == 403:
                logger.warning("초단기실황 API 미승인(403) — 공공데이터포털에서 '기상청_단기예보' 서비스 신청 필요")
                return None
            resp.raise_for_status()
            body = resp.json().get("response", {})
            code = body.get("header", {}).get("resultCode", "")
            items = body.get("body", {}).get("items", {}).get("item", [])
            if code == "00" and items:
                logger.info("초단기실황 수신 성공 (%s %s)", base_date, base_time)
                return {row["category"]: row["obsrValue"] for row in items}
            logger.debug("초단기실황 데이터 없음 (code=%s, %s %s) — 1시간 후퇴", code, base_date, base_time)
        except requests.RequestException as e:
            logger.warning("초단기실황 API 오류 (%s %s): %s", base_date, base_time, e)
            return None

    return None


def fetch_latest_weather(station_id: str) -> dict | None:
    """
    기상 데이터 조회 우선순위:
      1순위: 기상청 초단기실황 (getUltraSrtNcst) — 실시간, 별도 API 승인 필요
      2순위: 기상청 ASOS 지상관측 (getWthrDataList) — 1~2시간 지연
      3순위: 더미 데이터 (API 키 없거나 두 API 모두 실패 시)
    """
    if not API_KEY:
        logger.warning("WEATHER_API_KEY 미설정 — 더미 데이터를 사용합니다.")
        return _dummy_weather(station_id)

    # 1순위: 초단기실황
    station = _STATION_MAP.get(station_id)
    if station:
        nx, ny = latlon_to_grid(station["lat"], station["lon"])
        logger.debug("[%s] 격자 좌표: nx=%d, ny=%d", station_id, nx, ny)
        raw = _fetch_ncst(nx, ny)
        if raw is not None:
            logger.info("[%s] 초단기실황 데이터 사용", station_id)
            return {
                "ta": raw.get("T1H", "0"),
                "hm": raw.get("REH", "0"),
                "rn": raw.get("RN1", "0"),
                "ws": raw.get("WSD", "0"),
            }
        logger.warning("[%s] 초단기실황 실패 — ASOS로 전환", station_id)

    # 2순위: ASOS
    asos = _fetch_asos(station_id)
    if asos is not None:
        logger.info("[%s] ASOS 데이터 사용", station_id)
        return asos

    # 3순위: 더미
    logger.warning("[%s] ASOS도 실패 — 더미 데이터 사용", station_id)
    return _dummy_weather(station_id)


def _fetch_asos(station_id: str) -> dict | None:
    """ASOS 시간 관측 데이터 조회. 최근 6시간 이내 유효 데이터 탐색."""
    now = datetime.now()
    # 시스템 시계가 API 데이터 보유 범위를 초과하면 1년 전으로 보정
    if now.year > 2025:
        now = now.replace(year=2025)
    for hours_back in range(1, 7):
        target = now - timedelta(hours=hours_back)
        dt_str = target.strftime("%Y%m%d")
        hh_str = target.strftime("%H")
        params = {
            "serviceKey": API_KEY,
            "pageNo":     1,
            "numOfRows":  1,
            "dataType":   "JSON",
            "dataCd":     "ASOS",
            "dateCd":     "HR",
            "startDt":    dt_str,
            "startHh":    hh_str,
            "endDt":      dt_str,
            "endHh":      hh_str,
            "stnIds":     station_id,
        }
        try:
            resp = requests.get(ASOS_URL, params=params, timeout=15)
            resp.raise_for_status()
            body  = resp.json().get("response", {})
            code  = body.get("header", {}).get("resultCode", "")
            items = body.get("body", {}).get("items", {}).get("item", [])
            if code == "00" and items:
                row = items[0]
                logger.debug("[%s] ASOS 데이터 수신 (%s %s)", station_id, dt_str, hh_str)
                return {
                    "ta": row.get("ta", "0") or "0",
                    "hm": row.get("hm", "0") or "0",
                    "rn": row.get("rn", "0") or "0",
                    "ws": row.get("ws", "0") or "0",
                }
            logger.debug("[%s] ASOS 데이터 없음 (code=%s, %s %s)", station_id, code, dt_str, hh_str)
        except requests.RequestException as e:
            logger.warning("[%s] ASOS API 오류 (%s %s): %s", station_id, dt_str, hh_str, e)
    return None


# ── 더미 데이터 ─────────────────────────────────────────────────────────────

def _dummy_weather(station_id: str) -> dict:
    """API 키 미설정 또는 조회 실패 시 테스트용 랜덤 데이터."""
    import random
    return {
        "ta": str(round(random.uniform(-5, 10), 1)),
        "hm": str(random.randint(40, 95)),
        "rn": str(round(random.uniform(0, 3), 1)),
        "ws": str(round(random.uniform(0.5, 8), 1)),
    }


# ── 모델 로드 ────────────────────────────────────────────────────────────────

def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"모델 파일 없음: {MODEL_PATH}\n"
            "train_blackice.py를 먼저 실행하세요."
        )
    return joblib.load(MODEL_PATH), joblib.load(SCALER_PATH)


# ── 예측 + DB 저장 ───────────────────────────────────────────────────────────

def predict_and_save(station_id: str, model, scaler) -> dict | None:
    """관측소별 예측 후 PostGIS에 저장."""
    weather = fetch_latest_weather(station_id)
    if weather is None:
        return None

    try:
        temperature   = float(weather.get("ta", 0) or 0)
        humidity      = float(weather.get("hm", 0) or 0)
        precipitation = float(weather.get("rn", 0) or 0)
        wind_speed    = float(weather.get("ws", 0) or 0)
    except (ValueError, TypeError) as e:
        logger.warning("기상 데이터 파싱 실패 (station=%s): %s", station_id, e)
        return None

    features    = np.array([[temperature, humidity, precipitation, wind_speed]])
    features_sc = scaler.transform(features)
    risk_level  = int(model.predict(features_sc)[0])
    risk_label  = RISK_LABELS[risk_level]

    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.execute(
            "SELECT ST_X(location), ST_Y(location) FROM weather_station WHERE station_id = %s",
            (station_id,)
        )
        row = cur.fetchone()
        if row is None:
            logger.warning("관측소 좌표 없음: %s", station_id)
            return None

        lng, lat = row
        cur.execute("""
            INSERT INTO blackice_risk
                (station_id, location, risk_level, risk_label,
                 temperature, humidity, precipitation, wind_speed, predicted_at)
            VALUES (%s, ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    %s, %s, %s, %s, %s, %s, NOW())
        """, (
            station_id, lng, lat,
            risk_level, risk_label,
            temperature, humidity, precipitation, wind_speed,
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error("DB 저장 실패 (station=%s): %s", station_id, e)
        return None
    finally:
        cur.close()
        conn.close()

    logger.info("[%s] %s(L%d) | 기온=%.1f°C 습도=%.0f%% 강수=%.1fmm 풍속=%.1fm/s",
                station_id, risk_label, risk_level, temperature, humidity, precipitation, wind_speed)
    return {
        "station_id":    station_id,
        "risk_level":    risk_level,
        "risk_label":    risk_label,
        "temperature":   temperature,
        "humidity":      humidity,
        "precipitation": precipitation,
        "wind_speed":    wind_speed,
        "latitude":      lat,
        "longitude":     lng,
    }


# ── 전체 관측소 일괄 예측 ────────────────────────────────────────────────────

def run_prediction(station_ids: list[str] | None = None) -> list[dict]:
    model, scaler = load_model()
    targets = station_ids if station_ids else STATION_IDS
    results = []
    for sid in targets:
        r = predict_and_save(sid, model, scaler)
        if r:
            results.append(r)
    logger.info("블랙아이스 예측 완료: %d/%d 관측소", len(results), len(targets))
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run_prediction()
