from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from database import get_db, init_db
from crawler import crawl_all
from summarizer import summarize_all_pending
import asyncio

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lifespan context starting...")
    init_db()
    print("Database initialized.")
    # Start scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_job, 'interval', hours=2)
    scheduler.start()
    print("Scheduler started.")
    
    print("Starting initial background task...")
    asyncio.create_task(run_initial_work())
    print("Lifespan setup complete, yielding.")
    yield
    print("Shutting down scheduler...")
    scheduler.shutdown()
    print("Scheduler shut down.")

app = FastAPI(lifespan=lifespan)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from the React build directory
# Note: In production, the "dist" directory will contain the built assets.
if os.path.exists("dist"):
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

@app.get("/")
async def read_index():
    if os.path.exists("dist/index.html"):
        return FileResponse("dist/index.html")
    return {"message": "Frontend not built yet. Run 'npm run build'."}

# Catch-all route for SPA navigation (optional but good practice)
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    if not request.url.path.startswith("/api"):
        if os.path.exists("dist/index.html"):
            return FileResponse("dist/index.html")
    return {"detail": "Not Found"}

async def run_initial_work():
    print("Running initial crawl and summary...")
    crawl_all()
    summarize_all_pending()

def scheduled_job():
    print("Running scheduled crawl and summary...")
    crawl_all()
    summarize_all_pending()

@app.get("/api/news")
def get_news():
    today = datetime.now().strftime("%Y.%m.%d")
    conn = get_db()
    cursor = conn.cursor()
    
    # Try to get today's news
    cursor.execute("SELECT * FROM articles WHERE published_at LIKE ? AND summary IS NOT NULL ORDER BY published_at DESC", (f"{today}%",))
    news = [dict(row) for row in cursor.fetchall()]
    
    # If no news today, get the most recent from yesterday or before
    if not news:
        cursor.execute("SELECT * FROM articles WHERE summary IS NOT NULL ORDER BY published_at DESC")
        news = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return news

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
