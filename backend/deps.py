import os
from apscheduler.schedulers.background import BackgroundScheduler
from agents.crew import run_monitoring
import atexit

scheduler = BackgroundScheduler()

def start_jobs():
    # Daily 6AM crawl
    scheduler.add_job(run_monitoring, "cron", hour=6, id="reg_crawl", replace_existing=True)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
