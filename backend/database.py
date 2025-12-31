import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "news.db")

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

def get_today_summarized_news(date_str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles WHERE published_at LIKE ? AND summary IS NOT NULL ORDER BY published_at DESC", (f"{date_str}%",))
    news = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return news

def get_latest_summarized_news(limit=None):
    conn = get_db()
    cursor = conn.cursor()
    if limit:
        cursor.execute("SELECT * FROM articles WHERE summary IS NOT NULL ORDER BY published_at DESC LIMIT ?", (limit,))
    else:
        cursor.execute("SELECT * FROM articles WHERE summary IS NOT NULL ORDER BY published_at DESC")
    news = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return news

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
