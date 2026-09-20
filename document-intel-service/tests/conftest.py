import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings

# Force testing environment and SQLite shared in-memory test database before importing app components
settings.ENVIRONMENT = "testing"
settings.DATABASE_URL = "sqlite:///file:testdb?mode=memory&cache=shared&uri=true"

import app.database as app_db
from app.main import app
from app.database import Base, get_db

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False, "uri": True},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override application database engine and SessionLocal for background tasks in test suite
app_db.engine = engine
app_db.SessionLocal = TestingSessionLocal


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
