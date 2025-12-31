import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "news.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            title TEXT,
            content TEXT,
            url TEXT UNIQUE,
            published_at TEXT,
            summary TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def clear_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles")
    conn.commit()
    conn.close()
    print("Database cleared.")

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
