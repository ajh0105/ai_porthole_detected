# GIS 기반 도로 파손 탐지 플랫폼 — 작업 인수인계 문서

> 최종 업데이트: 2026-06-10

---

## 프로젝트 개요

도로 영상 기반 **포트홀/균열 자동 탐지** + 기상 데이터 기반 **블랙아이스 위험도 예측**을 GIS 지도에서 통합 관리하는 플랫폼.

```
project_1_fire_detected/
├── backend/        # Spring Boot 3.3.2 (Java 21)
├── frontend/       # React 18 + Vite + Leaflet.js
├── ai/             # Python FastAPI AI 서버
├── docker/         # Docker Compose (PostgreSQL + PostGIS)
└── reference/      # 기획 문서
```

---

## 현재 구현 완료 상태

| 영역 | 상태 | 비고 |
|------|------|------|
| DB 스키마 | ✅ | PostGIS, 샘플 데이터 포함 |
| Spring Boot API | ✅ | JWT 인증, 도로파손/블랙아이스 CRUD |
| FastAPI AI 서버 | ✅ | port 8000, CUDA 지원 |
| React 프론트엔드 | ✅ | Leaflet 지도, 대시보드, 통계 |
| 도로파손 탐지 모델 | ✅ | YOLOv12s, RDD2022 47,420장 학습된 사전학습 모델 |
| 블랙아이스 예측 모델 | ✅ | XGBoost+LightGBM, 데모 모델 (실제 ASOS 데이터로 재학습 권장) |
| 기상 API 연동 | ✅ | 기상청 ASOS fallback + 초단기실황 시도 |

---

## AI 모델 정보

### 도로 파손 탐지 모델
- **파일**: `ai/models/rdd2022-yolo12s-best.pt` (19MB)
- **출처**: HuggingFace `rezzzq/yolo12s-road-damage-rdd2022`
- **아키텍처**: YOLOv12s
- **학습 데이터**: RDD2022 전체 47,420장 (6개국)
- **탐지 클래스**: D00(세로균열), D10(가로균열), D20(악어균열), D40(포트홀), Repair(보수흔)
- **damage_type 매핑**: D40 → `pothole` / 나머지 → `crack`

### 블랙아이스 예측 모델
- **파일**: `ai/models/blackice_model.pkl`, `ai/models/blackice_scaler.pkl`
- **아키텍처**: XGBoost + LightGBM VotingClassifier
- **현재 상태**: 합성 데이터로 학습된 데모 모델
- **재학습 방법**: `python ai/train_blackice.py` (실제 ASOS 데이터 수집 후)

---

## 환경 설정

### 필수 설치
- Java 21 LTS
- Python 3.12
- Docker Desktop
- Node.js 18+
- CUDA 12.1 (`C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1`)

### .env 설정
`.env.example`을 복사해 `.env` 생성 후 아래 항목 입력:

```env
# DB
DB_HOST=localhost
DB_PORT=5432
DB_NAME=roadgis
DB_USER=roadgis
DB_PASSWORD=roadgis123

# JWT
JWT_SECRET=your-secret-key

# 기상청 API (공공데이터포털)
WEATHER_API_KEY=your-api-key   # 단기예보조회서비스 키

# AI 서버
AI_SERVER_URL=http://localhost:8000
```

### Python 패키지 설치
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install ultralytics fastapi uvicorn psycopg2-binary python-dotenv
pip install xgboost lightgbm scikit-learn pandas requests tqdm
```

---

## 서비스 실행 방법

### 1. DB 시작 (Docker)
```powershell
cd docker
docker compose up -d db
```

### 2. AI 서버 (FastAPI, port 8000)
```powershell
cd ai
python ai_server.py
```
- 헬스체크: http://localhost:8000/health
- API 문서: http://localhost:8000/docs

### 3. 백엔드 (Spring Boot, port 8080)
```powershell
cd backend
.\gradlew.bat bootRun
```

### 4. 프론트엔드 (React, port 5173)
```powershell
cd frontend
npm install
npm run dev
```

### 5. 실시간 학습 모니터 (선택)
```powershell
cd ai
python monitor.py
```

---

## 데이터셋 재구성 방법

학습 데이터는 용량 절약을 위해 제외됨. 재다운로드:

```bash
# Kaggle API 방식 (~47,420장, YOLO 포맷)
python ai/setup_dataset.py --method kaggle

# Figshare 직접 다운로드 (~3-4GB, VOC→YOLO 자동변환)
python ai/setup_dataset.py --method figshare
```

Kaggle 자격증명: `C:\Users\<사용자명>\.kaggle\kaggle.json` 필요

---

## YOLOv11 직접 학습 (선택)

```powershell
# 데이터셋 구성 후
python ai/train_yolo.py --epochs 100 --model yolo11s.pt --batch 32

# 학습 모니터링 (별도 터미널)
python ai/monitor.py
```

- GPU: RTX 4060 Laptop (VRAM 8.6GB)
- 예상 소요: epoch당 ~9분, 100 epochs ≈ 15시간
- 완료 후 가중치: `ai/models/pothole-crack.pt`

---

## 향후 로드맵

### Phase A — CCTV 실시간 탐지 + 관리자 알람
- RTSP 스트림 → YOLOv12 프레임 단위 탐지
- SSE/WebSocket → 관리자 브라우저 알람 + 이메일/SMS
- 추가 테이블: `camera`, `detection_event`

### Phase B — 블랙박스 영상 구간 탐지
- MP4 업로드 → GPS 동기화 → 파손 구간 Polyline 지도 표시
- Celery/APScheduler 비동기 처리

---

## 주요 API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/auth/login` | JWT 로그인 |
| GET | `/api/road-damage` | 파손 목록 (GeoJSON) |
| POST | `/api/road-damage` | 파손 등록 |
| GET | `/api/blackice` | 블랙아이스 위험도 목록 |
| POST | `/api/blackice/predict` | 예측 실행 (AI 서버 호출) |
| GET | `/api/blackice/current-weather` | 관측소별 현재 기상 |
| GET | `/api/report/pdf` | PDF 보고서 생성 |

---

## 알려진 이슈

1. **초단기실황 API 403**: 공공데이터포털에서 별도 승인 필요. 현재 ASOS로 fallback 처리.
2. **블랙아이스 모델**: 현재 합성 데이터 데모 모델. ASOS 실제 데이터 수집 후 `train_blackice.py`로 재학습 권장.
3. **시스템 날짜**: 현재 날짜(2026년)로 API 호출 시 데이터 없음 → `predict_blackice.py`에서 2025년으로 자동 보정 처리됨.
