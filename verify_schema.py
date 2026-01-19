import sqlite3

conn = sqlite3.connect('cognitiveai.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("✓ Database tables:")
for table in tables:
    print(f"  - {table[0]}")
    
    # Get schema for each table
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"    • {col[1]} ({col[2]})")

conn.close()
print("\n✓ Verification complete!")
