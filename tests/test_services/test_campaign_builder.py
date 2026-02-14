import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.campaign_builder import CampaignBuilder, CampaignBuilderException
from app.models.campaign import Template

@pytest.mark.asyncio
async def test_campaign_builder_initialization():
    mock_db = AsyncMock()
    builder = CampaignBuilder(mock_db)
    assert builder.db == mock_db
    assert builder.target_ids == []
    assert builder.use_attachment is False

@pytest.mark.asyncio
async def test_campaign_builder_set_name():
    mock_db = AsyncMock()
    builder = CampaignBuilder(mock_db)
    builder.set_name("Test Campaign")
    assert builder.name == "Test Campaign"

    with pytest.raises(CampaignBuilderException):
        builder.set_name("")

@pytest.mark.asyncio
async def test_campaign_builder_select_template():
    mock_db = AsyncMock()
    builder = CampaignBuilder(mock_db)
    builder.select_template("Phishing Template")
    assert builder.template_name == "Phishing Template"

@pytest.mark.asyncio
async def test_campaign_builder_build_success():
    mock_db = AsyncMock()
    
    # Mock Template Query
    mock_template = Template(id=1, name="Phishing Template", has_attachment=True)
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = mock_template
    mock_db.execute.return_value = mock_result
    
    mock_db.add = MagicMock() # .add is synchronous in SQLAlchemy 1.4/2.0 styl, but commit is async
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    builder = CampaignBuilder(mock_db)
    builder.set_name("Test Campaign") \
           .set_organization(1) \
           .set_target_group([10, 11]) \
           .select_template("Phishing Template") \
           .attach_payload(True)

    campaign = await builder.build()

    assert campaign.name == "Test Campaign"
    assert campaign.template_id == 1
    # Check if add was called (sychronous method on AsyncSession in some versions, but usually async)
    # verify call count
    assert mock_db.add.called
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_campaign_builder_build_missing_fields():
    mock_db = AsyncMock()
    builder = CampaignBuilder(mock_db)
    
    with pytest.raises(CampaignBuilderException, match="Campaign name is required"):
        await builder.build()
