"""Tests for the core cache functionality."""

import json
import os
import tempfile
import pytest

from petcache import PetCache
from .test_utils import transactional_cache


@pytest.fixture
def cache(tmp_path_factory):
    """Create a cache instance with transactional isolation."""
    db_path = str(tmp_path_factory.mktemp("data") / "test_cache.db")
    with transactional_cache(db_path) as cache_instance:
        yield cache_instance


def test_cache_initialization(cache):
    """Test cache initialization."""
    assert cache.db_path is not None
    assert len(cache) == 0


def test_set_and_get(cache):
    """Test setting and getting values."""
    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"


def test_get_nonexistent_key(cache):
    """Test getting a nonexistent key."""
    assert cache.get("nonexistent") is None


def test_delete(cache):
    """Test deleting a key."""
    cache.set("key_to_delete", "value")
    assert cache.delete("key_to_delete") is True
    assert cache.get("key_to_delete") is None


def test_delete_nonexistent_key(cache):
    """Test deleting a nonexistent key."""
    assert cache.delete("nonexistent") is False


def test_list_keys(cache):
    """Test listing all keys."""
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    
    keys = cache.list_keys()
    assert len(keys) == 3
    assert "key1" in keys
    assert "key2" in keys
    assert "key3" in keys


def test_list_all(cache):
    """Test listing all key-value pairs."""
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    
    entries = cache.list_all()
    assert len(entries) == 2
    assert ("key1", "value1") in entries
    assert ("key2", "value2") in entries


def test_clear(cache):
    """Test clearing the cache."""
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    
    count = cache.clear()
    assert count == 3
    assert len(cache) == 0


def test_len(cache):
    """Test the length of the cache."""
    assert len(cache) == 0
    
    cache.set("key1", "value1")
    assert len(cache) == 1
    
    cache.set("key2", "value2")
    assert len(cache) == 2
    
    cache.delete("key1")
    assert len(cache) == 1


def test_contains(cache):
    """Test the 'in' operator."""
    cache.set("existing_key", "value")
    
    assert "existing_key" in cache
    assert "nonexistent_key" not in cache


def test_update_value(cache):
    """Test updating an existing value."""
    cache.set("key", "old_value")
    assert cache.get("key") == "old_value"
    
    cache.set("key", "new_value")
    assert cache.get("key") == "new_value"


def test_filename_as_key(cache):
    """Test using filenames as keys."""
    cache.set("document.txt", "This is a document")
    cache.set("/path/to/file.py", "Python code here")
    cache.set("folder/subfolder/file.md", "Markdown content")
    
    assert cache.get("document.txt") == "This is a document"
    assert cache.get("/path/to/file.py") == "Python code here"
    assert cache.get("folder/subfolder/file.md") == "Markdown content"


def test_export_to_dict(cache):
    """Test exporting cache to a dictionary."""
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    
    data = cache.export_to_dict()
    assert data == {"key1": "value1", "key2": "value2"}


def test_export_to_json(cache):
    """Test exporting cache to a JSON file."""
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix=".json", delete=False) as f:
        json_path = f.name
    
    try:
        cache.export_to_json(json_path)
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        assert data == {"key1": "value1", "key2": "value2"}
    finally:
        os.remove(json_path)


def test_import_from_dict(cache):
    """Test importing cache from a dictionary."""
    data = {"key1": "value1", "key2": "value2", "key3": "value3"}
    count = cache.import_from_dict(data)
    
    assert count == 3
    assert cache.get("key1") == "value1"
    assert cache.get("key2") == "value2"
    assert cache.get("key3") == "value3"


def test_import_from_dict_with_clear(cache):
    """Test importing with clear_first option."""
    cache.set("old_key", "old_value")
    
    data = {"key1": "value1", "key2": "value2"}
    count = cache.import_from_dict(data, clear_first=True)
    
    assert count == 2
    assert cache.get("old_key") is None
    assert cache.get("key1") == "value1"


def test_import_from_json(cache):
    """Test importing cache from a JSON file."""
    data = {"key1": "value1", "key2": "value2"}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix=".json", delete=False) as f:
        json.dump(data, f)
        json_path = f.name
    
    try:
        count = cache.import_from_json(json_path)
        
        assert count == 2
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
    finally:
        os.remove(json_path)


def test_export_import_roundtrip(cache):
    """Test exporting and importing the same data."""
    original_data = {
        "file1.txt": "Content 1",
        "file2.py": "Python code",
        "notes.md": "Markdown notes"
    }
    
    cache.import_from_dict(original_data)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix=".json", delete=False) as f:
        json_path = f.name
    
    try:
        cache.export_to_json(json_path)
        
        # Create new temporary cache and import
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as db_f:
            new_db_path = db_f.name
            
            try:
                new_cache = PetCache(db_path=new_db_path)
                new_cache.import_from_json(json_path)
            
                exported = new_cache.export_to_dict()
                assert exported == original_data
            finally:
                try:
                    os.remove(new_db_path)
                except (PermissionError, FileNotFoundError):
                    pass
        
    finally:
        # Clean up JSON file
        try:
            os.remove(json_path)
        except (PermissionError, FileNotFoundError):
            pass


def test_repr(cache):
    """Test the string representation."""
    cache.set("key1", "value1")
    repr_str = repr(cache)
    assert "PetCache" in repr_str
    assert cache.db_path in repr_str
    assert "entries=1" in repr_str


def test_unicode_values(cache):
    """Test storing unicode text."""
    cache.set("unicode_key", "Hello 世界 🌍 Привет")
    assert cache.get("unicode_key") == "Hello 世界 🌍 Привет"


def test_multiline_values(cache):
    """Test storing multiline text."""
    multiline_text = """Line 1
Line 2
Line 3"""
    cache.set("multiline", multiline_text)
    assert cache.get("multiline") == multiline_text


def test_empty_value(cache):
    """Test storing empty string."""
    cache.set("empty", "")
    assert cache.get("empty") == ""
