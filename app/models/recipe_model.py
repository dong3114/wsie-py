from pydantic import BaseModel
from typing import List


class RecipeRequest(BaseModel):
    ingredients: List[str]


class RecipeData(BaseModel):
    title: str
    summary: str
    recipe_id: int


class RecipeResponse(BaseModel):
    recommendations: List[RecipeData]
