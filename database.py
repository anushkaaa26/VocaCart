"""Database layer for VocaCart."""
from __future__ import annotations

import sqlite3
from typing import Any

DB_FILE = "vocacart.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            is_organic INTEGER DEFAULT 0,
            is_seasonal INTEGER DEFAULT 0,
            season TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shopping_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            quantity REAL DEFAULT 1,
            unit TEXT DEFAULT 'item',
            product_id TEXT,
            category TEXT,
            unit_price REAL DEFAULT 0,
            status TEXT DEFAULT 'active',
            order_id INTEGER
        )
    """)

    try:
        cursor.execute("ALTER TABLE shopping_list ADD COLUMN order_id INTEGER")
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_amount REAL NOT NULL,
            items_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY DEFAULT 1,
            budget REAL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS message_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            intent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ("p1", "Classic Milk", "Dairy", 3.49, 0, 0, None),
            ("p2", "Organic Whole Milk", "Dairy", 4.99, 1, 0, None),
            ("p3", "Fresh Apples", "Produce", 2.99, 0, 1, "Fall"),
            ("p4", "Organic Honeycrisp Apples", "Produce", 4.49, 1, 1, "Fall"),
            ("p5", "Bananas", "Produce", 1.29, 0, 0, None),
            ("p6", "Whole Wheat Bread", "Pantry", 2.99, 0, 0, None),
            ("p7", "Farm Fresh Eggs", "Dairy", 3.49, 0, 0, None),
            ("p8", "Drinking Water", "Beverages", 1.99, 0, 0, None),
            ("p9", "Organic Honey", "Pantry", 8.99, 1, 0, None),
            ("p10", "Wildflower Honey", "Pantry", 5.49, 0, 0, None),
        ]
        cursor.executemany(
            "INSERT INTO products (id, name, category, price, is_organic, is_seasonal, season) VALUES (?, ?, ?, ?, ?, ?, ?)",
            sample_products,
        )

    cursor.execute("INSERT OR IGNORE INTO settings (id, budget) VALUES (1, 0)")
    conn.commit()
    conn.close()


def init_app_schema() -> None:
    """Alias for init_db to support UI schema initialization calls."""
    init_db()


def get_categories() -> list[str]:
    """Return a list of all distinct product categories in alphabetical order."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products ORDER BY category ASC")
    rows = cursor.fetchall()
    conn.close()
    return [row["category"] for row in rows]


def find_products(
    query: str = "",
    max_price: float | None = None,
    is_organic: bool | None = None,
    category: str | None = None,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM products WHERE 1=1"
    params: list[Any] = []

    if query and query.strip():
        sql += " AND (LOWER(name) LIKE ? OR LOWER(category) LIKE ?)"
        q = f"%{query.lower().strip()}%"
        params.extend([q, q])

    if category and category.strip() and category.lower() != "all":
        sql += " AND LOWER(category) = ?"
        params.append(category.lower().strip())

    if max_price is not None:
        sql += " AND price <= ?"
        params.append(float(max_price))

    if is_organic is not None and is_organic:
        sql += " AND is_organic = 1"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_products(
    category: str | None = None,
    query: str = "",
    max_price: float | None = None,
    is_organic: bool | None = None,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Fetch products matching optional filters."""
    return find_products(
        query=query,
        max_price=max_price,
        is_organic=is_organic,
        category=category,
        **kwargs,
    )


def get_product(product_id: str) -> dict[str, Any] | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def category_for(item_name: str) -> str:
    prods = find_products(item_name)
    if prods:
        return prods[0]["category"]
    return "Pantry"


def add_to_list(
    item_name: str,
    quantity: float = 1.0,
    unit: str = "item",
    product_id: str | None = None,
    category: str = "Pantry",
    unit_price: float = 0.0,
) -> dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO shopping_list (item_name, quantity, unit, product_id, category, unit_price) VALUES (?, ?, ?, ?, ?, ?)",
        (item_name, quantity, unit, product_id, category, unit_price),
    )
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return {
        "id": item_id,
        "item_name": item_name,
        "quantity": quantity,
        "unit": unit,
        "product_id": product_id,
        "category": category,
        "unit_price": unit_price,
    }


def remove_from_list(item_name: str) -> list[dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM shopping_list WHERE status = 'active' AND LOWER(item_name) LIKE ?",
        (f"%{item_name.lower()}%",),
    )
    rows = cursor.fetchall()
    removed = [dict(r) for r in rows]
    cursor.execute(
        "UPDATE shopping_list SET status = 'removed' WHERE status = 'active' AND LOWER(item_name) LIKE ?",
        (f"%{item_name.lower()}%",),
    )
    conn.commit()
    conn.close()
    return removed


def remove_list_item_by_id(item_id: int | str) -> bool:
    """Remove a specific item from the shopping list by its DB row ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE shopping_list SET status = 'removed' WHERE id = ?",
        (item_id,),
    )
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected


def update_list_item(item_name: str, quantity: float, unit: str | None = None) -> dict[str, Any] | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM shopping_list WHERE status = 'active' AND LOWER(item_name) LIKE ? ORDER BY id DESC LIMIT 1",
        (f"%{item_name.lower()}%",),
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    item = dict(row)
    new_unit = unit or item["unit"]
    cursor.execute(
        "UPDATE shopping_list SET quantity = ?, unit = ? WHERE id = ?",
        (quantity, new_unit, item["id"]),
    )
    conn.commit()
    conn.close()
    item["quantity"] = quantity
    item["unit"] = new_unit
    return item


def update_list_item_by_id(item_id: int | str, quantity: float, unit: str | None = None) -> bool:
    """Update quantity and optional unit of a shopping list item by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    if unit is not None:
        cursor.execute(
            "UPDATE shopping_list SET quantity = ?, unit = ? WHERE id = ?",
            (quantity, unit, item_id),
        )
    else:
        cursor.execute(
            "UPDATE shopping_list SET quantity = ? WHERE id = ?",
            (quantity, item_id),
        )
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected


def get_active_list() -> list[dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shopping_list WHERE status = 'active'")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_shopping_list() -> list[dict[str, Any]]:
    """Exposed for theme.py and UI module compatibility."""
    return get_active_list()


def clear_cart() -> None:
    """Clear all active items from the shopping list cart."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE shopping_list SET status = 'cleared' WHERE status = 'active'")
    conn.commit()
    conn.close()


def checkout(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Checkout active cart items, mark them completed, and insert an order record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shopping_list WHERE status = 'active'")
    items = [dict(r) for r in cursor.fetchall()]

    if not items:
        conn.close()
        return {"success": False, "message": "Cart is empty", "order_id": None, "total": 0.0}

    total_amount = sum(float(item.get("unit_price", 0) or 0) * float(item.get("quantity", 1) or 1) for item in items)
    summary = ", ".join(f"{item['quantity']}x {item['item_name']}" for item in items)

    cursor.execute(
        "INSERT INTO orders (total_amount, items_summary) VALUES (?, ?)",
        (total_amount, summary),
    )
    order_id = cursor.lastrowid
    cursor.execute(
        "UPDATE shopping_list SET status = 'completed', order_id = ? WHERE status = 'active'",
        (order_id,),
    )
    conn.commit()
    conn.close()

    return {
        "success": True,
        "order_id": order_id,
        "id": order_id,
        "total": total_amount,
        "total_amount": total_amount,
        "items": items,
        "summary": summary,
    }


def get_orders() -> list[dict[str, Any]]:
    """Fetch completed checkout orders."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_order_history() -> list[dict[str, Any]]:
    """Alias for order history UI compatibility."""
    return get_orders()


def get_transactions() -> list[dict[str, Any]]:
    """Fetch processed transaction records for Orders page."""
    return get_orders()


def get_transaction_items(order_id: int | str) -> list[dict[str, Any]]:
    """Fetch individual items tied to a specific order ID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM shopping_list WHERE order_id = ?", (order_id,))
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        cursor.execute("SELECT * FROM shopping_list WHERE status = 'completed'")
        rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_settings() -> dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM settings WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {"budget": 0.0}


def update_settings(budget: float) -> dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE settings SET budget = ? WHERE id = 1", (budget,))
    conn.commit()
    conn.close()
    return {"budget": budget}


def budget_status(budget: float | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    """Calculate budget status, providing 'spent' and 'total' keys for UI compatibility."""
    settings = get_settings()
    if budget is None and args:
        budget = args[0]
    
    if budget is None:
        budget_val = float(settings.get("budget", 0.0) or 0.0)
    else:
        try:
            budget_val = float(budget)
        except (ValueError, TypeError):
            budget_val = float(settings.get("budget", 0.0) or 0.0)

    items = get_active_list()
    spent = sum(float(item.get("unit_price", 0) or 0) * float(item.get("quantity", 1) or 1) for item in items)
    remaining = budget_val - spent
    is_over = spent > budget_val if budget_val > 0 else False

    return {
        "budget": budget_val,
        "spent": spent,
        "total": spent,  # Added to fix KeyError in Cart and Checkout pages
        "remaining": remaining,
        "over_budget": is_over,
        "is_over_budget": is_over,
        "status": "over_budget" if is_over else "ok",
        "percent_used": (spent / budget_val * 100) if budget_val > 0 else 0.0,
    }

def record_message(role: str, content: str, intent: str = "unknown") -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO message_history (role, content, intent) VALUES (?, ?, ?)",
        (role, content, intent),
    )
    conn.commit()
    conn.close()


init_db()