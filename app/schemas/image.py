from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ImageGenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = "blurry, low quality, distorted"
    num_inference_steps: Optional[int] = 30

class ImageResponse(BaseModel):
    id: int
    user_id: int
    asset_id: Optional[int] = None
    prompt: str
    negative_prompt: Optional[str]
    filepath: str
    url: Optional[str]
    steps: int
    created_at: datetime

    class Config:
        from_attributes = True
