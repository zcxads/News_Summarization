import google.generativeai as genai
import os
from dotenv import load_dotenv
from .database import get_db

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def summarize_article(article_id, title, content):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        prompt = f"""
        다음 인공지능 관련 뉴스 기사를 한국어로 요약해줘.
        - 형식: 한 문장의 제목 + 3개 이내의 핵심 불렛포인트
        - 톤: 객관적이고 전문적인 스타일
        - 가독성을 위해 불렛포인트는 간단명료하게 작성할 것.

        기사 제목: {title}
        기사 내용: {content}
        """

        response = model.generate_content(prompt)
        summary = response.text

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE articles SET summary = ? WHERE id = ?", (summary, article_id))
        conn.commit()
        conn.close()
        
        print(f"Summarized: {title}")
    except Exception as e:
        print(f"Error summarizing article {article_id}: {e}")

def summarize_all_pending():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content FROM articles WHERE summary IS NULL")
    pending = cursor.fetchall()
    conn.close()

    for row in pending:
        summarize_article(row["id"], row["title"], row["content"])

if __name__ == "__main__":
    summarize_all_pending()
