from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

# Create the scheduler instance
scheduler = BackgroundScheduler()

# Start the scheduler
scheduler.start()