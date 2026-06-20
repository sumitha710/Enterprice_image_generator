import os
import urllib.parse
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.generated_image import GeneratedImage
from app.schemas.image import ImageGenerationRequest
from app.services.stable_diffusion import generate_image

router = APIRouter(
    prefix="/generate",
    tags=["Stable Diffusion"]
)

# Ensure the generated image directory exists
GENERATED_DIR = os.path.join("app", "uploads", "generated")
os.makedirs(GENERATED_DIR, exist_ok=True)

@router.post("/")
def create_image(
    request: ImageGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Call image generation service directly from the prompt
    result = generate_image(
        prompt=request.prompt,
        negative_prompt=request.negative_prompt or "blurry, low quality, distorted",
        num_inference_steps=request.num_inference_steps or 30
    )

    # Handle service errors
    if isinstance(result, dict):
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "Image generation failed.")
        )

    # Save generated image to local storage
    timestamp = int(datetime.utcnow().timestamp())
    filename = f"gen_{current_user.id}_{timestamp}.png"
    filepath = os.path.join(GENERATED_DIR, filename)

    try:
        with open(filepath, "wb") as f:
            f.write(result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not save generated image to disk: {str(e)}"
        )

    # Save generated image metadata to the database
    db_image = GeneratedImage(
        user_id=current_user.id,
        asset_id=None,
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        filepath=filepath,
        url=f"/images/{filename}/download", # URL path to download it
        steps=request.num_inference_steps
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    # Return the generated file in the response with custom headers for metadata
    return FileResponse(
        path=filepath,
        media_type="image/png",
        headers={
            "X-Image-ID": str(db_image.id),
            "X-Prompt": urllib.parse.quote(str(db_image.prompt))
        }
    )