import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.brand_asset import BrandAsset
from app.schemas.asset import AssetResponse
from app.services.stable_diffusion import generate_image_img2img

router = APIRouter(
    prefix="/assets",
    tags=["Assets"]
)

# Ensure the upload directory exists
UPLOAD_DIR = os.path.join("app", "uploads", "logos")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=AssetResponse, status_code=201)
def upload_asset(
    file: UploadFile = File(...),
    prompt: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Create unique filename to prevent collisions
    timestamp = int(datetime.utcnow().timestamp())
    stored_name = f"{current_user.id}_{timestamp}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, stored_name)

    # Read uploaded file contents and apply prompt modifications
    try:
        raw_bytes = file.file.read()
        modified_bytes = generate_image_img2img(
            image_bytes=raw_bytes,
            prompt=prompt
        )
        with open(filepath, "wb") as buffer:
            buffer.write(modified_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not process or save file: {str(e)}"
        )

    # Determine file size
    file_size = os.path.getsize(filepath)

    # Create BrandAsset DB entry
    db_asset = BrandAsset(
        user_id=current_user.id,
        filename=file.filename,
        original_filename=file.filename,
        stored_filename=stored_name,
        filepath=filepath,
        file_size=file_size,
        file_type=file.content_type or "application/octet-stream",
        prompt=prompt
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)

    return db_asset

@router.get("/{asset_id}/download")
def download_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch asset and verify ownership
    asset = db.query(BrandAsset).filter(
        BrandAsset.id == asset_id,
        BrandAsset.user_id == current_user.id
    ).first()

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found or access denied."
        )

    # Convert fields to string to resolve static analysis type mismatch warnings
    filepath = str(asset.filepath)
    filename = str(asset.filename)
    file_type = str(asset.file_type)

    # Verify if the file actually exists on disk
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail="Asset file not found on disk."
        )

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type=file_type
    )
