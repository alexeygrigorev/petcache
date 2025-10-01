# petcache

Simple persistent cache for texts for your pet projects.

`petcache` is a lightweight, persistent text cache built on SQLite for Python 3.10+. It's perfect for caching text content, storing configuration, or maintaining a simple key-value store with file-like keys.

## Features

- 🔑 **Flexible Keys**: Use filenames or any string as keys
- 💾 **Persistent Storage**: SQLite-backed for reliability
- 🚀 **FastAPI Integration**: REST API out of the box
- 📦 **Import/Export**: Git-friendly JSON format
- 🧪 **Well Tested**: Comprehensive test coverage
- ⚡ **Modern Python**: Built for Python 3.10+
- 🛠️ **uv Integration**: Fast dependency management

## Installation

Using `uv` (recommended):

```bash
uv add petcache
```

Or with pip:

```bash
pip install petcache
```

## Quick Start

### Python API

```python
from petcache import PetCache

# Create a cache instance
cache = PetCache("my_cache.db")

# Store text
cache.set("document.txt", "This is my document content")
cache.set("config.json", '{"key": "value"}')

# Retrieve text
content = cache.get("document.txt")
print(content)  # "This is my document content"

# Check if key exists
if "document.txt" in cache:
    print("Document found!")

# List all keys
keys = cache.list_keys()
print(keys)  # ['config.json', 'document.txt']

# Delete a key
cache.delete("config.json")

# Get cache size
print(len(cache))  # 1

# Clear all entries
cache.clear()
```

### Export/Import

```python
# Export to JSON (git-friendly format)
cache.export_to_json("cache_backup.json", indent=2)

# Import from JSON
cache.import_from_json("cache_backup.json")

# Or use dictionaries
data = cache.export_to_dict()
cache.import_from_dict(data, clear_first=True)
```

### FastAPI Server

Start the API server:

```bash
python -m petcache
python -m petcache --help
```

The API will be available at `http://localhost:8909` (or your specified port)

#### API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /cache/{key}` - Get a value
- `POST /cache` - Set a value
- `DELETE /cache/{key}` - Delete a value
- `GET /cache` - List all entries
- `DELETE /cache` - Clear all entries
- `GET /export` - Export cache as JSON
- `POST /import` - Import cache from JSON

#### Example API Usage

```bash
# Set a value
curl -X POST http://localhost:8000/cache \
  -H "Content-Type: application/json" \
  -d '{"key": "test.txt", "value": "Hello, World!"}'

# Get a value
curl http://localhost:8000/cache/test.txt

# List all entries
curl http://localhost:8000/cache

# Export cache
curl http://localhost:8000/export

# Clear cache
curl -X DELETE http://localhost:8000/cache
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/alexeygrigorev/petcache.git
cd petcache

# Install dependencies with uv
make install
```


### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
uv run pytest tests/test_cache.py -v
```

## Running as a Server

### Using `python -m petcache`

You can run `petcache` as a server using the module interface. Here are various usage examples:

1. Basic Server (Default Settings)

```bash
python -m petcache
# Runs on 0.0.0.0:8909 with petcache.db
```

2. Custom Host and Port

```bash
python -m petcache --host localhost --port 9000
# Runs on localhost:9000
```

3. Custom Database Path

```bash
python -m petcache --db-path ./data/my_cache.db
# Uses custom database file
```

4. Development Mode with Auto-reload

```bash
python -m petcache --reload
# Automatically reloads on code changes
```

5. Full Configuration

```bash
python -m petcache --host 0.0.0.0 --port 8080 --db-path /path/to/cache.db --reload
# Complete custom setup
```

6. Get Help

```bash
python -m petcache --help
# Shows all available options
```

The server will start and display:
```
Starting petcache server...
Host: 0.0.0.0
Port: 8909
Database: /path/to/petcache.db
API docs: http://0.0.0.0:8909/docs
```

### Using Docker

#### Docker Examples

**Build and run with Docker:**
```bash
# Build the image
docker build -t petcache .

# Run with volume mapping for database persistence
docker run -p 8909:8909 -v $(pwd)/data:/app/data petcache

# Run with custom port mapping
docker run -p 8080:8909 -v $(pwd)/data:/app/data petcache

# Run in detached mode
docker run -d -p 8909:8909 -v $(pwd)/data:/app/data --name petcache-server petcache
```

The Docker setup automatically maps the `./data` directory for database persistence.

## Configuration

### Database Path

By default, `petcache` uses `petcache.db` in the current directory. You can specify a custom path:

```python
cache = PetCache("path/to/my/cache.db")
```

When running as a server:
- Use the `--db-path` argument: `python -m petcache --db-path /path/to/cache.db`
- Or set the `PETCACHE_DB_PATH` environment variable
- Docker containers use `/app/data/petcache.db` by default

## Examples

Check out the `examples/` directory for complete examples:

- `examples/example.py` - Basic Python API usage

Run the example:

```bash
# Basic Python API example
python examples/example.py
```

## Use Cases

- **Content Caching**: Cache API responses, web scraping results, or processed data, e.g. for [ai-data-pipelines](https://github.com/alexeygrigorev/ai-data-pipelines/)
- **Configuration Storage**: Store app configuration or user preferences
- **File Content Cache**: Cache file contents by filename for quick access
- **Development**: Store test data or fixtures
- **Prototyping**: Quick key-value storage for pet projects

## Requirements

- Python 3.10 or higher
- SQLite (included with Python)
- FastAPI (for API server)
- uvicorn (for API server)
