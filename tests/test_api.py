"""Tests for the FastAPI application."""

import pytest
import sqlite3
from contextlib import contextmanager
from fastapi.testclient import TestClient

from petcache.api import create_app
from petcache.cache import PetCache


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    """Create a shared test database for the entire test session."""
    return str(tmp_path_factory.mktemp("data") / "test_api.db")


@contextmanager
def transactional_app(db_path):
    """Context manager that provides a FastAPI app with database cleanup."""
    # Initialize database schema
    init_conn = sqlite3.connect(db_path)
    try:
        init_conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        init_conn.commit()
    finally:
        init_conn.close()
    
    # Create the app
    app = create_app(db_path=db_path)
    
    try:
        yield app
    finally:
        # Clean up database after test
        cleanup_conn = sqlite3.connect(db_path)
        try:
            cleanup_conn.execute("DELETE FROM cache")
            cleanup_conn.commit()
        finally:
            cleanup_conn.close()


@pytest.fixture
def app_instance(test_db_path):
    """Create a test app instance with transactional isolation."""
    with transactional_app(test_db_path) as app:
        yield app


@pytest.fixture
def cache_instance(test_db_path):
    """Create a cache instance for testing."""
    with transactional_app(test_db_path):
        yield PetCache(db_path=test_db_path)


@pytest.fixture
def client(app_instance):
    """Create a test client."""
    return TestClient(app_instance)


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "entries" in data
    assert "db_path" in data


def test_set_value(client):
    """Test setting a value via API."""
    response = client.post(
        "/cache",
        json={"key": "test_key", "value": "test_value"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "test_key"


def test_get_value(client):
    """Test getting a value via API."""
    # First set a value
    client.post("/cache", json={"key": "test_key", "value": "test_value"})
    
    # Then get it
    response = client.get("/cache/test_key")
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "test_key"
    assert data["value"] == "test_value"


def test_get_nonexistent_value(client):
    """Test getting a nonexistent value."""
    response = client.get("/cache/nonexistent")
    assert response.status_code == 404


def test_delete_value(client):
    """Test deleting a value via API."""
    # First set a value
    client.post("/cache", json={"key": "to_delete", "value": "value"})
    
    # Then delete it
    response = client.delete("/cache/to_delete")
    assert response.status_code == 200
    
    # Verify it's gone
    response = client.get("/cache/to_delete")
    assert response.status_code == 404


def test_delete_nonexistent_value(client):
    """Test deleting a nonexistent value."""
    response = client.delete("/cache/nonexistent")
    assert response.status_code == 404


def test_list_cache(client):
    """Test listing all cache entries."""
    # Add some values
    client.post("/cache", json={"key": "key1", "value": "value1"})
    client.post("/cache", json={"key": "key2", "value": "value2"})
    
    response = client.get("/cache")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["entries"]) == 2


def test_clear_cache(client):
    """Test clearing the cache via API."""
    # Add some values
    client.post("/cache", json={"key": "key1", "value": "value1"})
    client.post("/cache", json={"key": "key2", "value": "value2"})
    
    # Clear
    response = client.delete("/cache")
    assert response.status_code == 200
    data = response.json()
    assert data["deleted"] == 2
    
    # Verify it's empty
    response = client.get("/cache")
    data = response.json()
    assert data["count"] == 0


def test_export_cache(client):
    """Test exporting cache via API."""
    # Add some values
    client.post("/cache", json={"key": "key1", "value": "value1"})
    client.post("/cache", json={"key": "key2", "value": "value2"})
    
    response = client.get("/export")
    assert response.status_code == 200
    data = response.json()
    assert data == {"key1": "value1", "key2": "value2"}


def test_import_cache(client):
    """Test importing cache via API."""
    import_data = {
        "data": {
            "key1": "value1",
            "key2": "value2"
        },
        "clear_first": False
    }
    
    response = client.post("/import", json=import_data)
    assert response.status_code == 200
    data = response.json()
    assert data["imported"] == 2
    
    # Verify the data was imported
    response = client.get("/cache/key1")
    assert response.json()["value"] == "value1"


def test_import_with_clear(client):
    """Test importing with clear_first option."""
    # Set an existing value
    client.post("/cache", json={"key": "old_key", "value": "old_value"})
    
    # Import new data with clear
    import_data = {
        "data": {
            "key1": "value1"
        },
        "clear_first": True
    }
    
    response = client.post("/import", json=import_data)
    assert response.status_code == 200
    
    # Verify old key is gone
    response = client.get("/cache/old_key")
    assert response.status_code == 404
    
    # Verify new key exists
    response = client.get("/cache/key1")
    assert response.status_code == 200


def test_update_value(client):
    """Test updating an existing value."""
    # Set initial value
    client.post("/cache", json={"key": "key", "value": "old_value"})
    
    # Update it
    client.post("/cache", json={"key": "key", "value": "new_value"})
    
    # Verify it was updated
    response = client.get("/cache/key")
    assert response.json()["value"] == "new_value"


def test_filename_as_key_api(client):
    """Test using filenames as keys via API."""
    client.post("/cache", json={"key": "file.txt", "value": "content"})
    client.post("/cache", json={"key": "path:to:file.py", "value": "code"})
    
    response = client.get("/cache/file.txt")
    assert response.json()["value"] == "content"
    
    # Use colons instead of slashes for path-like keys in API
    response = client.get("/cache/path:to:file.py")
    assert response.json()["value"] == "code"


def test_unicode_values_api(client):
    """Test storing unicode text via API."""
    client.post("/cache", json={"key": "unicode", "value": "Hello 世界 🌍"})
    
    response = client.get("/cache/unicode")
    assert response.json()["value"] == "Hello 世界 🌍"


def test_empty_value_api(client):
    """Test storing empty string via API."""
    client.post("/cache", json={"key": "empty", "value": ""})
    
    response = client.get("/cache/empty")
    assert response.json()["value"] == ""


# No cleanup needed - transactions handle isolation
