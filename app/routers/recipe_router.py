from fastapi import APIRouter
from app.services import recipe_service
from app.models.recipe_model import RecipeRequest, RecipeResponse

router = APIRouter()


@router.post("/recommend", response_model=RecipeResponse)
def recommand_recipe_router(request_data: RecipeRequest):
    ingredients = request_data.ingredients
    result_recipes = recipe_service.recommend_recipes_by_ingredients(ingredients)
    return {"recommendations": result_recipes}
