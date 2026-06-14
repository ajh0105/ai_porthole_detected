# GIS 기반 AI 도로 파손 탐지 및 블랙아이스 위험 예측 플랫폼

## 프로젝트 진행 프로토콜

단계별 승인 방식으로 진행. 각 단계 완료 시 승인 후 다음 단계 진행.

---

## ✅ 1단계: 기획 및 요구사항 정의 (완료)

### 프로젝트 목표

도로 영상으로 포트홀·균열을 자동 탐지하고, 기상 데이터로 블랙아이스 위험도를 예측하여 GIS 지도에서 통합 시각화하는 관리 플랫폼 구축.

### 핵심 기능 명세

| 기능 | 설명 |
|------|------|
| F1. 도로 파손 탐지 | YOLOv11 기반 포트홀/균열 탐지, 신뢰도 점수 포함 |
| F2. GIS 좌표 매핑 | EXIF/GPS 파일로 좌표 추출 → PostGIS 저장 |
| F3. 블랙아이스 예측 | ASOS/AWS 기상 데이터 → 0~3 위험도 분류 |
| F4. GIS 시각화 | QGIS + Leaflet.js 이중 지원, 색상 코드별 위험도 표시 |
| F5. 통합 대시보드 | 지도/목록/통계/리포트/JWT 인증 |

### 가상 유저 시나리오

- **도로 관리 공무원**: 탐지 결과 확인 → 위험구간 필터링 → 보수 우선순위 보고서 생성
- **기상 담당자**: 블랙아이스 고위험 구간 확인 → 제설차 배차 결정
- **시스템 운영자**: 영상 업로드 → AI 파이프라인 실행 → DB 업데이트 모니터링

---

## ✅ 2단계: 아키텍처 및 Tech Stack 확정 (완료)

### Tech Stack

| 영역 | 기술 | 버전 |
|------|------|------|
| AI 탐지 | YOLOv11 (Ultralytics) | latest |
| 예측 모델 | XGBoost + LightGBM | latest |
| AI 런타임 | Python | 3.10+ |
| 백엔드 | Spring Boot | 3.2 |
| 언어 | Java | 21 LTS |
| 공간 DB | PostgreSQL + PostGIS | 15 / 3.4 |
| ORM | Spring Data JPA + Hibernate Spatial | - |
| 프론트엔드 | React + Vite | 18 |
| 지도 | Leaflet.js | 1.9 |
| 차트 | Recharts | latest |
| 인증 | JWT (Spring Security) | - |
| 상태관리 | Zustand | latest |
| 컨테이너 | Docker + Docker Compose | - |
| GIS 도구 | QGIS | 3.x |

### DB 테이블 구조

- `users` — 관리자 계정 (bcrypt 암호화)
- `road_damage` — 탐지 결과 (GIST 공간 인덱스)
- `weather_station` — 기상 관측소 정보
- `blackice_risk` — 블랙아이스 위험도 예측 결과
- `detection_batch` — AI 처리 배치 이력

### API 구조

- `POST /api/auth/login` — JWT 발급
- `GET/POST /api/road-damage/**` — 도로 파손 CRUD + GeoJSON
- `GET/POST /api/blackice/**` — 블랙아이스 조회 + 예측 트리거
- `GET /api/report/pdf|excel` — 보고서 생성

### 폴더 구조

```
project_1_fire_detected/
├── backend/        # Spring Boot 3.2 (Java 17)
├── frontend/       # React 18 + Vite + Leaflet.js
├── ai/             # Python AI Pipeline (YOLO + ML)
├── docker/         # Docker Compose + Dockerfile
└── reference/      # 기획 문서
```

---

## ✅ 3단계: 핵심 코드 스캐폴딩 및 구현 (완료)

### 구현 완료 목록

| 영역 | 파일/모듈 | 설명 |
|------|-----------|------|
| **Docker** | docker/docker-compose.yml | PostGIS 15 + Backend + Frontend |
| **Docker** | docker/init-db.sql | 테이블 생성 + 샘플 데이터 |
| **Spring Boot** | build.gradle | Java 21 LTS + Spring Boot 3.3.2 |
| **Spring Boot** | entity/ | User, RoadDamage, BlackIceRisk, WeatherStation, DetectionBatch |
| **Spring Boot** | repository/ | GIST 공간 쿼리 + bbox 필터 |
| **Spring Boot** | service/ | Auth, RoadDamage, BlackIce, AiPipeline, Report |
| **Spring Boot** | controller/ | Auth, RoadDamage, BlackIce, Report API |
| **Spring Boot** | security/ | JWT Provider + Filter |
| **Python AI** | detect_road.py | YOLOv11 탐지 + PostGIS 저장 (CUDA C:\cuda) |
| **Python AI** | train_yolo.py | YOLOv11 학습 스크립트 (CUDA C:\cuda) |
| **Python AI** | predict_blackice.py | XGBoost+LightGBM 앙상블 예측 + DB 저장 |
| **Python AI** | train_blackice.py | 블랙아이스 모델 학습 (CUDA 가속) |
| **Python AI** | data_collector.py | ASOS API 수집 + 레이블링 전처리 |
| **Python AI** | gps_mapper.py | EXIF / CSV GPS 추출 |
| **Python AI** | ai_server.py | FastAPI AI 마이크로서비스 (Spring Boot와 완전 분리, port:8000) |
| **Docker** | Dockerfile.ai | FastAPI 전용 컨테이너 |
| **React** | pages/ | Login, Dashboard, RoadDamage, BlackIce, Report |
| **React** | components/map/ | Leaflet 지도 + 레이어 토글 + 범례 |
| **React** | components/charts/ | PieChart(파손유형) + BarChart(위험도) |
| **React** | store/ | Zustand (auth, map 상태) |
| **React** | api/ | axios 인터셉터 + roadDamageApi + blackIceApi |

### CUDA 설정
- CUDA 경로: `C:\cuda`
- 적용 파일: detect_road.py, train_yolo.py, train_blackice.py
- XGBoost device=cuda / PyTorch cuda.is_available() 기반 자동 선택

---

## ✅ 4단계: 예외 처리, 고도화 및 리팩토링 (완료)

### 완료 항목

| 영역 | 내용 |
|------|------|
| **Spring Boot** | `BusinessException` 커스텀 예외 계층 (NOT_FOUND / BAD_REQUEST / UNAUTHORIZED / CONFLICT) |
| **Spring Boot** | `GlobalExceptionHandler` — Validation, TypeMismatch, MaxUpload, AccessDenied 처리 |
| **Spring Boot** | `ApiResponse` — `code` 필드 추가 (에러 분류 지원) |
| **Spring Boot** | Service 레이어 유효성 검증 (damageType, bbox 좌표 범위, riskLevel 범위) |
| **Spring Boot** | 단위 테스트 (AuthServiceTest, RoadDamageServiceTest, AuthControllerTest) |
| **FastAPI** | HTTP 요청 처리 시간 로깅 미들웨어 |
| **FastAPI** | 전역 예외 핸들러 (Exception, FileNotFoundError → 구조화된 JSON 응답) |
| **FastAPI** | 입력 유효성 검증 (Pydantic Field 제약: confThreshold 0.1~1.0, filePaths 최소 1개) |
| **FastAPI** | 업로드 파일 확장자 화이트리스트 검증 |
| **Python AI** | detect_road.py — DB 저장 실패 시 rollback + 다음 이미지 계속 처리 |
| **Python AI** | predict_blackice.py — API 키 미설정 시 더미 데이터로 개발 모드 동작 |
| **Python AI** | 구조적 로깅 (logging 모듈, 처리 건수/성공/실패 통계) |
| **QGIS** | `qgis/export_to_geojson.py` — PostGIS → GeoJSON/Shapefile export |
| **QGIS** | `qgis/qgis_style.qml` — 포트홀(빨강)/균열(주황) 스타일 파일 |
| **React** | `ErrorBoundary` 컴포넌트 — 렌더링 오류 화면 격리 |
| **React** | `LoadingSpinner` 컴포넌트 — 공통 로딩 상태 |
| **React** | `ToastContainer` (Zustand 기반) — 성공/실패/경고 알림 |
| **전체** | `.env.example` 환경변수 템플릿 |
| **전체** | `README.md` — 실행 가이드, API 명세, 모델 학습 절차 |

---

## 🗺️ 향후 로드맵 (미구현)

### Phase A: CCTV 실시간 탐지 + 관리자 알람

| 항목 | 내용 |
|------|------|
| 실시간 스트림 | RTSP/RTMP CCTV 스트림 → YOLOv11 프레임 단위 탐지 |
| 알람 시스템 | 파손 감지 시 SSE/WebSocket → 관리자 브라우저 알람 + 이메일/SMS |
| 로그 기록 | `detection_event` 테이블: 카메라ID, 파손유형, 신뢰도, 스크린샷 경로, 타임스탬프 |
| CCTV 관리 | `camera` 테이블: 카메라ID, 설치위치(PostGIS Point), 설치구간, 상태 |

### Phase B: 블랙박스 영상 기반 구간 파손 탐지

| 항목 | 내용 |
|------|------|
| 입력 | 로드맵 촬영 차량/관공서 차량 블랙박스 MP4 파일 |
| GPS 동기화 | 영상 타임스탬프 + GPS 로그 → 프레임별 좌표 매핑 |
| 구간 지도 표시 | 파손 감지 GPS 포인트를 선형 클러스터링 → Leaflet Polyline으로 위험 구간 시각화 |
| 배치 처리 | Celery/APScheduler로 업로드된 영상 비동기 분석 |

### 데이터셋 설정 (현재 진행 중)

- **데이터셋**: RDD2022 (Road Damage Detection Challenge 2022)
  - 47,420장 / 6개국 / 7클래스 (D00~D50)
  - 다운로드: `python ai/setup_dataset.py`
  - Kaggle: `sreekaraditya/rdd2022-yolo-crackscan-v2` (YOLO 포맷)
  - 대안: Figshare 직접 다운로드 → VOC→YOLO 자동 변환 포함
- **클래스 매핑**: D40→pothole, 나머지→crack (detect_road.py에서 자동 변환)
- **학습**: `python ai/train_yolo.py --epochs 100 --model yolo11s.pt`
