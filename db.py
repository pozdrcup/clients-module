# db.py - работа с базой данных

import psycopg2
from config import DB_CONFIG


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """создание таблиц если их нет"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(200) NOT NULL,
            phone VARCHAR(30),
            email VARCHAR(100),
            registration_date DATE DEFAULT CURRENT_DATE,
            notes TEXT
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
            description TEXT NOT NULL,
            amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
            order_date DATE DEFAULT CURRENT_DATE,
            status VARCHAR(30) DEFAULT 'новый'
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


# --- клиенты ---

def add_client(full_name, phone, email, notes=""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO clients (full_name, phone, email, notes) "
        "VALUES (%s, %s, %s, %s) RETURNING id;",
        (full_name, phone, email, notes)
    )
    client_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return client_id


def get_all_clients():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, full_name, phone, email, registration_date, notes "
        "FROM clients ORDER BY id;"
    )
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def search_clients(keyword):
    """поиск по фио, телефону или email"""
    conn = get_connection()
    cur = conn.cursor()
    like = f"%{keyword}%"
    cur.execute(
        "SELECT id, full_name, phone, email, registration_date, notes "
        "FROM clients "
        "WHERE full_name ILIKE %s OR phone ILIKE %s OR email ILIKE %s "
        "ORDER BY id;",
        (like, like, like)
    )
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def update_client(client_id, full_name, phone, email, notes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE clients SET full_name=%s, phone=%s, email=%s, notes=%s "
        "WHERE id=%s;",
        (full_name, phone, email, notes, client_id)
    )
    ok = cur.rowcount > 0
    conn.commit()
    cur.close()
    conn.close()
    return ok


def delete_client(client_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM clients WHERE id=%s;", (client_id,))
    ok = cur.rowcount > 0
    conn.commit()
    cur.close()
    conn.close()
    return ok


# --- заказы ---

def add_order(client_id, description, amount):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (client_id, description, amount) "
        "VALUES (%s, %s, %s) RETURNING id;",
        (client_id, description, amount)
    )
    order_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return order_id


def get_client_orders(client_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, description, amount, order_date, status "
        "FROM orders WHERE client_id=%s ORDER BY order_date DESC;",
        (client_id,)
    )
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def update_order_status(order_id, new_status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE orders SET status=%s WHERE id=%s;",
        (new_status, order_id)
    )
    ok = cur.rowcount > 0
    conn.commit()
    cur.close()
    conn.close()
    return ok


# --- отчеты ---

def report_by_date(date_from, date_to):
    """клиенты зарегистрированные за период"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, full_name, phone, email, registration_date "
        "FROM clients "
        "WHERE registration_date BETWEEN %s AND %s "
        "ORDER BY registration_date;",
        (date_from, date_to)
    )
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def report_summary():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM clients;")
    clients_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders;")
    orders_count = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(amount), 0) FROM orders;")
    total = cur.fetchone()[0]

    cur.close()
    conn.close()
    return {
        "clients": clients_count,
        "orders": orders_count,
        "total_sum": float(total)
    }
