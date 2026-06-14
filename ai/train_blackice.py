"""
블랙아이스 위험도 예측 모델 학습 (XGBoost + LightGBM 앙상블).
CUDA C:\cuda 환경 사용 (XGBoost GPU 가속).
"""

import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.ensemble import VotingClassifier
import xgboost as xgb
import lightgbm as lgb

# C:\cuda 환경 CUDA 설정
os.environ["CUDA_PATH"] = r"C:\cuda"

DATA_PATH  = Path(__file__).parent / "data" / "weather" / "blackice_dataset.csv"
MODEL_PATH = Path(__file__).parent / "models" / "blackice_model.pkl"
SCALER_PATH = Path(__file__).parent / "models" / "blackice_scaler.pkl"

FEATURES = ["temperature", "humidity", "precipitation", "wind_speed"]
TARGET   = "risk_level"


def load_data() -> tuple[pd.DataFrame, pd.Series]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"학습 데이터가 없습니다: {DATA_PATH}\n"
            "data_collector.py --collect --preprocess 를 먼저 실행하세요."
        )
    df = pd.read_csv(DATA_PATH)
    # 선택적 피처 추가
    optional = ["dew_point", "pressure"]
    active_features = FEATURES + [f for f in optional if f in df.columns]

    df = df.dropna(subset=active_features + [TARGET])
    X = df[active_features]
    y = df[TARGET].astype(int)
    print(f"[train_blackice] 데이터 로드: {len(df)}행, 피처={active_features}")
    print(f"  클래스 분포:\n{y.value_counts().sort_index()}")
    return X, y


def train():
    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    # XGBoost (GPU 지원)
    device = "cuda" if _cuda_available() else "cpu"
    xgb_clf = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="mlogloss",
        device=device,
        random_state=42,
    )

    # LightGBM
    lgb_clf = lgb.LGBMClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbose=-1,
    )

    # 소프트 보팅 앙상블
    ensemble = VotingClassifier(
        estimators=[("xgb", xgb_clf), ("lgb", lgb_clf)],
        voting="soft",
    )

    # 교차 검증
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(ensemble, X_train_sc, y_train, cv=cv, scoring="f1_macro")
    print(f"[train_blackice] CV F1-macro: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    ensemble.fit(X_train_sc, y_train)

    y_pred = ensemble.predict(X_test_sc)
    print("\n[train_blackice] 테스트 성능:")
    print(classification_report(y_test, y_pred, target_names=["안전", "관심", "주의", "위험"]))
    print("혼동 행렬:\n", confusion_matrix(y_test, y_pred))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(ensemble, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"[train_blackice] 모델 저장: {MODEL_PATH}")
    print(f"[train_blackice] 스케일러 저장: {SCALER_PATH}")
    return ensemble, scaler


def _cuda_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


if __name__ == "__main__":
    train()
