from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
from datetime import datetime
import asyncio
from contextlib import asynccontextmanager

# Import from backend package
from backend.database import init_db, get_today_summarized_news, get_latest_summarized_news
from backend.tasks import setup_scheduler, start_background_tasks

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lifespan context starting...")
    init_db()
    
    # Setup and start scheduler
    scheduler = setup_scheduler()
    
    # Run initial work in background
    asyncio.create_task(start_background_tasks())
    
    yield
    
    print("Shutting down scheduler...")
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from the React build directory
# main.py is now at root.
dist_path = os.path.join(os.getcwd(), "frontend", "dist")

if os.path.exists(dist_path):
    print(f"Serving static files from: {dist_path}")
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")

@app.get("/")
async def read_index():
    index_path = os.path.join(dist_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend not built yet. Run 'npm run build' in frontend directory."}

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    if not request.url.path.startswith("/api"):
        index_path = os.path.join(dist_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    return {"detail": "Not Found"}

@app.get("/api/news")
def get_news():
    today = datetime.now().strftime("%Y.%m.%d")
    
    # Try to get today's news
    news = get_today_summarized_news(today)
    
    # If no news for today, fallback to latest available news
    if not news:
        print("No news for today, fetching latest available news...")
        news = get_latest_summarized_news()
    
    return news

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
