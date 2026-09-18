import sqlite3
import os
from pathlib import Path

# Rruga drejt skedarit të bazës së të dhënave
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "restaurant.db"


def get_db_connection():
    """Krijon dhe kthen një lidhje me bazën e të dhënave SQLite."""
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Kthen rreshtat si fjalorë (dict-like)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")  # Optimizim për lexim/shkrim paralel
    return conn


def init_database():
    """Krijon të gjitha tabelat e nevojshme nëse nuk ekzistojnë."""
    # Sigurohemi që ekziston dosja prind
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Tabela e Kategorive
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            color TEXT DEFAULT '#2980b9',
            icon TEXT DEFAULT 'bi-tag',
            display_order INTEGER DEFAULT 0
        );
    """)

    # 2. Tabela e Artikujve të Menysë
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            price REAL NOT NULL,
            stock_quantity INTEGER DEFAULT 100,
            description TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        );
    """)

    # 3. Tabela e Tavolinave
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurant_tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER NOT NULL UNIQUE,
            capacity INTEGER DEFAULT 4,
            section TEXT DEFAULT 'Salla Kryesore',
            status TEXT DEFAULT 'e_lire' -- 'e_lire', 'e_zene', 'e_rezervuar'
        );
    """)

    # 4. Tabela e Përdoruesve / Stafit
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'kamarier', -- 'kamarier', 'kuzhine', 'menaxher'
            pin_code TEXT DEFAULT '1234',
            is_active INTEGER DEFAULT 1
        );
    """)

    # 5. Tabela e Porosive
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER NOT NULL,
            waiter_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'E Re', -- 'E Re', 'Në Përgatitje', 'Gati', 'E Përfunduar'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            payment_method TEXT DEFAULT 'Kesh', -- 'Kesh', 'Kartelë'
            total_amount REAL DEFAULT 0.0,
            notes TEXT DEFAULT ''
        );
    """)

    # 6. Tabela e Artikujve të Porosisë
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            item_id INTEGER,
            item_name TEXT NOT NULL,
            unit_price REAL NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            subtotal REAL NOT NULL,
            notes TEXT DEFAULT '',
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES menu_items(id) ON DELETE SET NULL
        );
    """)

    # 7. Tabela e Faturave të Arkëtuara
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT NOT NULL UNIQUE,
            order_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            waiter_name TEXT NOT NULL,
            table_number INTEGER NOT NULL,
            issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_database()
    print("Baza e të dhënave u inicializua me sukses!")
