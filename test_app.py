import pytest
from app import app, items


@pytest.fixture(autouse=True)
def clear_items():
    items.clear()
    yield
    items.clear()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_items_stored_in_memory_after_post(client):
    client.post("/api/items", json={"name": "Widget", "description": "A widget"})
    assert len(items) == 1
    assert items[0]["name"] == "Widget"
    assert items[0]["description"] == "A widget"


def test_get_items_returns_in_memory_list(client):
    items.append({"id": 1, "name": "Foo", "description": "Bar"})
    response = client.get("/api/items")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "Foo"


def test_multiple_items_accumulate_in_memory(client):
    client.post("/api/items", json={"name": "A", "description": "desc A"})
    client.post("/api/items", json={"name": "B", "description": "desc B"})
    assert len(items) == 2
    response = client.get("/api/items")
    assert len(response.get_json()) == 2


def test_items_list_empty_on_fresh_start(client):
    response = client.get("/api/items")
    assert response.status_code == 200
    assert response.get_json() == []


def test_post_item_returns_created_item(client):
    response = client.post("/api/items", json={"name": "Thing", "description": "A thing"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Thing"
    assert data["description"] == "A thing"
    assert "id" in data


def test_post_item_missing_fields_returns_400(client):
    response = client.post("/api/items", json={"name": "No desc"})
    assert response.status_code == 400


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
