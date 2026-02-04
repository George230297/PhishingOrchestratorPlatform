from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.campaign import Campaign, Template, CampaignDispatch
from app.models.organization import Target, Department, Organization

class CampaignBuilderException(Exception):
    """Exception raised for errors in the CampaignBuilder process."""
    pass

class CampaignBuilder:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.name: Optional[str] = None
        self.org_id: Optional[int] = None
        self.template_id: Optional[int] = None
        self.target_ids: List[int] = []
        self.use_attachment: bool = False
        
        # Internal state
        self._template: Optional[Template] = None

    def set_name(self, name: str) -> "CampaignBuilder":
        if not name:
            raise CampaignBuilderException("Campaign name cannot be empty.")
        self.name = name
        return self

    def set_organization(self, org_id: int) -> "CampaignBuilder":
        self.org_id = org_id
        return self

    async def select_template_by_name(self, template_name: str) -> "CampaignBuilder":
        # Deprecated or internal use if needed, but for builder pattern we want sync
        pass

    def select_template(self, template_name: str) -> "CampaignBuilder":
        """
        Selects a template by name (validation deferred to build()).
        """
        self.template_name = template_name
        return self

    def set_target_group(self, target_ids: List[int]) -> "CampaignBuilder":
        """
        Sets the target group for the campaign.
        Currently accepts a list of target IDs.
        """
        if not target_ids:
            raise CampaignBuilderException("Target group cannot be empty.")
        self.target_ids = target_ids
        return self
    
    def attach_payload(self, use_attachment: bool) -> "CampaignBuilder":
        """
        Configures whether the campaign should include a payload.
        (Validation deferred to build()).
        """
        self.use_attachment = use_attachment
        return self

    async def build(self) -> Campaign:
        """
        Finalizes the campaign creation.
        Resolves template, validates configuration, persists the Campaign 
        and creates initial CampaignDispatch entries.
        Returns the created Campaign object.
        """
        # 1. Basic Validation
        if not self.name:
            raise CampaignBuilderException("Campaign name is required.")
        if not self.org_id:
            raise CampaignBuilderException("Organization ID is required.")
        if not self.target_ids:
            raise CampaignBuilderException("No targets selected.")
        if not hasattr(self, 'template_name') or not self.template_name:
             raise CampaignBuilderException("Template must be selected.")

        # 2. Async Validation / Resolution
        # Resolve Template
        query = select(Template).where(Template.name == self.template_name)
        result = await self.db.execute(query)
        template = result.scalars().first()
        
        if not template:
            raise CampaignBuilderException(f"Template '{self.template_name}' not found.")
        
        self.template_id = template.id
        self._template = template

        # Validate Payload Compatibility
        if self.use_attachment and not self._template.has_attachment:
             raise CampaignBuilderException(f"Template '{self.template_name}' does not support attachments, but attach_payload(True) was requested.")

        # 3. Create Campaign
        campaign = Campaign(
            name=self.name,
            org_id=self.org_id,
            template_id=self.template_id,
            # If there are other defaults or params, set them here
        )
        self.db.add(campaign)
        await self.db.flush() # Get ID

        # 4. Create Dispatches
        for target_id in self.target_ids:
            dispatch = CampaignDispatch(
                campaign_id=campaign.id,
                target_id=target_id,
                dispatch_status="DRAFT"
            )
            self.db.add(dispatch)

        await self.db.commit()
        await self.db.refresh(campaign)
        
        return campaign
