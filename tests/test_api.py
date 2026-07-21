import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app import crud, schemas

# --- Тестовая БД (в памяти) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


# Переопределяем зависимость get_db для тестов
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Создаём клиент
client = TestClient(app)


# --- Фикстура: создание таблиц перед тестами ---
@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# --- Фикстура: тестовый пользователь Designer ---
@pytest.fixture
def designer_headers():
    return {"User-id": "test-designer", "Role": "Designer"}


# --- Фикстура: тестовый пользователь Viewer ---
@pytest.fixture
def viewer_headers():
    return {"User-id": "test-viewer", "Role": "Viewer"}


# --- Фикстура: создание дашборда для тестов ---
@pytest.fixture
def sample_dashboard():
    return {
        "dashboard_id": "test-dashboard",
        "title": "Тестовый дашборд",
        "layout": {"type": "grid", "columns": 12},
        "widgets": [
            {
                "widget_id": "w1",
                "type": "line_chart",
                "position": {"x": 0, "y": 0, "w": 6, "h": 4},
                "data_source": {"provider": "csv_provider", "dataset_id": "sales_2026"},
                "config": {"x_field": "date", "y_field": "revenue"}
            }
        ]
    }


# ============================================================
# ТЕСТЫ
# ============================================================

class TestAuth:
    """Тесты авторизации и ролей"""

    def test_create_dashboard_with_designer(self, designer_headers, sample_dashboard):
        """Designer может создать дашборд"""
        response = client.post(
            "/api/v1/dashboards",
            json=sample_dashboard,
            headers=designer_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["dashboard_id"] == "test-dashboard"
        assert data["author"] == "test-designer"
        assert "created_at" in data

    def test_create_dashboard_without_role(self, sample_dashboard):
        """Без заголовка Role — ошибка 422 (валидация FastAPI)"""
        response = client.post(
            "/api/v1/dashboards",
            json=sample_dashboard,
            headers={"User-id": "test-user"}
        )
        assert response.status_code == 422

    def test_create_dashboard_with_viewer(self, viewer_headers, sample_dashboard):
        """Viewer НЕ может создать дашборд (только Designer)"""
        response = client.post(
            "/api/v1/dashboards",
            json=sample_dashboard,
            headers=viewer_headers
        )
        assert response.status_code == 403
        assert "только для Designer" in response.text

    def test_update_dashboard_with_viewer(self, designer_headers, viewer_headers, sample_dashboard):
        """Viewer НЕ может обновить дашборд"""
        # Сначала создаём дашборд как Designer
        client.post("/api/v1/dashboards", json=sample_dashboard,
                    headers=designer_headers)

        # Пытаемся обновить как Viewer
        updated = sample_dashboard.copy()
        updated["title"] = "Обновлённый дашборд"
        response = client.put(
            "/api/v1/dashboards/test-dashboard",
            json=updated,
            headers=viewer_headers
        )
        assert response.status_code == 403

    def test_delete_dashboard_with_viewer(self, designer_headers, viewer_headers, sample_dashboard):
        """Viewer НЕ может удалить дашборд"""
        client.post("/api/v1/dashboards", json=sample_dashboard,
                    headers=designer_headers)

        response = client.delete(
            "/api/v1/dashboards/test-dashboard",
            headers=viewer_headers
        )
        assert response.status_code == 403


class TestDashboardsCRUD:
    """Тесты CRUD операций с дашбордами"""

    def test_create_dashboard_success(self, designer_headers, sample_dashboard):
        """Успешное создание дашборда"""
        response = client.post(
            "/api/v1/dashboards",
            json=sample_dashboard,
            headers=designer_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["dashboard_id"] == "test-dashboard"
        assert data["title"] == "Тестовый дашборд"
        assert data["author"] == "test-designer"
        assert data["widgets"] == sample_dashboard["widgets"]

    def test_create_dashboard_duplicate(self, designer_headers, sample_dashboard):
        """Попытка создать дубликат — ошибка 409"""
        client.post("/api/v1/dashboards", json=sample_dashboard,
                    headers=designer_headers)

        response = client.post(
            "/api/v1/dashboards",
            json=sample_dashboard,
            headers=designer_headers
        )
        assert response.status_code == 409
        assert "уже существует" in response.text

    def test_create_dashboard_invalid_id(self, designer_headers):
        """Некорректный dashboard_id — ошибка валидации"""
        invalid = {
            "dashboard_id": "test dashboard!",  # пробел и !
            "title": "Тест",
            "layout": {"type": "grid", "columns": 12},
            "widgets": []
        }
        response = client.post(
            "/api/v1/dashboards",
            json=invalid,
            headers=designer_headers
        )
        assert response.status_code == 422  # ValidationError

    def test_get_dashboard_success(self, designer_headers, sample_dashboard):
        """Получение дашборда по ID"""
        client.post("/api/v1/dashboards", json=sample_dashboard,
                    headers=designer_headers)

        response = client.get("/api/v1/dashboards/test-dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["dashboard_id"] == "test-dashboard"
        assert data["title"] == "Тестовый дашборд"

    def test_get_dashboard_not_found(self):
        """Запрос несуществующего дашборда — 404"""
        response = client.get("/api/v1/dashboards/non-existent")
        assert response.status_code == 404
        assert "не найден" in response.text

    def test_get_all_dashboards(self, designer_headers, sample_dashboard):
        """Получение списка всех дашбордов"""
        client.post("/api/v1/dashboards", json=sample_dashboard,
                    headers=designer_headers)

        # Создаём второй дашборд
        second = sample_dashboard.copy()
        second["dashboard_id"] = "second-dashboard"
        second["title"] = "Второй дашборд"
        client.post("/api/v1/dashboards", json=second,
                    headers=designer_headers)

        response = client.get("/api/v1/dashboards")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        ids = [d["dashboard_id"] for d in data]
        assert "test-dashboard" in ids
        assert "second-dashboard" in ids

    def test_update_dashboard_success(self, designer_headers, sample_dashboard):
        """Успешное обновление дашборда"""
        client.post("/api/v1/dashboards", json=sample_dashboard,
                    headers=designer_headers)

        updated = sample_dashboard.copy()
        updated["title"] = "Обновлённый дашборд"
        updated["widgets"] = []

        response = client.put(
            "/api/v1/dashboards/test-dashboard",
            json=updated,
            headers=designer_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Обновлённый дашборд"
        assert data["widgets"] == []

    def test_update_dashboard_wrong_id(self, designer_headers, sample_dashboard):
        """ID в пути не совпадает с ID в теле — ошибка 400"""
        client.post("/api/v1/dashboards", json=sample_dashboard,
                    headers=designer_headers)

        updated = sample_dashboard.copy()
        updated["dashboard_id"] = "different-id"

        response = client.put(
            "/api/v1/dashboards/test-dashboard",
            json=updated,
            headers=designer_headers
        )
        assert response.status_code == 400
        assert "не совпадают" in response.text

    def test_delete_dashboard_success(self, designer_headers, sample_dashboard):
        """Успешное удаление дашборда"""
        client.post("/api/v1/dashboards", json=sample_dashboard,
                    headers=designer_headers)

        response = client.delete(
            "/api/v1/dashboards/test-dashboard",
            headers=designer_headers
        )
        assert response.status_code == 204

        # Проверяем, что дашборд действительно удалён
        get_response = client.get("/api/v1/dashboards/test-dashboard")
        assert get_response.status_code == 404

    def test_delete_dashboard_not_found(self, designer_headers):
        """Удаление несуществующего дашборда — 404"""
        response = client.delete(
            "/api/v1/dashboards/non-existent",
            headers=designer_headers
        )
        assert response.status_code == 404


class TestMetadata:
    """Тесты метаданных (заглушки)"""

    def test_get_sources(self):
        """Получение списка источников"""
        response = client.get("/api/v1/sources")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 4
        assert any(s["id"] == "postgres" for s in data)

    def test_get_widgets(self):
        """Получение списка виджетов"""
        response = client.get("/api/v1/widgets")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 6
        assert any(w["id"] == "line_chart" for w in data)


class TestLogin:
    """Тесты логина"""

    def test_login_success(self):
        """Успешный вход"""
        response = client.post(
            "/api/v1/login/",
            params={"username": "testuser", "role": "Designer"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "Designer"
        assert "testuser" in data["message"]
