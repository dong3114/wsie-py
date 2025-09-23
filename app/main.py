# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analyze  # /analyze, /analyze/graph 등을 담은 라우터

app = FastAPI(title="WSIE-PY", version="0.1.0")

# CORS: React(3000), Spring(8080)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록: 모든 엔드포인트에 /api/v1 접두사 부여
# 최종 경로 예) /api/v1/analyze , /api/v1/analyze/graph
app.include_router(analyze.router, prefix="/api/v1")

# (선택) 추천 라우터가 있다면 자동 등록 시도
try:
    from app.routers import recommend
    app.include_router(recommend.router, prefix="/api/v1")
except Exception:
    # 추천 라우터가 없거나 초기화 실패해도 서버 기동은 계속
    pass

@app.get("/health")
def health():
    return "OK"
