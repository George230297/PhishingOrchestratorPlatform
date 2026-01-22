from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.enums import AttackVectorEnum

class CampaignBase(BaseModel):
    name: str
    template_id: int
    is_anonymous_reporting: bool = False

class CampaignCreate(CampaignBase):
    target_ids: List[int]
    # Org ID usually comes from current user (JWT), but simple for now:
    org_id: int 

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    is_anonymous_reporting: Optional[bool] = None

class CampaignResponse(CampaignBase):
    id: int
    org_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class CampaignDetailResponse(CampaignResponse):
    stats: dict
    timeline: List[dict]
