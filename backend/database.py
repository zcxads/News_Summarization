import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_db():
    """Get a database connection using DATABASE_URL environment variable"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    return conn

def init_db():
    """Initialize the database schema"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            source TEXT,
            title TEXT,
            content TEXT,
            url TEXT UNIQUE,
            published_at TEXT,
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def clear_db():
    """Clear all articles from the database"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles")
    conn.commit()
    conn.close()
    print("Database cleared.")

def get_today_summarized_news(date_str):
    """Get today's summarized news articles"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM articles WHERE published_at LIKE %s AND summary IS NOT NULL ORDER BY published_at DESC",
        (f"{date_str}%",)
    )
    news = cursor.fetchall()
    conn.close()
    return news

def get_latest_summarized_news(limit=None):
    """Get latest summarized news articles"""
    conn = get_db()
    cursor = conn.cursor()
    if limit:
        cursor.execute(
            "SELECT * FROM articles WHERE summary IS NOT NULL ORDER BY published_at DESC LIMIT %s",
            (limit,)
        )
    else:
        cursor.execute("SELECT * FROM articles WHERE summary IS NOT NULL ORDER BY published_at DESC")
    news = cursor.fetchall()
    conn.close()
    return news

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
