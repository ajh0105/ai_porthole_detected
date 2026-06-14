"""
데모용 블랙아이스 예측 모델 즉시 생성 스크립트.
실제 기상 API 없이도 모델 파일을 만들어 예측 기능을 테스트할 수 있음.
"""

import os
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

MODEL_PATH  = Path(__file__).parent / "models" / "blackice_model.pkl"
SCALER_PATH = Path(__file__).parent / "models" / "blackice_scaler.pkl"


def generate_synthetic_data(n=5000, seed=42):
    """기온/습도/강수/풍속 기반으로 현실적인 블랙아이스 위험도 라벨 생성."""
    rng = np.random.default_rng(seed)

    temperature   = rng.uniform(-15, 15, n)
    humidity      = rng.uniform(20, 100, n)
    precipitation = rng.exponential(0.5, n).clip(0, 20)
    wind_speed    = rng.uniform(0, 15, n)

    # 규칙 기반 라벨링 (도메인 지식 반영)
    risk = np.zeros(n, dtype=int)

    cond_safe    = temperature > 5
    cond_caution = (temperature <= 5)  & (temperature > 0)  & (humidity < 70)
    cond_watch   = (temperature <= 2)  & (humidity >= 70)   | (precipitation > 0.5)
    cond_danger  = (temperature < -2) & (humidity >= 80)   | (precipitation > 2) | \
                   ((temperature < 0) & (wind_speed > 8))

    risk[cond_caution] = 1
    risk[cond_watch]   = 2
    risk[cond_danger]  = 3
    risk[cond_safe]    = 0  # safe overrides cautionary patterns

    X = np.column_stack([temperature, humidity, precipitation, wind_speed])
    return X, risk


def train():
    try:
        import xgboost as xgb
        import lightgbm as lgb
    except ImportError:
        print("[ERROR] xgboost / lightgbm 패키지가 없습니다.")
        print("  pip install xgboost lightgbm 을 먼저 실행하세요.")
        raise

    print("[demo] 합성 데이터 생성 중...")
    X, y = generate_synthetic_data(n=8000)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    xgb_clf = xgb.XGBClassifier(
        n_estimators=200, max_depth=5, learning_rate=0.1,
        eval_metric="mlogloss", random_state=42, verbosity=0,
    )
    lgb_clf = lgb.LGBMClassifier(
        n_estimators=200, max_depth=5, learning_rate=0.1,
        random_state=42, verbose=-1,
    )
    ensemble = VotingClassifier(
        estimators=[("xgb", xgb_clf), ("lgb", lgb_clf)],
        voting="soft",
    )

    print("[demo] 모델 학습 중 (XGBoost + LightGBM 앙상블)...")
    ensemble.fit(X_train_sc, y_train)

    y_pred = ensemble.predict(X_test_sc)
    print("[demo] 테스트 성능:")
    print(classification_report(y_test, y_pred,
          target_names=["안전(0)", "관심(1)", "주의(2)", "위험(3)"]))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(ensemble, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"[demo] 모델 저장 완료: {MODEL_PATH}")
    print(f"[demo] 스케일러 저장 완료: {SCALER_PATH}")
    print("\n이제 AI 서버에서 /predict/blackice 엔드포인트를 사용할 수 있습니다.")


if __name__ == "__main__":
    train()
