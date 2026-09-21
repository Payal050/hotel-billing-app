import sqlite3
import os


DATABASE_NAME = "hotel.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row

    # Foreign keys enabled for normal database operation
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ============================================================
# CHECK TABLE COLUMNS
# ============================================================

def get_columns(cursor, table_name):
    rows = cursor.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return [row["name"] for row in rows]


# ============================================================
# ADD COLUMN IF MISSING
# ============================================================

def add_column_if_missing(
    cursor,
    table_name,
    column_name,
    definition
):
    columns = get_columns(cursor, table_name)

    if column_name not in columns:
        try:
            cursor.execute(
                f"""
                ALTER TABLE {table_name}
                ADD COLUMN {column_name} {definition}
                """
            )
        except sqlite3.OperationalError:
            pass


# ============================================================
# CHECK WHETHER RESERVATIONS TABLE HAS BAD FOREIGN KEY
# ============================================================

def reservations_has_foreign_key_problem(cursor):
    """
    Check the existing reservations table for a foreign-key
    relationship that can cause:

    foreign key mismatch -
    "reservations" referencing "customers"
    """

    try:
        rows = cursor.execute(
            "PRAGMA foreign_key_list(reservations)"
        ).fetchall()

        for row in rows:
            referenced_table = row["table"]

            if referenced_table == "customers":
                # We intentionally use a clean relationship-free
                # reservations table because the existing database
                # may contain an incompatible old FK definition.
                return True

        return False

    except Exception:
        return False


# ============================================================
# REPAIR RESERVATIONS TABLE
# ============================================================

def repair_reservations_table(connection, cursor):
    """
    Repairs an old reservations table that contains an invalid
    foreign-key relationship to customers.

    Existing reservation records are preserved whenever possible.

    The reservation module still stores customer_id, but the
    database does not enforce the broken old FK constraint.
    """

    # Table does not exist yet
    existing_tables = cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='reservations'
        """
    ).fetchone()

    if existing_tables is None:
        cursor.execute("""
            CREATE TABLE reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                customer_name TEXT NOT NULL DEFAULT '',
                phone TEXT NOT NULL DEFAULT '',
                table_id INTEGER,
                reservation_date TEXT NOT NULL DEFAULT '',
                reservation_time TEXT NOT NULL DEFAULT '',
                number_of_guests INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'Reserved',
                special_request TEXT DEFAULT '',
                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        return

    # Check old columns before migration
    old_columns = get_columns(cursor, "reservations")

    needs_repair = reservations_has_foreign_key_problem(cursor)

    # Even if no FK is reported, make sure all required columns exist.
    required_columns = {
        "customer_id",
        "customer_name",
        "phone",
        "table_id",
        "reservation_date",
        "reservation_time",
        "number_of_guests",
        "status",
        "special_request",
        "created_at"
    }

    if not needs_repair and required_columns.issubset(set(old_columns)):
        return

    print("------------------------------------------")
    print("Repairing reservations table...")
    print("------------------------------------------")

    # SQLite does not allow changing/removing a foreign-key
    # constraint directly. We therefore create a clean table.
    #
    # Foreign keys must be disabled before the migration.
    connection.commit()
    connection.execute("PRAGMA foreign_keys = OFF")

    try:

        cursor.execute("""
            CREATE TABLE reservations_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                customer_name TEXT NOT NULL DEFAULT '',
                phone TEXT NOT NULL DEFAULT '',
                table_id INTEGER,
                reservation_date TEXT NOT NULL DEFAULT '',
                reservation_time TEXT NOT NULL DEFAULT '',
                number_of_guests INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'Reserved',
                special_request TEXT DEFAULT '',
                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Copy old data column-by-column.
        #
        # This avoids errors if an older version of the database
        # did not have all columns.
        destination_columns = [
            "id",
            "customer_id",
            "customer_name",
            "phone",
            "table_id",
            "reservation_date",
            "reservation_time",
            "number_of_guests",
            "status",
            "special_request",
            "created_at"
        ]

        available_columns = [
            column
            for column in destination_columns
            if column in old_columns
        ]

        if available_columns:
            columns_sql = ", ".join(available_columns)

            cursor.execute(
                f"""
                INSERT INTO reservations_new
                ({columns_sql})
                SELECT {columns_sql}
                FROM reservations
                """
            )

        # Remove broken old table
        cursor.execute("DROP TABLE reservations")

        # Rename repaired table
        cursor.execute(
            "ALTER TABLE reservations_new RENAME TO reservations"
        )

        connection.commit()

        print("Reservations table repaired successfully.")

    except Exception:
        connection.rollback()

        # Try to remove temporary table if it exists
        try:
            cursor.execute(
                "DROP TABLE IF EXISTS reservations_new"
            )
            connection.commit()
        except Exception:
            pass

        raise

    finally:
        connection.execute("PRAGMA foreign_keys = ON")


# ============================================================
# CREATE / REPAIR DATABASE
# ============================================================

def create_tables():

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # ====================================================
        # CUSTOMERS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL DEFAULT '',

                phone TEXT NOT NULL DEFAULT '',

                email TEXT DEFAULT '',

                address TEXT DEFAULT '',

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        add_column_if_missing(
            cursor,
            "customers",
            "name",
            "TEXT DEFAULT ''"
        )

        add_column_if_missing(
            cursor,
            "customers",
            "phone",
            "TEXT DEFAULT ''"
        )

        add_column_if_missing(
            cursor,
            "customers",
            "email",
            "TEXT DEFAULT ''"
        )

        add_column_if_missing(
            cursor,
            "customers",
            "address",
            "TEXT DEFAULT ''"
        )

        add_column_if_missing(
            cursor,
            "customers",
            "created_at",
            "TIMESTAMP"
        )


        # ====================================================
        # MENU ITEMS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu_items (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                item_name TEXT NOT NULL DEFAULT '',

                category TEXT DEFAULT '',

                price REAL NOT NULL DEFAULT 0,

                description TEXT DEFAULT '',

                available INTEGER DEFAULT 1,

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        add_column_if_missing(
            cursor,
            "menu_items",
            "item_name",
            "TEXT DEFAULT ''"
        )

        add_column_if_missing(
            cursor,
            "menu_items",
            "category",
            "TEXT DEFAULT ''"
        )

        add_column_if_missing(
            cursor,
            "menu_items",
            "price",
            "REAL DEFAULT 0"
        )

        add_column_if_missing(
            cursor,
            "menu_items",
            "description",
            "TEXT DEFAULT ''"
        )

        add_column_if_missing(
            cursor,
            "menu_items",
            "available",
            "INTEGER DEFAULT 1"
        )

        add_column_if_missing(
            cursor,
            "menu_items",
            "created_at",
            "TIMESTAMP"
        )


        # ====================================================
        # RESTAURANT TABLES
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS restaurant_tables (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                table_number INTEGER NOT NULL,

                seats INTEGER NOT NULL DEFAULT 4,

                status TEXT NOT NULL DEFAULT 'Available',

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        add_column_if_missing(
            cursor,
            "restaurant_tables",
            "table_number",
            "INTEGER DEFAULT 1"
        )

        add_column_if_missing(
            cursor,
            "restaurant_tables",
            "seats",
            "INTEGER DEFAULT 4"
        )

        add_column_if_missing(
            cursor,
            "restaurant_tables",
            "status",
            "TEXT DEFAULT 'Available'"
        )

        add_column_if_missing(
            cursor,
            "restaurant_tables",
            "created_at",
            "TIMESTAMP"
        )


        # ====================================================
        # ORDERS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                bill_number TEXT NOT NULL UNIQUE,

                customer_id INTEGER,

                customer_name TEXT DEFAULT '',

                customer_phone TEXT DEFAULT '',

                table_number INTEGER DEFAULT 1,

                subtotal REAL DEFAULT 0,

                discount REAL DEFAULT 0,

                cgst REAL DEFAULT 0,

                sgst REAL DEFAULT 0,

                total REAL DEFAULT 0,

                payment_mode TEXT DEFAULT 'Cash',

                status TEXT DEFAULT 'Paid',

                order_date TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        add_column_if_missing(
            cursor,
            "orders",
            "bill_number",
            "TEXT"
        )

        add_column_if_missing(
            cursor,
            "orders",
            "customer_id",
            "INTEGER"
        )

        add_column_if_missing(
            cursor,
            "orders",
            "customer_name",
            "TEXT DEFAULT ''"
        )

        add_column_if_missing(
            cursor,
            "orders",
            "customer_phone",
            "TEXT DEFAULT ''"
        )

        add_column_if_missing(
            cursor,
            "orders",
            "table_number",
            "INTEGER DEFAULT 1"
        )

        add_column_if_missing(
            cursor,
            "orders",
            "subtotal",
            "REAL DEFAULT 0"
        )

        add_column_if_missing(
            cursor,
            "orders",
            "discount",
            "REAL DEFAULT 0"
        )

        add_column_if_missing(
            cursor,
            "orders",
            "cgst",
            "REAL DEFAULT 0"
        )

        add_column_if_missing(
            cursor,
            "orders",
            "sgst",
            "REAL DEFAULT 0"
        )

        add_column_if_missing(
            cursor,
            "orders",
            "total",
            "REAL DEFAULT 0"
        )

        add_column_if_missing(
            cursor,
            "orders",
            "payment_mode",
            "TEXT DEFAULT 'Cash'"
        )

        add_column_if_missing(
            cursor,
            "orders",
            "status",
            "TEXT DEFAULT 'Paid'"
        )

        add_column_if_missing(
            cursor,
            "orders",
            "order_date",
            "TIMESTAMP"
        )


        # ====================================================
        # ORDER ITEMS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                order_id INTEGER NOT NULL,

                item_name TEXT NOT NULL DEFAULT '',

                quantity INTEGER NOT NULL DEFAULT 1,

                price REAL NOT NULL DEFAULT 0,

                amount REAL NOT NULL DEFAULT 0
            )
        """)

        add_column_if_missing(
            cursor,
            "order_items",
            "order_id",
            "INTEGER DEFAULT 0"
        )

        add_column_if_missing(
            cursor,
            "order_items",
            "item_name",
            "TEXT DEFAULT ''"
        )

        add_column_if_missing(
            cursor,
            "order_items",
            "quantity",
            "INTEGER DEFAULT 1"
        )

        add_column_if_missing(
            cursor,
            "order_items",
            "price",
            "REAL DEFAULT 0"
        )

        add_column_if_missing(
            cursor,
            "order_items",
            "amount",
            "REAL DEFAULT 0"
        )


        # ====================================================
        # RESERVATIONS
        # ====================================================

        # IMPORTANT:
        # We DO NOT simply use CREATE TABLE IF NOT EXISTS here.
        #
        # Your existing database has an incompatible foreign key
        # involving reservations -> customers.
        #
        # repair_reservations_table() safely rebuilds the table
        # when that bad relationship exists.

        repair_reservations_table(
            connection,
            cursor
        )

        # Make sure all reservation columns exist.
        add_column_if_missing(
            cursor,
            "reservations",
            "customer_id",
            "INTEGER"
        )

        add_column_if_missing(
            cursor,
            "reservations",
            "customer_name",
            "TEXT DEFAULT ''"
        )

        add_column_if_missing(
            cursor,
            "reservations",
            "phone",
            "TEXT DEFAULT ''"
        )

        add_column_if_missing(
            cursor,
            "reservations",
            "table_id",
            "INTEGER"
        )

        add_column_if_missing(
            cursor,
            "reservations",
            "reservation_date",
            "TEXT DEFAULT ''"
        )

        add_column_if_missing(
            cursor,
            "reservations",
            "reservation_time",
            "TEXT DEFAULT ''"
        )

        add_column_if_missing(
            cursor,
            "reservations",
            "number_of_guests",
            "INTEGER DEFAULT 1"
        )

        add_column_if_missing(
            cursor,
            "reservations",
            "status",
            "TEXT DEFAULT 'Reserved'"
        )

        add_column_if_missing(
            cursor,
            "reservations",
            "special_request",
            "TEXT DEFAULT ''"
        )

        add_column_if_missing(
            cursor,
            "reservations",
            "created_at",
            "TIMESTAMP"
        )


        # ====================================================
        # DEFAULT RESTAURANT TABLES
        # ====================================================

        count = cursor.execute("""
            SELECT COUNT(*)
            FROM restaurant_tables
        """).fetchone()[0]

        if count == 0:

            default_tables = [

                (1, 4, "Available"),
                (2, 4, "Available"),
                (3, 4, "Available"),
                (4, 4, "Available"),
                (5, 4, "Available"),
                (6, 6, "Available"),
                (7, 6, "Available"),
                (8, 6, "Available"),
                (9, 8, "Available"),
                (10, 8, "Available")

            ]

            cursor.executemany("""
                INSERT INTO restaurant_tables
                (
                    table_number,
                    seats,
                    status
                )
                VALUES (?, ?, ?)
            """, default_tables)


        # ====================================================
        # FIX NULL VALUES
        # ====================================================

        cursor.execute("""
            UPDATE customers
            SET name = ''
            WHERE name IS NULL
        """)

        cursor.execute("""
            UPDATE customers
            SET phone = ''
            WHERE phone IS NULL
        """)

        cursor.execute("""
            UPDATE menu_items
            SET item_name = ''
            WHERE item_name IS NULL
        """)

        cursor.execute("""
            UPDATE menu_items
            SET category = ''
            WHERE category IS NULL
        """)

        cursor.execute("""
            UPDATE menu_items
            SET price = 0
            WHERE price IS NULL
        """)

        cursor.execute("""
            UPDATE menu_items
            SET available = 1
            WHERE available IS NULL
        """)

        cursor.execute("""
            UPDATE orders
            SET subtotal = 0
            WHERE subtotal IS NULL
        """)

        cursor.execute("""
            UPDATE orders
            SET discount = 0
            WHERE discount IS NULL
        """)

        cursor.execute("""
            UPDATE orders
            SET cgst = 0
            WHERE cgst IS NULL
        """)

        cursor.execute("""
            UPDATE orders
            SET sgst = 0
            WHERE sgst IS NULL
        """)

        cursor.execute("""
            UPDATE orders
            SET total = 0
            WHERE total IS NULL
        """)

        cursor.execute("""
            UPDATE reservations
            SET customer_name = ''
            WHERE customer_name IS NULL
        """)

        cursor.execute("""
            UPDATE reservations
            SET phone = ''
            WHERE phone IS NULL
        """)

        cursor.execute("""
            UPDATE reservations
            SET reservation_date = ''
            WHERE reservation_date IS NULL
        """)

        cursor.execute("""
            UPDATE reservations
            SET reservation_time = ''
            WHERE reservation_time IS NULL
        """)

        cursor.execute("""
            UPDATE reservations
            SET number_of_guests = 1
            WHERE number_of_guests IS NULL
        """)

        cursor.execute("""
            UPDATE reservations
            SET status = 'Reserved'
            WHERE status IS NULL
        """)


        # ====================================================
        # COMMIT
        # ====================================================

        connection.commit()

        print("==========================================")
        print(" HOTEL NILAYAM DATABASE")
        print("==========================================")
        print("Database repaired successfully.")
        print("Customers table checked.")
        print("Reservations table checked.")
        print("Reservation foreign-key issue repaired.")
        print("All required columns checked.")
        print("==========================================")


    except Exception as e:

        connection.rollback()

        print("DATABASE ERROR:")
        print(e)

        raise

    finally:

        connection.close()


# ============================================================
# RUN SETUP
# ============================================================

if __name__ == "__main__":

    create_tables()