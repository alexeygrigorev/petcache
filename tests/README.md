# Creating New Tests

## Quick Start

### For Cache Tests

Create a new test file (e.g., `test_new_feature.py`):

```python
import pytest
from petcache import PetCache
from .test_utils import transactional_cache

@pytest.fixture
def cache(tmp_path_factory):
    """Create a cache instance with transactional isolation."""
    db_path = str(tmp_path_factory.mktemp("data") / "test_cache.db")
    with transactional_cache(db_path, PetCache) as cache_instance:
        yield cache_instance

def test_your_feature(cache):
    """Test your new feature."""
    cache.set("key", "value")
    assert cache.get("key") == "value"
    # Each test automatically gets a clean database state
```

### For API Tests

Create a new API test file:

```python
import pytest
from fastapi.testclient import TestClient
from petcache.api import create_app

@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    return str(tmp_path_factory.mktemp("data") / "test_api_new.db")

@pytest.fixture
def client(test_db_path):
    """Create a test client with database cleanup."""
    app = create_app(db_path=test_db_path)
    with TestClient(app) as test_client:
        yield test_client
        # Database is automatically cleaned after each test

def test_your_api_endpoint(client):
    """Test your API endpoint."""
    response = client.post("/cache/set", json={"key": "test", "value": "data"})
    assert response.status_code == 200
```

## Key Points

- **Cache tests**: Use `transactional_cache` fixture for automatic rollback after each test
- **API tests**: Database is cleaned (not rolled back) after each test due to threading limitations  
- **No ResourceWarnings**: Both approaches properly manage SQLite connections
- **Isolation**: Each test gets a clean database state
- **Just copy the fixture patterns above** - they handle all the complexity

## Run Your Tests

```bash
uv run pytest tests/test_your_new_file.py --no-cov  # Clean output, no warnings
```
