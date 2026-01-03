from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from datetime import datetime

def init_db():
    conn = sqlite3.connect("project4.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS menu (
        menu_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        price REAL,
        description TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        street_address TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        phone_number TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        order_number TEXT,
        date_time TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT,
        menu_id INTEGER,
        quantity INTEGER
    )
    """)

    conn.commit()
    conn.close()

app = Flask(__name__)
init_db()
app.secret_key = "chaiChenakSecret"

def get_db():
    conn = sqlite3.connect("project4.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        name = request.form.get("name", "")
        category = request.form.get("category", "")
        price = request.form.get("price", 0)
        description = request.form.get("description", "")

        try:
            cur.execute("INSERT INTO menu (name, category, price, description) VALUES (?, ?, ?, ?)",
                      (name, category, float(price), description))
            conn.commit()
        except Exception as e:
            print(f"Error adding menu item: {e}")

    cur.execute("SELECT * FROM menu ORDER BY category, name")
    menu = cur.fetchall()

    cur.execute("SELECT * FROM customers")
    customers = cur.fetchall()

    conn.close()
    return render_template("admin.html", menu=menu, customers=customers)

@app.route("/start_order", methods=["GET", "POST"])
def start_order():

    if request.method == "POST":
        conn = get_db()
        cur = conn.cursor()

        customer_type = request.form.get("type")

        if customer_type == "new":
            name = request.form.get("name")
            street_address = request.form.get("street_address")
            city = request.form.get("city")
            state = request.form.get("state")
            zip_code = request.form.get("zip_code")
            phone_number = request.form.get("phone_number")

            cur.execute("INSERT INTO customers (name, street_address, city, state, zip_code, phone_number) VALUES (?, ?, ?, ?, ?, ?)",
                      (name, street_address, city, state, zip_code, phone_number))
            customer_id = cur.lastrowid
        else:
            search_by = request.form.get("search_by")
            if search_by == "id":
                customer_id = request.form.get("customer_id")
                if not customer_id:
                    conn.close()
                    return "Customer ID required. <a href='/start_order'>Try again</a>"
                cur.execute("SELECT customer_id FROM customers WHERE customer_id = ?", (customer_id,))
                row = cur.fetchone()
                if row:
                    customer_id = row["customer_id"]
                else:
                    conn.close()
                    return "Customer ID not found. <a href='/start_order'>Try again</a>"
            else:
                name = request.form.get("name")
                if not name:
                    conn.close()
                    return "Name required. <a href='/start_order'>Try again</a>"
                cur.execute("SELECT customer_id FROM customers WHERE name = ?", (name,))
                row = cur.fetchone()
                if row:
                    customer_id = row["customer_id"]
                else:
                    conn.close()
                    return "Customer not found. <a href='/start_order'>Try again</a>"

        order_number = "ABC" + datetime.now().strftime('%Y%m%d%H%M%S')
        date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cur.execute("INSERT INTO orders (customer_id, order_number, date_time) VALUES (?, ?, ?)",
                  (customer_id, order_number, date_time))
        conn.commit()

        session["order_number"] = order_number

        conn.close()
        return redirect("/order")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers")
    customers = cur.fetchall()
    conn.close()

    return render_template("start_order.html", customers=customers)

@app.route("/order", methods=["GET", "POST"])
def order():
    if "order_number" not in session:
        return redirect("/start_order")

    conn = get_db()
    cur = conn.cursor()
    order_number = session.get("order_number")

    if request.method == "POST":
        for key, value in request.form.items():
            if key.startswith("quantity_"):
                menu_id = int(key.split("_")[1])
                try:
                    quantity = int(value)
                    if quantity > 0:
                        cur.execute("INSERT INTO order_items (order_number, menu_id, quantity) VALUES (?, ?, ?)",
                                  (order_number, menu_id, quantity))
                except ValueError:
                    pass
        conn.commit()
        return redirect("/order_summary")

    cur.execute("""
        SELECT c.name FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.order_number = ?
    """, (order_number,))
    customer_result = cur.fetchone()
    customer_name = customer_result["name"] if customer_result else "Unknown Customer"

    category = request.args.get("category", "")

    if category:
        cur.execute("SELECT * FROM menu WHERE category = ? ORDER BY name", (category,))
        menu_items = cur.fetchall()
    else:
        menu_items = []

    cur.execute("""
        SELECT oi.order_item_id, m.name, m.price, oi.quantity
        FROM order_items oi
        JOIN menu m ON oi.menu_id = m.menu_id
        WHERE oi.order_number = ?
    """, (order_number,))
    order_items = cur.fetchall()

    subtotal = sum(item["price"] * item["quantity"] for item in order_items)
    conn.close()

    return render_template("order.html",
                         order_number=order_number,
                         customer_name=customer_name,
                         category=category,
                         menu_items=menu_items,
                         order_items=order_items,
                         subtotal=subtotal)

@app.route("/add_to_order", methods=["POST"])
def add_to_order():
    if "order_number" not in session:
        return redirect("/start_order")

    conn = get_db()
    cur = conn.cursor()
    order_number = session.get("order_number")

    menu_id = request.form.get("menu_id")
    quantity = request.form.get("quantity", 1)

    try:
        menu_id = int(menu_id)
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        cur.execute(
            "SELECT order_item_id, quantity FROM order_items WHERE order_number = ? AND menu_id = ?",
            (order_number, menu_id)
        )
        existing_item = cur.fetchone()

        if existing_item:
            new_quantity = existing_item["quantity"] + quantity
            cur.execute(
                "UPDATE order_items SET quantity = ? WHERE order_item_id = ?",
                (new_quantity, existing_item["order_item_id"])
            )
        else:
            cur.execute(
                "INSERT INTO order_items (order_number, menu_id, quantity) VALUES (?, ?, ?)",
                (order_number, menu_id, quantity)
            )
        conn.commit()

    except (ValueError, TypeError) as e:
        print(f"Error adding item to order: {e}")
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

    referer = request.referrer or ""
    if "category=" in referer:
        category = referer.split("category=")[-1]
        return redirect(f"/order?category={category}")
    else:
        return redirect("/order")

@app.route("/modify_item", methods=["POST"])
def modify_item():
    if "order_number" not in session:
        return redirect("/start_order")

    conn = get_db()
    cur = conn.cursor()

    try:
        item_id = int(request.form.get("item_id"))
        action = request.form.get("action")

        if action == "update":
            new_quantity = int(request.form.get("new_quantity", 1))
            if new_quantity > 0:
                cur.execute(
                    "UPDATE order_items SET quantity = ? WHERE order_item_id = ?",
                    (new_quantity, item_id)
                )
            else:
                cur.execute("DELETE FROM order_items WHERE order_item_id = ?", (item_id,))

        elif action == "remove":
            cur.execute("DELETE FROM order_items WHERE order_item_id = ?", (item_id,))

        conn.commit()

    except Exception as e:
        print(f"Error modifying order item: {e}")
    finally:
        conn.close()

    return redirect("/order")

@app.route("/order_summary", methods=["GET", "POST"])
def order_summary():
    if "order_number" not in session:
        return redirect("/start_order")

    conn = get_db()
    cur = conn.cursor()
    order_number = session.get("order_number")

    if request.method == "POST":
        coupon_type = request.form.get("coupon_type")
        coupon_value = request.form.get("coupon_value", 0)

        try:
            coupon_value = float(coupon_value)
        except ValueError:
            coupon_value = 0

        tip_percentage = request.form.get("tip_percentage")
        try:
            tip_percentage = float(tip_percentage)
        except ValueError:
            tip_percentage = 15

        delivery_option = request.form.get("delivery_option", "pickup")

        session["coupon_type"] = coupon_type
        session["coupon_value"] = coupon_value
        session["tip_percentage"] = tip_percentage
        session["delivery_option"] = delivery_option

        return redirect("/order_summary")

    cur.execute("""
        SELECT m.name, m.price, oi.quantity, (m.price * oi.quantity) AS total_price
        FROM order_items oi
        JOIN menu m ON m.menu_id = oi.menu_id
        WHERE oi.order_number = ?
    """, (order_number,))
    items = cur.fetchall()

    cur.execute("""
        SELECT c.* FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.order_number = ?
    """, (order_number,))
    customer = cur.fetchone()

    cur.execute("SELECT date_time FROM orders WHERE order_number = ?", (order_number,))
    order_date = cur.fetchone()["date_time"]

    subtotal = sum(item["total_price"] for item in items)

    coupon_type = session.get("coupon_type", "none")
    coupon_value = session.get("coupon_value", 0)
    discount = 0

    if coupon_type == "percentage" and coupon_value > 0:
        discount = subtotal * (coupon_value / 100)
    elif coupon_type == "fixed" and coupon_value > 0:
        discount = min(coupon_value, subtotal)

    amount_after_discount = subtotal - discount

    tip_percentage = session.get("tip_percentage", 15)
    tip = amount_after_discount * (tip_percentage / 100)

    tax = amount_after_discount * 0.06625

    delivery_option = session.get("delivery_option", "pickup")
    delivery_fee = 5.0 if delivery_option == "delivery" else 0.0

    total = amount_after_discount + tip + tax + delivery_fee

    customer_address = ""
    customer_name = ""
    customer_phone = ""

    if customer:
        customer_name = customer["name"]
        customer_address = f"{customer['street_address']}, {customer['city']}, {customer['state']} {customer['zip_code']}"
        customer_phone = customer["phone_number"]

    conn.close()
    return render_template("order_summary.html",
                         order_number=order_number,
                         order_date=order_date,
                         customer_name=customer_name,
                         customer_address=customer_address,
                         customer_phone=customer_phone,
                         summary=items,
                         subtotal=subtotal,
                         discount=discount,
                         amount_after_discount=amount_after_discount,
                         tip_percentage=tip_percentage,
                         tip=tip,
                         tax=tax,
                         delivery_fee=delivery_fee,
                         delivery_option=delivery_option,
                         total=total)

@app.route("/complete_order", methods=["POST"])
def complete_order():
    if "order_number" not in session:
        return redirect("/start_order")

    order_number = session.pop("order_number", None)
    session.pop("coupon_type", None)
    session.pop("coupon_value", None)
    session.pop("tip_percentage", None)
    session.pop("delivery_option", None)

    return render_template("order_complete.html", order_number=order_number)

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
