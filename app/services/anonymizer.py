from typing import List, Dict, Any
from app.models.campaign import Campaign, CampaignEvent

import hashlib
import os

# Salt for anonymization - could come from config, but a stable or campaign-specific salt works.
# If we want it distinct per campaign, use campaign.id or generic salt.
ANONYMIZER_SALT = os.getenv("ANONYMIZER_SALT", "default_secure_salt_value").encode()

def sanitize_report_data(campaign: Campaign, events: List[CampaignEvent]) -> List[Dict[str, Any]]:
    """
    Sanitizes event data for reporting based on campaign anonymity settings.
    
    If campaign.is_anonymous_reporting is True:
        - Hashes PII (email, target_id) with SHA-256 and a salt to retain
          uniqueness without revealing identity.
        - Names are REDACTED.
        - Removes tracking data like User-Agent, keeping only generic OS/Browser.
    
    If False:
        - Returns full data including PII.
    """
    sanitized_data = []

    for event in events:
        # Access relationship data
        target = event.dispatch.target
        
        event_dict = {
            "event_type": event.event_type,
            "timestamp": event.created_at,
            "department": target.department.name if target.department else "Unknown",
            "device_info": {
                "os": event.os_fingerprint,
                "browser": event.browser_fingerprint,
            }
        }

        if getattr(campaign, 'is_anonymous_reporting', False):
            # Anonymized View using salted hashes
            # We want equal target_ids to map to equal hashes, but unreversibly
            hashed_id = hashlib.sha256(f"{target.id}".encode() + ANONYMIZER_SALT).hexdigest()
            hashed_email = hashlib.sha256(f"{target.email}".encode() + ANONYMIZER_SALT).hexdigest()
            
            event_dict.update({
                "target_id": hashed_id,
                "email": hashed_email,
                "first_name": "REDACTED",
                "last_name": "REDACTED",
            })
        else:
             # Full View
             event_dict["device_info"]["user_agent"] = event.user_agent
             event_dict.update({
                "target_id": target.id,
                "email": target.email,
                "first_name": target.first_name,
                "last_name": target.last_name
             })
            
        sanitized_data.append(event_dict)

    return sanitized_data
