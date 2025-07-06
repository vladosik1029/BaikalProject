import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Тестовая БД
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем таблицы перед тестами
@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Переопределяем зависимость get_db для тестов
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def admin_token(client):
    # Создаем тестового админа
    admin_data = {
        "username": "admin",
        "email": "admin@test.com",
        "password": "adminpass",
        "role": "admin"
    }
    client.post("/admin/users/", json=admin_data)
    
    # Получаем токен
    response = client.post("/token", data={
        "username": "admin",
        "password": "adminpass"
    })
    return response.json()["access_token"]

def test_public_route(client):
    response = client.get("/public/")
    assert response.status_code == 200
    assert response.json()["message"] == "This is public data"

def test_admin_access(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/admin/users/", headers=headers)
    assert response.status_code == 200