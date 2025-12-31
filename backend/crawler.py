from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from .database import get_db, clear_db

SITEC_CONFIG = {
    "aitimes.kr": {
        "name": "인공지능신문",
        "url": "https://www.aitimes.kr/news/articleList.html?view_type=sm",
        "base": "https://www.aitimes.kr",
        "title_selectors": [".article-head-title", "h1.heading", ".aht-title-view", ".titles h2", ".title"],
        "date_selectors": [".info-text li", ".date-date", ".view-info li"],
        "body_selector": "#article-view-content-div",
        "list_item_selector": "ul.type2 li",
        "list_date_selector": ".byline em:last-child",
    },
    "aitimes.com": {
        "name": "AI타임즈",
        "url": "https://www.aitimes.com/news/articleList.html?view_type=sm",
        "base": "https://www.aitimes.com",
        "title_selectors": [".article-head-title", "h1.heading", ".aht-title-view", ".titles h2", ".title"],
        "date_selectors": [".info-text li", ".date-date", ".view-info li"],
        "body_selector": "#article-view-content-div",
        "list_item_selector": "li.altlist-webzine-item",
        "list_date_selector": ".altlist-info-item:last-child",
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_date(date_str, domain):
    try:
        # Expected format: YYYY-MM-DD
        if domain == "aitimes.kr":
            # 2025.12.30 17:37
            match = re.search(r"(\d{4})\.(\d{2})\.(\d{2})", date_str)
            if match:
                return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        elif domain == "aitimes.com":
            # 12-30 18:00
            match = re.search(r"(\d{2})-(\d{2})", date_str)
            if match:
                year = datetime.now().year
                return f"{year}-{match.group(1)}-{match.group(2)}"
    except Exception as e:
        print(f"Error parsing date {date_str}: {e}")
    return None

def normalize_date(date_str):
    """Normalize various date formats to YYYY.MM.DD HH:MM"""
    if not date_str:
        return datetime.now().strftime("%Y.%m.%d %H:%M")
    
    # Already YYYY.MM.DD HH:MM?
    if re.match(r"\d{4}\.\d{2}\.\d{2}\s\d{2}:\d{2}", date_str):
        return date_str
    
    # 2025.12.30 (without time)
    match = re.search(r"(\d{4})\.(\d{2})\.(\d{2})", date_str)
    if match and ":" not in date_str:
        return f"{match.group(1)}.{match.group(2)}.{match.group(3)} 00:00"

    # 12-31 12:17 (AITimes format)
    match = re.search(r"(\d{2})-(\d{2})\s(\d{2}:\d{2})", date_str)
    if match:
        year = datetime.now().year
        return f"{year}.{match.group(1)}.{match.group(2)} {match.group(3)}"
    
    # 12-31 (AITimes format without time)
    match = re.search(r"(\d{2})-(\d{2})", date_str)
    if match and ":" not in date_str:
        year = datetime.now().year
        return f"{year}.{match.group(1)}.{match.group(2)} 00:00"
        
    return date_str

def crawl_article(url, source, config, list_date=None):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title = ""
        for sel in config["title_selectors"]:
            el = soup.select_one(sel)
            if el:
                text = el.get_text(strip=True)
                if text and len(text) > 5:
                    title = text
                    break
        
        if not title:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text(strip=True).split("<")[0].split("-")[0].strip()

        date_str = ""
        for sel in config["date_selectors"]:
            elements = soup.select(sel)
            for el in elements:
                text = el.get_text(strip=True)
                if "입력" in text or "2025." in text:
                    match = re.search(r"\d{4}\.\d{2}\.\d{2}\s\d{2}:\d{2}", text)
                    if match:
                        date_str = match.group(0)
                        break
            if date_str:
                break
        
        if not date_str and list_date:
            # Use date from list page if extraction from detail page fails
            date_str = list_date

        # Normalize date format for DB consistency
        normalized_date = normalize_date(date_str)

        body_el = soup.select_one(config["body_selector"])
        content = body_el.get_text("\n", strip=True) if body_el else ""

        if not title or not content:
            print(f"Skipping article {url}: Title or Content missing")
            return

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO articles (source, title, content, url, published_at)
            VALUES (?, ?, ?, ?, ?)
        """, (source, title, content, url, normalized_date))
        conn.commit()
        conn.close()
        print(f"Saved: {title} ({normalized_date})")

    except Exception as e:
        print(f"Error crawling article {url}: {e}")

def crawl_all():
    # print("Clearing old articles from database...")
    # clear_db()
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    for domain, config in SITEC_CONFIG.items():
        try:
            print(f"Checking {domain} for articles...")
            response = requests.get(config["url"], headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            items = soup.select(config["list_item_selector"])
            today_articles = []
            yesterday_articles = []
            
            for item in items:
                link_el = item.find("a", href=True)
                date_el = item.select_one(config["list_date_selector"])
                
                if link_el and date_el:
                    href = link_el["href"]
                    full_url = href if href.startswith("http") else config["base"] + href
                    raw_date = date_el.get_text(strip=True)
                    parsed_date = parse_date(raw_date, domain)
                    print(f"[{domain}] Raw date: {raw_date}, Parsed: {parsed_date}")
                    
                    if parsed_date == today_str:
                        today_articles.append((full_url, raw_date))
                    elif parsed_date == yesterday_str:
                        yesterday_articles.append((full_url, raw_date))
            
            # Select target date
            if today_articles:
                print(f"Found {len(today_articles)} articles for today ({today_str})")
                targets = today_articles
            elif yesterday_articles:
                print(f"No articles for today. Found {len(yesterday_articles)} articles for yesterday ({yesterday_str})")
                targets = yesterday_articles
            else:
                print(f"No articles found for today or yesterday for {domain}")
                targets = []
            
            # Efficient Crawling: Check DB before fetching body
            conn = get_db()
            cursor = conn.cursor()
            
            for url, raw_date in targets:
                cursor.execute("SELECT 1 FROM articles WHERE url = ?", (url,))
                if cursor.fetchone():
                    print(f"Skipping (Already exists): {url}")
                    continue
                
                # Fetch and save new article
                crawl_article(url, domain, config, list_date=raw_date)
            
            conn.close()
                
        except Exception as e:
            print(f"Error crawling {domain}: {e}")

if __name__ == "__main__":
    from database import init_db
    init_db()
    crawl_all()

