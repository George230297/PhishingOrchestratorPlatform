import pytest
from app.models.campaign import Campaign, CampaignDispatch, CampaignEvent
from app.models.organization import Target, Department
from app.services.anonymizer import sanitize_report_data, ANONYMIZER_SALT
import hashlib

def test_sanitize_report_data_anonymous():
    # Setup mock data
    department = Department(id=1, name="IT")
    target = Target(id=10, email="john.doe@example.com", first_name="John", last_name="Doe", department=department)
    dispatch = CampaignDispatch(id=100, target=target)
    event1 = CampaignEvent(event_type="CLICK", os_fingerprint="Windows", browser_fingerprint="Chrome", user_agent="Mozilla/5.0", dispatch=dispatch)
    event2 = CampaignEvent(event_type="LOGIN", os_fingerprint="Windows", browser_fingerprint="Chrome", user_agent="Mozilla/5.0", dispatch=dispatch)
    events = [event1, event2]
    
    # Setup campaign
    campaign = Campaign(id=1, is_anonymous_reporting=True)

    sanitized = sanitize_report_data(campaign, events)

    assert len(sanitized) == 2
    for item in sanitized:
        assert item["first_name"] == "REDACTED"
        assert item["last_name"] == "REDACTED"
        # Check salted hashes
        expected_hash_id = hashlib.sha256(b"10" + ANONYMIZER_SALT).hexdigest()
        assert item["target_id"] == expected_hash_id
        
        expected_hash_email = hashlib.sha256(b"john.doe@example.com" + ANONYMIZER_SALT).hexdigest()
        assert item["email"] == expected_hash_email
        
        assert item["department"] == "IT"
        assert "user_agent" not in item["device_info"]

def test_sanitize_report_data_full():
    # Setup mock data
    department = Department(id=1, name="Sales")
    target = Target(id=20, email="jane.doe@example.com", first_name="Jane", last_name="Doe", department=department)
    dispatch = CampaignDispatch(id=101, target=target)
    event1 = CampaignEvent(event_type="OPEN", os_fingerprint="Mac", browser_fingerprint="Safari", user_agent="Mozilla/5.0", dispatch=dispatch)
    events = [event1]
    
    campaign = Campaign(id=2, is_anonymous_reporting=False)

    sanitized = sanitize_report_data(campaign, events)

    assert len(sanitized) == 1
    item = sanitized[0]
    assert item["first_name"] == "Jane"
    assert item["last_name"] == "Doe"
    assert item["target_id"] == 20
    assert item["email"] == "jane.doe@example.com"
    assert item["department"] == "Sales"
    assert "user_agent" in item["device_info"]
    assert item["device_info"]["user_agent"] == "Mozilla/5.0"
