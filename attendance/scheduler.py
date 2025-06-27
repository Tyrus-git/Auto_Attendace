# attendance/scheduler.py
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
from django.utils.timezone import now

logger = logging.getLogger(__name__)

def fetch_router_data_job():
    logger.info(f"Running fetch_router_data command at {now()}")
    call_command('fetch_router_data')

def start():
    scheduler = BackgroundScheduler()
    # Schedule job every 1 minute
    scheduler.add_job(fetch_router_data_job, 'interval', minutes=1, id='fetch_router_data_job', replace_existing=True)
    scheduler.start()
    logger.info("Scheduler started.")
