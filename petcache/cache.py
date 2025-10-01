"""Core cache implementation using SQLite."""

import json
import sqlite3
from typing import Optional, Dict, List, Tuple


class PetCache:
    """Simple persistent text cache using SQLite."""
    
    def __init__(self, db_path: str = "petcache.db"):
        """Initialize the cache with a database path.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS update_timestamp
                AFTER UPDATE ON cache
                FOR EACH ROW
                BEGIN
                    UPDATE cache SET updated_at = CURRENT_TIMESTAMP
                    WHERE key = NEW.key;
                END
            """)
            conn.commit()
    
    def set(self, key: str, value: str) -> None:
        """Set a key-value pair in the cache.
        
        Args:
            key: The key (can be a filename or any string)
            value: The text value to store
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, value) VALUES (?, ?)",
                (key, value)
            )
            conn.commit()
    
    def get(self, key: str) -> Optional[str]:
        """Get a value from the cache.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The cached value or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value FROM cache WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            return row[0] if row else None
    
    def delete(self, key: str) -> bool:
        """Delete a key from the cache.
        
        Args:
            key: The key to delete
            
        Returns:
            True if the key was deleted, False if it didn't exist
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM cache WHERE key = ?",
                (key,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def list_keys(self) -> List[str]:
        """List all keys in the cache.
        
        Returns:
            List of all keys
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT key FROM cache ORDER BY key")
            return [row[0] for row in cursor.fetchall()]
    
    def list_all(self) -> List[Tuple[str, str]]:
        """List all key-value pairs in the cache.
        
        Returns:
            List of (key, value) tuples
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT key, value FROM cache ORDER BY key")
            return cursor.fetchall()
    
    def clear(self) -> int:
        """Clear all entries from the cache.
        
        Returns:
            Number of entries deleted
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM cache")
            conn.commit()
            return cursor.rowcount
    
    def export_to_dict(self) -> Dict[str, str]:
        """Export all cache entries to a dictionary.
        
        Returns:
            Dictionary with all key-value pairs
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT key, value FROM cache")
            return {key: value for key, value in cursor.fetchall()}
    
    def export_to_json(self, output_path: str, indent: int = 2) -> None:
        """Export cache to a JSON file (git-friendly format).
        
        Args:
            output_path: Path to the output JSON file
            indent: JSON indentation for readability
        """
        data = self.export_to_dict()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, sort_keys=True)
    
    def import_from_dict(self, data: Dict[str, str], clear_first: bool = False) -> int:
        """Import cache entries from a dictionary.
        
        Args:
            data: Dictionary with key-value pairs
            clear_first: If True, clear existing cache before import
            
        Returns:
            Number of entries imported
        """
        if clear_first:
            self.clear()
        
        count = 0
        for key, value in data.items():
            self.set(key, value)
            count += 1
        
        return count
    
    def import_from_json(self, input_path: str, clear_first: bool = False) -> int:
        """Import cache from a JSON file.
        
        Args:
            input_path: Path to the input JSON file
            clear_first: If True, clear existing cache before import
            
        Returns:
            Number of entries imported
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return self.import_from_dict(data, clear_first=clear_first)
    
    def __len__(self) -> int:
        """Return the number of entries in the cache."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            return cursor.fetchone()[0]
    
    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        return self.get(key) is not None
    
    def __repr__(self) -> str:
        """Return a string representation of the cache."""
        return f"PetCache(db_path='{self.db_path}', entries={len(self)})"
    
    def close(self) -> None:
        """Explicitly close any cached connections (for compatibility)."""
        # SQLite connections are automatically closed with context managers
        # This method is provided for explicit cleanup if needed
        pass
    
    def __del__(self) -> None:
        """Cleanup when the object is destroyed."""
        try:
            self.close()
        except Exception:
            pass  # Ignore errors during cleanup
