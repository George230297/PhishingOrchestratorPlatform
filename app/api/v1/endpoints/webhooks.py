from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api import deps
from app.models.campaign import CampaignDispatch
from app.models.execution import CampaignEvent
from app.models.enums import EventTypeEnum

router = APIRouter()

@router.get("/track/{token}")
async def track_click(
    token: str,
    request: Request,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Webhook endpoint to track user clicks via unique token.
    Uses UUID token to find dispatch and log event.
    """
    # 1. Find Dispatch
    # Note: token is UUID in DB, but str in URL. SQLAlchemy handles conversion if mapped correctly.
    query = select(CampaignDispatch).where(CampaignDispatch.unique_tracking_token == token)
    result = await db.execute(query)
    dispatch = result.scalars().first()
    
    if not dispatch:
        raise HTTPException(status_code=404, detail="Invalid token")

    # 2. Log Event
    event = CampaignEvent(
        dispatch_id=dispatch.id,
        event_type=EventTypeEnum.CLICKED,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        # In a real app, use a proper parser for OS/Browser fingerprint
        os_fingerprint="Unknown", 
        browser_fingerprint="Unknown" 
    )
    db.add(event)
    await db.commit()

    # 3. Redirect to Landing Page (or return fake 404/Login page content)
    # For now, just return success
    return {"message": "Tracking successful", "landing_url": "http://malicious.example.com"}
