import sqlite3

connection = sqlite3.connect("database/hotel.db")
cursor = connection.cursor()

print("\nTABLES IN DATABASE:")
tables = cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

print(tables)

print("\nMENU ITEM COUNT:")

try:
    count = cursor.execute(
        "SELECT COUNT(*) FROM menu_items"
    ).fetchone()[0]

    print(count)

except Exception as e:
    print("ERROR:", e)

connection.close()