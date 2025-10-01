"""FastAPI application for petcache."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict
import os

from .cache import PetCache
from .__version__ import __version__


class CacheItem(BaseModel):
    """Model for a cache item."""
    key: str
    value: str


class CacheValue(BaseModel):
    """Model for just a value."""
    value: str


class ImportData(BaseModel):
    """Model for import data."""
    data: Dict[str, str]
    clear_first: bool = False


def create_app(db_path: str = None) -> FastAPI:
    """Create a FastAPI application with the specified database path.
    
    Args:
        db_path: Path to the SQLite database file. If None, uses environment variable
                or default "petcache.db"
    
    Returns:
        Configured FastAPI application
    """
    if db_path is None:
        db_path = os.environ.get("PETCACHE_DB_PATH", "petcache.db")
    
    # Initialize cache with the specified database path
    cache = PetCache(db_path=db_path)
    
    app = FastAPI(
        title="petcache",
        description="Simple persistent cache for texts for your pet projects",
        version=__version__,
    )

    @app.get("/")
    def root():
        """Root endpoint."""
        return {
            "message": "petcache API",
            "version": __version__,
            "endpoints": {
                "get": "GET /cache/{key}",
                "set": "POST /cache",
                "delete": "DELETE /cache/{key}",
                "list": "GET /cache",
                "clear": "DELETE /cache",
                "export": "GET /export",
                "import": "POST /import"
            }
        }

    @app.get("/cache/{key}")
    def get_value(key: str):
        """Get a value from the cache."""
        value = cache.get(key)
        if value is None:
            raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
        return {"key": key, "value": value}

    @app.post("/cache")
    def set_value(item: CacheItem):
        """Set a value in the cache."""
        cache.set(item.key, item.value)
        return {"message": "Value set successfully", "key": item.key}

    @app.delete("/cache/{key}")
    def delete_value(key: str):
        """Delete a value from the cache."""
        if cache.delete(key):
            return {"message": f"Key '{key}' deleted successfully"}
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found")

    @app.get("/cache")
    def list_cache():
        """List all entries in the cache."""
        entries = cache.list_all()
        return {
            "count": len(entries),
            "entries": [{"key": key, "value": value} for key, value in entries]
        }

    @app.delete("/cache")
    def clear_cache():
        """Clear all entries from the cache."""
        count = cache.clear()
        return {"message": "Cache cleared successfully", "deleted": count}

    @app.get("/export")
    def export_cache():
        """Export all cache entries as JSON."""
        data = cache.export_to_dict()
        return JSONResponse(content=data)

    @app.post("/import")
    def import_cache(import_data: ImportData):
        """Import cache entries from JSON data."""
        count = cache.import_from_dict(import_data.data, clear_first=import_data.clear_first)
        return {"message": "Import successful", "imported": count}

    @app.get("/health")
    def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "entries": len(cache),
            "db_path": cache.db_path
        }
    
    return app


# Default app instance for backward compatibility
app = create_app()
