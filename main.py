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

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global scheduler reference
scheduler = None

@app.on_event("startup")
async def startup_event():
    global scheduler
    print("Application startup event triggered")
    init_db()
    
    # Setup scheduler
    scheduler = setup_scheduler()
    
    # Start background task
    print("Starting background task...")
    asyncio.create_task(start_background_tasks())

@app.on_event("shutdown")
async def shutdown_event():
    global scheduler
    if scheduler:
        print("Shutting down scheduler...")
        scheduler.shutdown()

# Determine base paths
base_dir = os.path.dirname(os.path.abspath(__file__))
dist_path = os.path.join(base_dir, "frontend", "dist")

print(f"Current Working Directory: {os.getcwd()}")
print(f"Base Directory: {base_dir}")
print(f"Checking for dist folder at: {dist_path}")

if os.path.exists(dist_path):
    print(f"Serving static files from: {dist_path}")
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")
else:
    print(f"WARNING: Frontend dist folder not found at {dist_path}")

@app.get("/")
async def read_index():
    index_path = os.path.join(dist_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "status": "online",
        "message": "Backend is running, but frontend dist/index.html was not found.",
        "dist_path": dist_path,
        "exists": os.path.exists(dist_path),
        "files_in_frontend": os.listdir(os.path.join(base_dir, "frontend")) if os.path.exists(os.path.join(base_dir, "frontend")) else "frontend dir missing"
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "time": str(datetime.now())}

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    if not request.url.path.startswith("/api"):
        index_path = os.path.join(dist_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    return {"detail": f"Path {request.url.path} Not Found"}

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
