import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Test client for FastAPI app.
    """
    # Create transport for in-process testing without binding to a port
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

# Patch passlib to work with newer bcrypt (logic kept just in case, though we switched to argon2)
import passlib.handlers.bcrypt
import bcrypt
if passlib.handlers.bcrypt._bcrypt is None:
    passlib.handlers.bcrypt._bcrypt = bcrypt

_bcrypt = passlib.handlers.bcrypt._bcrypt
if not hasattr(_bcrypt, '__about__'):
    class MockAbout:
        __version__ = "4.0.1" 
    _bcrypt.__about__ = MockAbout()
