#!/usr/bin/env python3
"""
数据库操作模块
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "orders.db"

def get_db():
    """获取数据库连接"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库（如果不存在）"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            budget_min INTEGER,
            budget_max INTEGER,
            deadline TEXT,
            requirement_summary TEXT,
            requirement_detail TEXT,
            attachments TEXT,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            sender TEXT,
            content TEXT,
            attachments TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_order ON messages(order_id)")

    conn.commit()
    conn.close()

def create_order(data: dict) -> int:
    """创建订单"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO orders (client_name, budget_min, budget_max, deadline,
                          requirement_summary, requirement_detail, attachments, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
    """, (
        data.get('client_name'),
        data.get('budget_min'),
        data.get('budget_max'),
        data.get('deadline'),
        data.get('requirement_summary'),
        data.get('requirement_detail'),
        json.dumps(data.get('attachments', []))
    ))

    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return order_id

def get_order(order_id: int) -> dict:
    """获取订单"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None

def list_orders(status: str = None) -> list:
    """列出订单"""
    conn = get_db()
    cursor = conn.cursor()

    if status:
        cursor.execute("SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC", (status,))
    else:
        cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_order_status(order_id: int, status: str) -> bool:
    """更新订单状态"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE orders SET status = ?, updated_at = ? WHERE id = ?
    """, (status, datetime.now().isoformat(), order_id))

    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def add_message(order_id: int, sender: str, content: str, attachments: list = None) -> int:
    """添加消息"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (order_id, sender, content, attachments)
        VALUES (?, ?, ?, ?)
    """, (order_id, sender, content, json.dumps(attachments or [])))

    msg_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return msg_id

def get_messages(order_id: int) -> list:
    """获取订单的所有消息"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM messages WHERE order_id = ? ORDER BY created_at ASC
    """, (order_id,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init_db()
        print("数据库初始化完成")