import sqlite3
from datetime import datetime

schema = """
CREATE TABLE menu (
    menu_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT
);

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    street_address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    phone_number TEXT
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    order_number TEXT UNIQUE NOT NULL,
    date_time TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT NOT NULL,
    menu_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (order_number) REFERENCES orders(order_number),
    FOREIGN KEY (menu_id) REFERENCES menu(menu_id)
);
"""

conn = sqlite3.connect("project4.db")
cursor = conn.cursor()

cursor.executescript(schema)
print("Database schema created.")

def insert_menu_items(conn):
    cursor = conn.cursor()

    appetizers = {
        "Aloo Samosa (2 Pcs)": (5.00, "Crispy pastry filled with spiced potatoes"),
        "Dal Kachori (2 Pcs)": (6.00, "Fried pastry filled with spiced lentils"),
        "Samosa Chaat": (8.00, "Samosa topped with chickpeas, yogurt, and chutneys"),
        "Channa Papri Chat": (8.00, "Crispy wafers with chickpeas, potatoes, yogurt and chutneys"),
        "Dahi Puri Chat": (8.00, "Hollow crispy puris filled with potatoes, yogurt and chutneys"),
        "Gol Gappay / Pani Puri": (8.00, "Hollow puris filled with flavored water, potatoes and chickpeas"),
        "Chicken Chatpata": (9.00, "Spicy chicken appetizer with tangy flavors"),
        "Finger Fish": (10.00, "Fish fingers with special spices")
    }

    entrees = {
        "Bhuna Bun Kabab (Chicken)": (10.00, "Spiced chicken patty served in a bun"),
        "Bhuna Bun Kabab (Dal)": (8.00, "Spiced lentil patty served in a bun"),
        "Anday Wala Burger (Chicken)": (12.00, "Chicken burger with egg"),
        "Anday Wala Burger (Dal)": (10.00, "Lentil burger with egg"),
        "Chai Chenak Beef Burger": (10.00, "Special beef burger with house sauce"),
        "Chai Chenak Chicken Burger": (8.00, "Special chicken burger with house sauce"),
        "Chicken Tikka Club Sandwich": (12.00, "Triple-decker sandwich with chicken tikka")
    }

    desserts = {
        "Special Badshahi Falooda": (11.00, "Traditional dessert drink with vermicelli, basil seeds, and ice cream"),
        "Special Mango Falooda": (12.00, "Mango-flavored dessert drink with vermicelli"),
        "Kulfa Ice Cream": (6.00, "Traditional Indian ice cream with pistachios"),
        "Mango Ice Cream": (6.00, "Creamy mango-flavored ice cream"),
        "Kulfi Dandiwali": (5.00, "Traditional frozen dairy dessert on a stick")
    }

    beverages = {
        "Doodh Patti Chai": (3.00, "Strong milk tea"),
        "Kashmiri Chai": (4.00, "Pink tea with cardamom and nuts"),
        "Masala Chai": (4.00, "Spiced tea with ginger and cardamom"),
        "Zafrani Chai": (5.00, "Saffron-infused tea"),
        "Coffee Chai": (5.00, "Coffee-flavored tea")
    }

    fries = {
        "Karachi Matka Fries (Chicken)": (10.00, "Fries topped with chicken and special spices"),
        "Curly Fries": (5.00, "Spiral-cut fried potatoes"),
        "Masala Curly Fries": (5.00, "Spiced spiral-cut fried potatoes"),
        "Chicken Nuggets & Fries": (8.00, "Chicken nuggets served with fries"),
        "Chicken Fingers & Fries": (9.00, "Breaded chicken strips with fries")
    }

    rolls = {
        "Chicken Tikka Mayo Roll": (8.00, "Chicken tikka with mayo in flatbread"),
        "Chicken Garlic Mayo Roll": (8.00, "Chicken with garlic mayo in flatbread"),
        "Chicken Tikka Chutni Roll": (8.00, "Chicken tikka with chutney in flatbread"),
        "Chicken Tikka Cheese Roll": (9.00, "Chicken tikka with cheese in flatbread"),
        "Chicken Tikka Chingari Roll": (9.00, "Spicy chicken tikka roll")
    }

    soft_drinks = {
        "Water Bottle": (2.00, "Bottled water"),
        "Soft Drink": (2.00, "Carbonated beverage"),
        "Pakola": (4.00, "Pakistani cream soda"),
        "Lychee Pakola": (4.00, "Lychee-flavored Pakistani soda"),
        "Mint Shikanji": (5.00, "Mint-flavored lemonade")
    }

    for name, (price, description) in appetizers.items():
        cursor.execute(
            "INSERT INTO menu (name, category, price, description) VALUES (?, ?, ?, ?)",
            (name, "Appetizer", price, description)
        )

    for name, (price, description) in entrees.items():
        cursor.execute(
            "INSERT INTO menu (name, category, price, description) VALUES (?, ?, ?, ?)",
            (name, "Entree", price, description)
        )

    for name, (price, description) in desserts.items():
        cursor.execute(
            "INSERT INTO menu (name, category, price, description) VALUES (?, ?, ?, ?)",
            (name, "Dessert", price, description)
        )

    for name, (price, description) in beverages.items():
        cursor.execute(
            "INSERT INTO menu (name, category, price, description) VALUES (?, ?, ?, ?)",
            (name, "Beverage", price, description)
        )

    for name, (price, description) in fries.items():
        cursor.execute(
            "INSERT INTO menu (name, category, price, description) VALUES (?, ?, ?, ?)",
            (name, "Fries", price, description)
        )

    for name, (price, description) in rolls.items():
        cursor.execute(
            "INSERT INTO menu (name, category, price, description) VALUES (?, ?, ?, ?)",
            (name, "Rolls", price, description)
        )

    for name, (price, description) in soft_drinks.items():
        cursor.execute(
            "INSERT INTO menu (name, category, price, description) VALUES (?, ?, ?, ?)",
            (name, "Soft Drinks", price, description)
        )

    conn.commit()
    print("Menu items inserted successfully!")

cursor.execute(
    """INSERT INTO customers (name, street_address, city, state, zip_code, phone_number)
       VALUES (?, ?, ?, ?, ?, ?)""",
    ("Noorulain Balouch", "123 Main St", "Jersey City", "NJ", "07306", "(201) 555-1234")
)

insert_menu_items(conn)

conn.commit()
conn.close()
print("Database initialized with menu items and one test customer.")
