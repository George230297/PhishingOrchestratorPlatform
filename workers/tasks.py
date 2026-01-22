import asyncio
from asgiref.sync import async_to_sync
from app.worker import celery_app
from app.core.database import AsyncSessionLocal
from app.models.campaign import CampaignDispatch, CampaignEvent, Campaign, Template
from app.models.organization import Target
from app.models.enums import EventTypeEnum
from app.services.engine import RotationEngine
from workers.email_sender import EmailSender

async def _send_phishing_email_async(dispatch_id: int):
    async with AsyncSessionLocal() as session:
        engine = RotationEngine(session)
        sender = EmailSender()
        
        # 1. Fetch Dispatch Data
        dispatch = await session.get(CampaignDispatch, dispatch_id)
        if not dispatch:
            return "Dispatch not found"
        
        campaign = await session.get(Campaign, dispatch.campaign_id)
        target = await session.get(Target, dispatch.target_id)
        if not campaign or not target:
             return "Campaign or Target not found"
        
        template = await session.get(Template, campaign.template_id)
        if not template:
            return "Template not found"

        # 2. Select Sending Node
        node = await engine.select_sending_node()
        if not node:
            return "No healthy sending nodes available"

        # 3. Send Email
        success = await sender.send_email(
            node=node,
            to_email=target.email,
            subject=template.subject_line,
            html_content=template.html_content
        )

        # 4. Update Status & Metrics
        if success:
            await engine.register_success(node.id)
            
            event = CampaignEvent(
                dispatch_id=dispatch.id,
                event_type=EventTypeEnum.SENT
            )
            session.add(event)
            
            dispatch.dispatch_status = "SENT"
            dispatch.sending_node_id = node.id
            
            await session.commit()
            return f"Email sent to {target.email} via Node {node.id}"
        else:
            await engine.register_failure(node.id)
            dispatch.dispatch_status = "FAILED"
            await session.commit()
            return f"Failed to send email to {target.email}"

@celery_app.task(bind=True, acks_late=True, name="send_phishing_email")
def send_phishing_email(self, dispatch_id: int):
    result = async_to_sync(_send_phishing_email_async)(dispatch_id)
    return result
