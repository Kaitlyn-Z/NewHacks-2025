from backend.stock_analysis import run_alert_pipeline
import sqlite3

def main():
    # Run pipeline and get DataFrame
    active_alerts_df = run_alert_pipeline(days=1)

    # Save to database or JSON for frontend
    active_alerts_df.to_sql("latest_alerts_dashboard", sqlite3.connect("backend/alerts.db"), if_exists="replace", index=False)
    print("Active alerts updated for dashboard.")

if __name__ == "__main__":
    main()