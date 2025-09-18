from fastapi import APIRouter, UploadFile, File
import shutil
import tempfile
from app.services.model_service import analyze_image
from app.models.report import Report

router = APIRouter()

@router.post("/analyze", response_model=Report)
async def analyze(file: UploadFile = File(...)):
    # 업로드된 파일 임시 저장
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    with open(temp_file.name, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 분석 로직 실행 (현재는 더미 결과)
    result = analyze_image(temp_file.name)

    return result
