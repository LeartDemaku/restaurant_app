from datetime import datetime
from typing import List, Dict, Any, Optional
from .db import get_db_connection


# ==========================================
# 1. KATEGORITË DHE MENYJA
# ==========================================

def get_categories() -> List[Dict[str, Any]]:
    """Merr të gjitha kategoritë nga baza e të dhënave."""
    conn = get_db_connection()
    categories = conn.execute(
        "SELECT * FROM categories ORDER BY display_order ASC, id ASC"
    ).fetchall()
    conn.close()
    return [dict(c) for c in categories]


def get_menu_items(category_id: Optional[int] = None, active_only: bool = True) -> List[Dict[str, Any]]:
    """Merr artikujt e menysë, me mundësi filtrimi sipas kategorisë."""
    conn = get_db_connection()
    query = """
        SELECT m.*, c.name as category_name, c.color as category_color 
        FROM menu_items m
        JOIN categories c ON m.category_id = c.id
        WHERE 1=1
    """
    params = []
    if active_only:
        query += " AND m.is_active = 1"
    if category_id is not None:
        query += " AND m.category_id = ?"
        params.append(category_id)

    query += " ORDER BY c.display_order ASC, m.name ASC"
    items = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(item) for item in items]


def get_menu_item_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    """Gjen një artikull sipas ID-së."""
    conn = get_db_connection()
    item = conn.execute(
        "SELECT m.*, c.name as category_name FROM menu_items m JOIN categories c ON m.category_id = c.id WHERE m.id = ?",
        (item_id,)
    ).fetchone()
    conn.close()
    return dict(item) if item else None


def add_menu_item(name: str, category_id: int, price: float, stock_quantity: int = 100, description: str = "") -> int:
    """Shton një artikull të ri në meny."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO menu_items (name, category_id, price, stock_quantity, description, is_active)
           VALUES (?, ?, ?, ?, ?, 1)""",
        (name.strip(), category_id, price, stock_quantity, description.strip())
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def update_menu_item(item_id: int, name: str, category_id: int, price: float, stock_quantity: int, description: str = "") -> bool:
    """Përditëson të dhënat e një artikulli ekzistues."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE menu_items 
           SET name = ?, category_id = ?, price = ?, stock_quantity = ?, description = ?
           WHERE id = ?""",
        (name.strip(), category_id, price, stock_quantity, description.strip(), item_id)
    )
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    return rows > 0


def delete_menu_item(item_id: int) -> bool:
    """Çaktivizon (ose fshin) një artikull nga menyja."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE menu_items SET is_active = 0 WHERE id = ?", (item_id,))
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    return rows > 0


# ==========================================
# 2. TAVOLINAT DHE STAFI
# ==========================================

def get_tables() -> List[Dict[str, Any]]:
    """Merr listën e të gjitha tavolinave bashkë me statusin e tyre aktual dhe faturën aktive nëse ka."""
    conn = get_db_connection()
    tables = conn.execute("SELECT * FROM restaurant_tables ORDER BY table_number ASC").fetchall()
    result = []
    for t in tables:
        t_dict = dict(t)
        # Gjejmë nëse ka ndonjë porosi aktive të papaguar për këtë tavolinë
        active_order = conn.execute(
            """SELECT id, total_amount, waiter_name, created_at 
               FROM orders 
               WHERE table_number = ? AND status != 'E Përfunduar' AND status != 'Anuluar'
               ORDER BY id DESC LIMIT 1""",
            (t_dict["table_number"],)
        ).fetchone()

        if active_order:
            t_dict["active_order"] = dict(active_order)
            t_dict["status"] = "e_zene"
        else:
            t_dict["active_order"] = None
            if t_dict["status"] == "e_zene":
                t_dict["status"] = "e_lire"

        result.append(t_dict)
    conn.close()
    return result


def update_table_status(table_number: int, status: str) -> bool:
    """Ndryshon statusin e një tavoline ('e_lire', 'e_zene', 'e_rezervuar')."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE restaurant_tables SET status = ? WHERE table_number = ?", (status, table_number))
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    return rows > 0


def get_staff_list() -> List[Dict[str, Any]]:
    """Merr listën e stafit (kamarierë, kuzhina, menaxherë)."""
    conn = get_db_connection()
    staff = conn.execute("SELECT id, name, role, pin_code, is_active FROM staff WHERE is_active = 1 ORDER BY name ASC").fetchall()
    conn.close()
    return [dict(s) for s in staff]


# ==========================================
# 3. POROSITË DHE ARTIKUJT E POROSISË
# ==========================================

def create_order(table_number: int, waiter_name: str, items: List[Dict[str, Any]], notes: str = "", payment_method: str = "Kesh") -> int:
    """
    Krijon një porosi të re.
    items është listë e formatit: [{'id': item_id, 'name': emri, 'price': cmimi, 'quantity': sasia, 'notes': shenime}]
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    total_amount = sum(float(item["price"]) * int(item["quantity"]) for item in items)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """INSERT INTO orders (table_number, waiter_name, status, created_at, updated_at, payment_method, total_amount, notes)
           VALUES (?, ?, 'E Re', ?, ?, ?, ?, ?)""",
        (table_number, waiter_name, now_str, now_str, payment_method, round(total_amount, 2), notes)
    )
    order_id = cursor.lastrowid

    # Shtojmë artikujt individualë
    for item in items:
        item_id = item.get("id")
        item_name = item.get("name", "Artikull")
        unit_price = float(item.get("price", 0.0))
        quantity = int(item.get("quantity", 1))
        subtotal = round(unit_price * quantity, 2)
        item_notes = item.get("notes", "")

        cursor.execute(
            """INSERT INTO order_items (order_id, item_id, item_name, unit_price, quantity, subtotal, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (order_id, item_id, item_name, unit_price, quantity, subtotal, item_notes)
        )

        # Ulim sasinë në stok nëse artikulli ka ID të vlefshme
        if item_id:
            cursor.execute(
                "UPDATE menu_items SET stock_quantity = MAX(0, stock_quantity - ?) WHERE id = ?",
                (quantity, item_id)
            )

    # Tavolinën e shënojmë si të zënë
    cursor.execute("UPDATE restaurant_tables SET status = 'e_zene' WHERE table_number = ?", (table_number,))

    conn.commit()
    conn.close()
    return order_id


def get_orders(status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """Merr listën e porosive bashkë me artikujt e tyre."""
    conn = get_db_connection()
    query = "SELECT * FROM orders WHERE 1=1"
    params = []

    if status and status != "Të Gjitha":
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    orders = conn.execute(query, params).fetchall()
    result = []

    for o in orders:
        o_dict = dict(o)
        items = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (o_dict["id"],)).fetchall()
        o_dict["items"] = [dict(i) for i in items]
        result.append(o_dict)

    conn.close()
    return result


def get_order_by_id(order_id: int) -> Optional[Dict[str, Any]]:
    """Gjen një porosi sipas ID-së bashkë me të gjithë artikujt e saj."""
    conn = get_db_connection()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        conn.close()
        return None

    o_dict = dict(order)
    items = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
    o_dict["items"] = [dict(i) for i in items]
    conn.close()
    return o_dict


def update_order_status(order_id: int, new_status: str) -> bool:
    """Ndryshon statusin e një porosie ('E Re', 'Në Përgatitje', 'Gati', 'E Përfunduar', 'Anuluar')."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "UPDATE orders SET status = ?, updated_at = ? WHERE id = ?",
        (new_status, now_str, order_id)
    )

    # Nëse porosia përfundohet ose anulohet, lirojmë tavolinën nëse nuk ka porosi të tjera aktive
    if new_status in ("E Përfunduar", "Anuluar"):
        order = conn.execute("SELECT table_number FROM orders WHERE id = ?", (order_id,)).fetchone()
        if order:
            table_no = order["table_number"]
            # Kontrollojmë a ka porosi tjetër aktive për këtë tavolinë
            active_other = conn.execute(
                "SELECT id FROM orders WHERE table_number = ? AND status NOT IN ('E Përfunduar', 'Anuluar') AND id != ?",
                (table_no, order_id)
            ).fetchone()
            if not active_other:
                cursor.execute("UPDATE restaurant_tables SET status = 'e_lire' WHERE table_number = ?", (table_no,))

    conn.commit()
    rows = cursor.rowcount
    conn.close()
    return rows > 0


def complete_and_pay_order(order_id: int, payment_method: str = "Kesh") -> Optional[str]:
    """Përfundon porosinë, regjistron faturën dhe kthen numrin e faturës."""
    conn = get_db_connection()
    cursor = conn.cursor()

    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        conn.close()
        return None

    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    invoice_number = f"FAT-{now.strftime('%Y%m%d')}-{order_id:04d}"

    # Përditësojmë porosinë
    cursor.execute(
        "UPDATE orders SET status = 'E Përfunduar', payment_method = ?, updated_at = ? WHERE id = ?",
        (payment_method, now_str, order_id)
    )

    # Krijojmë faturën
    cursor.execute(
        """INSERT OR REPLACE INTO invoices (invoice_number, order_id, total_amount, payment_method, waiter_name, table_number, issued_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (invoice_number, order_id, order["total_amount"], payment_method, order["waiter_name"], order["table_number"], now_str)
    )

    # Lirojmë tavolinën
    cursor.execute("UPDATE restaurant_tables SET status = 'e_lire' WHERE table_number = ?", (order["table_number"],))

    conn.commit()
    conn.close()
    return invoice_number


# ==========================================
# 4. STATISTIKAT DHE RAPORTET
# ==========================================

def get_daily_statistics(target_date: Optional[str] = None) -> Dict[str, Any]:
    """Llogarit statistikat për datën e specifikuar (parazgjedhur: sot)."""
    if not target_date:
        target_date = datetime.now().strftime("%Y-%m-%d")

    conn = get_db_connection()

    # Xhiroja dhe numri i porosive për ditën
    stats = conn.execute(
        """SELECT 
            COUNT(id) as total_orders,
            COALESCE(SUM(total_amount), 0.0) as total_revenue,
            COALESCE(AVG(total_amount), 0.0) as average_order
           FROM orders 
           WHERE date(created_at) = date(?) AND status != 'Anuluar'""",
        (target_date,)
    ).fetchone()

    # Porositë e përfunduara vs aktive
    status_counts = conn.execute(
        """SELECT status, COUNT(id) as count 
           FROM orders 
           WHERE date(created_at) = date(?)
           GROUP BY status""",
        (target_date,)
    ).fetchall()

    # Artikujt më të shitur të ditës
    popular_items = conn.execute(
        """SELECT oi.item_name, SUM(oi.quantity) as total_qty, SUM(oi.subtotal) as total_sum
           FROM order_items oi
           JOIN orders o ON oi.order_id = o.id
           WHERE date(o.created_at) = date(?) AND o.status != 'Anuluar'
           GROUP BY oi.item_name
           ORDER BY total_qty DESC LIMIT 5""",
        (target_date,)
    ).fetchall()

    # Xhiroja dhe porositë sipas secilit kamarier për këtë datë
    waiter_stats = conn.execute(
        """SELECT 
            waiter_name,
            COUNT(id) as total_orders,
            COALESCE(SUM(total_amount), 0.0) as total_sales,
            COALESCE(AVG(total_amount), 0.0) as average_sales
           FROM orders 
           WHERE date(created_at) = date(?) AND status != 'Anuluar'
           GROUP BY waiter_name
           ORDER BY total_sales DESC""",
        (target_date,)
    ).fetchall()

    # Lista e porosive të ditës
    day_orders = conn.execute(
        """SELECT id, table_number, waiter_name, total_amount, status, created_at, payment_method
           FROM orders 
           WHERE date(created_at) = date(?)
           ORDER BY id DESC""",
        (target_date,)
    ).fetchall()

    conn.close()

    return {
        "date": target_date,
        "total_orders": stats["total_orders"],
        "total_revenue": round(stats["total_revenue"], 2),
        "average_order": round(stats["average_order"], 2),
        "status_breakdown": {row["status"]: row["count"] for row in status_counts},
        "popular_items": [dict(p) for p in popular_items],
        "waiter_stats": [dict(w) for w in waiter_stats],
        "orders": [dict(o) for o in day_orders]
    }


def get_all_time_waiter_stats() -> List[Dict[str, Any]]:
    """Kthen statistikat e përgjithshme historike të shitjeve për secilin kamarier."""
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT 
            waiter_name,
            COUNT(id) as total_orders,
            COALESCE(SUM(total_amount), 0.0) as total_sales,
            COALESCE(AVG(total_amount), 0.0) as average_sales,
            MIN(created_at) as first_order,
            MAX(created_at) as last_order
           FROM orders 
           WHERE status != 'Anuluar'
           GROUP BY waiter_name
           ORDER BY total_sales DESC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_order(order_id: int) -> bool:
    """Fshin plotësisht një porosi, artikujt e saj, faturën dhe liron tavolinën."""
    conn = get_db_connection()
    cursor = conn.cursor()

    order = conn.execute("SELECT table_number FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        conn.close()
        return False

    table_no = order["table_number"]

    cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
    cursor.execute("DELETE FROM invoices WHERE order_id = ?", (order_id,))
    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))

    # Kontrollojmë nëse ka porosi të tjera aktive për këtë tavolinë
    active_other = conn.execute(
        "SELECT id FROM orders WHERE table_number = ? AND status NOT IN ('E Përfunduar', 'Anuluar')",
        (table_no,)
    ).fetchone()
    if not active_other:
        cursor.execute("UPDATE restaurant_tables SET status = 'e_lire' WHERE table_number = ?", (table_no,))

    conn.commit()
    conn.close()
    return True


def clear_all_orders() -> bool:
    """Fshin të gjitha porositë, faturat, artikujt e porosive dhe reseton të gjitha tavolinat në të lira."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM order_items")
    cursor.execute("DELETE FROM invoices")
    cursor.execute("DELETE FROM orders")
    cursor.execute("UPDATE restaurant_tables SET status = 'e_lire'")
    # Resetohet edhe auto_increment për porositë që të fillojë nga 1
    cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('orders', 'order_items', 'invoices')")

    conn.commit()
    conn.close()
    return True
