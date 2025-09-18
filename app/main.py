from fastapi import FastAPI
from app.routers import analyze

app = FastAPI(title="WSIE-PY AI Server")

# 라우터 등록
app.include_router(analyze.router)

@app.get("/")
async def root():
    return {"message": "WSIE-PY server is running"}
