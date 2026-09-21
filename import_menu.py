import pandas as pd
from database import get_connection

CSV_PATH = "dataset/hotel_nilayam_baner_menu_dataset.csv"


def import_menu():

    print("Reading Hotel Nilayam menu dataset...")

    df = pd.read_csv(CSV_PATH)

    connection = get_connection()
    cursor = connection.cursor()

    imported = 0

    for _, row in df.iterrows():

        try:

            item_name = str(row["item"]).strip()

            if not item_name or item_name.lower() == "nan":
                continue

            price = float(row["price"])

            food_type = str(
                row["veg or non-veg"]
            ).strip()

            category = str(
                row["menu"]
            ).strip()

            cursor.execute("""
                INSERT INTO menu_items
                (item_name, category, food_type, price)
                VALUES (?, ?, ?, ?)
            """, (
                item_name,
                category,
                food_type,
                price
            ))

            imported += 1

        except Exception as e:
            print("Skipped row:", e)

    connection.commit()
    connection.close()

    print("--------------------------------")
    print(f"Successfully imported {imported} menu items.")
    print("Hotel Nilayam menu is now stored in database.")


if __name__ == "__main__":
    import_menu()