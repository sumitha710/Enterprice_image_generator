from pydantic import BaseModel
from datetime import datetime

class AssetResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    filepath: str
    prompt: str
    file_size: int
    file_type: str
    uploaded_at: datetime

    class Config:
        from_attributes = True
