# GIS 기반 AI 도로 파손 탐지 및 블랙아이스 위험 예측 플랫폼

> **포트폴리오 프로젝트** — YOLOv11 · XGBoost/LightGBM · Spring Boot · React · PostGIS

---

## 라이브 데모

| 링크 | 설명 |
|------|------|
| **[GitHub Pages 대시보드](https://ajh0105.github.io/ai_porthole_detected/)** | React 프론트엔드 시연 (샘플 데이터 기반 데모) |
| **[Hugging Face Space](https://huggingface.co/spaces/simonahn/ai_porthole_detected)** | YOLOv11 포트홀 탐지 + 블랙아이스 예측 AI 기능 직접 체험 |

> **GitHub Pages 데모 안내**
> - 백엔드/DB 없이 **샘플 데이터**로 동작합니다 (서울 지역 도로 파손 30건, 기상관측소 6개소)
> - 로그인: `admin` / `admin1234`
> - 실제 AI 탐지(이미지 업로드, 예측 실행)는 Hugging Face Space에서 체험 가능합니다

---

## 프로젝트 개요

| 기능 | 설명 |
|------|------|
| 도로 파손 탐지 | YOLOv11 기반 포트홀/균열 자동 탐지, 신뢰도 점수 포함 |
| GIS 좌표 매핑 | EXIF/GPS 파일로 좌표 추출 → PostGIS 저장 |
| 블랙아이스 예측 | ASOS 기상 데이터 → XGBoost+LightGBM 앙상블 0~3 위험도 분류 |
| GIS 시각화 | Leaflet.js 지도, 색상 코드별 위험도 표시 |
| 통합 대시보드 | 지도 / 목록 / 통계 / 보고서 / JWT 인증 |

---

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
# API 문서: http://localhost:8080/swagger-ui.html
# AI 문서:  http://localhost:8000/docs
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
psql -U postgres -f docker/init-db.sql
```

### 2. Python AI 서버

```bash
cd ai
python -m venv venv
venv\Scripts\activate

# CUDA 12.1 PyTorch 설치
pip install torch==2.3.0+cu121 torchvision==0.18.0+cu121 --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

copy .env.example .env
python ai_server.py
# → http://localhost:8000/docs
```

### 3. AI 모델 학습

#### 도로 파손 (YOLOv11)

```bash
cd ai
# data/dataset/ 에 YOLO 형식 데이터셋 배치 후
python train_yolo.py --epochs 100 --batch 16 --validate
# → models/pothole-crack.pt 저장
```

#### 블랙아이스 예측 (XGBoost + LightGBM)

```bash
cd ai
python data_collector.py --collect --preprocess   # 기상청 API 키 필요
python train_blackice.py
# → models/blackice_model.pkl 저장
```

### 4. Spring Boot 백엔드

```bash
cd backend
./gradlew bootRun
```

### 5. React 프론트엔드

```bash
cd frontend
npm install
npm run dev      # 개발: http://localhost:5173
npm run build    # 프로덕션 빌드 (GitHub Pages 데모 모드 포함)
```

---

## GitHub Pages 배포 구조

```
portfolio 브랜치 push
    └─> GitHub Actions (.github/workflows/deploy.yml)
            └─> npm run build (VITE_DEMO_MODE=true 자동 적용)
                    └─> frontend/dist → gh-pages 브랜치 배포
```

- **데모 모드**: 백엔드 없이 샘플 데이터로 전체 UI 동작
- **라우팅**: BrowserRouter + `/ai_porthole_detected/` base path
- **배포 트리거**: `portfolio` 브랜치에 push 시 자동 배포

---

## AI 기능 (Hugging Face Space)

Hugging Face Space에서 실제 AI 모델을 테스트할 수 있습니다:

- **YOLOv11 포트홀/균열 탐지**: 이미지 업로드 → 바운딩박스 + 신뢰도 결과
- **블랙아이스 위험도 예측**: 기온/습도/강수량/풍속 입력 → 0~3단계 위험도 분류

→ [Hugging Face Space 바로가기](https://huggingface.co/spaces/simonahn/ai_porthole_detected)

---

## API 주요 엔드포인트

### Spring Boot (port 8080)

| Method | URL | 설명 |
|--------|-----|------|
| POST | `/api/auth/login` | 로그인 (JWT 발급) |
| GET | `/api/road-damage` | 도로 파손 목록 |
| GET | `/api/road-damage/map` | 지도용 GeoJSON |
| GET | `/api/road-damage/stats` | 통계 |
| POST | `/api/road-damage/upload` | 영상 업로드 + AI 탐지 트리거 |
| GET | `/api/blackice` | 블랙아이스 목록 |
| GET | `/api/blackice/map` | 지도용 GeoJSON |
| POST | `/api/blackice/predict` | 예측 실행 |
| GET | `/api/report/excel` | Excel 보고서 |
| GET | `/api/report/pdf` | PDF 보고서 |

### FastAPI AI 서버 (port 8000)

| Method | URL | 설명 |
|--------|-----|------|
| POST | `/detect/road` | 도로 파손 탐지 |
| POST | `/detect/road/upload` | 이미지 직접 업로드 탐지 |
| POST | `/predict/blackice` | 블랙아이스 예측 |
| GET | `/health` | 헬스체크 + CUDA 상태 |
| GET | `/docs` | Swagger UI |

---

## QGIS 연동

```bash
cd ai
# PostGIS → GeoJSON 내보내기
python qgis/export_to_geojson.py --all --output-dir ./qgis_output

# QGIS에서 GeoJSON 열고 qgis/qgis_style.qml 스타일 적용
```

---

## 프로젝트 구조

```
ai_porthole_detected/
├── .github/workflows/    GitHub Actions (GitHub Pages 자동 배포)
├── backend/              Spring Boot 3.3 (Java 21)
├── frontend/             React 18 + Vite + Leaflet.js
│   ├── src/api/          mockData.js (데모 모드 샘플 데이터 포함)
│   └── .env.production   VITE_DEMO_MODE=true
├── ai/                   Python FastAPI + YOLOv11 + XGBoost/LightGBM
│   ├── qgis/             QGIS 연동 스크립트
│   ├── models/           학습된 모델 파일 (.pt, .pkl)
│   └── data/             데이터셋 및 기상 데이터
└── docker/               Docker Compose + Dockerfile
```
