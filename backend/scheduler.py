import time
import schedule
import subprocess

def run_scraper():
    subprocess.run(["python", "backend/main_2.py"], check=True)

schedule.every(30).minutes.do(run_scraper)

if __name__ == "__main__":
    print("Scheduler started. Running every 30 minutes...")
    while True:
        schedule.run_pending()
        time.sleep(10)