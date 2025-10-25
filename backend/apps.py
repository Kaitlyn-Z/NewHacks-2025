# FastAPI backend

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware # to allow requests from React frontend
from pydantic import BaseModel
import sqlite3
# from backend.notifier import send_alert_email: Is this needed?
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server 
    # --> need to to communicate with FastAPI backend (hosted on localhost:8000)
    allow_methods=["*"],
    allow_headers=["*"]
)

class UserPreference(BaseModel): # When a class inherits from pydantic.BaseModel, 
    # it gains the ability to automatically validate incoming data based on the type 
    # annotations provided for its attributes.
    email: str
    alerts: list[str]

def init_db():
    with sqlite3.connect("backend/alerts.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_prefs (
                email TEXT PRIMARY KEY,
                alerts TEXT
            )
        """)
init_db()

# Auto-generates a database (file in directory is alerts.db) to store user preferences for email alerts.

@app.post("/preferences") # (Dropdown menu? Or separate url path?) 
async def save_preferences(pref: UserPreference): # Tells FastAPI what to do when a POST request is recieved
    # UserPreference parses the incoming JSON body from React frontend into an object in Python (defined earlier)
    alerts_str = ",".join(pref.alerts) # joins list into single string so it can be stored more easily
    with sqlite3.connect("backend/alerts.db") as conn: # connects to SQLite database file, alerts.db (in this directory)
        conn.execute("REPLACE INTO user_prefs (email, alerts) VALUES (?, ?)", (pref.email, alerts_str)) # Inserts or updates user preference
        # (Stores email + selected alert levels)
    return {"status": "ok", "message": f"Preferences saved for {pref.email}"} # Confirms to frontend that user preferences are saved

@app.post("/update-preferences")
async def update_preferences(data: dict):
    """Save user alert preferences from frontend (new format)"""
    email = data.get('email')
    preferences = data.get('preferences', {})
    
    if not email:
        return {"status": "error", "message": "Email is required"}
    
    # Convert frontend preferences (high/medium/low booleans) to backend format
    alert_list = []
    if preferences.get('high', False):
        alert_list.append('High Alert')
    if preferences.get('medium', False):
        alert_list.append('Medium Alert')
    if preferences.get('low', False):
        alert_list.append('Low Alert')
    
    alerts_str = ",".join(alert_list)
    
    with sqlite3.connect("backend/alerts.db") as conn:
        conn.execute("REPLACE INTO user_prefs (email, alerts) VALUES (?, ?)", (email, alerts_str))
    
    return {"status": "ok", "message": f"Preferences saved for {email}", "saved_alerts": alerts_str}

@app.get("/preferences/{email}") # GET request to retrieve user preferences based on email
async def get_preferences(email: str):
    with sqlite3.connect("backend/alerts.db") as conn:
        row = conn.execute("SELECT alerts FROM user_prefs WHERE email=?", (email,)).fetchone()
    if row:
        return {"email": email, "alerts": row[0].split(",")}
    else:
        return {"email": email, "alerts": []}
    
@app.get("/latest-alerts") # Uses latest_alerts table in alerts.db
async def latest_alerts():
    conn = sqlite3.connect("backend/alerts.db")
    rows = conn.execute("""
        SELECT Ticker, Close, Volume, volume_z, Volume_Ratio, Volume_Alert, RSI, 
               Price_Change, Sentiment_Score, Mention_Count, Timestamp 
        FROM latest_alerts
    """).fetchall()
    conn.close()
    
    # Map priority names for frontend
    def map_priority(alert_level):
        if 'High' in alert_level:
            return 'high'
        elif 'Medium' in alert_level:
            return 'medium'
        elif 'Low' in alert_level:
            return 'low'
        return 'normal'
    
    # Return data in format matching frontend StockAlert interface
    return [{
        "id": f"{r[0]}-{r[10]}",  # Ticker-Timestamp as ID
        "ticker": r[0],
        "currentPrice": round(r[1], 2) if r[1] else 0,
        "mentionCount": r[9] if r[9] else 0,
        "volumeRatio": round(r[4], 2) if r[4] else 1.0,
        "priceChange": round(r[7], 2) if r[7] else 0,
        "detectedAt": r[10] if r[10] else "",
        "priority": map_priority(r[5]),
        "volumeZScore": round(r[3], 2) if r[3] else 0,
        "rsi": round(r[6], 2) if r[6] else 50,
        "sentimentScore": round(r[8], 2) if r[8] else 0
    } for r in rows]
