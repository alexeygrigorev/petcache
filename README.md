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
# Using make
make run

# Or directly with uvicorn
uvicorn petcache.api:app --reload
```

The API will be available at `http://localhost:8000`

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

### Available Commands

```bash
make help          # Show all available commands
make install       # Install dependencies
make test          # Run tests
make test-cov      # Run tests with coverage report
make run           # Run the FastAPI application
make dev           # Run in development mode (0.0.0.0:8000)
make clean         # Clean up generated files
make example       # Run example script
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

## Configuration

### Database Path

By default, `petcache` uses `petcache.db` in the current directory. You can specify a custom path:

```python
cache = PetCache("path/to/my/cache.db")
```

For the API server, set the `PETCACHE_DB_PATH` environment variable:

```bash
export PETCACHE_DB_PATH=/path/to/cache.db
uvicorn petcache.api:app
```

## Use Cases

- **Content Caching**: Cache API responses, web scraping results, or processed data
- **Configuration Storage**: Store app configuration or user preferences
- **File Content Cache**: Cache file contents by filename for quick access
- **Development**: Store test data or fixtures
- **Prototyping**: Quick key-value storage for pet projects

## Requirements

- Python 3.10 or higher
- SQLite (included with Python)
- FastAPI (for API server)
- uvicorn (for API server)

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- SQLite - Reliable embedded database
