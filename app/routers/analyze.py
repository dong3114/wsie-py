from fastapi import APIRouter, File, UploadFile, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict
from app.services.model_service import simple_image_analyze
from app.services.food_analyzer_adapter import analyze_image_bytes_to_report

router = APIRouter()

# 기존 간단 분석 응답
class AnalyzeResponse(BaseModel):
    menu: str
    waste_ratio: float
    suggestion: str

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(file: UploadFile = File(...)):
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="빈 파일")
        menu, waste, sug = simple_image_analyze(content)
        return AnalyzeResponse(menu=menu, waste_ratio=waste, suggestion=sug)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analyze failed: {e}") from e

# 그래프 기반 심화 분석 응답
class GraphAnalyzeResponse(BaseModel):
    report: str
    improvements: List[Dict[str, str]]

@router.post("/analyze/graph", response_model=GraphAnalyzeResponse)
async def analyze_graph(file: UploadFile = File(...)):
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="빈 파일")
        result = analyze_image_bytes_to_report(content)
        return GraphAnalyzeResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AnalyzeGraph failed: {e}") from e
