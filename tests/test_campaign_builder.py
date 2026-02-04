import pytest
from unittest.mock import MagicMock, AsyncMock
from app.services.campaign_builder import CampaignBuilder, CampaignBuilderException
from app.models.campaign import Template, Campaign

@pytest.mark.asyncio
async def test_campaign_builder_flow():
    # Mock DB Session
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    
    # Mock Template Query Result
    mock_template = Template(id=1, name="HR_Update", has_attachment=True)
    
    # Setup mock execute return
    # When select(Template) is executed, return a mock result
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = mock_template
    mock_db.execute.return_value = mock_result

    # Build Campaign
    # validation happens in build(), so setup expectations for build() call
    
    # Instantiate Builder
    builder = CampaignBuilder(mock_db)
    
    # Configure synchronously
    builder.set_name("Test Campaign") \
           .set_organization(100) \
           .select_template("HR_Update") \
           .set_target_group([1, 2, 3]) \
           .attach_payload(True)

    # Perform build (async)
    result = await builder.build()

    # Assertions
    assert isinstance(result, Campaign)
    assert result.name == "Test Campaign"
    assert result.org_id == 100
    assert result.template_id == 1
    
    # Verify DB calls
    assert mock_db.add.call_count >= 1 # Campaign + 3 Dispatches
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_campaign_builder_validation_failure():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    # Template without attachment
    mock_template = Template(id=2, name="Simple_Msg", has_attachment=False)
    
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = mock_template
    mock_db.execute.return_value = mock_result

    builder = CampaignBuilder(mock_db)
    
    # Configure synchronously
    builder.select_template("Simple_Msg") \
           .attach_payload(True) \
           .set_name("Fail Campaign") \
           .set_organization(100) \
           .set_target_group([1])

    # Expect error during build()
    with pytest.raises(CampaignBuilderException) as excinfo:
        await builder.build()
    
    assert "does not support attachments" in str(excinfo.value)
