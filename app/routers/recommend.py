# app/routers/recommend.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from app.services.recipe_service import recommend_recipes_by_ingredients, initialize_retriever

router = APIRouter()

class RecommendByIngredientsRequest(BaseModel):
    ingredients: List[str] = Field(min_items=1)
    top_k: int = 3

class RecipeItem(BaseModel):
    title: str
    summary: str
    recipe_id: int
    ingredients: List[str]
    full_recipe: str

@router.post("/recommend/by-ingredients", response_model=List[RecipeItem])
async def recommend_by_ingredients(req: RecommendByIngredientsRequest):
    try:
        # 최초 호출시 전역 RETRIEVER 초기화
        initialize_retriever()
        items = recommend_recipes_by_ingredients(req.ingredients, req.top_k)
        return [RecipeItem(**x) for x in items]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommend failed: {e}") from e
