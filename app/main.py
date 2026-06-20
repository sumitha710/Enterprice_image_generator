from fastapi import FastAPI

from app.core.database import (
    Base,
    engine
)

from app.routers.auth import router as auth_router
from app.routers.generate import router as generate_router
from app.routers.assets import router as assets_router
from app.routers.images import router as images_router

import os

# Drop tables conditionally to apply schema updates
if os.getenv("RECREATE_DB", "false").lower() == "true":
    Base.metadata.drop_all(bind=engine)

Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="Enterprise Branded Image Generator"
)

app.include_router(auth_router)
app.include_router(generate_router)
app.include_router(assets_router)
app.include_router(images_router)