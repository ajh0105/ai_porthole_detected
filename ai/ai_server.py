"""
FastAPI AI 서버 — Spring Boot에서 HTTP로 호출하는 독립 AI 마이크로서비스.

엔드포인트:
  POST /detect/road       : 도로 파손 탐지 (YOLOv11)
  POST /detect/road/upload: 이미지 직접 업로드 후 탐지
  POST /predict/blackice  : 블랙아이스 위험도 예측
  GET  /health            : 헬스체크 + CUDA 상태
"""

import logging
import shutil
import tempfile
import time
from pathlib import Path

import torch
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# ── 로깅 설정 ───────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ai_server")

# ── FastAPI 앱 ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="RoadGIS AI Server",
    description="도로 파손 탐지(YOLOv11) 및 블랙아이스 예측(XGBoost+LightGBM) 마이크로서비스",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 요청 처리 시간 로깅 미들웨어 ─────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = (time.time() - start) * 1000
    logger.info(
        "%s %s → %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )
    return response


# ── 전역 예외 핸들러 ──────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": "AI 서버 내부 오류가 발생했습니다.", "type": type(exc).__name__},
    )


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request: Request, exc: FileNotFoundError):
    logger.warning("FileNotFoundError: %s", exc)
    return JSONResponse(
        status_code=503,
        content={"success": False, "detail": str(exc), "type": "ModelNotReady"},
    )


# ── 요청/응답 스키마 ──────────────────────────────────────────────────────────
class DetectRequest(BaseModel):
    batchId: int = Field(..., gt=0, description="Spring Boot detection_batch ID")
    filePaths: list[str] = Field(..., min_length=1, description="처리할 이미지 절대경로 목록")
    gpsCsv: str | None = Field(None, description="GPS CSV 파일 경로 (EXIF 없는 경우)")
    confThreshold: float = Field(0.4, ge=0.1, le=1.0, description="탐지 신뢰도 임계값")


class DetectResponse(BaseModel):
    success: bool
    batchId: int
    detectedCount: int
    results: list[dict]


class PredictResponse(BaseModel):
    success: bool
    predictedCount: int
    results: list[dict]


# ── 라우터 ────────────────────────────────────────────────────────────────────
@app.post("/detect/road", response_model=DetectResponse, tags=["Road Damage"])
async def detect_road(req: DetectRequest):
    """YOLOv11 도로 파손 탐지. Spring Boot가 업로드한 파일 경로 목록을 받아 처리."""
    logger.info("도로 탐지 요청: batchId=%d, 파일=%d장", req.batchId, len(req.filePaths))

    missing = [p for p in req.filePaths if not Path(p).exists()]
    if missing:
        raise HTTPException(status_code=422, detail=f"파일을 찾을 수 없습니다: {missing[:3]}")

    from detect_road import detect_images
    results = detect_images(
        req.filePaths,
        gps_csv=req.gpsCsv,
        conf_threshold=req.confThreshold,
        batch_id=req.batchId,
    )
    logger.info("탐지 완료: batchId=%d, 탐지건=%d", req.batchId, len(results))
    return DetectResponse(success=True, batchId=req.batchId, detectedCount=len(results), results=results)


@app.post("/detect/road/upload", tags=["Road Damage"])
async def detect_road_upload(files: list[UploadFile] = File(...)):
    """이미지 직접 업로드 후 탐지. 테스트 및 소량 처리용."""
    if not files:
        raise HTTPException(status_code=422, detail="파일이 없습니다.")

    allowed_ext = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    for f in files:
        ext = Path(f.filename or "").suffix.lower()
        if ext not in allowed_ext:
            raise HTTPException(status_code=422, detail=f"지원하지 않는 파일 형식: {f.filename}")

    tmp_dir = Path(tempfile.mkdtemp())
    try:
        saved: list[str] = []
        for file in files:
            dest = tmp_dir / (file.filename or "image.jpg")
            with open(dest, "wb") as f:
                shutil.copyfileobj(file.file, f)
            saved.append(str(dest))

        from detect_road import detect_images
        results = detect_images(saved)
        return {"success": True, "detectedCount": len(results), "results": results}
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@app.post("/predict/blackice", response_model=PredictResponse, tags=["Black Ice"])
async def predict_blackice():
    """최신 기상 데이터를 수집해 블랙아이스 위험도 예측 후 DB 저장."""
    logger.info("블랙아이스 예측 요청")
    from predict_blackice import run_prediction
    results = run_prediction()
    logger.info("블랙아이스 예측 완료: %d개 관측소", len(results))
    return PredictResponse(success=True, predictedCount=len(results), results=results)


@app.get("/health", tags=["System"])
async def health():
    """헬스체크 + CUDA 상태 반환."""
    cuda_ok = torch.cuda.is_available()
    return {
        "status": "ok",
        "cuda_available": cuda_ok,
        "cuda_device": torch.cuda.get_device_name(0) if cuda_ok else None,
        "cuda_path": "C:\\cuda",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False, log_level="info")
