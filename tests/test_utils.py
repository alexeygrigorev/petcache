"""Test utilities for database testing with transactional isolation."""

import sqlite3
from contextlib import contextmanager

from petcache import PetCache


class TransactionalConnection:
    """A connection wrapper that prevents commits and enables rollback.
    
    This class wraps SQLite connections to provide Django-style transactional
    isolation for tests. All commits are prevented, and transactions can be
    rolled back to ensure test isolation.
    """
    
    def __init__(self, real_conn):
        self.real_conn = real_conn
        self._in_transaction = True
        
    def execute(self, sql, *args, **kwargs):
        return self.real_conn.execute(sql, *args, **kwargs)
    
    def executemany(self, sql, *args, **kwargs):
        return self.real_conn.executemany(sql, *args, **kwargs)
    
    def commit(self):
        # Prevent commits during test - we'll rollback at the end
        pass
    
    def rollback(self):
        return self.real_conn.rollback()
    
    def close(self):
        return self.real_conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Don't commit on context exit
        pass
    
    def __getattr__(self, name):
        # Delegate other attributes to the real connection
        return getattr(self.real_conn, name)


@contextmanager
def transactional_cache(db_path, cache_class=PetCache):
    """Context manager that provides a cache with transactional isolation.
    
    Similar to Django's transaction.atomic(), this ensures each test
    runs in its own transaction that gets rolled back at the end.
    
    Args:
        db_path: Path to the database file
        cache_class: The cache class to instantiate (e.g., PetCache)
        
    Yields:
        A cache instance with transactional isolation
    """
    # Initialize database schema first
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
    
    # Set up the transactional connection
    real_conn = sqlite3.connect(db_path)
    real_conn.execute("BEGIN")
    
    # Create a transactional wrapper
    trans_conn = TransactionalConnection(real_conn)
    
    # Temporarily replace sqlite3.connect to return our transactional connection
    original_connect = sqlite3.connect
    
    def transactional_connect(path, *args, **kwargs):
        if path == db_path:
            return trans_conn
        # For other paths, create a properly managed connection
        conn = original_connect(path, *args, **kwargs)
        return conn
    
    sqlite3.connect = transactional_connect
    
    try:
        # Create cache after patching sqlite3.connect
        cache = cache_class(db_path=db_path)
        yield cache
    finally:
        # Always rollback to ensure test isolation
        try:
            real_conn.rollback()
        except sqlite3.OperationalError:
            pass  # Transaction might not be active
        real_conn.close()
        # Restore original connect function
        sqlite3.connect = original_connect