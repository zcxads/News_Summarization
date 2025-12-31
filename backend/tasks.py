from datetime import datetime
from .database import get_db
from apscheduler.schedulers.background import BackgroundScheduler
from .crawler import crawl_all
from .summarizer import summarize_all_pending
import asyncio

def run_initial_work():
    print("Running initial crawl and summary...")
    crawl_all()
    summarize_all_pending()

def scheduled_job():
    print("Running scheduled crawl and summary...")
    crawl_all()
    summarize_all_pending()

def setup_scheduler():
    scheduler = BackgroundScheduler()
    # Run crawl and summary every 2 hours
    scheduler.add_job(scheduled_job, 'interval', hours=2)
    
    # Cleanup job is disabled as per user request
    # scheduler.add_job(cleanup_old_articles, 'cron', hour=0, minute=5)
    
    scheduler.start()
    print("Background scheduler started.")
    return scheduler

async def start_background_tasks():
    print("Starting initial background task in 30 seconds...")
    await asyncio.sleep(30)  # Wait 30 seconds for server to fully start
    run_initial_work()
