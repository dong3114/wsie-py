# app/services/model_service.py
from typing import Tuple
from PIL import Image
import io

def simple_image_analyze(img_bytes: bytes) -> Tuple[str, float, str]:
    """
    더미 분석: 이미지 크기/채널 등을 이용해 일관된 결과 생성 (데모용).
    실제 모델 연결 시 이 함수를 교체하세요.
    """
    try:
        im = Image.open(io.BytesIO(img_bytes))
        w, h = im.size
        pixels = w * h

        # 매우 단순한 규칙으로 결과 생성 (일관성 보장용)
        if pixels < 250_000:
            menu = "미니 토마토 에그 샐러드"
            waste = 0.15
            suggestion = "소량 재료는 콜드 디쉬로 전환하면 잔반이 줄어요."
        elif pixels < 800_000:
            menu = "감자 양파 스프"
            waste = 0.32
            suggestion = "감자·양파는 대량 삶아 냉장 보관 후 회전시키세요."
        else:
            menu = "토마토 파스타"
            waste = 0.48
            suggestion = "면 삶기 수율 표준화로 오버쿠킹/과다 제공을 줄이세요."

        return menu, float(round(waste, 2)), suggestion
    except Exception:
        # 이미지 헤더 판독 실패 시 기본값
        return "오늘의 셰프 특선", 0.35, "분석 오류 시 기본 특선으로 안내합니다."
