from .food_analyzer_graph import analyze_food, build_graph
import tempfile, os, json

def analyze_image_bytes_to_report(img_bytes: bytes) -> dict:
    if not img_bytes:
        raise ValueError("empty image bytes")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(img_bytes)
        tmp_path = tmp.name

    try:
        # 1) 이미지 파일경로 기반 1차 분석(JSON 문자열 가정)
        analysis_json = analyze_food(tmp_path)
        if not analysis_json:
            raise RuntimeError("analyze_food returned empty")

        # 2) LangGraph 파이프라인 실행
        graph = build_graph()
        result = graph.invoke({"analysis": analysis_json})

        # 표준화
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except Exception:
                result = {"report": result, "improvements": []}

        report = result.get("report", "")
        improvements = result.get("improvements", [])
        if not isinstance(improvements, list):
            improvements = []

        return {"report": report, "improvements": improvements}
    finally:
        try: os.remove(tmp_path)
        except Exception: pass
