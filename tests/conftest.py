"""
Pytest configuration and fixtures for testing
"""

import asyncio
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.models.user import User
from app.models.savings import SavingPlan, WeeklyAmount


# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create a test database session"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session
    
    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
def client(test_db):
    """Create a test client with dependency override"""
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(test_db):
    """Create a test user"""
    user = User(
        id="test-user-uuid-123",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        provider="email"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_saving_plan(test_db, test_user):
    """Create a test saving plan"""
    from decimal import Decimal
    
    plan = SavingPlan(
        user_id=test_user.id,
        savings_name="Test Savings Plan",
        amount=Decimal('1000.00'),
        number_of_weeks=52,
        total_saved_amount=Decimal('0.00')
    )
    test_db.add(plan)
    await test_db.commit()
    await test_db.refresh(plan)
    return plan


@pytest_asyncio.fixture
async def test_weekly_amount(test_db, test_saving_plan):
    """Create a test weekly amount"""
    from decimal import Decimal
    
    weekly = WeeklyAmount(
        saving_plan_id=test_saving_plan.id,
        amount=Decimal('50.00'),
        week_index=1,
        selected=False
    )
    test_db.add(weekly)
    await test_db.commit()
    await test_db.refresh(weekly)
    return weekly


def mock_get_current_user(user: User):
    """Create a mock dependency for current user"""
    def _mock_get_current_user():
        return user
    return _mock_get_current_user