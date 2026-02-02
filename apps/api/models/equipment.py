from pydantic import BaseModel, Field
from typing import Optional

class Equipment(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1)
    brand: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    deletedAt: Optional[str] = None
