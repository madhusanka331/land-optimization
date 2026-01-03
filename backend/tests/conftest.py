"""
Pytest configuration and fixtures for backend testing.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.models.db_models import Base
from src.models.schemas import LandInputSchema, DirectionEnum, LandShapeEnum
from src.api.main import app
from src.api.database import get_db


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a test client with dependency override.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_land_input():
    """
    Sample land input for testing.
    """
    return LandInputSchema(
        length=20.0,
        width=15.0,
        bedrooms=3,
        toilets=2,
        living_room=1,
        dining_room=1,
        kitchen=1,
        garden_area=10.0,
        front_direction=DirectionEnum.NORTH,
        road_side=DirectionEnum.SOUTH,
        land_shape=LandShapeEnum.RECTANGULAR,
    )


@pytest.fixture
def small_land_input():
    """
    Small land input for testing edge cases.
    """
    return LandInputSchema(
        length=10.0,
        width=8.0,
        bedrooms=1,
        toilets=1,
        living_room=0,
        dining_room=0,
        kitchen=1,
        garden_area=0.0,
        front_direction=DirectionEnum.EAST,
        road_side=DirectionEnum.WEST,
        land_shape=LandShapeEnum.RECTANGULAR,
    )


@pytest.fixture
def large_land_input():
    """
    Large land input for testing.
    """
    return LandInputSchema(
        length=30.0,
        width=25.0,
        bedrooms=5,
        toilets=3,
        living_room=1,
        dining_room=1,
        kitchen=1,
        garden_area=50.0,
        front_direction=DirectionEnum.WEST,
        road_side=DirectionEnum.EAST,
        land_shape=LandShapeEnum.RECTANGULAR,
    )
