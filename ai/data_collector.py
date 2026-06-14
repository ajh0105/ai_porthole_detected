"""
기상청 ASOS/AWS 데이터 수집 모듈.
공공데이터포털 기상청_지상(종관, ASOS) 시간자료 조회서비스 사용.
"""

import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from db_client import get_connection

load_dotenv()

API_KEY      = os.getenv("WEATHER_API_KEY", "")
ASOS_URL     = "http://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList"
SAVE_DIR     = Path(__file__).parent / "data" / "weather"

# 서울 인근 주요 ASOS 지점 번호
STATION_IDS = ["108", "119", "133", "143", "156", "159"]


def fetch_asos_hourly(
    station_id: str,
    date_from: str,   # "202311010000"
    date_to: str,     # "202403312300"
    page_size: int = 720,
) -> pd.DataFrame:
    """ASOS 시간자료 API 호출 → DataFrame 반환."""
    all_rows = []
    page_no = 1

    while True:
        params = {
            "serviceKey":    API_KEY,
            "pageNo":        page_no,
            "numOfRows":     page_size,
            "dataType":      "JSON",
            "dataCd":        "ASOS",
            "dateCd":        "HR",
            "startDt":       date_from[:8],
            "startHh":       date_from[8:10],
            "endDt":         date_to[:8],
            "endHh":         date_to[8:10],
            "stnIds":        station_id,
        }

        resp = requests.get(ASOS_URL, params=params, timeout=30)
        resp.raise_for_status()
        body = resp.json().get("response", {}).get("body", {})
        items = body.get("items", {}).get("item", [])

        if not items:
            break

        all_rows.extend(items)
        total = int(body.get("totalCount", 0))
        if page_no * page_size >= total:
            break
        page_no += 1
        time.sleep(0.5)  # API 호출 제한 준수

    if not all_rows:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    return df


def collect_winter_data(years: list[int] | None = None) -> pd.DataFrame:
    """
    최근 5년 동절기(11월~3월) ASOS 데이터 수집.
    저장: data/weather/asos_winter.csv
    """
    if years is None:
        current_year = datetime.now().year
        years = list(range(current_year - 5, current_year))

    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    all_dfs = []

    for year in years:
        for station_id in STATION_IDS:
            print(f"  수집 중: 지점={station_id}, {year}년 11월 ~ {year+1}년 3월")

            date_from = f"{year}11010000"
            date_to   = f"{year+1}03312300"

            df = fetch_asos_hourly(station_id, date_from, date_to)
            if df.empty:
                print(f"  [경고] 데이터 없음: 지점={station_id}, 기간={date_from}~{date_to}")
                continue

            df["station_id"] = station_id
            all_dfs.append(df)
            time.sleep(1)

    if not all_dfs:
        print("[data_collector] 수집된 데이터 없음")
        return pd.DataFrame()

    combined = pd.concat(all_dfs, ignore_index=True)
    save_path = SAVE_DIR / "asos_winter.csv"
    combined.to_csv(save_path, index=False, encoding="utf-8-sig")
    print(f"[data_collector] 저장 완료: {save_path} ({len(combined)}행)")
    return combined


def preprocess_for_blackice(df: pd.DataFrame) -> pd.DataFrame:
    """
    수집된 ASOS 데이터를 블랙아이스 예측 모델 학습용으로 전처리.
    블랙아이스 발생 조건 기반 레이블 생성:
      - 0 (안전):   기온 > 2°C
      - 1 (관심):   0°C < 기온 ≤ 2°C
      - 2 (주의):  -2°C < 기온 ≤ 0°C 이고 강수 있음
      - 3 (위험):   기온 ≤ -2°C 이고 강수 있음 또는 습도 ≥ 80%
    """
    rename_map = {
        "ta":  "temperature",    # 기온
        "hm":  "humidity",       # 습도
        "rn":  "precipitation",  # 1시간 강수량
        "ws":  "wind_speed",     # 풍속
        "td":  "dew_point",      # 이슬점 온도
        "pa":  "pressure",       # 기압
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    numeric_cols = ["temperature", "humidity", "precipitation", "wind_speed", "dew_point", "pressure"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["precipitation"] = df["precipitation"].fillna(0)
    df = df.dropna(subset=["temperature", "humidity"])

    def label_risk(row):
        t = row["temperature"]
        h = row["humidity"]
        p = row.get("precipitation", 0)
        if t > 2:
            return 0
        elif 0 < t <= 2:
            return 1
        elif -2 < t <= 0 and p > 0:
            return 2
        elif t <= -2 and (p > 0 or h >= 80):
            return 3
        else:
            return 1

    df["risk_level"] = df.apply(label_risk, axis=1)
    df["risk_label"] = df["risk_level"].map({0: "안전", 1: "관심", 2: "주의", 3: "위험"})

    save_path = SAVE_DIR / "blackice_dataset.csv"
    df.to_csv(save_path, index=False, encoding="utf-8-sig")
    print(f"[data_collector] 전처리 완료: {save_path} ({len(df)}행)")
    return df


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--collect",    action="store_true", help="ASOS 데이터 수집")
    parser.add_argument("--preprocess", action="store_true", help="블랙아이스 레이블링 전처리")
    args = parser.parse_args()

    if args.collect:
        df = collect_winter_data()

    if args.preprocess:
        csv_path = SAVE_DIR / "asos_winter.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            preprocess_for_blackice(df)
        else:
            print("먼저 --collect 옵션으로 데이터를 수집하세요.")
