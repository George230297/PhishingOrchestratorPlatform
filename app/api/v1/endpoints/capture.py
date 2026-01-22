from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.core.security import hash_captured_credential
from app.services.template_render import TemplateRenderService
from app.models.campaign import CampaignDispatch, CampaignEvent, CapturedCredential, Template, Campaign
from app.models.enums import EventTypeEnum

router = APIRouter()

# 1x1 Transparent PNG bytes
PIXEL_BYTES = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x03\x00\x08\xfc\x02\xfe\xa7\x9a\xa0\xa0\x00\x00\x00\x00IEND\xaeB`\x82'

async def _log_event(
    db: AsyncSession,
    dispatch_id: int,
    event_type: EventTypeEnum,
    request: Request
):
    """Helper to log campaign events with user agent info."""
    user_agent = request.headers.get("user-agent", "Unknown")
    # In a real app, use user-agents library to parse OS/Browser
    os_fingerprint = "Detected from UA" 
    browser_fingerprint = "Detected from UA"

    event = CampaignEvent(
        dispatch_id=dispatch_id,
        event_type=event_type,
        ip_address=request.client.host,
        user_agent=user_agent,
        os_fingerprint=os_fingerprint,
        browser_fingerprint=browser_fingerprint
    )
    db.add(event)
    await db.commit()

@router.get("/track/{token}/pixel.png")
async def track_pixel(
    token: str,
    request: Request,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    1. Tracking Pixel Endpoint.
    Logs OPENED event and returns an invisible image.
    """
    result = await db.execute(select(CampaignDispatch).where(CampaignDispatch.unique_tracking_token == token))
    dispatch = result.scalars().first()

    if dispatch:
        # Check if already opened to avoid noise? Or log every open? 
        # Requirement implies logging.
        await _log_event(db, dispatch.id, EventTypeEnum.OPENED, request)

    return Response(content=PIXEL_BYTES, media_type="image/png")

@router.get("/portal/{token}", response_class=HTMLResponse)
async def serve_landing_page(
    token: str,
    request: Request,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    2. Landing Page Endpoint.
    Logs CLICKED event and renders the phishing template.
    """
    # Find Dispatch
    result = await db.execute(select(CampaignDispatch).where(CampaignDispatch.unique_tracking_token == token))
    dispatch = result.scalars().first()
    
    if not dispatch:
        # Return a generic 404 or a fake 404 to avoid scanning
        return HTMLResponse("<h1>404 Not Found</h1>", status_code=404)

    # Log Click
    await _log_event(db, dispatch.id, EventTypeEnum.CLICKED, request)

    # Fetch Template
    campaign = await db.get(Campaign, dispatch.campaign_id)
    if not campaign:
        return HTMLResponse("<h1>Campaign Error</h1>", status_code=500)
    
    template = await db.get(Template, campaign.template_id)
    if not template or not template.landing_page_html:
        return HTMLResponse("<h1>Template Error</h1>", status_code=500)

    # Render Template
    # We inject the capture URL so the form knows where to submit
    context = {
        "capture_url": f"/api/v1/capture/{token}", # Assuming relative path works for the frontend context
        "email": "victim@target.com" # Could inject victim details to make it look real
    }
    
    # If the user stored {{ capture_url }} in their template, Jinja will replace it.
    rendered_html = TemplateRenderService.render_template(template.landing_page_html, context)
    
    return HTMLResponse(content=rendered_html)

@router.post("/capture/{token}")
async def capture_credentials(
    token: str,
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(deps.get_db)
):
    """
    3. Credential Capture Endpoint.
    Hashes password immediately, stores it, logs SUBMITTED_DATA, and redirects.
    """
    result = await db.execute(select(CampaignDispatch).where(CampaignDispatch.unique_tracking_token == token))
    dispatch = result.scalars().first()

    if not dispatch:
         return HTMLResponse("<h1>404 Not Found</h1>", status_code=404)

    # Security: Hash Password
    hashed_password = hash_captured_credential(password)

    # Store Credential
    credential = CapturedCredential(
        dispatch_id=dispatch.id,
        username_entered=username,
        password_hash=hashed_password,
        was_password_leaked=True
    )
    db.add(credential)

    # Log Event
    await _log_event(db, dispatch.id, EventTypeEnum.SUBMITTED_DATA, request)

    # Redirect to Education
    return RedirectResponse(url="/api/v1/education/warning", status_code=303)

@router.get("/education/warning", response_class=HTMLResponse)
async def education_page():
    """
    4. Educational Teachable Moment.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Security Alert</title>
        <style>
            body { font-family: sans-serif; text-align: center; padding: 50px; background-color: #f8d7da; color: #721c24; }
            .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); display: inline-block; }
            h1 { color: #d9534f; }
            ul { text-align: left; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚠️ Access Denied: Phishing Simulation</h1>
            <p>This was a security awareness simulation. If this had been a real attack, your credentials would have been compromised.</p>
            <p><strong>Your password was NOT saved in plain text. It was securely hashed.</strong></p>
            <h3>Security Tips:</h3>
            <ul>
                <li>Check the URL carefully before entering passwords.</li>
                <li>Be skeptical of urgent requests.</li>
                <li>Report suspicious emails to your security team.</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
