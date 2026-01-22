from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignDetailResponse
from app.models.campaign import Campaign, CampaignDispatch, Template
from app.models.execution import CampaignEvent
from app.models.organization import Target
from app.services.anonymizer import sanitize_report_data
from workers.tasks import send_phishing_email

router = APIRouter()

@router.post("/", response_model=CampaignResponse)
async def create_campaign(
    campaign_in: CampaignCreate,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Create a new Campaign and pre-allocate Dispatches in DRAFT state.
    """
    # 1. Verify Template
    template = await db.get(Template, campaign_in.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # 2. Create Campaign
    campaign = Campaign(
        org_id=campaign_in.org_id,
        name=campaign_in.name,
        template_id=campaign_in.template_id,
        is_anonymous_reporting=campaign_in.is_anonymous_reporting
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    # 3. Create Draft Dispatches for Targets
    # Note: Validating targets exist is good practice, skipping for brevity/speed as per prompt scope
    for target_id in campaign_in.target_ids:
        dispatch = CampaignDispatch(
            campaign_id=campaign.id,
            target_id=target_id,
            dispatch_status="DRAFT"
        )
        db.add(dispatch)
    
    await db.commit()
    return campaign

@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    List campaigns with pagination.
    """
    query = select(Campaign).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{campaign_id}", response_model=CampaignDetailResponse)
async def get_campaign_detail(
    campaign_id: int,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Get campaign details with sanitized stats.
    """
    # Load campaign
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalars().first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Load All Events (This could be heavy in prod, should be aggregated via SQL)
    # Using python-side sanitization as requested
    events_result = await db.execute(
        select(CampaignEvent)
        .join(CampaignDispatch)
        .where(CampaignDispatch.campaign_id == campaign_id)
        .options(selectinload(CampaignEvent.dispatch).selectinload(CampaignDispatch.target).selectinload(Target.department))
    )
    events = events_result.scalars().all()

    # Sanitize
    sanitized_timeline = sanitize_report_data(campaign, events)

    # Simple Stats Aggregation
    stats = {
        "total_sent": len([e for e in sanitized_timeline if e['event_type'] == 'SENT']),
        "opened": len([e for e in sanitized_timeline if e['event_type'] == 'OPENED']),
        "clicked": len([e for e in sanitized_timeline if e['event_type'] == 'CLICKED']),
        "credentials_captured": len([e for e in sanitized_timeline if e['event_type'] == 'SUBMITTED_DATA'])
    }

    return CampaignDetailResponse(
        **campaign.__dict__,
        id=campaign.id,
        org_id=campaign.org_id,
        template_id=campaign.template_id,
        stats=stats,
        timeline=sanitized_timeline
    )

@router.post("/{campaign_id}/launch")
async def launch_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Launch the campaign: Convert DRAFT dispatches to QUEUED and trigger Celery.
    """
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Select Draft Dispatches
    result = await db.execute(
        select(CampaignDispatch)
        .where(
            CampaignDispatch.campaign_id == campaign_id,
            CampaignDispatch.dispatch_status == "DRAFT"
        )
    )
    dispatches = result.scalars().all()

    if not dispatches:
        raise HTTPException(status_code=400, detail="No draft targets found for this campaign or already launched.")

    # Update and Trigger
    count = 0
    for dispatch in dispatches:
        dispatch.dispatch_status = "QUEUED"
        # Trigger Celery Task
        send_phishing_email.delay(dispatch.id)
        count += 1
    
    await db.commit()

    return {"message": f"Campaign launched. {count} emails queued."}
