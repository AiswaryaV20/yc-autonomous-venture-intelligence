from apscheduler.schedulers.blocking import BlockingScheduler
from scraper.run_scraper import run_scraper
from agents.task_worker import process_tasks
from agents.trend_detector import detect_trends

scheduler = BlockingScheduler()

def safe_job(job_func, job_name):
    def wrapper():
        print(f"\n--- Running {job_name} ---")
        try:
            job_func()
            print(f"--- Finished {job_name} ---")
        except Exception as e:
            print(f"Error in {job_name}: {e}")
    return wrapper


# Run immediately at startup
safe_job(run_scraper, "Scraper")()
safe_job(process_tasks, "Task Worker")()
safe_job(detect_trends, "Trend Detector")()

# Scheduled jobs
scheduler.add_job(
    safe_job(run_scraper, "Scraper"),
    'interval',
    minutes=30,
    coalesce=True,
    misfire_grace_time=60
)

scheduler.add_job(
    safe_job(process_tasks, "Task Worker"),
    'interval',
    minutes=5,
    coalesce=True,
    misfire_grace_time=60
)

scheduler.add_job(
    safe_job(detect_trends, "Trend Detector"),
    'interval',
    hours=1,
    coalesce=True,
    misfire_grace_time=60
)

print("\n🚀 Autonomous AI system started...")

scheduler.start()