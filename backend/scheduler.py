from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess

scheduler = BlockingScheduler()

@scheduler.scheduled_job('interval', minutes=30) # every 30 minutes
def run_analysis():
    subprocess.run(["python", "../main_2.py"])

scheduler.start()

# Regularly runs main_2.py every 30 minutes to update alerts.db with latest stock analysis results.