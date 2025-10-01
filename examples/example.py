"""Example usage of petcache."""

from petcache import PetCache

def main():
    # Create a cache instance
    cache = PetCache("example.db")
    
    print("=== petcache Example ===\n")
    
    # Store some text
    print("1. Storing values...")
    cache.set("document.txt", "This is my document content")
    cache.set("code.py", "def hello(): print('world')")
    cache.set("notes.md", "# My Notes\n\nSome important notes here")
    print(f"   Stored 3 items\n")
    
    # Retrieve a value
    print("2. Retrieving a value...")
    content = cache.get("document.txt")
    print(f"   document.txt: {content}\n")
    
    # List all keys
    print("3. Listing all keys...")
    keys = cache.list_keys()
    print(f"   Keys: {keys}\n")
    
    # Check if key exists
    print("4. Checking if key exists...")
    print(f"   'document.txt' in cache: {'document.txt' in cache}")
    print(f"   'missing.txt' in cache: {'missing.txt' in cache}\n")
    
    # Export to JSON
    print("5. Exporting to JSON...")
    cache.export_to_json("cache_backup.json", indent=2)
    print(f"   Exported to cache_backup.json\n")
    
    # Clear and import
    print("6. Clearing cache...")
    cache.clear()
    print(f"   Cache size: {len(cache)}\n")
    
    print("7. Importing from JSON...")
    count = cache.import_from_json("cache_backup.json")
    print(f"   Imported {count} items")
    print(f"   Cache size: {len(cache)}\n")
    
    # Show cache info
    print("8. Cache info:")
    print(f"   {cache}\n")
    
    print("=== Example Complete ===")

if __name__ == "__main__":
    main()
