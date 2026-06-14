# GIS 기반 AI 도로 파손 탐지 및 블랙아이스 위험 예측 플랫폼

## 시스템 구성

| 서비스 | 기술 | 포트 |
|--------|------|------|
| Web 대시보드 | React 18 + Vite + Leaflet.js | 3000 |
| REST API | Spring Boot 3.3 (Java 21) | 8080 |
| AI 파이프라인 | FastAPI + YOLOv11 + XGBoost | 8000 |
| 공간 DB | PostgreSQL 15 + PostGIS 3.4 | 5432 |

---

## 빠른 시작 (Docker Compose)

```bash
# 1. 환경변수 파일 복사 후 API 키 입력
copy .env.example .env

# 2. Docker Compose 실행
cd docker
docker-compose up -d

# 3. 접속
# 대시보드: http://localhost:3000
# API 문서: http://localhost:8080/swagger-ui.html (Spring)
# AI 문서:  http://localhost:8000/docs (FastAPI)
# 기본 계정: admin / admin1234
```

---

## 로컬 개발 환경 설정

### 사전 요구사항

- Java 21 LTS
- Python 3.10+
- CUDA 12.1 (`C:\cuda` 경로)
- PostgreSQL 15 + PostGIS 3.4
- Node.js 20+

### 1. DB 초기화

```bash
# PostgreSQL 접속 후 실행
psql -U postgres -f docker/init-db.sql
```

### 2. Python AI 서버

```bash
cd ai

# 가상환경 생성 (권장)
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

# CUDA 12.1 버전 PyTorch 설치 (C:\cuda 기준)
pip install torch==2.3.0+cu121 torchvision==0.18.0+cu121 --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

# 환경변수 설정
copy .env.example .env
# .env 파일에서 DB 정보 및 WEATHER_API_KEY 입력

# AI 서버 실행
python ai_server.py
# → http://localhost:8000/docs 에서 API 확인
```

### 3. AI 모델 학습 (최초 1회)

#### 도로 파손 모델 (YOLOv11)

```bash
cd ai

# 데이터셋 준비: data/dataset/ 폴더에 YOLO 형식 데이터셋 배치
# (Roboflow 등에서 다운로드 후 data/dataset/images/, labels/ 구조 구성)

# 학습
python train_yolo.py --epochs 100 --batch 16 --validate

# 학습 완료 시 models/pothole-crack.pt 자동 저장
```

#### 블랙아이스 예측 모델

```bash
cd ai

# Step 1: 기상 데이터 수집 (기상청 API 키 필요)
python data_collector.py --collect --preprocess

# Step 2: 모델 학습
python train_blackice.py

# 완료 시 models/blackice_model.pkl, models/blackice_scaler.pkl 저장
```

### 4. Spring Boot 백엔드

```bash
cd backend

# 환경변수 설정 후 실행
./gradlew bootRun

# 또는 환경변수 직접 전달
SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5432/roadgis \
SPRING_DATASOURCE_USERNAME=roadgis \
SPRING_DATASOURCE_PASSWORD=roadgis1234 \
./gradlew bootRun
```

### 5. React 프론트엔드

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## AI 파이프라인 사용법

### 도로 파손 탐지

```bash
# 단일 이미지 탐지 (CLI)
cd ai
python detect_road.py image1.jpg image2.jpg --gps-csv gps_data.csv

# GPS CSV 형식
# filename,latitude,longitude
# image1.jpg,37.5714,126.9658
```

### 블랙아이스 예측

```bash
cd ai
python predict_blackice.py
```

### QGIS 내보내기

```bash
cd ai

# 전체 레이어 GeoJSON 내보내기
python qgis/export_to_geojson.py --all --output-dir ./qgis_output

# 특정 레이어만
python qgis/export_to_geojson.py --layer road_damage --output ./output/road.geojson
python qgis/export_to_geojson.py --layer blackice_risk --output ./output/ice.geojson

# GeoJSON 파일을 QGIS에서 직접 열어 qgis/qgis_style.qml 스타일 적용
```

---

## API 주요 엔드포인트

### Spring Boot (port 8080)

| Method | URL | 설명 |
|--------|-----|------|
| POST | `/api/auth/login` | 로그인 (body: username, password) |
| GET | `/api/road-damage` | 도로 파손 목록 |
| GET | `/api/road-damage/map` | 지도용 GeoJSON |
| GET | `/api/road-damage/stats` | 통계 |
| POST | `/api/road-damage/upload` | 영상 업로드 + AI 탐지 트리거 |
| GET | `/api/blackice` | 블랙아이스 목록 |
| GET | `/api/blackice/map` | 지도용 GeoJSON |
| POST | `/api/blackice/predict` | 예측 실행 |
| GET | `/api/report/excel` | Excel 보고서 |
| GET | `/api/report/pdf` | PDF 보고서 |

### FastAPI (port 8000)

| Method | URL | 설명 |
|--------|-----|------|
| POST | `/detect/road` | 도로 파손 탐지 |
| POST | `/detect/road/upload` | 이미지 직접 업로드 탐지 |
| POST | `/predict/blackice` | 블랙아이스 예측 |
| GET | `/health` | 헬스체크 + CUDA 상태 |
| GET | `/docs` | Swagger UI |

---

## 프로젝트 구조

```
project_1_fire_detected/
├── backend/        Spring Boot 3.3 (Java 21)
├── frontend/       React 18 + Vite + Leaflet.js
├── ai/             Python FastAPI + YOLOv11 + XGBoost/LightGBM
│   ├── qgis/       QGIS 연동 스크립트
│   ├── models/     학습된 모델 파일 (.pt, .pkl)
│   └── data/       데이터셋 및 기상 데이터
├── docker/         Docker Compose + Dockerfile
└── reference/      기획 문서
```
