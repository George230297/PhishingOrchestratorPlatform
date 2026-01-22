from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class EventStats(BaseModel):
    total_sent: int
    opened: int
    clicked: int
    credentials_captured: int

class CampaignReport(BaseModel):
    campaign_id: int
    campaign_name: str
    stats: EventStats
    timeline: List[Dict[str, Any]]
