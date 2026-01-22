from typing import List, Dict, Any
from app.models.campaign import Campaign, CampaignEvent

def sanitize_report_data(campaign: Campaign, events: List[CampaignEvent]) -> List[Dict[str, Any]]:
    """
    Sanitizes event data for reporting based on campaign anonymity settings.
    
    If campaign.is_anonymous_reporting is True:
        - Replaces PII (email, names) with 'REDACTED'.
        - Keeps Department and Device Info for metrics.
    
    If False:
        - Returns full data including PII.
    """
    sanitized_data = []

    for event in events:
        # Access relationship data
        # Note: Ensure eager loading is used when querying events to avoid N+1 queries here
        target = event.dispatch.target
        
        event_dict = {
            "event_type": event.event_type,
            "timestamp": event.created_at,
            "department": target.department.name if target.department else "Unknown",
            "device_info": {
                "os": event.os_fingerprint,
                "browser": event.browser_fingerprint,
                "user_agent": event.user_agent
            }
        }

        if campaign.is_anonymous_reporting:
            # Anonymized View
            event_dict.update({
                "target_id": "REDACTED", # Or a safe hash of ID if tracking unique users is needed without knowing who
                "email": "REDACTED",
                "first_name": "REDACTED",
                "last_name": "REDACTED"
            })
        else:
            # Full View
            event_dict.update({
                "target_id": target.id,
                "email": target.email,
                "first_name": target.first_name,
                "last_name": target.last_name
            })
            
        sanitized_data.append(event_dict)

    return sanitized_data
