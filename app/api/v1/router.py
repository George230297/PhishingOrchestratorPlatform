from fastapi import APIRouter
from app.api.v1.endpoints import campaigns, webhooks, capture

api_router = APIRouter()
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
# Capture endpoints are often root-level for deceptive URL looks, but keeping inside api/v1 for structure
# We mount them directly to /api/v1 so the paths are /api/v1/portal/{token}, etc.
api_router.include_router(capture.router, tags=["capture"])
