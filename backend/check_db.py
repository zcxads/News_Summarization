import sqlite3
import os
from prettytable import PrettyTable
from database import get_db

DB_PATH = os.path.join(os.path.dirname(__file__), "news.db")

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        return

    try:
        conn = get_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Summary statistics
        cursor.execute("SELECT COUNT(*) as total, COUNT(summary) as summarized FROM articles;")
        stats = cursor.fetchone()
        print(f"\n--- Database Summary ---")
        print(f"Total articles: {stats['total']}")
        print(f"Summarized articles: {stats['summarized']}")
        
        # Table view of articles
        cursor.execute("SELECT source, title, published_at, (summary IS NOT NULL) as has_summary FROM articles ORDER BY published_at DESC LIMIT 20;")
        rows = cursor.fetchall()
        
        if rows:
            table = PrettyTable()
            table.field_names = ["Source", "Title", "Published At", "Summarized"]
            table.align["Title"] = "l"  # Align title to the left
            
            for row in rows:
                # Truncate long titles for better display
                title = row['title']
                if len(title) > 50:
                    title = title[:47] + "..."
                
                table.add_row([
                    row['source'],
                    title,
                    row['published_at'],
                    "Yes" if row['has_summary'] else "No"
                ])
            print(f"\n--- Recent Articles (Last 20) ---")
            print(table)
        else:
            print("\nNo articles found in the database.")
            
        conn.close()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    check_db()
