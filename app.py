from flask import Flask, render_template, render_template_string, request, jsonify, redirect, url_for, session
from database import get_connection, create_tables
import re
from datetime import datetime


# ============================================================
# APPLICATION
# ============================================================

app = Flask(__name__)

app.secret_key = "hotel_nilayam_secret_key"


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

create_tables()


# ============================================================
# LOGIN
# ============================================================

@app.route("/", methods=["GET"])
def login_page():

    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    username = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    ).strip()


    if username == "admin" and password == "admin123":

        session["logged_in"] = True
        session["username"] = username

        return redirect(
            url_for("home")
        )


    return render_template(
        "login.html",
        error="Invalid username or password."
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login_page")
    )


# ============================================================
# HOME / DASHBOARD
# ============================================================

@app.route("/home")
def home():

    if not session.get("logged_in"):

        return redirect(
            url_for("login_page")
        )


    return render_template(
        "home.html"
    )


# ============================================================
# POS BILLING
# ============================================================

@app.route("/pos")
def pos():

    if not session.get("logged_in"):

        return redirect(
            url_for("login_page")
        )


    connection = get_connection()
    cursor = connection.cursor()


    try:

        menu_items = cursor.execute("""
            SELECT *
            FROM menu_items
            WHERE available = 1
            ORDER BY category, item_name
        """).fetchall()


        categories = cursor.execute("""
            SELECT DISTINCT category
            FROM menu_items
            WHERE category IS NOT NULL
            AND category != ''
            ORDER BY category
        """).fetchall()


    except Exception as e:

        connection.close()

        return f"""
        <h2>POS Database Error</h2>
        <p>{e}</p>
        """


    connection.close()


    return render_template(
        "pos.html",
        menu_items=menu_items,
        categories=[
            row["category"]
            for row in categories
        ]
    )


# ============================================================
# MENU MANAGEMENT
# ============================================================

@app.route("/menu")
def menu_management():

    if not session.get("logged_in"):

        return redirect(
            url_for("login_page")
        )


    connection = get_connection()
    cursor = connection.cursor()


    try:

        menu_items = cursor.execute("""
            SELECT *
            FROM menu_items
            ORDER BY category, item_name
        """).fetchall()


    except Exception as e:

        connection.close()

        return f"""
        <h2>Menu Database Error</h2>
        <p>{e}</p>
        """


    connection.close()


    return render_template(
        "menu.html",
        menu_items=menu_items
    )


# ============================================================
# MENU ENDPOINT ALIAS
# ============================================================

# Keeps compatibility with templates that use:
# url_for("menu")

app.add_url_rule(
    "/menu",
    endpoint="menu",
    view_func=menu_management
)


# ============================================================
# CUSTOMERS
# ============================================================

@app.route("/customers")
def customers():

    if not session.get("logged_in"):

        return redirect(
            url_for("login_page")
        )


    connection = get_connection()
    cursor = connection.cursor()


    try:

        customers_list = cursor.execute("""
            SELECT *
            FROM customers
            ORDER BY id DESC
        """).fetchall()


    except Exception as e:

        connection.close()

        return f"""
        <h2>Customer Database Error</h2>
        <p>{e}</p>
        """


    connection.close()


    return render_template(
        "customers.html",
        customers=customers_list
    )


# ============================================================
# ADD CUSTOMER
# ============================================================

@app.route("/customers/add", methods=["POST"])
def add_customer():

    if not session.get("logged_in"):

        return jsonify({
            "success": False,
            "message": "Please login first."
        })


    data = request.get_json(silent=True) or {}


    if not data:

        return jsonify({
            "success": False,
            "message": "No customer data received."
        })


    name = data.get(
        "name",
        ""
    ).strip()

    phone = str(data.get(
        "phone",
        ""
    )).strip()

    email = data.get(
        "email",
        ""
    ).strip()

    address = data.get(
        "address",
        ""
    ).strip()


    if not name:

        return jsonify({
            "success": False,
            "message": "Customer name is required."
        })


    if not re.fullmatch(
        r"[6-9][0-9]{9}",
        phone
    ):

        return jsonify({
            "success": False,
            "message":
                "Enter a valid 10-digit Indian mobile number."
        })


    connection = get_connection()
    cursor = connection.cursor()


    try:

        existing = cursor.execute("""
            SELECT id
            FROM customers
            WHERE phone = ?
        """, (
            phone,
        )).fetchone()


        if existing:

            return jsonify({
                "success": False,
                "message":
                    "A customer with this phone number already exists."
            })


        cursor.execute("""
            INSERT INTO customers
            (
                name,
                phone,
                email,
                address
            )
            VALUES (?, ?, ?, ?)
        """, (
            name,
            phone,
            email,
            address
        ))


        connection.commit()


        return jsonify({
            "success": True,
            "message":
                "Customer added successfully."
        })


    except Exception as e:

        connection.rollback()


        return jsonify({
            "success": False,
            "message": str(e)
        })


    finally:

        connection.close()


# ============================================================
# UPDATE CUSTOMER
# ============================================================

@app.route("/customers/update", methods=["POST"])
def update_customer():

    if not session.get("logged_in"):

        return jsonify({
            "success": False,
            "message": "Please login first."
        })


    data = request.get_json(silent=True) or {}


    customer_id = data.get("id")

    name = data.get(
        "name",
        ""
    ).strip()

    phone = data.get(
        "phone",
        ""
    ).strip()

    email = data.get(
        "email",
        ""
    ).strip()

    address = data.get(
        "address",
        ""
    ).strip()


    if not customer_id:

        return jsonify({
            "success": False,
            "message":
                "Customer ID is missing."
        })


    if not name:

        return jsonify({
            "success": False,
            "message":
                "Customer name is required."
        })


    if not re.fullmatch(
        r"[6-9][0-9]{9}",
        phone
    ):

        return jsonify({
            "success": False,
            "message":
                "Enter a valid 10-digit Indian mobile number."
        })


    connection = get_connection()
    cursor = connection.cursor()


    try:

        existing = cursor.execute("""
            SELECT id
            FROM customers
            WHERE phone = ?
            AND id != ?
        """, (
            phone,
            customer_id
        )).fetchone()


        if existing:

            return jsonify({
                "success": False,
                "message":
                    "Another customer already uses this phone number."
            })


        cursor.execute("""
            UPDATE customers
            SET
                name = ?,
                phone = ?,
                email = ?,
                address = ?
            WHERE id = ?
        """, (
            name,
            phone,
            email,
            address,
            customer_id
        ))


        connection.commit()


        return jsonify({
            "success": True,
            "message":
                "Customer updated successfully."
        })


    except Exception as e:

        connection.rollback()


        return jsonify({
            "success": False,
            "message": str(e)
        })


    finally:

        connection.close()


# ============================================================
# DELETE CUSTOMER
# ============================================================

@app.route("/customers/delete", methods=["POST"])
def delete_customer():

    if not session.get("logged_in"):

        return jsonify({
            "success": False,
            "message": "Please login first."
        })


    data = request.get_json(silent=True) or {}

    customer_id = data.get("id")


    if not customer_id:

        return jsonify({
            "success": False,
            "message":
                "Customer ID is missing."
        })


    connection = get_connection()
    cursor = connection.cursor()


    try:

        cursor.execute("""
            DELETE FROM customers
            WHERE id = ?
        """, (
            customer_id,
        ))


        connection.commit()


        return jsonify({
            "success": True,
            "message":
                "Customer deleted successfully."
        })


    except Exception as e:

        connection.rollback()


        return jsonify({
            "success": False,
            "message": str(e)
        })


    finally:

        connection.close()


# ============================================================
# SAVE CUSTOMER FROM BILLING
# ============================================================

@app.route("/save_customer", methods=["POST"])
def save_customer():

    if not session.get("logged_in"):

        return jsonify({
            "success": False,
            "message":
                "Please login first."
        })


    data = request.get_json(silent=True) or {}


    name = data.get(
        "name",
        ""
    ).strip()

    phone = data.get(
        "phone",
        ""
    ).strip()


    if not name:

        return jsonify({
            "success": False,
            "message":
                "Customer name is required."
        })


    if not re.fullmatch(
        r"[6-9][0-9]{9}",
        phone
    ):

        return jsonify({
            "success": False,
            "message":
                "Enter a valid 10-digit Indian mobile number."
        })


    connection = get_connection()
    cursor = connection.cursor()


    try:

        existing = cursor.execute("""
            SELECT id
            FROM customers
            WHERE phone = ?
        """, (
            phone,
        )).fetchone()


        if existing:

            customer_id = existing["id"]


            cursor.execute("""
                UPDATE customers
                SET name = ?
                WHERE id = ?
            """, (
                name,
                customer_id
            ))


        else:

            cursor.execute("""
                INSERT INTO customers
                (
                    name,
                    phone
                )
                VALUES (?, ?)
            """, (
                name,
                phone
            ))


            customer_id = cursor.lastrowid


        connection.commit()


        return jsonify({
            "success": True,
            "customer_id":
                customer_id,
            "message":
                "Customer saved successfully."
        })


    except Exception as e:

        connection.rollback()


        return jsonify({
            "success": False,
            "message": str(e)
        })


    finally:

        connection.close()


# ============================================================
# CUSTOMER HISTORY
# ============================================================

@app.route("/customers/<int:customer_id>/history")
def customer_history(customer_id):
    if not session.get("logged_in"):
        return redirect(url_for("login_page"))

    connection = get_connection()
    cursor = connection.cursor()
    try:
        customer = cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
        if not customer:
            return "Customer not found", 404

        bills = cursor.execute("SELECT * FROM orders WHERE customer_id = ? ORDER BY order_date DESC, id DESC", (customer_id,)).fetchall()
        reservations_list = cursor.execute("""
            SELECT r.*, t.table_number
            FROM reservations r
            LEFT JOIN restaurant_tables t ON r.table_id = t.id
            WHERE r.customer_id = ?
            ORDER BY r.reservation_date DESC, r.reservation_time DESC, r.id DESC
        """, (customer_id,)).fetchall()
    except Exception as e:
        return f"<h2>Customer History Error</h2><p>{e}</p>", 500
    finally:
        connection.close()

    return render_template_string("""
    <!DOCTYPE html><html><head><title>Customer History</title>
    <style>body{font-family:Arial;background:#f4f7fb;margin:0;color:#14213d}.top{background:#111827;color:white;padding:18px 30px}.page{padding:30px;max-width:1200px;margin:auto}.card{background:white;padding:24px;border-radius:16px;box-shadow:0 8px 25px rgba(0,0,0,.07);margin-bottom:20px}table{width:100%;border-collapse:collapse}th{background:#111827;color:white;padding:12px;text-align:left}td{padding:12px;border-bottom:1px solid #e5e7eb}a{color:#2563eb;text-decoration:none}</style></head><body>
    <div class="top">🏨 HOTEL NILAYAM — CUSTOMER HISTORY</div><div class="page">
    <p><a href="/customers">← Back to Customers</a></p>
    <div class="card"><h1>{{ customer["name"] }}</h1><p>📞 {{ customer["phone"] }}</p><p>✉️ {{ customer["email"] or "-" }}</p><p>📍 {{ customer["address"] or "-" }}</p></div>
    <div class="card"><h2>Billing History</h2><table><tr><th>Bill</th><th>Table</th><th>Total</th><th>Payment</th><th>Date</th></tr>{% for b in bills %}<tr><td>{{ b["bill_number"] }}</td><td>{{ b["table_number"] }}</td><td>₹{{ "%.2f"|format(b["total"] or 0) }}</td><td>{{ b["payment_mode"] }}</td><td>{{ b["order_date"] }}</td></tr>{% else %}<tr><td colspan="5">No bills found.</td></tr>{% endfor %}</table></div>
    <div class="card"><h2>Reservation History</h2><table><tr><th>Date</th><th>Time</th><th>Table</th><th>Guests</th><th>Status</th></tr>{% for r in reservations %}<tr><td>{{ r["reservation_date"] }}</td><td>{{ r["reservation_time"] }}</td><td>{{ r["table_number"] }}</td><td>{{ r["number_of_guests"] }}</td><td>{{ r["status"] }}</td></tr>{% else %}<tr><td colspan="5">No reservations found.</td></tr>{% endfor %}</table></div>
    </div></body></html>
    """, customer=customer, bills=bills, reservations=reservations_list)


# ============================================================
# TABLE MANAGEMENT
# ============================================================

@app.route("/tables")
def tables():

    if not session.get("logged_in"):

        return redirect(
            url_for("login_page")
        )


    connection = get_connection()
    cursor = connection.cursor()


    try:

        tables_list = cursor.execute("""
            SELECT *
            FROM restaurant_tables
            ORDER BY table_number
        """).fetchall()


    except Exception as e:

        connection.close()

        return f"""
        <h2>Table Database Error</h2>
        <p>{e}</p>
        """


    connection.close()


    return render_template(
        "tables.html",
        tables=tables_list
    )


# ============================================================
# ADD TABLE
# ============================================================

@app.route("/tables/add", methods=["POST"])
def add_table():

    if not session.get("logged_in"):

        return jsonify({
            "success": False,
            "message":
                "Please login first."
        })


    data = request.get_json(silent=True) or {}


    table_number = data.get(
        "table_number"
    )

    seats = data.get(
        "seats"
    )


    if not table_number or not seats:

        return jsonify({
            "success": False,
            "message":
                "Table number and seats are required."
        })


    connection = get_connection()
    cursor = connection.cursor()


    try:

        existing = cursor.execute("""
            SELECT id
            FROM restaurant_tables
            WHERE table_number = ?
        """, (
            table_number,
        )).fetchone()


        if existing:

            return jsonify({
                "success": False,
                "message":
                    "This table number already exists."
            })


        cursor.execute("""
            INSERT INTO restaurant_tables
            (
                table_number,
                seats,
                status
            )
            VALUES (?, ?, ?)
        """, (
            table_number,
            seats,
            "Available"
        ))


        connection.commit()


        return jsonify({
            "success": True,
            "message":
                "Table added successfully."
        })


    except Exception as e:

        connection.rollback()


        return jsonify({
            "success": False,
            "message": str(e)
        })


    finally:

        connection.close()


# ============================================================
# UPDATE TABLE
# ============================================================

@app.route("/tables/update", methods=["POST"])
def update_table():

    if not session.get("logged_in"):

        return jsonify({
            "success": False,
            "message":
                "Please login first."
        })


    data = request.get_json(silent=True) or {}


    table_id = data.get("id")

    table_number = data.get(
        "table_number"
    )

    seats = data.get(
        "seats"
    )


    if not table_id:

        return jsonify({
            "success": False,
            "message":
                "Table ID is missing."
        })


    connection = get_connection()
    cursor = connection.cursor()


    try:

        existing = cursor.execute("""
            SELECT id
            FROM restaurant_tables
            WHERE table_number = ?
            AND id != ?
        """, (
            table_number,
            table_id
        )).fetchone()


        if existing:

            return jsonify({
                "success": False,
                "message":
                    "Another table already uses this number."
            })


        cursor.execute("""
            UPDATE restaurant_tables
            SET
                table_number = ?,
                seats = ?
            WHERE id = ?
        """, (
            table_number,
            seats,
            table_id
        ))


        connection.commit()


        return jsonify({
            "success": True,
            "message":
                "Table updated successfully."
        })


    except Exception as e:

        connection.rollback()


        return jsonify({
            "success": False,
            "message": str(e)
        })


    finally:

        connection.close()


# ============================================================
# CHANGE TABLE STATUS
# ============================================================

@app.route("/tables/status", methods=["POST"])
def update_table_status():

    if not session.get("logged_in"):

        return jsonify({
            "success": False,
            "message":
                "Please login first."
        })


    data = request.get_json(silent=True) or {}


    table_id = data.get("id")

    status = data.get(
        "status"
    )


    allowed_statuses = [
        "Available",
        "Occupied",
        "Reserved"
    ]


    if status not in allowed_statuses:

        return jsonify({
            "success": False,
            "message":
                "Invalid table status."
        })


    connection = get_connection()
    cursor = connection.cursor()


    try:

        cursor.execute("""
            UPDATE restaurant_tables
            SET status = ?
            WHERE id = ?
        """, (
            status,
            table_id
        ))


        connection.commit()


        return jsonify({
            "success": True,
            "message":
                "Table status updated successfully."
        })


    except Exception as e:

        connection.rollback()


        return jsonify({
            "success": False,
            "message": str(e)
        })


    finally:

        connection.close()


# ============================================================
# DELETE TABLE
# ============================================================

@app.route("/tables/delete", methods=["POST"])
def delete_table():

    if not session.get("logged_in"):

        return jsonify({
            "success": False,
            "message":
                "Please login first."
        })


    data = request.get_json(silent=True) or {}

    table_id = data.get("id")


    if not table_id:

        return jsonify({
            "success": False,
            "message":
                "Table ID is missing."
        })


    connection = get_connection()
    cursor = connection.cursor()


    try:

        cursor.execute("""
            DELETE FROM restaurant_tables
            WHERE id = ?
        """, (
            table_id,
        ))


        connection.commit()


        return jsonify({
            "success": True,
            "message":
                "Table deleted successfully."
        })


    except Exception as e:

        connection.rollback()


        return jsonify({
            "success": False,
            "message": str(e)
        })


    finally:

        connection.close()


# ============================================================
# RESERVATIONS
# ============================================================

@app.route("/reservations", methods=["GET", "POST"])
def reservations():

    # Some older reservation forms submit directly to /reservations.
    # Keep GET for the page and safely accept POST as well.
    if request.method == "POST":
        return add_reservation()

    if not session.get("logged_in"):

        return redirect(
            url_for("login_page")
        )


    connection = get_connection()
    cursor = connection.cursor()


    try:

        reservations_list = cursor.execute("""
            SELECT
                reservations.*,
                restaurant_tables.table_number
            FROM reservations
            LEFT JOIN restaurant_tables
                ON reservations.table_id =
                   restaurant_tables.id
            ORDER BY
                reservation_date ASC,
                reservation_time ASC
        """).fetchall()


        available_tables = cursor.execute("""
            SELECT *
            FROM restaurant_tables
            WHERE status = 'Available'
            ORDER BY table_number
        """).fetchall()


    except Exception as e:

        connection.close()

        return f"""
        <h2>Reservation Database Error</h2>
        <p>{e}</p>
        """


    connection.close()


    return render_template(
        "reservations.html",

        reservations=reservations_list,

        available_tables=available_tables
    )


# ============================================================
# ADD RESERVATION
# ============================================================

@app.route("/reservations/add", methods=["POST"])
@app.route("/create_reservation", methods=["POST"])
@app.route("/add_reservation", methods=["POST"])
def add_reservation():

    if not session.get("logged_in"):

        return jsonify({
            "success": False,
            "message":
                "Please login first."
        })


    data = request.get_json(silent=True) or request.form.to_dict() or {}


    customer_name = data.get(
        "customer_name",
        data.get("name", "")
    ).strip()

    phone = data.get(
        "phone",
        ""
    ).strip()

    reservation_date = str(data.get(
        "reservation_date",
        data.get("date", "")
    )).strip()

    reservation_time = str(data.get(
        "reservation_time",
        data.get("time", "")
    )).strip()

    number_of_guests = data.get(
        "number_of_guests",
        data.get("guests")
    )

    table_id = data.get(
        "table_id",
        data.get("table")
    )

    special_request = data.get(
        "special_request",
        ""
    ).strip()


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not customer_name:

        return jsonify({
            "success": False,
            "message":
                "Customer name is required."
        })


    if not re.fullmatch(
        r"[6-9][0-9]{9}",
        phone
    ):

        return jsonify({
            "success": False,
            "message":
                "Enter a valid 10-digit mobile number."
        })


    if not reservation_date:

        return jsonify({
            "success": False,
            "message":
                "Reservation date is required."
        })


    if not reservation_time:

        return jsonify({
            "success": False,
            "message":
                "Reservation time is required."
        })


    if not table_id:

        return jsonify({
            "success": False,
            "message":
                "Please select a table."
        })


    try:

        number_of_guests = int(
            number_of_guests
        )

    except:

        return jsonify({
            "success": False,
            "message":
                "Invalid number of guests."
        })


    if number_of_guests <= 0:

        return jsonify({
            "success": False,
            "message":
                "Number of guests must be at least 1."
        })


    connection = get_connection()
    cursor = connection.cursor()


    try:

        # ----------------------------------------------------
        # CHECK TABLE
        # ----------------------------------------------------

        table = cursor.execute("""
            SELECT *
            FROM restaurant_tables
            WHERE id = ?
        """, (
            table_id,
        )).fetchone()


        if not table:

            return jsonify({
                "success": False,
                "message":
                    "Selected table does not exist."
            })


        # ----------------------------------------------------
        # CHECK TABLE CAPACITY
        # ----------------------------------------------------

        if number_of_guests > table["seats"]:

            return jsonify({
                "success": False,
                "message":
                    f"Table {table['table_number']} "
                    f"has only {table['seats']} seats."
            })


        # ----------------------------------------------------
        # CHECK TABLE STATUS
        # ----------------------------------------------------

        if table["status"] != "Available":

            return jsonify({
                "success": False,
                "message":
                    f"Table {table['table_number']} "
                    f"is currently {table['status']}."
            })


        # ----------------------------------------------------
        # CHECK EXISTING RESERVATION
        # ----------------------------------------------------

        existing_reservation = cursor.execute("""
            SELECT id
            FROM reservations
            WHERE table_id = ?

            AND reservation_date = ?

            AND reservation_time = ?

            AND status = 'Reserved'
        """, (
            table_id,
            reservation_date,
            reservation_time
        )).fetchone()


        if existing_reservation:

            return jsonify({
                "success": False,
                "message":
                    "This table is already reserved "
                    "for this date and time."
            })


        # ----------------------------------------------------
        # FIND / CREATE CUSTOMER
        # ----------------------------------------------------

        customer = cursor.execute("""
            SELECT id
            FROM customers
            WHERE phone = ?
        """, (
            phone,
        )).fetchone()


        if customer:

            customer_id = customer["id"]


            cursor.execute("""
                UPDATE customers
                SET name = ?
                WHERE id = ?
            """, (
                customer_name,
                customer_id
            ))


        else:

            cursor.execute("""
                INSERT INTO customers
                (
                    name,
                    phone
                )
                VALUES (?, ?)
            """, (
                customer_name,
                phone
            ))


            customer_id = cursor.lastrowid


        # ----------------------------------------------------
        # CREATE RESERVATION
        # ----------------------------------------------------

        cursor.execute("""
            INSERT INTO reservations
            (
                customer_id,
                customer_name,
                phone,
                table_id,
                reservation_date,
                reservation_time,
                number_of_guests,
                status,
                special_request
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_id,
            customer_name,
            phone,
            table_id,
            reservation_date,
            reservation_time,
            number_of_guests,
            "Reserved",
            special_request
        ))


        # ----------------------------------------------------
        # CHANGE TABLE STATUS
        # ----------------------------------------------------

        cursor.execute("""
            UPDATE restaurant_tables
            SET status = 'Reserved'
            WHERE id = ?
        """, (
            table_id,
        ))


        connection.commit()


        return jsonify({
            "success": True,
            "message":
                "Reservation created successfully."
        })


    except Exception as e:

        connection.rollback()


        return jsonify({
            "success": False,
            "message": str(e)
        })


    finally:

        connection.close()


# ============================================================
# UPDATE RESERVATION STATUS
# ============================================================

@app.route("/reservations/status", methods=["POST"])
@app.route("/update_reservation_status/<int:reservation_id>", methods=["POST"])
@app.route("/reservation/update_status/<int:reservation_id>", methods=["POST"])
def update_reservation_status(reservation_id=None):

    if not session.get("logged_in"):

        return jsonify({
            "success": False,
            "message":
                "Please login first."
        })


    data = request.get_json(silent=True) or {}


    reservation_id = reservation_id or data.get(
        "id"
    )

    new_status = data.get(
        "status"
    ) or request.form.get("status")


    allowed_statuses = [
        "Reserved",
        "Completed",
        "Cancelled"
    ]


    if new_status not in allowed_statuses:

        return jsonify({
            "success": False,
            "message":
                "Invalid reservation status."
        })


    connection = get_connection()
    cursor = connection.cursor()


    try:

        reservation = cursor.execute("""
            SELECT *
            FROM reservations
            WHERE id = ?
        """, (
            reservation_id,
        )).fetchone()


        if not reservation:

            return jsonify({
                "success": False,
                "message":
                    "Reservation not found."
            })


        # ----------------------------------------------------
        # UPDATE RESERVATION
        # ----------------------------------------------------

        cursor.execute("""
            UPDATE reservations
            SET status = ?
            WHERE id = ?
        """, (
            new_status,
            reservation_id
        ))


        # ----------------------------------------------------
        # UPDATE TABLE STATUS
        # ----------------------------------------------------

        if new_status == "Reserved":

            table_status = "Reserved"

        else:

            table_status = "Available"


        cursor.execute("""
            UPDATE restaurant_tables
            SET status = ?
            WHERE id = ?
        """, (
            table_status,
            reservation["table_id"]
        ))


        connection.commit()


        if new_status == "Completed":

            message = (
                "Reservation completed. "
                "Table is now available."
            )

        elif new_status == "Cancelled":

            message = (
                "Reservation cancelled. "
                "Table is now available."
            )

        else:

            message = (
                "Reservation status updated."
            )


        return jsonify({
            "success": True,
            "message": message
        })


    except Exception as e:

        connection.rollback()


        return jsonify({
            "success": False,
            "message": str(e)
        })


    finally:

        connection.close()


# ============================================================
# RESERVATION STATUS URL COMPATIBILITY
# ============================================================

@app.route("/reservation_status", methods=["GET", "POST"], endpoint="reservation_status")
@app.route("/reservation_status/<int:reservation_id>", methods=["GET", "POST"], endpoint="reservation_status")
@app.route("/reservation-status/<int:reservation_id>/<status>", methods=["GET", "POST"], endpoint="reservation_status")
def reservation_status_alias(reservation_id=None, status=None):
    """Compatibility endpoint for reservation templates.

    Supports both old GET links and POST forms, including templates that
    call url_for('reservation_status') without an id.
    """
    if not session.get("logged_in"):
        return redirect(url_for("login_page"))

    data = request.get_json(silent=True) or request.form.to_dict() or {}

    if reservation_id is None:
        reservation_id = data.get("reservation_id") or data.get("id")
        if reservation_id:
            try:
                reservation_id = int(reservation_id)
            except (TypeError, ValueError):
                return jsonify({"success": False, "message": "Invalid reservation ID."}), 400

    status = status or data.get("status") or request.args.get("status")

    # This form is also used by older templates only to generate an endpoint.
    # Returning a harmless JSON response prevents BuildError/Method Not Allowed.
    if reservation_id is None:
        return jsonify({
            "success": True,
            "message": "Reservation status endpoint is available."
        })

    connection = get_connection()
    cursor = connection.cursor()
    try:
        reservation = cursor.execute(
            "SELECT * FROM reservations WHERE id = ?",
            (reservation_id,)
        ).fetchone()

        if not reservation:
            return jsonify({
                "success": False,
                "message": "Reservation not found."
            }), 404

        if status is None:
            return jsonify({
                "success": True,
                "reservation": dict(reservation)
            })

        allowed_statuses = ["Reserved", "Confirmed", "Completed", "Cancelled"]
        if status not in allowed_statuses:
            return jsonify({
                "success": False,
                "message": "Invalid reservation status."
            }), 400

        cursor.execute(
            "UPDATE reservations SET status = ? WHERE id = ?",
            (status, reservation_id)
        )

        table_status = "Reserved" if status in ["Reserved", "Confirmed"] else "Available"
        cursor.execute(
            "UPDATE restaurant_tables SET status = ? WHERE id = ?",
            (table_status, reservation["table_id"])
        )

        connection.commit()

        # AJAX/JSON requests get JSON; normal old links get redirected.
        if request.method == "POST" or request.is_json:
            return jsonify({
                "success": True,
                "message": "Reservation status updated successfully."
            })

    except Exception as e:
        connection.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
    finally:
        connection.close()

    return redirect(url_for("reservations"))


# ============================================================

# ============================================================

@app.route("/generate_bill", methods=["POST"])
def generate_bill():

    if not session.get("logged_in"):

        return jsonify({
            "success": False,
            "message":
                "Please login first."
        })


    data = request.get_json(silent=True) or {}


    if not data:

        return jsonify({
            "success": False,
            "message":
                "No bill data received."
        })


    customer_name = data.get(
        "customer_name",
        ""
    ).strip()

    customer_phone = data.get(
        "customer_phone",
        ""
    ).strip()

    table_number = data.get(
        "table_number",
        1
    )

    items = data.get(
        "items",
        []
    )

    payment_mode = data.get(
        "payment_mode",
        "Cash"
    )


    if not customer_name:

        return jsonify({
            "success": False,
            "message":
                "Please enter customer name."
        })


    if not re.fullmatch(
        r"[6-9][0-9]{9}",
        customer_phone
    ):

        return jsonify({
            "success": False,
            "message":
                "Please enter a valid mobile number."
        })


    if not items:

        return jsonify({
            "success": False,
            "message":
                "Cart is empty."
        })


    # --------------------------------------------------------
    # CALCULATE BILL
    # --------------------------------------------------------

    subtotal = 0


    for item in items:

        quantity = int(
            item["quantity"]
        )

        price = float(
            item["price"]
        )

        amount = (
            quantity *
            price
        )

        item["amount"] = amount

        subtotal += amount


    discount = 0


    taxable_amount = (
        subtotal -
        discount
    )


    cgst = (
        taxable_amount *
        0.025
    )

    sgst = (
        taxable_amount *
        0.025
    )


    total = (
        taxable_amount +
        cgst +
        sgst
    )


    connection = get_connection()
    cursor = connection.cursor()


    try:

        # ----------------------------------------------------
        # FIND CUSTOMER
        # ----------------------------------------------------

        customer = cursor.execute("""
            SELECT *
            FROM customers
            WHERE phone = ?
        """, (
            customer_phone,
        )).fetchone()


        if customer:

            customer_id = customer["id"]


            cursor.execute("""
                UPDATE customers
                SET name = ?
                WHERE id = ?
            """, (
                customer_name,
                customer_id
            ))


        else:

            cursor.execute("""
                INSERT INTO customers
                (
                    name,
                    phone
                )
                VALUES (?, ?)
            """, (
                customer_name,
                customer_phone
            ))


            customer_id = cursor.lastrowid


        # ----------------------------------------------------
        # BILL NUMBER
        # ----------------------------------------------------

        bill_number = (
            "NILAYAM-"
            +
            datetime.now().strftime(
                "%Y%m%d%H%M%S"
            )
        )


        # ----------------------------------------------------
        # INSERT ORDER
        # ----------------------------------------------------

        cursor.execute("""
            INSERT INTO orders
            (
                bill_number,
                customer_id,
                customer_name,
                customer_phone,
                table_number,
                subtotal,
                discount,
                cgst,
                sgst,
                total,
                payment_mode,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bill_number,
            customer_id,
            customer_name,
            customer_phone,
            table_number,
            subtotal,
            discount,
            cgst,
            sgst,
            total,
            payment_mode,
            "Paid"
        ))


        order_id = cursor.lastrowid


        # ----------------------------------------------------
        # INSERT ORDER ITEMS
        # ----------------------------------------------------

        for item in items:

            cursor.execute("""
                INSERT INTO order_items
                (
                    order_id,
                    item_name,
                    quantity,
                    price,
                    amount
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                order_id,
                item["name"],
                item["quantity"],
                item["price"],
                item["amount"]
            ))


        # ----------------------------------------------------
        # IF TABLE IS USED FOR BILLING
        # MAKE IT AVAILABLE AGAIN
        # ----------------------------------------------------

        try:

            cursor.execute("""
                UPDATE restaurant_tables
                SET status = 'Available'
                WHERE table_number = ?
            """, (
                table_number,
            ))

        except:

            pass


        connection.commit()


        return jsonify({
            "success": True,
            "bill_number":
                bill_number,
            "order_id":
                order_id,
            "total":
                round(total, 2)
        })


    except Exception as e:

        connection.rollback()


        return jsonify({
            "success": False,
            "message": str(e)
        })


    finally:

        connection.close()


# ============================================================
# BILL DISPLAY
# ============================================================

@app.route("/bill/<int:order_id>")
def bill(order_id):

    if not session.get("logged_in"):

        return redirect(
            url_for("login_page")
        )


    connection = get_connection()
    cursor = connection.cursor()


    try:

        order = cursor.execute("""
            SELECT *
            FROM orders
            WHERE id = ?
        """, (
            order_id,
        )).fetchone()


        if not order:

            connection.close()

            return "Bill not found", 404


        items = cursor.execute("""
            SELECT *
            FROM order_items
            WHERE order_id = ?
        """, (
            order_id,
        )).fetchall()


    except Exception as e:

        connection.close()

        return f"""
        <h2>Bill Error</h2>
        <p>{e}</p>
        """


    connection.close()


    return render_template(
        "bill.html",
        order=order,
        items=items
    )


# ============================================================
# BILL HISTORY COMPATIBILITY
# ============================================================

@app.route("/bill-history", endpoint="bill_history")
@app.route("/bill-history-alias", endpoint="bill_history_alias")
def bill_history_compat():
    return redirect(url_for("history"))


# ============================================================
# BILL HISTORY
# ============================================================

@app.route("/history")
def history():

    if not session.get("logged_in"):

        return redirect(
            url_for("login_page")
        )


    connection = get_connection()
    cursor = connection.cursor()


    try:

        bills = cursor.execute("""
            SELECT *
            FROM orders
            ORDER BY order_date DESC
        """).fetchall()


    except Exception as e:

        connection.close()

        return f"""
        <h2>Bill History Error</h2>
        <p>{e}</p>
        """


    connection.close()


    return render_template(
        "history.html",
        bills=bills
    )


# ============================================================
# BILLS
# ============================================================

@app.route("/bills")
def bills():

    return redirect(
        url_for("history")
    )


# ============================================================
# BILL DETAILS
# ============================================================

@app.route("/bill_details/<int:order_id>")
def bill_details(order_id):

    return redirect(
        url_for(
            "bill",
            order_id=order_id
        )
    )


# ============================================================
# REPORTS
# ============================================================

@app.route("/reports")
def reports():

    if not session.get("logged_in"):

        return redirect(
            url_for("login_page")
        )


    connection = get_connection()
    cursor = connection.cursor()


    try:

        total_bills = cursor.execute("""
            SELECT COUNT(*)
            FROM orders
        """).fetchone()[0]


        total_sales = cursor.execute("""
            SELECT COALESCE(
                SUM(total),
                0
            )
            FROM orders
        """).fetchone()[0]


        today_sales = cursor.execute("""
            SELECT COALESCE(
                SUM(total),
                0
            )
            FROM orders
            WHERE DATE(order_date)
                = DATE('now')
        """).fetchone()[0]


        today_bills = cursor.execute("""
            SELECT COUNT(*)
            FROM orders
            WHERE DATE(order_date)
                = DATE('now')
        """).fetchone()[0]


        popular_items = cursor.execute("""
            SELECT
                item_name,
                SUM(quantity) AS quantity
            FROM order_items
            GROUP BY item_name
            ORDER BY quantity DESC
            LIMIT 10
        """).fetchall()


        payment_data = cursor.execute("""
            SELECT
                payment_mode,
                COUNT(*) AS count,
                COALESCE(
                    SUM(total),
                    0
                ) AS amount
            FROM orders
            GROUP BY payment_mode
        """).fetchall()


    except Exception as e:

        connection.close()

        return f"""
        <h2>Reports Error</h2>
        <p>{e}</p>
        """


    connection.close()


    return render_template(
        "reports.html",

        total_bills=total_bills,

        total_sales=total_sales,

        today_sales=today_sales,

        today_bills=today_bills,

        popular_items=popular_items,

        payment_data=payment_data
    )
@app.route("/about")
def about():
    if not session.get("logged_in"):
        return redirect(url_for("login_page"))

    return render_template("about.html")

# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )