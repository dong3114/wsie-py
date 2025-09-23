from fastapi import FastAPI
from .routers import recipe_router
from .services import recipe_service


def create_app():
    app = FastAPI(title="AI Recipe Recommender")
    app.include_router(recipe_router.router, prefix="/api")

    @app.on_event("startup")
    def on_startup():
        recipe_service.initialize_retriever()

    return app
