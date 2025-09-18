from app.models.report import Report

def analyze_image(file_path: str) -> Report:
    """
    이미지 분석 → 음식 종류/잔반 비율 계산 (현재는 더미 데이터 반환)
    """
    return Report(
        menu="김치찌개",
        waste_ratio=0.20,
        suggestion="국물 양 줄이기"
    )
