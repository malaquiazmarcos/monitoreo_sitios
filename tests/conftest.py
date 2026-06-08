import pytest
import os
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, StaticPool
from app.main import app
from app.database import get_session
from app.routers.sites import verify_admin_key

# 1. Base de datos de prueba en memoria
# ...
sqlite_url = "sqlite://"
engine = create_engine(
    sqlite_url, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

@pytest.fixture(name="session")
def session_fixture():
    # Crea las tablas para el test
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    # Override de la base de datos
    def get_session_override():
        yield session

    # Override de la seguridad (Bypass)
    # Esto hace que la función de validación no haga nada y el test pase siempre
    async def verify_admin_key_override():
        return True

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[verify_admin_key] = verify_admin_key_override
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()
