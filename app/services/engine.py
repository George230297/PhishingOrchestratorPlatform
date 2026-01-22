from datetime import datetime
from sqlalchemy import select, update, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.infrastructure import SendingNode
from app.models.enums import HealthStatusEnum

class RotationEngine:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def select_sending_node(self) -> SendingNode | None:
        """
        Selects the best available SendingNode based on:
        1. Status is HEALTHY
        2. Daily limit not reached
        3. Ordered by Reputation (Highest first)
        """
        query = select(SendingNode).where(
            and_(
                SendingNode.status == HealthStatusEnum.HEALTHY,
                SendingNode.current_daily_sends < SendingNode.daily_send_limit
            )
        ).order_by(SendingNode.current_reputation.desc())
        
        result = await self.session.execute(query)
        node = result.scalars().first()
        return node

    async def register_success(self, node_id: int):
        stmt = (
            update(SendingNode)
            .where(SendingNode.id == node_id)
            .values(
                current_daily_sends=SendingNode.current_daily_sends + 1,
                last_used_at=datetime.utcnow()
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def register_failure(self, node_id: int):
        # Penalize reputation by 10 points
        stmt = (
            update(SendingNode)
            .where(SendingNode.id == node_id)
            .values(
                current_reputation=SendingNode.current_reputation - 10,
                # If reputation drops below 50, burn it
                status=func.case(
                    (SendingNode.current_reputation - 10 < 50, HealthStatusEnum.BURNED),
                    else_=SendingNode.status
                )
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()
