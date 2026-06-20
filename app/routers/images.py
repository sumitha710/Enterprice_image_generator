import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.generated_image import GeneratedImage
from app.schemas.image import ImageResponse

router = APIRouter(
    prefix="/images",
    tags=["Images"]
)

# Directory containing generated images
GENERATED_DIR = os.path.join("app", "uploads", "generated")

@router.get("/history", response_model=List[ImageResponse])
def get_image_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all generated images history for the authenticated user.
    """
    images = db.query(GeneratedImage).filter(
        GeneratedImage.user_id == current_user.id
    ).order_by(GeneratedImage.created_at.desc()).all()
    
    return images

@router.get("/{filename}/download")
def download_generated_image(
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download a specific generated image file, verifying access permissions.
    """
    # Verify DB record to ensure ownership
    image_record = db.query(GeneratedImage).filter(
        GeneratedImage.user_id == current_user.id,
        GeneratedImage.filepath.like(f"%{filename}")
    ).first()

    if not image_record:
        raise HTTPException(
            status_code=404,
            detail="Image metadata not found or access denied."
        )

    filepath = os.path.join(GENERATED_DIR, filename)

    # Verify if file exists on disk
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail="Image file not found on disk."
        )

    return FileResponse(
        path=filepath,
        media_type="image/png"
    )
